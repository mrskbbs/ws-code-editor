package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

type Payload struct {
	Code string `json:"code"`
}

func main(){
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
				fmt.Fprint(w, "js", body.Code)
			case "cpp":
				fmt.Fprint(w, "cpp", body.Code)
			case "py":
				fmt.Fprint(w, "py", body.Code)
			default:
				http.Error(w, "Invalid language", 400)
		}
	})

	err := http.ListenAndServe(":8080", nil)
	log.Fatal(err)
}
