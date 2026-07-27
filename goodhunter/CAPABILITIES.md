# GoodHunter — Capacidades de Software de Monitoramento

> O que cada ferramenta pode ver, capturar e reportar sobre você.
> Base de conhecimento baseada em análise de 59 softwares de vigilância.
> Atualizado em julho de 2026.

---

## Índice

1. [O que pode ser monitorado](#1-o-que-pode-ser-monitorado)
2. [Por categoria de risco](#2-por-categoria-de-risco)
3. [Ferramentas corporativas (as mais comuns em empresas)](#3-ferramentas-corporativas)
4. [Stalkerware (espionagem não-consensual)](#4-stalkerware)
5. [Ferramentas brasileiras](#5-ferramentas-brasileiras)
6. [Telemetria nativa do Windows](#6-telemetria-nativa-do-windows)
7. [Como cada tipo de captura funciona tecnicamente](#7-como-cada-tipo-de-captura-funciona)
8. [O que o RH/IT vê no dashboard](#8-o-que-o-rhit-vê-no-dashboard)
9. [Mitigações práticas](#9-mitigações-práticas)

---

## 1. O que pode ser monitorado

### 1.1 Captura de tela

| Tipo | Descrição | Ferramentas que fazem |
|------|-----------|----------------------|
| Screenshot periódico | Captura da tela a cada N segundos/minutos | ActivTrak (10-60s), Hubstaff (10min), Time Doctor (10min), StaffCop (5-30s) |
| Screen recording (vídeo) | Gravação contínua da tela em vídeo | Teramind, InterGuard, Veriato, Controlio |
| Screen recording (evento) | Grava apenas quando detecta atividade suspeita | StaffCop, SentryPC |
| Webcam snapshot | Foto via webcam durante o uso | Spyrix, Spytech, Actual Keylogger |

**O que a captura de tela vê:**
- Todas as janelas abertas (incluindo abas de navegador)
- Documentos, planilhas, código, mensagens
- Senhas visíveis na tela (campos não-mascarados)
- Vídeos, imagens, qualquer conteúdo do monitor

### 1.2 Captura de teclado (keystroke logging)

| Tipo | Descrição | Ferramentas |
|------|-----------|-------------|
| Keylogging total | Todas as teclas pressionadas | Teramind, InterGuard, Veriato, StaffCop, Controlio, FlexiSPY |
| Keylogging seletivo | Apenas em campos/aplicativos específicos | ActivTrak (parcial), StaffCop |
| Keylogging com contexto | Teclas + janela onde foram digitadas | Teramind, InterGuard |

**O que o keylogger captura:**
- Tudo que você digita: senhas, emails, mensagens, código, documentos
- **Senhas de bancos, e-mail pessoal, redes sociais** — se você digitar, está gravado
- Texto apagado e re-digitado
- Combinações de teclas (Ctrl+C, Ctrl+V)

### 1.3 Monitoramento de aplicativos

| O que é visto | Como |
|---------------|------|
| Apps em execução | Nome do executável, janela ativa, tempo de uso |
| Título da janela ativa | "Contrato.pdf - Adobe Reader", "Reunião - Zoom" |
| Tempo por app | Quanto tempo gasto em cada programa |
| Mouse/keyboard idle | Tempo sem movimento (idle time) |

### 1.4 Monitoramento web

| O que é visto | Como |
|---------------|------|
| URLs visitadas | Domínio + path completo (ex: `facebook.com/profile/...`) |
| Tempo por site | Quanto tempo gasto em cada domínio |
| Downloads | Arquivos baixados |
| Pesquisas | Termos buscados no Google/Bing |
| Acesso a sites bloqueados | Categoria: redes sociais, streaming, pornografia |

### 1.5 Captura de áudio

| Tipo | Descrição | Ferramentas |
|------|-----------|-------------|
| Gravação ambiente | Microfone grava o que se ouve no ambiente | FlexiSPY, mSpy, Spyrix |
| Gravação de chamadas | VoIP ou chamadas de áudio | FlexiSPY, XNSPY, Hoverwatch |
| Ativação remota | Microfone ligado remotamente sem indicador | FlexiSPY, OgyMogy |

### 1.6 Captura de comunicação

| Tipo | Descrição | Ferramentas |
|------|-----------|-------------|
| Email | Conteúdo de emails enviados/recebidos | Teramind, InterGuard, Veriato, StaffCop, FlexiSPY |
| Chat/IM | Mensagens do WhatsApp Web, Telegram, Slack, Teams | Teramind, InterGuard, StaffCop, mSpy, FlexiSPY |
| Clipboard | Tudo que é copiado (Ctrl+C) | Teramind, InterGuard |

### 1.7 Monitoramento de arquivos

| O que é visto | Como |
|---------------|------|
| Arquivos abertos | Nome, caminho, hora de acesso |
| Arquivos modificados | Criação, edição, exclusão |
| Arquivos copiados para USB | Nome, tamanho, destino |
| Downloads | Arquivos baixados da internet |
| Uploads | Arquivos enviados (Google Drive, Dropbox, etc.) |

### 1.8 Monitoramento de rede

| O que é visto | Como |
|---------------|------|
| Conexões ativas | IPs de destino, portas, protocolo |
| Tráfego por app | Quantos bytes cada app enviou/recebeu |
| Criptografia | Sites HTTP vs HTTPS (mas não o conteúdo HTTPS) |
| VPN detection | Se você está usando VPN |

### 1.9 Geolocalização

| O que é visto | Como |
|---------------|------|
| GPS (laptop) | Localização via Wi-Fi triangulação |
| GPS (mobile) | Coordenadas precisas |
| IP geolocation | Cidade aproximada baseada no IP |

### 1.10 Periféricos e hardware

| O que é visto |
|---------------|
| Dispositivos USB conectados (modelo, serial) |
| Monitores conectados |
| Webcam ativada/desativada |
| Microfone ativado/desativado |

---

## 2. Por categoria de risco

| Risco | O que significa | Exemplos |
|-------|----------------|----------|
| **Crítico** | Captura TUDO: tela, teclado, áudio, câmera, arquivos, comunicação. Stalkerware. | FlexiSPY, mSpy, Spyrix, PC Tattletale, Spytech, XNSPY |
| **Alto** | Captura tela + teclado + apps + web + comunicação corporativa. | Teramind, ActivTrak, InterGuard, Veriato, StaffCop, Controlio |
| **Médio** | Screenshots periódicos + apps + web. Sem keylogging. | Hubstaff, Time Doctor, WorkTime, DeskTime, TeamViewer |
| **Baixo** | Telemetria do sistema, sem captura de conteúdo. | Windows Telemetry, EDR (CrowdStrike, Defender), OBS |

---

## 3. Ferramentas corporativas

### Teramind — Nível: Alto

**O que captura:**
- Tela: gravação contínua em vídeo
- Teclado: todas as teclas (incluindo senhas)
- Apps: nome + título da janela + tempo
- Web: todos os URLs visitados
- Email: conteúdo completo
- Chat: Slack, Teams, WhatsApp Web
- Clipboard: tudo copiado
- Arquivos: abertos, modificados, USB

**Comportamento:**
- Watchdog: SIM — se o processo morre, outro sobe
- Alerta se morto: SIM — heartbeat falha em segundos
- Stealth: SIM — pode se esconder do Task Manager
- Ofiline: SIM — captura local e sincroniza quando volta

**Frequência de screenshots:** Contínuo (vídeo), compressão por eventos

### ActivTrak — Nível: Alto

**O que captura:**
- Tela: screenshots a cada 10-60 segundos
- Apps: nome + tempo
- Web: URLs visitados
- Teclado: **NÃO** (não faz keylogging)

**Comportamento:**
- Watchdog: NÃO
- Alerta se morto: SIM — heartbeat perdido
- Cloud: 100% cloud, sem armazenamento local

### StaffCop — Nível: Alto

**O que captura:**
- Tela: screenshots a cada 5-30 segundos ou gravação por evento
- Teclado: todas as teclas (com contexto da janela)
- Apps: nome + título
- Web: URLs com categorização
- Email: conteúdo
- Chat: mensagens

**Comportamento:**
- Watchdog: SIM
- Alerta se morto: SIM
- Stealth: SIM (processo oculto)

### InterGuard — Nível: Alto

**O que captura:**
- Tela: gravação contínua
- Teclado: total
- Email: completo (incluindo webmail)
- Chat: IM
- Apps: completo
- Web: URLs

**Comportamento:**
- Watchdog: SIM
- Alerta se morto: SIM
- Stealth: SIM

### Hubstaff — Nível: Médio

**O que captura:**
- Tela: screenshots a cada 10 minutos
- Apps: nome + tempo
- Web: URLs
- GPS: localização (mobile)
- Teclado: **NÃO**

**Observação:** É uma ferramenta de time tracking, não vigilância pesada. Ideal para home office onde a empresa confia mas quer métricas.

### Time Doctor — Nível: Médio

**O que captura:**
- Tela: screenshots periódicos (configurável)
- Apps: nome + tempo
- Web: URLs
- Teclado: **NÃO**

---

## 4. Stalkerware

> Softwares vendidos como "monitoramento parental" ou "rastreador de celular", mas usados para espionagem não-consensual.

### FlexiSPY — Nível: Crítico

**O que captura:**
- Tela: gravação remota
- Teclado: total
- Áudio: gravação ambiente (liga o microfone remotamente)
- Webcam: captura remota
- Chat: WhatsApp, Facebook, Skype, Line, Viber
- Email: completo
- GPS: localização em tempo real
- Arquivos: acesso remoto
- Clipboard: sim

**Diferencial:** Permite ativar remotamente o microfone mesmo com o telefone bloqueado. O usuário não sabe que está sendo ouvido.

### mSpy — Nível: Crítico

**O que captura:**
- Tela: screenshots
- Teclado: total
- Chat: WhatsApp, Instagram, Snapchat, Facebook
- GPS: tracking
- Áudio: gravação ambiente
- Webcam: captura

### Spyrix — Nível: Crítico

**O que captura:**
- Tela: screenshots + gravação
- Teclado: total
- Webcam: snapshots periódicas
- Chat: Skype, Facebook, WhatsApp
- Áudio: gravação
- Apps: completo

---

## 5. Ferramentas brasileiras

### Surepoint (Desk Copilot) — Nível: Alto

**O que captura:**
- Tela: screenshots periódicos
- Apps: nome + tempo
- Web: URLs
- Teclado: **NÃO** (segundo documentação)

**Comportamento:**
- Watchdog: PARCIAL
- Alerta se morto: SIM
- Popular em: empresas brasileiras de médio porte, call centers

### Tecnicon (DDS) — Nível: Alto

**O que captura:**
- Tela: screenshots periódicos
- Apps: nome + tempo
- Web: URLs
- Ponto eletrônico: integrado

**Observação:** Comum em indústrias e empresas com controle de ponto + monitoramento.

### Intelipos — Nível: Médio

**O que captura:**
- Apps: nome + tempo
- Web: URLs
- Tela: **NÃO** (foco em ponto eletrônico e produtividade)

### PontoTel — Nível: Médio

**O que captura:**
- Apps: tempo
- Tela: **NÃO** (foco em ponto eletrônico)

---

## 6. Telemetria nativa do Windows

### Windows DiagTrack (Telemetria)

**O que captura:**
- Apps que você usa e por quanto tempo
- Sites visitados (Edge)
- Pesquisas no Bing
- Erros e crashes
- Hardware e drivers
- Localização aproximada

**Não captura:**
- Conteúdo de tela
- Teclado
- Comunicações

### Microsoft 365 / Office Telemetry

**O que captura:**
- Documentos abertos e tempo de edição
- Recursos do Office usados
- Erros e performance

---

## 7. Como cada tipo de captura funciona tecnicamente

### Captura de tela

```
Aplicativo → Win32 API (BitBlt / DirectX) → Buffer de imagem → Compressão JPEG → Upload
```

- `BitBlt` (GDI): captura a tela via Windows API. Detectável por EDRs.
- `DirectX Capture`: captura via Direct3D. Mais rápido, funciona com jogos.
- `Mirror Driver`: driver de vídeo virtual que recebe toda a saída. Indetectável por software.

### Keylogging

```
Teclado → Windows Hook (WH_KEYBOARD_LL) → Callback → Log → Upload
```

- `SetWindowsHookEx(WH_KEYBOARD_LL)`: hook global de baixo nível. O mais comum.
- `GetAsyncKeyState`: polling do estado de cada tecla. Mais lento, mais difícil de detectar.
- `Kernel-mode driver`: captura no nível do kernel. Indetectável por software de usuário.

### Monitoramento de apps

```
Windows → EnumWindows / GetForegroundWindow → GetWindowText → Log → Upload
```

- Um timer a cada 1-5 segundos verifica qual janela está em primeiro plano.
- Lê o título da janela e o nome do processo.
- Compatível com todos os apps, inclusive jogos em fullscreen.

### Captura de rede

```
Proxy / LSP / WFP → Pacotes → Filtro → Log
```

- `Windows Filtering Platform`: driver do Windows usado por firewalls legítimos e monitoramento.
- `WinPcap / Npcap`: captura de pacotes bruta.
- `Proxy configurado no navegador`: redireciona todo o tráfego HTTP.

---

## 8. O que o RH/IT vê no dashboard

### Painel típico de um software corporativo

```
+--------------------------------------------------+
|  DASHBOARD — TERAMIND                            |
+--------------------------------------------------+
|  Funcionário  | Atividade | Produt. | Screenshots |
|  João Silva   | 87%       | 92%     | [▶ Ver]    |
|  Maria Souza  | 63%       | 45%     | [▶ Ver]    |
|  Pedro Santos | 12%       | 10%     | [▶ Ver]    |
+--------------------------------------------------+
```

**Métricas comuns:**

| Métrica | Como é calculada |
|---------|------------------|
| Atividade (%) | Tempo com mouse/teclado ativo / tempo total |
| Produtividade (%) | Tempo em apps "produtivos" / tempo total |
| Aplicativos mais usados | Ranking por tempo de uso |
| Sites mais visitados | Ranking por tempo ou visitas |
| Screenshots | Galeria de imagens com timestamp |
| Linha do tempo | Timeline do dia: quais apps em cada horário |
| Alertas | Acesso a sites bloqueados, idle prolongado |

**Alertas que o RH recebe:**

- ❌ Funcionário ficou mais de 30min inativo
- ❌ Funcionário acessou site bloqueado (streaming, redes sociais)
- ❌ Funcionário está usando apps não-autorizados
- ❌ Agente de monitoramento foi desligado (CRÍTICO)
- ❌ Funcionário acessou horário não-convencional
- ⚠️ Produtividade abaixo de 40% por 3+ dias consecutivos

---

## 9. Mitigações práticas

### Organizadas por superfície de ataque

| Superfície | O que fazer | Risco da mitigação |
|-------------|-------------|-------------------|
| Tela | Usar `goodhunter shield` (janela transparente) | Mínimo — não bloqueia interação |
| Tela | Minimizar janelas sensíveis quando não estiver usando | Nenhum |
| Tela | Trabalhar em janela pequena, não maximizada (menos conteúdo no screenshot) | Nenhum |
| Teclado | Usar teclado virtual do Windows para senhas | Baixo |
| Teclado | Usar password manager (Bitwarden, KeePass) com autotype | Baixo |
| Teclado | Digitar senhas em ordem diferente e corrigir depois | Médio (trabalhoso) |
| Rede | `goodhunter firewall` — bloquear processos no firewall | Médio (precisa admin) |
| Rede | `goodhunter block` — bloquear C2 no hosts | Baixo (pode não precisar admin) |
| Rede | Usar VPN pessoal (se não for bloqueada) | Médio (pode ser proibido) |
| Produtividade | `goodhunter evade` — mouse jiggler + atividade falsa | Mínimo |
| Consciência | `goodhunter watch` — monitorar indicadores de vigilância | Nenhum |
| Geral | Fazer tarefas pessoais no celular (não no PC) | Nenhum |
| Geral | Usar VM local (VirtualBox) para tarefas sensíveis | Baixo |
| Geral | Nunca digitar senha pessoal no PC corporativo | Nenhum |

### O que NÃO fazer

| Ação | Consequência |
|------|-------------|
| Matar/desabilitar o agente | Alerta imediato no IT |
| Desinstalar o software | Log no Windows + alerta |
| Renomear o executável | Pode corromper a instalação, gerando alerta |
| Usar ferramentas anti-monitoramento óbvias | EDR detecta e reporta |

---

## Disclaimer

> Este documento é uma compilação de informações públicas e análise técnica.
> As capacidades descritas refletem funcionalidades documentadas e engenharia
> reversa dos softwares listados. O objetivo é educacional — entender o que
> um software de monitoramento pode fazer ajuda a tomar decisões informadas
> sobre segurança e privacidade.
>
> O uso de técnicas de evasão em equipamentos corporativos pode violar
> políticas internas e leis trabalhistas. Consulte o departamento jurídico
> antes de implementar qualquer contra-medida.

---

*Gerado por GoodHunter — julho/2026*
