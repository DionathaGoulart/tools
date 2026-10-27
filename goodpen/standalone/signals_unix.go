//go:build !windows

package main

import (
	"os"
	"syscall"
)

func menuSignals() []os.Signal {
	return []os.Signal{os.Interrupt, syscall.SIGTERM, syscall.SIGHUP}
}

func menuSignalExitCode(s os.Signal) int {
	if numero, ok := s.(syscall.Signal); ok {
		return 128 + int(numero)
	}
	return 1
}
