package main

import (
	"dockerproxy/sandboxes"
	"dockerproxy/utils"
	"encoding/json"
	"log"
	"net/http"

	moby "github.com/moby/moby/client"
)

type Payload struct {
	Code string `json:"code"`
}

func main(){
	docker, err := moby.New(moby.FromEnv)

	if err != nil {
		panic(err)
	}

	py_sandbox := sandboxes.NewPySandbox(docker, utils.NewUIDPicker())
	js_sandbox := sandboxes.NewJSSandbox(docker, utils.NewUIDPicker())
	cpp_sandbox := sandboxes.NewCppSandbox(docker, utils.NewUIDPicker())

	http.HandleFunc("POST /{language}/exec", func(w http.ResponseWriter, r *http.Request) {
		language := r.PathValue("language")
		var body Payload

		err := json.NewDecoder(r.Body).Decode(&body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			log.Fatal(err.Error())
			return
		}

		var output *sandboxes.ExecutionOutput
		switch language{
			case "js":
				output, err = js_sandbox.ExecuteCode(body.Code)
			case "cpp":
				output, err = cpp_sandbox.ExecuteCode(body.Code)
			case "py":
				output, err = py_sandbox.ExecuteCode(body.Code)
			default:
				http.Error(w, "Invalid language", http.StatusBadRequest)
		}

		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return 
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)

		if err := json.NewEncoder(w).Encode(output); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	err = http.ListenAndServe(":1337", nil)
	log.Fatal(err)
}
