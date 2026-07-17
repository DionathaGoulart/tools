package main

import (
	"bytes"
	"crypto/rand"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/big"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"filippo.io/age"
)

const (
	pubKeyFile    = "key.pub"
	secretKeyFile = "key.age" // age secret key, encrypted with the passphrase (scrypt)
	storeDirName  = "store"
	configFile    = "config.json"
	entryExt      = ".age"
)

var entryNameRe = regexp.MustCompile(`^[a-zA-Z0-9][a-zA-Z0-9._@/-]*$`)

type Config struct {
	Pendrive string `json:"pendrive,omitempty"`
}

type Vault struct {
	Dir       string
	recipient *age.X25519Recipient
	identity  *age.X25519Identity // nil until Unlock
}

func vaultDir() string {
	if d := os.Getenv("COFRE_DIR"); d != "" {
		return d
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ".cofre"
	}
	return filepath.Join(home, ".cofre")
}

func VaultExists() bool {
	_, err := os.Stat(filepath.Join(vaultDir(), pubKeyFile))
	return err == nil
}

// InitVault generates a fresh keypair and writes the vault skeleton.
func InitVault(passphrase string) (*Vault, error) {
	dir := vaultDir()
	if VaultExists() {
		return nil, errors.New("cofre já existe em " + dir)
	}
	id, err := age.GenerateX25519Identity()
	if err != nil {
		return nil, err
	}
	return writeVault(dir, id, passphrase)
}

// RestoreVault imports an existing secret key (e.g. scanned from a QR backup).
func RestoreVault(secretKey, passphrase string) (*Vault, error) {
	dir := vaultDir()
	if VaultExists() {
		return nil, errors.New("cofre já existe em " + dir)
	}
	id, err := age.ParseX25519Identity(strings.TrimSpace(secretKey))
	if err != nil {
		return nil, errors.New("chave inválida — esperava uma linha começando com AGE-SECRET-KEY-1")
	}
	return writeVault(dir, id, passphrase)
}

func writeVault(dir string, id *age.X25519Identity, passphrase string) (*Vault, error) {
	if err := os.MkdirAll(filepath.Join(dir, storeDirName), 0o700); err != nil {
		return nil, err
	}
	if err := os.WriteFile(filepath.Join(dir, pubKeyFile), []byte(id.Recipient().String()+"\n"), 0o600); err != nil {
		return nil, err
	}
	scrypt, err := age.NewScryptRecipient(passphrase)
	if err != nil {
		return nil, err
	}
	enc, err := encryptTo([]byte(id.String()), scrypt)
	if err != nil {
		return nil, err
	}
	if err := os.WriteFile(filepath.Join(dir, secretKeyFile), enc, 0o600); err != nil {
		return nil, err
	}
	return &Vault{Dir: dir, recipient: id.Recipient(), identity: id}, nil
}

func LoadVault() (*Vault, error) {
	dir := vaultDir()
	raw, err := os.ReadFile(filepath.Join(dir, pubKeyFile))
	if err != nil {
		return nil, errors.New("nenhum cofre encontrado — rode: cofre init")
	}
	rec, err := age.ParseX25519Recipient(strings.TrimSpace(string(raw)))
	if err != nil {
		return nil, fmt.Errorf("chave pública corrompida: %w", err)
	}
	return &Vault{Dir: dir, recipient: rec}, nil
}

func (v *Vault) Unlocked() bool { return v.identity != nil }

// Unlock decrypts the secret key with the passphrase and keeps it in memory.
func (v *Vault) Unlock(passphrase string) error {
	if v.identity != nil {
		return nil
	}
	raw, err := os.ReadFile(filepath.Join(v.Dir, secretKeyFile))
	if err != nil {
		return fmt.Errorf("chave secreta não encontrada em %s", v.Dir)
	}
	scrypt, err := age.NewScryptIdentity(passphrase)
	if err != nil {
		return err
	}
	dec, err := decryptWith(raw, scrypt)
	if err != nil {
		return errors.New("passphrase incorreta")
	}
	id, err := age.ParseX25519Identity(strings.TrimSpace(string(dec)))
	if err != nil {
		return fmt.Errorf("chave secreta corrompida: %w", err)
	}
	if id.Recipient().String() != v.recipient.String() {
		return errors.New("chave secreta não corresponde à chave pública do cofre")
	}
	v.identity = id
	return nil
}

func (v *Vault) SecretKey() (string, error) {
	if v.identity == nil {
		return "", errors.New("cofre trancado")
	}
	return v.identity.String(), nil
}

func (v *Vault) PublicKey() string { return v.recipient.String() }

func (v *Vault) storePath() string { return filepath.Join(v.Dir, storeDirName) }

func (v *Vault) entryPath(name string) (string, error) {
	if !entryNameRe.MatchString(name) || strings.Contains(name, "..") {
		return "", fmt.Errorf("nome inválido: %q (use letras, números, . _ - @ /)", name)
	}
	return filepath.Join(v.storePath(), filepath.FromSlash(name)+entryExt), nil
}

func (v *Vault) List() ([]string, error) {
	var names []string
	root := v.storePath()
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, entryExt) {
			return err
		}
		rel, _ := filepath.Rel(root, path)
		names = append(names, filepath.ToSlash(strings.TrimSuffix(rel, entryExt)))
		return nil
	})
	sort.Strings(names)
	return names, err
}

// Set encrypts and stores an entry. Only needs the PUBLIC key — no unlock required.
func (v *Vault) Set(name, content string) error {
	path, err := v.entryPath(name)
	if err != nil {
		return err
	}
	enc, err := encryptTo([]byte(content), v.recipient)
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	return os.WriteFile(path, enc, 0o600)
}

// Get decrypts an entry. Requires Unlock first.
func (v *Vault) Get(name string) (string, error) {
	if v.identity == nil {
		return "", errors.New("cofre trancado — passphrase necessária")
	}
	path, err := v.entryPath(name)
	if err != nil {
		return "", err
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		return "", fmt.Errorf("senha '%s' não existe", name)
	}
	dec, err := decryptWith(raw, v.identity)
	if err != nil {
		return "", fmt.Errorf("falha ao descriptografar '%s': %w", name, err)
	}
	return string(dec), nil
}

func (v *Vault) Delete(name string) error {
	path, err := v.entryPath(name)
	if err != nil {
		return err
	}
	if _, err := os.Stat(path); err != nil {
		return fmt.Errorf("senha '%s' não existe", name)
	}
	return os.Remove(path)
}

func (v *Vault) LoadConfig() Config {
	var c Config
	raw, err := os.ReadFile(filepath.Join(v.Dir, configFile))
	if err == nil {
		_ = json.Unmarshal(raw, &c)
	}
	return c
}

func (v *Vault) SaveConfig(c Config) {
	raw, _ := json.MarshalIndent(c, "", "  ")
	_ = os.WriteFile(filepath.Join(v.Dir, configFile), raw, 0o600)
}

// ── crypto helpers ─────────────────────────────────────────────────────

func encryptTo(data []byte, r age.Recipient) ([]byte, error) {
	var buf bytes.Buffer
	w, err := age.Encrypt(&buf, r)
	if err != nil {
		return nil, err
	}
	if _, err := w.Write(data); err != nil {
		return nil, err
	}
	if err := w.Close(); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func decryptWith(data []byte, ids ...age.Identity) ([]byte, error) {
	r, err := age.Decrypt(bytes.NewReader(data), ids...)
	if err != nil {
		return nil, err
	}
	return io.ReadAll(r)
}

// GeneratePassword returns a cryptographically random password.
func GeneratePassword(length int, symbols bool) string {
	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	if symbols {
		charset += "!@#$%^&*()-_=+[]{}<>?"
	}
	out := make([]byte, length)
	for i := range out {
		n, _ := rand.Int(rand.Reader, big.NewInt(int64(len(charset))))
		out[i] = charset[n.Int64()]
	}
	return string(out)
}
