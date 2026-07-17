package main

import (
	"crypto/rand"
	"math"
	"math/big"
	"strings"
)

// Curated PT-BR word list for diceware-style passphrases: common, concrete,
// 3-7 letters, no accents (typeable on any keyboard layout), all distinct.
var wordList = strings.Fields(`
abelha aberto acorde adubo agulha alce aldeia alface alga almoco altar amarelo ameixa amora ancora anel anexo anjo
antena apito arado aranha arco areia arroz asa atum aviao azul babado bacia baleia bambu banana banco banho barata
barco barro batata bau bebida beijo beringela berro bezerro bicicleta bico bigode biscoito bloco boca bola bolo bolso
bomba boneco borboleta borracha bosque bota braco brasa brinco brisa bronze bruxa bufalo buraco burro cabana cabelo cabra
cacau cacho cadeado caderno cafe caixa cajado caju calca camelo caminho campo caneca caneta canoa cantiga capa capim
caracol caranguejo cardume carneiro carroca carta casaco cascata castelo cavalo caverna cebola cedro cenoura cereja cesta chave chinelo
chuva cidade cinto cipreste circo clima cobra coco coelho cofre colar colher colina cometa concha coral coroa correio
cortina coruja costa couve cozinha cristal cubo curva dado dama danca dedo degrau dente deserto diamante dinossauro disco
dobra doce domino dourado dragao duende dueto dunas eco elefante enxada era ervilha escada escudo esfera espada
espelho espiga esponja esquilo estrada estrela fada faisca falcao farinha farol fatia fava fazenda feijao feltro ferro festa
figo fila filtro fita fivela flauta flecha flor floresta fogao fogo foguete folha fonte forno fosforo fralda framboesa
frasco freio frigideira fruta fumaca funil futebol gaita galho galinha gansos garfo garrafa gato gaveta geleia gelo gemada
genciana gergelim gesso girafa girassol gis globo goiaba golfinho gota granizo grama grilo gruta guarda guitarra harpa hera
hipopotamo horta iate igreja ilha ima incenso indio inseto inverno jabuti jacare janela jangada jardim jarra jasmim jaula
jegue jiboia joelho jogo joia jornal juba lagarto lago lagosta lampada lanterna lapis laranja lareira largo lata leao
legume leite lenco lenha leque lesma leste libelula lima limao linho lirio livro lobo lontra lousa lua luneta
luva maca macaco machado madeira maleta mamao manga mangueira manha mapa margarida marfim marreco martelo mastro mato medalha
meia mel melancia melao menta mercado mesa milho mina moeda moinho mola moldura monte morango morcego moringa
morro mosca mostarda moto muralha musgo nabo navio neblina neve ninho nogueira norte nota nuvem oasis oculos oeste
ola oliveira onda oregano orquidea osso ostra ouro outono ovelha pacote padaria pagina palco palha palmeira panela pantano
papel parque passaro pasta pato pavao pedra peixe pelicano pena pente pepino pera pergaminho perola pessego piano picole
pijama pilha pimenta pinha pinguim pintor pipa pipoca planta plumas poco polvo pomar ponte porta portao prado praia
prata prato prego presente primavera prisma prumo quadro quartzo queijo quintal rabanete raio raiz rampa raposa rede regua
relogio remo repolho riacho rio rocha roda rolha roma rosa roupa sabonete saco sala salgueiro salmao sapato sapo
sela selo semente serra sereia sino sitio sofa sol sombra sopa sorvete sotao tabua taca tambor tampa tapete
tartaruga tatu teatro tecido telhado tenda terra tesoura tigela tigre tijolo tinta toalha tomate torre touca trem trevo
trigo trilha trilho trombeta tronco trovao tulipa turquesa urso uva vaca vagalume vale varanda vaso vela veleiro vento
verao verde vidro vila vinagre violao violeta vitrine voleibol vulcao xadrez xicara zebra zinco
`)

// GeneratePassphrase picks n random words (crypto/rand) joined by hyphens.
func GeneratePassphrase(n int) string {
	words := make([]string, n)
	for i := range words {
		idx, _ := rand.Int(rand.Reader, big.NewInt(int64(len(wordList))))
		words[i] = wordList[idx.Int64()]
	}
	return strings.Join(words, "-")
}

// PassphraseEntropyBits returns the entropy of an n-word passphrase from this list.
func PassphraseEntropyBits(n int) int {
	return int(float64(n) * math.Log2(float64(len(wordList))))
}
