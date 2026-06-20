package sandboxes

type ExecutionOutput struct {
	stdout string
	stderr string
}

type LanguageSandbox interface {
	Init() 
	Exec() ExecutionOutput
}

type BaseLanguageSandbox struct {
	docker string
}
func (b BaseLanguageSandbox) Init() {

}
