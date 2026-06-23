package sandboxes

import (
	"bytes"
	"dockerproxy/utils"
	"fmt"
	"github.com/google/uuid"
	"github.com/moby/moby/api/pkg/stdcopy"
	moby "github.com/moby/moby/client"
)

type PySandbox struct { BaseLanguageSandbox }

func (s *PySandbox) Exec(code string) (*ExecutionOutput, error) {
	name := fmt.Sprintf("%s.py", uuid.New().String())

	tar_reader, err := utils.TarFile(name, code)

	if err != nil {
		return nil, err
	}

	if _, err := s.docker.CopyToContainer(s.ctx, "py-sandbox", moby.CopyToContainerOptions{
		DestinationPath: "/home/sandbox",
		Content: tar_reader,
		CopyUIDGID: true,
	}); err != nil {
		return nil, err
	}

	exec_res, err := s.docker.ExecCreate(s.ctx, "py-sandbox", moby.ExecCreateOptions{
		Cmd: []string{"bash", "-c", fmt.Sprintf("python %[1]s && rm -f %[1]s", name)},
		AttachStdin: true,
		AttachStdout: true,
		AttachStderr: true,
		TTY: true,
		User: "sandbox",
		WorkingDir: "/home/sandbox",
	})

	if err != nil {
		return nil, err
	}

	hijack, err := s.docker.ExecAttach(s.ctx, exec_res.ID, moby.ExecAttachOptions{})
	if err != nil {
		return nil, err
	}

	defer hijack.Close()

	var stdout_raw, stderr_raw bytes.Buffer

	if _, err := stdcopy.StdCopy(&stdout_raw, &stderr_raw, hijack.Reader); err != nil {
		return nil, err
	}

	stdout := stdout_raw.String()
	stderr := stderr_raw.String()

	return &ExecutionOutput{
		Stdout: stdout,
		Stderr: stderr,
	}, nil
}
