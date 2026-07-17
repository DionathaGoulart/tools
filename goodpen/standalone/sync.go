package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// Sync strategy: the pendrive holds a mirror at <pendrive>/cofre/.
// Push copies local → pendrive, pull copies pendrive → local.
// Both directions are a union merge: a file is copied when it's missing on
// the destination or the source copy is newer. Nothing is ever deleted.
// Mtimes are preserved so "newer wins" works across machines; FAT32 stores
// mtimes with 2s resolution, so comparisons use a 2s tolerance.

const mtimeSlack = 2 * time.Second

type syncResult struct {
	Copied  int
	Skipped int
}

func remoteDir(pendrive string) string { return filepath.Join(pendrive, "cofre") }

func (v *Vault) Push(pendrive string) (syncResult, error) {
	dst := remoteDir(pendrive)
	if err := os.MkdirAll(filepath.Join(dst, storeDirName), 0o755); err != nil {
		return syncResult{}, err
	}
	// public key travels with the backup (harmless); the SECRET key never does
	if err := copyFile(filepath.Join(v.Dir, pubKeyFile), filepath.Join(dst, pubKeyFile)); err != nil {
		return syncResult{}, err
	}
	return mergeDir(v.storePath(), filepath.Join(dst, storeDirName))
}

func (v *Vault) Pull(pendrive string) (syncResult, error) {
	src := filepath.Join(remoteDir(pendrive), storeDirName)
	if _, err := os.Stat(src); err != nil {
		return syncResult{}, fmt.Errorf("nenhum backup do cofre em %s", pendrive)
	}
	return mergeDir(src, v.storePath())
}

func mergeDir(src, dst string) (syncResult, error) {
	var res syncResult
	err := filepath.WalkDir(src, func(path string, d os.DirEntry, err error) error {
		if err != nil || d.IsDir() || !strings.HasSuffix(path, entryExt) {
			return err
		}
		rel, _ := filepath.Rel(src, path)
		target := filepath.Join(dst, rel)
		srcInfo, err := os.Stat(path)
		if err != nil {
			return err
		}
		if dstInfo, err := os.Stat(target); err == nil {
			if !srcInfo.ModTime().After(dstInfo.ModTime().Add(mtimeSlack)) {
				res.Skipped++
				return nil
			}
		}
		if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
			return err
		}
		if err := copyFile(path, target); err != nil {
			return err
		}
		res.Copied++
		return nil
	})
	return res, err
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return err
	}
	if _, err := io.Copy(out, in); err != nil {
		out.Close()
		return err
	}
	if err := out.Close(); err != nil {
		return err
	}
	if info, err := os.Stat(src); err == nil {
		_ = os.Chtimes(dst, info.ModTime(), info.ModTime())
	}
	return nil
}
