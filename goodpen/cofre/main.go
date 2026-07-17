package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/atotto/clipboard"
	"golang.org/x/term"
)

const (
	cReset = "\033[0m"
	cBold  = "\033[1m"
	cCyan  = "\033[36m"
	cGreen = "\033[32m"
	cRed   = "\033[31m"
	cGray  = "\033[90m"
)

var stdin = bufio.NewReader(os.Stdin)

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		runMenu()
		return
	}
	switch args[0] {
	case "init":
		cmdInit()
	case "restore", "restaurar":
		cmdRestore()
	case "ls", "list", "listar":
		withVault(func(v *Vault) { cmdList(v) })
	case "add", "nova":
		requireArg(args, "cofre add <nome>")
		withVault(func(v *Vault) { cmdAdd(v, args[1]) })
	case "gen", "gerar":
		requireArg(args, "cofre gen <nome> [tamanho]")
		n := 20
		if len(args) > 2 {
			if x, err := strconv.Atoi(args[2]); err == nil {
				n = x
			}
		}
		withVault(func(v *Vault) { cmdGen(v, args[1], n) })
	case "get", "ver":
		requireArg(args, "cofre get <nome>")
		withVault(func(v *Vault) { cmdGet(v, args[1], false) })
	case "cp", "copiar":
		requireArg(args, "cofre cp <nome>")
		withVault(func(v *Vault) { cmdGet(v, args[1], true) })
	case "rm", "apagar":
		requireArg(args, "cofre rm <nome>")
		withVault(func(v *Vault) { cmdDelete(v, args[1]) })
	case "push", "enviar":
		withVault(func(v *Vault) { cmdSync(v, argOr(args, 1, ""), true) })
	case "pull", "puxar":
		withVault(func(v *Vault) { cmdSync(v, argOr(args, 1, ""), false) })
	case "frase", "passphrase":
		fmt.Println("Sugestões de passphrase (escolha uma e decore — nada é salvo):")
		for i := 0; i < 3; i++ {
			fmt.Println("  " + GeneratePassphrase(5))
		}
		fmt.Printf("%s(~%d bits de entropia cada)%s\n", cGray, PassphraseEntropyBits(5), cReset)
	case "qr", "chave":
		withVault(func(v *Vault) { cmdExportKey(v) })
	case "web", "janela":
		withVault(func(v *Vault) {
			if err := runWeb(v); err != nil {
				die(err.Error())
			}
		})
	case "help", "-h", "--help", "ajuda":
		printHelp()
	default:
		// convenience: `cofre nubank` == `cofre get nubank`
		withVault(func(v *Vault) { cmdGet(v, args[0], false) })
	}
}

func printHelp() {
	fmt.Print(cBold + "cofre" + cReset + " — gerenciador de senhas em um único arquivo (age + pendrive)\n\n" +
		"  cofre                menu interativo\n" +
		"  cofre web            abre a interface no navegador\n" +
		"  cofre init           cria um cofre novo\n" +
		"  cofre restore        restaura de um backup de chave (QR/arquivo)\n\n" +
		"  cofre ls             lista as senhas\n" +
		"  cofre add <nome>     salva uma senha (digitada)\n" +
		"  cofre gen <nome> [n] gera senha aleatória de n caracteres (padrão 20)\n" +
		"  cofre get <nome>     mostra uma senha\n" +
		"  cofre cp <nome>      copia pro clipboard (limpa em 45s)\n" +
		"  cofre rm <nome>      apaga uma senha\n\n" +
		"  cofre push [dir]     envia backup pro pendrive\n" +
		"  cofre pull [dir]     puxa do pendrive\n" +
		"  cofre qr             exporta a chave secreta (QR / arquivo)\n" +
		"  cofre frase          sugere passphrases fortes (diceware PT-BR)\n")
}

// ── interactive menu ───────────────────────────────────────────────────

func runMenu() {
	if !VaultExists() {
		firstRun()
		return
	}
	v, err := LoadVault()
	if err != nil {
		die(err.Error())
	}
	for {
		names, _ := v.List()
		fmt.Printf("\n%s🔐 cofre%s %s— %d senha(s)%s\n\n", cBold, cReset, cGray, len(names), cReset)
		fmt.Println("  1) listar      2) ver         3) copiar     4) nova senha")
		fmt.Println("  5) gerar       6) apagar")
		fmt.Println("  7) enviar pro pendrive        8) puxar do pendrive")
		fmt.Println("  9) exportar chave (backup)    w) abrir no navegador")
		fmt.Println("  0) sair")
		switch strings.ToLower(readLine("\n> ")) {
		case "1":
			cmdList(v)
		case "2":
			cmdGet(v, readLine("nome: "), false)
		case "3":
			cmdGet(v, readLine("nome: "), true)
		case "4":
			cmdAdd(v, readLine("nome (ex: banco/nubank): "))
		case "5":
			cmdGen(v, readLine("nome: "), 20)
		case "6":
			cmdDelete(v, readLine("nome: "))
		case "7":
			cmdSync(v, "", true)
		case "8":
			cmdSync(v, "", false)
		case "9":
			cmdExportKey(v)
		case "w":
			if err := runWeb(v); err != nil {
				fail(err.Error())
			}
		case "0", "q", "sair":
			return
		}
	}
}

func firstRun() {
	fmt.Printf("\n%s🔐 cofre%s — nenhum cofre encontrado nesta máquina.\n\n", cBold, cReset)
	fmt.Println("  1) criar um cofre NOVO")
	fmt.Println("  2) restaurar de um backup (tenho minha chave AGE-SECRET-KEY)")
	fmt.Println("  0) sair")
	switch readLine("\n> ") {
	case "1":
		cmdInit()
	case "2":
		cmdRestore()
	}
}

// ── commands ───────────────────────────────────────────────────────────

func cmdInit() {
	fmt.Println("\nSua " + cBold + "passphrase" + cReset + " é a única senha que você decora.")
	fmt.Println("Dica: 4 palavras aleatórias (ex: cavalo-bateria-grampo-correto)")
	pass := readSecretConfirm()
	v, err := InitVault(pass)
	if err != nil {
		die(err.Error())
	}
	ok("Cofre criado em " + v.Dir)
	fmt.Println("\n" + cBold + "⚠ FAÇA O BACKUP DA CHAVE AGORA." + cReset)
	fmt.Println("Sem ele, perder este computador = perder todas as senhas.")
	cmdExportKey(v)
}

func cmdRestore() {
	fmt.Println("\nCole sua chave secreta (a linha AGE-SECRET-KEY-1... do QR/arquivo):")
	key := readLine("> ")
	fmt.Println("\nAgora crie a passphrase pra proteger a chave NESTA máquina:")
	pass := readSecretConfirm()
	v, err := RestoreVault(key, pass)
	if err != nil {
		die(err.Error())
	}
	ok("Chave restaurada. Cofre pronto em " + v.Dir)
	fmt.Println("Agora puxe suas senhas do pendrive:  " + cCyan + "cofre pull" + cReset)
}

func cmdList(v *Vault) {
	names, err := v.List()
	if err != nil {
		fail(err.Error())
		return
	}
	if len(names) == 0 {
		fmt.Println(cGray + "(cofre vazio — salve com: cofre add <nome>)" + cReset)
		return
	}
	for _, n := range names {
		fmt.Println("  " + n)
	}
}

func cmdAdd(v *Vault, name string) {
	if name == "" {
		fail("nome vazio")
		return
	}
	pw := readSecret("senha pra '" + name + "': ")
	if pw == "" {
		fail("senha vazia — nada salvo")
		return
	}
	if err := v.Set(name, pw); err != nil {
		fail(err.Error())
		return
	}
	ok("salvo: " + name)
}

func cmdGen(v *Vault, name string, length int) {
	if name == "" {
		fail("nome vazio")
		return
	}
	pw := GeneratePassword(length, true)
	if err := v.Set(name, pw); err != nil {
		fail(err.Error())
		return
	}
	ok(fmt.Sprintf("gerada e salva: %s (%d caracteres)", name, length))
	copyToClipboard(pw)
}

func cmdGet(v *Vault, name string, toClipboard bool) {
	if name == "" {
		fail("nome vazio")
		return
	}
	if err := unlockInteractive(v); err != nil {
		fail(err.Error())
		return
	}
	content, err := v.Get(name)
	if err != nil {
		fail(err.Error())
		return
	}
	if toClipboard {
		copyToClipboard(strings.SplitN(content, "\n", 2)[0])
	} else {
		fmt.Println(content)
	}
}

func cmdDelete(v *Vault, name string) {
	if name == "" {
		fail("nome vazio")
		return
	}
	if strings.ToLower(readLine("apagar '"+name+"'? [s/N]: ")) != "s" {
		fmt.Println("cancelado")
		return
	}
	if err := v.Delete(name); err != nil {
		fail(err.Error())
		return
	}
	ok("apagada: " + name)
}

func cmdSync(v *Vault, path string, push bool) {
	cfg := v.LoadConfig()
	if path == "" {
		hint := cfg.Pendrive
		if hint != "" {
			path = readLine("caminho do pendrive [" + hint + "]: ")
			if path == "" {
				path = hint
			}
		} else {
			fmt.Println(cGray + "exemplos: /Volumes/PENDRIVE (mac)  /media/user/PENDRIVE (linux)  E:\\ (windows)" + cReset)
			path = readLine("caminho do pendrive: ")
		}
	}
	if st, err := os.Stat(path); err != nil || !st.IsDir() {
		fail("caminho inválido: " + path)
		return
	}
	var res syncResult
	var err error
	if push {
		res, err = v.Push(path)
	} else {
		res, err = v.Pull(path)
	}
	if err != nil {
		fail(err.Error())
		return
	}
	cfg.Pendrive = path
	v.SaveConfig(cfg)
	dir := "→ pendrive"
	if !push {
		dir = "← pendrive"
	}
	ok(fmt.Sprintf("sincronizado %s: %d copiada(s), %d já em dia", dir, res.Copied, res.Skipped))
	if push {
		fmt.Println(cGray + "pode ejetar o pendrive com segurança" + cReset)
	}
}

func cmdExportKey(v *Vault) {
	if err := unlockInteractive(v); err != nil {
		fail(err.Error())
		return
	}
	secret, err := v.SecretKey()
	if err != nil {
		fail(err.Error())
		return
	}
	fmt.Println("\nComo você quer o backup da chave?")
	fmt.Println("  1) QR code no terminal (escaneia com o celular → cola no Bitwarden)")
	fmt.Println("  2) QR code em PNG (cofre-chave-qr.png)")
	fmt.Println("  3) mostrar a chave em texto (anotar no papel / colar em nota segura)")
	fmt.Println("  0) agora não")
	switch readLine("\n> ") {
	case "1":
		fmt.Println()
		showQRTerminal(secret)
		fmt.Println(cBold + "⚠ Este QR É a sua chave secreta." + cReset + " Escaneie e guarde SÓ em local")
		fmt.Println("criptografado (nota segura do Bitwarden/1Password) ou papel guardado.")
	case "2":
		path := "cofre-chave-qr.png"
		if err := saveQRPNG(secret, path); err != nil {
			fail(err.Error())
			return
		}
		ok("salvo: " + path)
		fmt.Println(cBold+"⚠ Apague este arquivo"+cReset, "depois de guardar o backup — ele é a chave em claro.")
	case "3":
		fmt.Println("\n" + secret)
		fmt.Println(cGray + "\n(a linha acima é a chave inteira — papel, Bitwarden, ou segundo pendrive)" + cReset)
	}
}

// ── helpers ────────────────────────────────────────────────────────────

func withVault(fn func(*Vault)) {
	v, err := LoadVault()
	if err != nil {
		die(err.Error())
	}
	fn(v)
}

func unlockInteractive(v *Vault) error {
	for tries := 0; !v.Unlocked(); tries++ {
		if tries == 3 {
			return fmt.Errorf("3 tentativas erradas")
		}
		if err := v.Unlock(readSecret("passphrase: ")); err != nil {
			fmt.Println(cRed + "✗ " + err.Error() + cReset)
		}
	}
	return nil
}

func copyToClipboard(s string) {
	if err := clipboard.WriteAll(s); err != nil {
		fail("clipboard indisponível (" + err.Error() + ") — use 'cofre get' pra ver na tela")
		return
	}
	ok("copiado pro clipboard — limpa em 45s (se o cofre continuar aberto)")
	go func() {
		time.Sleep(45 * time.Second)
		if cur, err := clipboard.ReadAll(); err == nil && cur == s {
			_ = clipboard.WriteAll("")
		}
	}()
}

func readLine(prompt string) string {
	fmt.Print(prompt)
	line, err := stdin.ReadString('\n')
	if err != nil && line == "" {
		// stdin closed (EOF) — bail out instead of looping on empty reads
		fmt.Println()
		os.Exit(1)
	}
	return strings.TrimSpace(line)
}

func readSecret(prompt string) string {
	fmt.Print(prompt)
	if term.IsTerminal(int(os.Stdin.Fd())) {
		raw, err := term.ReadPassword(int(os.Stdin.Fd()))
		fmt.Println()
		if err == nil {
			return strings.TrimSpace(string(raw))
		}
	}
	// piped/scripted input
	line, err := stdin.ReadString('\n')
	if err != nil && line == "" {
		fmt.Println()
		os.Exit(1)
	}
	fmt.Println()
	return strings.TrimSpace(line)
}

func readSecretConfirm() string {
	fmt.Println("  1) gerar uma passphrase forte pra mim (recomendado)")
	fmt.Println("  2) digitar a minha própria")
	if readLine("> ") == "1" {
		return generatePassphraseInteractive()
	}
	for {
		a := readSecret("passphrase: ")
		if len(a) < 8 {
			fmt.Println(cRed + "✗ muito curta (mínimo 8 caracteres)" + cReset)
			continue
		}
		if a == readSecret("repita:     ") {
			return a
		}
		fmt.Println(cRed + "✗ não bateu, tenta de novo" + cReset)
	}
}

func generatePassphraseInteractive() string {
	const words = 5
	for {
		phrase := GeneratePassphrase(words)
		fmt.Printf("\n  %s%s%s\n", cBold+cCyan, phrase, cReset)
		fmt.Printf("  %s(%d palavras, ~%d bits de entropia — séculos contra força bruta)%s\n",
			cGray, words, PassphraseEntropyBits(words), cReset)
		switch strings.ToLower(readLine("\nusar essa? [S = sim / r = sortear outra]: ")) {
		case "", "s", "sim":
			fmt.Println("\nDecore AGORA. Digite ela de volta pra fixar:")
			for tries := 0; tries < 3; tries++ {
				if readSecret("> ") == phrase {
					return phrase
				}
				fmt.Println(cRed + "✗ não bateu — olha de novo:  " + cReset + phrase)
			}
			fmt.Println(cGray + "vamos sortear outra mais fácil de lembrar..." + cReset)
		case "r":
			continue
		}
	}
}

func requireArg(args []string, usage string) {
	if len(args) < 2 || args[1] == "" {
		die("uso: " + usage)
	}
}

func argOr(args []string, i int, def string) string {
	if len(args) > i {
		return args[i]
	}
	return def
}

func ok(msg string)   { fmt.Println(cGreen + "✓ " + cReset + msg) }
func fail(msg string) { fmt.Println(cRed + "✗ " + cReset + msg) }
func die(msg string) {
	fail(msg)
	os.Exit(1)
}
