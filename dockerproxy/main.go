package main

import (
	"dockerproxy/sandboxes"
	"dockerproxy/utils"
	"encoding/json"
	"fmt"
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
			http.Error(w, err.Error(), 400)
			log.Fatal(err.Error())
			return
		}

		switch language{
			case "js":
				output, err := js_sandbox.ExecuteCode(body.Code)

				if err != nil {
					http.Error(w, err.Error(), 500)
					return 
				}

				fmt.Fprint(w, "js", output.Stdout)
			case "cpp":
				output, err := cpp_sandbox.ExecuteCode(body.Code)

				if err != nil {
					http.Error(w, err.Error(), 500)
					return 
				}

				fmt.Fprint(w, "cpp", output.Stdout)
			case "py":
				output, err := py_sandbox.ExecuteCode(body.Code)

				if err != nil {
					http.Error(w, err.Error(), 500)
					return 
				}

				fmt.Fprint(w, "py", output.Stdout)
			default:
				http.Error(w, "Invalid language", 400)
		}
	})

	err = http.ListenAndServe(":8080", nil)
	log.Fatal(err)
}
