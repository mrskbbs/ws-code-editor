package sandboxes

import (
	"fmt"
	"github.com/google/uuid"
	"dockerproxy/utils"
	moby "github.com/moby/moby/client"
)

type PySandbox struct { BaseLanguageSandbox }

func (s *PySandbox) ExecuteCode(code string) (*ExecutionOutput, error) {
	uid, err := s.uidPicker.Pick()

	if err != nil {
		return nil, err
	}

	defer s.uidPicker.Release(uid)

	file_id := uuid.New().String()
	filename := fmt.Sprintf("%s.py", file_id)
	
	if err := s.copyCodeToContainer(filename, code, uid); err != nil {
		return nil, err
	}

	output, err := s.executeSandboxedCmd(
		[]string{"bash", "-c", fmt.Sprintf("python %[1]s", filename)},
		uid,
	)	

	if err != nil {
		return nil, err
	}

	if err := s.cleanupCodeOnContainer(file_id); err != nil {
		return nil, err
	}

	return output, nil
}

func NewPySandbox(client *moby.Client, uidPicker *utils.UIDPicker) *PySandbox{
	sandbox := PySandbox{}
	sandbox.container_name = "py-sandbox"
	sandbox.init(client, uidPicker)
	return &sandbox
}
