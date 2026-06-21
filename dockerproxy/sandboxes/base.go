package sandboxes

import (
	"context"
	moby "github.com/moby/moby/client"
)

type LanguageSandbox interface {
	Init(client *moby.Client)
	Exec() ExecutionOutput
}

type BaseLanguageSandbox struct {
	docker *moby.Client
	ctx context.Context
}

func (b *BaseLanguageSandbox) Init(client *moby.Client) {
	b.docker = client
	b.ctx = context.Background()
}
