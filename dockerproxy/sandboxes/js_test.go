package sandboxes

import (
	"dockerproxy/utils"
	"testing"
	"strings"

	moby "github.com/moby/moby/client"
)

func TestJSSuccessfullRun (t *testing.T) {
	docker, err := moby.New(moby.FromEnv)

	if err != nil {
		t.Fatal(err)
	}

	sandbox := NewJSSandbox(docker, utils.NewUIDPicker())

	output, err := sandbox.ExecuteCode(`
		let a = 20;
		console.log(a * 3 + 3);
	`)

	if err != nil {
		t.Fatal(err)
	}

	if !(strings.TrimSpace(output.Stdout) == "63" && strings.TrimSpace(output.Stderr) == "") {
		t.Fatalf("Invalid output\nStdout: %s\nStderr: %s", output.Stdout, output.Stderr)
	}
}

func TestJSUnsuccesfullRun (t *testing.T) {
	docker, err := moby.New(moby.FromEnv)

	if err != nil {
		t.Fatal(err)
	}

	sandbox := NewJSSandbox(docker, utils.NewUIDPicker())

	output, err := sandbox.ExecuteCode(`
		console.log(a * 3 + 3);
	`)

	if err != nil {
		t.Fatal(err)
	}

	if !(strings.TrimSpace(output.Stderr) != "" && strings.TrimSpace(output.Stdout) == "") {
		t.Fatalf("Invalid output\nStdout: %s\nStderr: %s", output.Stdout, output.Stderr)
	}
}
