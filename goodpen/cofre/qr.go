package main

import (
	"fmt"
	"os"

	"github.com/mdp/qrterminal/v3"
	qrcode "github.com/skip2/go-qrcode"
)

func showQRTerminal(content string) {
	qrterminal.GenerateHalfBlock(content, qrterminal.L, os.Stdout)
}

func saveQRPNG(content, path string) error {
	if err := qrcode.WriteFile(content, qrcode.Medium, 512, path); err != nil {
		return fmt.Errorf("falha ao salvar PNG: %w", err)
	}
	return nil
}
