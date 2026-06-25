package sandboxes

import (
	"bytes"
	"context"
	"dockerproxy/utils"
	"fmt"
	"archive/tar"

	"github.com/moby/moby/api/pkg/stdcopy"

	moby "github.com/moby/moby/client"
)

type LanguageSandbox interface {
	Init(client *moby.Client)
	ExecuteCode(code string) (*ExecutionOutput, error)

	executeSandboxedCmd(cmd []string) (*ExecutionOutput, error)
	copyCodeToContainer(filename, code string) error
	cleanupCodeOnContainer(id string) error
}

type BaseLanguageSandbox struct {
	docker *moby.Client
	ctx context.Context
	container_name string
	uidPicker *utils.UIDPicker
}

func (b *BaseLanguageSandbox) Init(client *moby.Client, uidPicker *utils.UIDPicker) {
	b.docker = client
	b.ctx = context.Background()
	b.uidPicker = uidPicker
}

func (b *BaseLanguageSandbox) copyCodeToContainer(filename string, code string, random_id int) error {
	tar_reader, err := utils.TarFile(
		filename,
		code,
		&tar.Header{
			Name: filename,
			Mode: 0500,
			Uid: random_id,
			Gid: random_id,
			Size: int64(len(code)),
		},
	)

	if err != nil {
		return err
	}
	
	if _, err := b.docker.CopyToContainer(
		b.ctx, 
		b.container_name,
		moby.CopyToContainerOptions{
			DestinationPath: "/sandbox",
			Content: tar_reader,
			CopyUIDGID: false,
		},
	); err != nil {
		return err
	}

	return nil
}

func (b *BaseLanguageSandbox) cleanupCodeOnContainer(id string) error {
	exec_res, err := b.docker.ExecCreate(
		b.ctx, 
		b.container_name, 
		moby.ExecCreateOptions{
			Cmd: []string{"bash", "-c", fmt.Sprintf("rm -f %s*", id)},
			User: "root",
			WorkingDir: "/sandbox",
		},
	)

	if err != nil {
		return  err
	}

	if _, err := b.docker.ExecStart(
		b.ctx, 
		exec_res.ID, 
		moby.ExecStartOptions{},
	); err != nil {
		return  err
	}

	return nil
}

func (b *BaseLanguageSandbox) executeSandboxedCmd (cmd []string, random_id int) (*ExecutionOutput, error) {
	exec_res, err := b.docker.ExecCreate(
		b.ctx, 
		b.container_name, 
		moby.ExecCreateOptions{
			Cmd: cmd,
			AttachStdin: true,
			AttachStdout: true,
			AttachStderr: true,
			TTY: true,
			User: fmt.Sprintf("%[1]d:%[1]d", random_id),
			WorkingDir: "/sandbox",
		},
	)

	if err != nil {
		return nil, err
	}

	hijack, err := b.docker.ExecAttach(b.ctx, exec_res.ID, moby.ExecAttachOptions{})
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

	return  &ExecutionOutput{
		Stdout: stdout,
		Stderr: stderr,
	}, nil
}
