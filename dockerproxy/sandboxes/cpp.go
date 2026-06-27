package sandboxes

import (
	"fmt"
	"github.com/google/uuid"
	"dockerproxy/utils"
	moby "github.com/moby/moby/client"
)

type CppSandbox struct { BaseLanguageSandbox }

func (s *CppSandbox) ExecuteCode(code string) (*ExecutionOutput, error) {
	uid, err := s.uidPicker.Pick()

	if err != nil {
		return nil, err
	}

	defer s.uidPicker.Release(uid)

	file_id := uuid.New().String()
	filename := fmt.Sprintf("%s.cpp", file_id)
	
	if err := s.copyCodeToContainer(filename, code, uid); err != nil {
		return nil, err
	}

	output, err := s.executeSandboxedCmd(
		[]string{"bash", "-c", fmt.Sprintf("g++ %[1]s -o %[2]s && ./%[2]s", filename, file_id)},
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

func NewCppSandbox(client *moby.Client, uidPicker *utils.UIDPicker) *CppSandbox{
	sandbox := CppSandbox{}
	sandbox.container_name = "cpp-sandbox"
	sandbox.init(client, uidPicker)
	return &sandbox
}
