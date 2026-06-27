package utils

import (
	"testing"
)


func TestUidPicker (t *testing.T) {
	picker := NewUIDPicker()

	uid, err := picker.Pick()

	if err != nil {
		t.Fatal(err)
	}

	if !picker.used[uid] {
		t.Fatalf("Uid was not marked as used")
	}

	picker.Release(uid)

	if picker.used[uid] {
		t.Fatalf("Uid was not properly released")
	}
}
