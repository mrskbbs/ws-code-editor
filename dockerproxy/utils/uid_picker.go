package utils

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"sync"
)

const (
	uidMin = 10000
	uidMax = 60000
)

type UIDPicker struct {
	mu   sync.Mutex
	used map[int]bool
}

func NewUIDPicker() *UIDPicker {
	return &UIDPicker{used: make(map[int]bool)}
}

func (p *UIDPicker) Pick() (int, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	span := uidMax - uidMin + 1
	if len(p.used) >= span {
		return 0, fmt.Errorf("uid pool exhausted (%d in use)", len(p.used))
	}

	for {
		n, err := rand.Int(rand.Reader, big.NewInt(int64(span)))
		if err != nil {
			return 0, err
		}
		uid := uidMin + int(n.Int64())
		if !p.used[uid] {
			p.used[uid] = true
			return uid, nil
		}
	}
}

func (p *UIDPicker) Release(uid int) {
	p.mu.Lock()
	defer p.mu.Unlock()
	delete(p.used, uid)
}
