package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os/exec"
	"runtime"
	"strconv"
)

type webServer struct {
	vault *Vault
	token string
}

func runWeb(v *Vault) error {
	tok := make([]byte, 16)
	if _, err := rand.Read(tok); err != nil {
		return err
	}
	srv := &webServer{vault: v, token: hex.EncodeToString(tok)}

	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return err
	}
	base := "/t/" + srv.token
	mux := http.NewServeMux()
	mux.HandleFunc(base+"/", srv.index)
	mux.HandleFunc(base+"/api/status", srv.status)
	mux.HandleFunc(base+"/api/unlock", srv.unlock)
	mux.HandleFunc(base+"/api/list", srv.list)
	mux.HandleFunc(base+"/api/get", srv.get)
	mux.HandleFunc(base+"/api/add", srv.add)
	mux.HandleFunc(base+"/api/del", srv.del)
	mux.HandleFunc(base+"/api/gen", srv.gen)

	url := fmt.Sprintf("http://127.0.0.1:%d%s/", ln.Addr().(*net.TCPAddr).Port, base)
	ui.Modulo("cofre_web", "127.0.0.1 · sessao local")
	ui.KV("URL", url)
	ui.Aviso("ctrl+c", "encerra o servidor — o cofre so e acessivel nesta maquina")
	openBrowser(url)
	return http.Serve(ln, mux)
}

func openBrowser(url string) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "darwin":
		cmd = exec.Command("open", url)
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}
	_ = cmd.Start()
}

func jsonOut(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(v)
}

func jsonErr(w http.ResponseWriter, code int, msg string) {
	w.WriteHeader(code)
	jsonOut(w, map[string]string{"error": msg})
}

func (s *webServer) index(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, _ = w.Write([]byte(webPage))
}

func (s *webServer) status(w http.ResponseWriter, r *http.Request) {
	jsonOut(w, map[string]bool{"unlocked": s.vault.Unlocked()})
}

func (s *webServer) unlock(w http.ResponseWriter, r *http.Request) {
	var body struct{ Passphrase string }
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		jsonErr(w, 400, "corpo inválido")
		return
	}
	if err := s.vault.Unlock(body.Passphrase); err != nil {
		jsonErr(w, 403, err.Error())
		return
	}
	jsonOut(w, map[string]bool{"ok": true})
}

func (s *webServer) list(w http.ResponseWriter, r *http.Request) {
	names, err := s.vault.List()
	if err != nil {
		jsonErr(w, 500, err.Error())
		return
	}
	if names == nil {
		names = []string{}
	}
	jsonOut(w, names)
}

func (s *webServer) get(w http.ResponseWriter, r *http.Request) {
	content, err := s.vault.Get(r.URL.Query().Get("name"))
	if err != nil {
		jsonErr(w, 403, err.Error())
		return
	}
	jsonOut(w, map[string]string{"content": content})
}

func (s *webServer) add(w http.ResponseWriter, r *http.Request) {
	var body struct{ Name, Content string }
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil || body.Name == "" || body.Content == "" {
		jsonErr(w, 400, "nome e senha são obrigatórios")
		return
	}
	if err := s.vault.Set(body.Name, body.Content); err != nil {
		jsonErr(w, 400, err.Error())
		return
	}
	jsonOut(w, map[string]bool{"ok": true})
}

func (s *webServer) del(w http.ResponseWriter, r *http.Request) {
	var body struct{ Name string }
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		jsonErr(w, 400, "corpo inválido")
		return
	}
	if err := s.vault.Delete(body.Name); err != nil {
		jsonErr(w, 400, err.Error())
		return
	}
	jsonOut(w, map[string]bool{"ok": true})
}

func (s *webServer) gen(w http.ResponseWriter, r *http.Request) {
	n, err := strconv.Atoi(r.URL.Query().Get("len"))
	if err != nil || n < 8 || n > 128 {
		n = 20
	}
	jsonOut(w, map[string]string{"password": GeneratePassword(n, true)})
}

const webPage = `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>cofre</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; margin: 0; }
  body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
         background: #101418; color: #e6e9ec; min-height: 100vh;
         display: flex; justify-content: center; padding: 40px 16px; }
  main { width: 100%; max-width: 560px; }
  h1 { font-size: 22px; margin-bottom: 4px; }
  .sub { color: #8a939c; font-size: 13px; margin-bottom: 24px; }
  .card { background: #1a2027; border: 1px solid #2a323b; border-radius: 10px;
          padding: 16px; margin-bottom: 14px; }
  input, button { font: inherit; border-radius: 8px; padding: 9px 12px; }
  input { width: 100%; background: #0d1115; border: 1px solid #2a323b; color: inherit; }
  input:focus { outline: 2px solid #4a90d9; border-color: transparent; }
  button { background: #2f6feb; color: #fff; border: 0; cursor: pointer; }
  button:hover { background: #3b7bf5 } button:active { opacity: .85 }
  button.ghost { background: transparent; color: #9fb3c8; border: 1px solid #2a323b; }
  button.danger { background: transparent; color: #d9776f; border: 1px solid #3a2a2a; }
  .row { display: flex; gap: 8px; margin-top: 10px; }
  .row input { flex: 1 }
  ul { list-style: none; }
  li { display: flex; align-items: center; gap: 8px; padding: 9px 4px;
       border-bottom: 1px solid #222932; }
  li:last-child { border: 0 }
  li .name { flex: 1; font-family: ui-monospace, monospace; font-size: 14px; }
  .msg { min-height: 20px; font-size: 13px; margin-top: 10px; color: #7dbd7a; }
  .msg.err { color: #d9776f }
  .hidden { display: none }
  .pw { font-family: ui-monospace, monospace; background: #0d1115; padding: 8px 10px;
        border-radius: 8px; margin-top: 10px; word-break: break-all; }
</style>
</head>
<body>
<main>
  <h1>🔐 cofre</h1>
  <p class="sub">suas senhas, criptografadas, só nesta máquina</p>

  <div id="lock" class="card">
    <p style="margin-bottom:10px">Digite sua passphrase pra destrancar:</p>
    <div class="row">
      <input id="pass" type="password" placeholder="passphrase" autofocus>
      <button onclick="unlock()">Destrancar</button>
    </div>
    <p id="lockmsg" class="msg err"></p>
  </div>

  <div id="app" class="hidden">
    <div class="card">
      <strong>Nova senha</strong>
      <div class="row">
        <input id="newname" placeholder="nome (ex: banco/nubank)">
      </div>
      <div class="row">
        <input id="newpw" placeholder="senha (ou clique em gerar)">
        <button class="ghost" onclick="gen()">🎲 Gerar</button>
        <button onclick="add()">Salvar</button>
      </div>
      <p id="addmsg" class="msg"></p>
    </div>

    <div class="card">
      <strong>Senhas salvas</strong>
      <ul id="list"></ul>
      <div id="reveal" class="pw hidden"></div>
      <p id="msg" class="msg"></p>
    </div>
  </div>
</main>
<script>
const api = p => location.pathname.replace(/\/$/, '') + '/api/' + p;
const $ = id => document.getElementById(id);

async function unlock() {
  const r = await fetch(api('unlock'), { method: 'POST',
    body: JSON.stringify({ Passphrase: $('pass').value }) });
  if (r.ok) { $('lock').classList.add('hidden'); $('app').classList.remove('hidden'); load(); }
  else $('lockmsg').textContent = (await r.json()).error;
}
$('pass').addEventListener('keydown', e => e.key === 'Enter' && unlock());

async function load() {
  const names = await (await fetch(api('list'))).json();
  $('list').innerHTML = names.length ? '' : '<li><span class="name" style="color:#8a939c">(vazio — salve a primeira acima)</span></li>';
  for (const n of names) {
    const li = document.createElement('li');
    li.innerHTML = '<span class="name"></span>' +
      '<button class="ghost">👁 Ver</button>' +
      '<button class="ghost">📋 Copiar</button>' +
      '<button class="danger">✕</button>';
    li.querySelector('.name').textContent = n;
    const [see, copy, del] = li.querySelectorAll('button');
    see.onclick = () => show(n);
    copy.onclick = () => copyPw(n);
    del.onclick = () => remove(n);
    $('list').appendChild(li);
  }
}

async function getPw(n) {
  const r = await fetch(api('get') + '?name=' + encodeURIComponent(n));
  const j = await r.json();
  if (!r.ok) throw j.error;
  return j.content;
}

async function show(n) {
  try {
    const pw = await getPw(n);
    const el = $('reveal');
    el.textContent = n + ' → ' + pw;
    el.classList.remove('hidden');
    setTimeout(() => el.classList.add('hidden'), 15000);
  } catch (e) { flash('msg', e, true); }
}

async function copyPw(n) {
  try {
    await navigator.clipboard.writeText((await getPw(n)).split('\n')[0]);
    flash('msg', 'copiado! (some do clipboard em 45s)');
    setTimeout(() => navigator.clipboard.writeText(''), 45000);
  } catch (e) { flash('msg', e, true); }
}

async function add() {
  const r = await fetch(api('add'), { method: 'POST',
    body: JSON.stringify({ Name: $('newname').value.trim(), Content: $('newpw').value }) });
  if (r.ok) { $('newname').value = ''; $('newpw').value = ''; flash('addmsg', 'salvo!'); load(); }
  else flash('addmsg', (await r.json()).error, true);
}

async function gen() {
  const j = await (await fetch(api('gen') + '?len=20')).json();
  $('newpw').value = j.password;
}

async function remove(n) {
  if (!window.confirm('Apagar "' + n + '"?')) return;
  await fetch(api('del'), { method: 'POST', body: JSON.stringify({ Name: n }) });
  load();
}

function flash(id, text, err) {
  const el = $(id);
  el.textContent = text;
  el.className = 'msg' + (err ? ' err' : '');
  setTimeout(() => { el.textContent = ''; }, 4000);
}
</script>
</body>
</html>`
