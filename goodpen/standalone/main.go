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
		cmdPassphrase()
	case "qr", "chave":
		withVault(func(v *Vault) { cmdExportKey(v) })
	case "web", "janela":
		withVault(func(v *Vault) {
			if err := runWeb(v); err != nil {
				die(err.Error())
			}
		})
	case "temas", "themes":
		ui.CatalogoTemas()
	case "help", "-h", "--help", "ajuda":
		printHelp()
	default:
		// convenience: `cofre nubank` == `cofre get nubank`
		withVault(func(v *Vault) { cmdGet(v, args[0], false) })
	}
}

func printHelp() {
	ui.Modulo("cofre", "gerenciador de senhas · age + pendrive")
	ui.Secao("sessao")
	ui.Item("$", pad("cofre", 20), "menu interativo")
	ui.Item("$", pad("cofre web", 20), "abre a interface no navegador")
	ui.Item("$", pad("cofre init", 20), "cria um cofre novo")
	ui.Item("$", pad("cofre restore", 20), "restaura de um backup de chave (QR/arquivo)")
	fmt.Println()
	ui.Secao("senhas")
	ui.Item("$", pad("cofre ls", 20), "lista as senhas")
	ui.Item("$", pad("cofre add <nome>", 20), "salva uma senha (digitada)")
	ui.Item("$", pad("cofre gen <nome> [n]", 20), "gera senha aleatoria de n chars (padrao 20)")
	ui.Item("$", pad("cofre get <nome>", 20), "mostra uma senha")
	ui.Item("$", pad("cofre cp <nome>", 20), "copia pro clipboard (limpa em 45s)")
	ui.Item("$", pad("cofre rm <nome>", 20), "apaga uma senha")
	fmt.Println()
	ui.Secao("backup e ambiente")
	ui.Item("$", pad("cofre push [dir]", 20), "envia backup pro pendrive")
	ui.Item("$", pad("cofre pull [dir]", 20), "puxa do pendrive")
	ui.Item("$", pad("cofre qr", 20), "exporta a chave secreta (QR / arquivo)")
	ui.Item("$", pad("cofre frase", 20), "sugere passphrases fortes (diceware PT-BR)")
	ui.Item("$", pad("cofre temas", 20), "lista as paletas disponiveis")
	fmt.Println()
	ui.KV("TEMA ATIVO", strings.ToUpper(ui.Tema))
	ui.KV("VARIAVEIS", "COFRE_TEMA · RETRO_TEMA")
	fmt.Println()
}

func pad(s string, n int) string { return fmt.Sprintf("%-*s", n, s) }

// ── interactive menu ───────────────────────────────────────────────────

var menuOpcoes = [][4]string{
	{"1", "LISTAR", "2", "VER"},
	{"3", "COPIAR", "4", "NOVA SENHA"},
	{"5", "GERAR", "6", "APAGAR"},
	{"7", "ENVIAR PENDRIVE", "8", "PUXAR PENDRIVE"},
	{"9", "EXPORTAR CHAVE", "W", "NAVEGADOR"},
}

func menuLinhas() []string {
	linhas := make([]string, 0, len(menuOpcoes))
	for _, o := range menuOpcoes {
		esq := ui.SItem("["+o[0]+"]", o[1], "")
		linhas = append(linhas, ui.Preenche(esq, 24)+ui.SItem("["+o[2]+"]", o[3], ""))
	}
	return linhas
}

func drawMenu(n int) {
	meta := fmt.Sprintf("%d SENHA(S)", n)
	linhas := menuLinhas()
	rodape := "[0] SAIR · [1-9] ACAO"
	if !ui.Caixa {
		ui.Modulo("vault_menu", meta)
		for _, l := range linhas {
			fmt.Println("  " + l)
		}
		fmt.Println()
		ui.Item("[0]", "SAIR", "")
		return
	}
	fmt.Println()
	ui.Topo()
	ui.Chrome("root@cofre: ~/vault", meta)
	ui.Sep()
	ui.Linha(ui.ACC + ui.BOLD + "[ MODULE: VAULT_MENU ]" + ui.RESET)
	ui.Linha("")
	for _, l := range linhas {
		ui.Linha(l)
	}
	ui.Sep()
	ui.Status(rodape, "● PRONTO")
	ui.Base()
	ui.Sombra()
}

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
		drawMenu(len(names))
		switch strings.ToLower(readLine("\n" + ui.ACC30 + ">" + ui.RESET + " ")) {
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
	ui.Modulo("cofre", "nenhum cofre encontrado nesta maquina")
	ui.Item("[1]", "CRIAR UM COFRE NOVO", "")
	ui.Item("[2]", "RESTAURAR DE UM BACKUP", "tenho minha AGE-SECRET-KEY")
	ui.Item("[0]", "SAIR", "")
	switch readLine("\n" + ui.ACC30 + ">" + ui.RESET + " ") {
	case "1":
		cmdInit()
	case "2":
		cmdRestore()
	}
}

// ── commands ───────────────────────────────────────────────────────────

func cmdPassphrase() {
	ui.Modulo("passphrase_suggest", "diceware pt-br · nada e salvo")
	for i := 0; i < 3; i++ {
		ui.Item("►", GeneratePassphrase(5), "")
	}
	fmt.Println()
	ui.KV("ENTROPIA", fmt.Sprintf("~%d BITS CADA", PassphraseEntropyBits(5)))
	fmt.Println()
}

func cmdInit() {
	ui.Modulo("vault_init", "")
	ui.Item("·", "sua PASSPHRASE e a unica senha que voce decora", "")
	ui.Item("·", "dica: 4 palavras aleatorias (cavalo-bateria-grampo-correto)", "")
	fmt.Println()
	pass := readSecretConfirm()
	v, err := InitVault(pass)
	if err != nil {
		die(err.Error())
	}
	ui.Ok("cofre criado")
	ui.KV("DIRETORIO", v.Dir)
	fmt.Println()
	ui.Aviso("atencao", ui.Forte("FACA O BACKUP DA CHAVE AGORA."))
	ui.Item("·", "sem ele, perder este computador = perder todas as senhas", "")
	cmdExportKey(v)
}

func cmdRestore() {
	ui.Modulo("vault_restore", "")
	ui.Item("·", "cole sua chave secreta (a linha AGE-SECRET-KEY-1... do QR/arquivo)", "")
	key := readLine("\n" + ui.ACC30 + ">" + ui.RESET + " ")
	fmt.Println()
	ui.Item("·", "agora crie a passphrase pra proteger a chave NESTA maquina", "")
	fmt.Println()
	pass := readSecretConfirm()
	v, err := RestoreVault(key, pass)
	if err != nil {
		die(err.Error())
	}
	ui.Ok("chave restaurada")
	ui.KV("DIRETORIO", v.Dir)
	ui.Proximo("cofre pull", "puxe suas senhas do pendrive:")
}

func cmdList(v *Vault) {
	names, err := v.List()
	if err != nil {
		fail(err.Error())
		return
	}
	ui.Modulo("vault_list", "src: "+v.storePath())
	if len(names) == 0 {
		ui.Aviso("vazio", "")
		ui.Proximo("cofre add <nome>", "salve a primeira:")
		fmt.Println()
		return
	}
	for _, n := range names {
		ui.Item("►", n, "")
	}
	fmt.Println()
	ui.KV("TOTAL", fmt.Sprintf("%d SENHA(S)", len(names)))
	fmt.Println()
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
	ui.Ok("salvo")
	ui.KV("ENTRADA", name)
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
	ui.Ok("gerada e salva")
	ui.KV("ENTRADA", name)
	ui.KV("TAMANHO", fmt.Sprintf("%d CARACTERES", length))
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
		ui.Aviso("cancelado", "")
		return
	}
	if err := v.Delete(name); err != nil {
		fail(err.Error())
		return
	}
	ui.Ok("apagada")
	ui.KV("ENTRADA", name)
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
			ui.Aviso("exemplos", "/Volumes/PENDRIVE (mac) · /media/user/PENDRIVE (linux) · E:\\ (windows)")
			path = readLine("caminho do pendrive: ")
		}
	}
	if st, err := os.Stat(path); err != nil || !st.IsDir() {
		fail("caminho invalido: " + path)
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
	sentido := "LOCAL → PENDRIVE"
	if !push {
		sentido = "PENDRIVE → LOCAL"
	}
	ui.Ok("sincronizado")
	ui.KV("SENTIDO", sentido)
	ui.KV("PENDRIVE", path)
	ui.KV("COPIADAS", fmt.Sprintf("%d ARQUIVO(S)", res.Copied))
	ui.KV("JA EM DIA", fmt.Sprintf("%d ARQUIVO(S)", res.Skipped))
	if push {
		ui.Aviso("seguro", "pode ejetar o pendrive")
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
	ui.Modulo("key_backup", "como voce quer o backup da chave?")
	ui.Item("[1]", "QR CODE NO TERMINAL", "escaneia no celular → Bitwarden")
	ui.Item("[2]", "QR CODE EM PNG", "cofre-chave-qr.png")
	ui.Item("[3]", "CHAVE EM TEXTO", "papel / nota segura")
	ui.Item("[0]", "AGORA NAO", "")
	switch readLine("\n" + ui.ACC30 + ">" + ui.RESET + " ") {
	case "1":
		fmt.Println()
		showQRTerminal(secret)
		ui.Aviso("atencao", ui.Forte("ESTE QR E A SUA CHAVE SECRETA."))
		ui.Item("·", "guarde SO em local criptografado (Bitwarden/1Password) ou papel", "")
	case "2":
		path := "cofre-chave-qr.png"
		if err := saveQRPNG(secret, path); err != nil {
			fail(err.Error())
			return
		}
		ui.Ok("salvo")
		ui.KV("ARQUIVO", path)
		ui.Aviso("atencao", "apague este arquivo depois do backup — e a chave em claro")
	case "3":
		fmt.Println("\n" + secret)
		fmt.Println()
		ui.Aviso("chave", "a linha acima e a chave inteira — papel, Bitwarden ou 2o pendrive")
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
			ui.Erro(err.Error())
		}
	}
	return nil
}

func copyToClipboard(s string) {
	if err := clipboard.WriteAll(s); err != nil {
		fail("clipboard indisponivel (" + err.Error() + ")")
		ui.Proximo("cofre get <nome>", "veja na tela com:")
		return
	}
	ui.Ok("copiado pro clipboard")
	ui.KV("EXPIRA EM", "45S")
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
	ui.Item("[1]", "GERAR UMA PASSPHRASE FORTE PRA MIM", "recomendado")
	ui.Item("[2]", "DIGITAR A MINHA PROPRIA", "")
	if readLine("\n"+ui.ACC30+">"+ui.RESET+" ") == "1" {
		return generatePassphraseInteractive()
	}
	for {
		a := readSecret("passphrase: ")
		if len(a) < 8 {
			ui.Erro("muito curta (minimo 8 caracteres)")
			continue
		}
		if a == readSecret("repita:     ") {
			return a
		}
		ui.Erro("nao bateu, tenta de novo")
	}
}

func generatePassphraseInteractive() string {
	const words = 5
	for {
		phrase := GeneratePassphrase(words)
		ui.Modulo("passphrase_suggest", "diceware pt-br")
		ui.Item("►", phrase, "")
		fmt.Println()
		ui.KV("PALAVRAS", fmt.Sprintf("%d", words))
		ui.KV("ENTROPIA", fmt.Sprintf("~%d BITS", PassphraseEntropyBits(words)))
		switch strings.ToLower(readLine("\nusar essa? [S = sim / r = sortear outra]: ")) {
		case "", "s", "sim":
			ui.Item("·", "decore AGORA. digite ela de volta pra fixar", "")
			for tries := 0; tries < 3; tries++ {
				if readSecret("> ") == phrase {
					return phrase
				}
				ui.Erro("nao bateu — olha de novo: " + ui.Forte(phrase))
			}
			ui.Aviso("nova tentativa", "vamos sortear outra mais facil de lembrar")
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

func fail(msg string) { ui.Erro(msg) }
func die(msg string) {
	fail(msg)
	os.Exit(1)
}
