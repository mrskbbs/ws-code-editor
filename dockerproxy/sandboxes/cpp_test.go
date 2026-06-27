package sandboxes

import (
	"dockerproxy/utils"
	"strings"
	"testing"

	moby "github.com/moby/moby/client"
)

func TestCppSuccessfullRun (t *testing.T) {
	docker, err := moby.New(moby.FromEnv)

	if err != nil {
		t.Fatal(err)
	}

	sandbox := NewCppSandbox(docker, utils.NewUIDPicker())

	output, err := sandbox.ExecuteCode(`
		#include <iostream>

		using namespace std;

		int main(){
			int a = 20;
			cout << a * 3 + 3 << endl;
			return 0;
		}
	`)

	if err != nil {
		t.Fatal(err)
	}

	if !(strings.TrimSpace(output.Stdout) == "63" && strings.TrimSpace(output.Stderr) == "") {
		t.Fatalf("Invalid output\nStdout: %s\nStderr: %s", output.Stdout, output.Stderr)
	}
}

func TestCppUnsuccesfullRun (t *testing.T) {
	docker, err := moby.New(moby.FromEnv)

	if err != nil {
		t.Fatal(err)
	}

	sandbox := NewCppSandbox(docker, utils.NewUIDPicker())

	output, err := sandbox.ExecuteCode(`
		#include <iostream>

		using namespace std;

		int main(){
			cout << 20 * 3 + 3 << ;
			return 0;
		}
	`)

	if err != nil {
		t.Fatal(err)
	}

	if !(strings.TrimSpace(output.Stderr) != "" && strings.TrimSpace(output.Stdout) == "") {
		t.Fatalf("Invalid output\nStdout: %s\nStderr: %s", output.Stdout, output.Stderr)
	}
}
