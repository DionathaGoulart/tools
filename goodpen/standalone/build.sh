#!/usr/bin/env bash
# build.sh — cross-compila o cofre pra todas as plataformas em dist/
# Requer Go instalado. Uso:  bash build.sh
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p dist
FLAGS=(-trimpath -ldflags "-s -w")

echo "→ macOS (Apple Silicon)"
GOOS=darwin GOARCH=arm64 go build "${FLAGS[@]}" -o dist/cofre-mac-m1 .
echo "→ macOS (Intel)"
GOOS=darwin GOARCH=amd64 go build "${FLAGS[@]}" -o dist/cofre-mac-intel .
echo "→ Linux (amd64)"
GOOS=linux GOARCH=amd64 go build "${FLAGS[@]}" -o dist/cofre-linux .
echo "→ Windows (amd64)"
GOOS=windows GOARCH=amd64 go build "${FLAGS[@]}" -o dist/cofre-windows.exe .

echo
ls -lh dist/
