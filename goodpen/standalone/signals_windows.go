//go:build windows

package main

import "os"

func menuSignals() []os.Signal { return []os.Signal{os.Interrupt} }

func menuSignalExitCode(os.Signal) int { return 130 }
