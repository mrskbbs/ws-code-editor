package main

import (
	"fmt"
	"log"
	"net/http"
	moby "github.com/moby/moby/client"
	"dockerproxy/sandboxes"
	"encoding/json"
)

type Payload struct {
	Code string `json:"code"`
}

func main(){
	docker, err := moby.New(moby.FromEnv)

	if err != nil {
		panic(err)
	}

	py_sandbox := sandboxes.PySandbox{}
	py_sandbox.Init(docker)

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
				fmt.Fprint(w, "js")
			case "cpp":
				fmt.Fprint(w, "cpp")
			case "py":
				output, err := py_sandbox.Exec(body.Code)

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
