package handlers

import (
	"fmt" 
	"net/http"
)

func GetSandboxes(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "welcome to website")
}

