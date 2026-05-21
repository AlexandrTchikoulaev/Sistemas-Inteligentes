"""
P2 - SNS24 Chatbot com RAG + Ollama + Integração MYCIN
Porta: 8081  |  Modelo: llama3.2:3b
RAG: construído automaticamente a partir de base_conhecimento_a.pl + base_conhecimento_b.pl

Iniciar: python chatbot_server.py
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import uuid
import re
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
import uvicorn

app = FastAPI(title="SNS24 Chatbot P2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api"
MODEL      = "llama3.2:3b"
PROLOG_URL = "http://localhost:8080"

# Localização dos ficheiros Prolog (mesmo directório do script)
_DIR = os.path.dirname(os.path.abspath(__file__))
KB_A = os.path.join(_DIR, "base_conhecimento_a.pl")
KB_B = os.path.join(_DIR, "base_conhecimento_b.pl")

# ── PARSER PROLOG ────────────────────────────────────────────────────────────

def _ler(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[AVISO] Ficheiro não encontrado: {path}")
        return ""

def _extrair_mapa(texto: str, predicado: str) -> dict:
    """Extrai predicado(Chave, 'Valor') → {chave: valor}."""
    mapa = {}
    pat  = rf"{re.escape(predicado)}\(\s*(\w+)\s*,\s*'([^']*)'\s*\)"
    for m in re.finditer(pat, texto):
        mapa[m.group(1)] = m.group(2)
    return mapa

def _extrair_niveis(texto: str) -> dict:
    """nivel(id, 'Nome', 'Recomendação') → {id: (nome, rec)}."""
    niveis = {}
    for m in re.finditer(
        r"nivel\(\s*(\w+)\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*\)", texto
    ):
        niveis[m.group(1)] = (m.group(2), m.group(3))
    return niveis

def _extrair_regras(texto: str) -> list:
    """regra(id, se([premissas]), entao(nivel), CF) → lista de dicts."""
    regras = []
    for m in re.finditer(
        r"regra\(\s*(\w+)\s*,\s*se\(\[([^\]]*)\]\)\s*,\s*entao\(\s*(\w+)\s*\)\s*,\s*([\d.]+)\s*\)",
        texto,
    ):
        rid      = m.group(1)
        prems_s  = m.group(2).strip()
        nivel    = m.group(3)
        cf       = float(m.group(4))
        premissas = [p.strip() for p in prems_s.split(",") if p.strip()]
        regras.append({"id": rid, "nivel": nivel, "cf": cf, "premissas": premissas})
    return regras


def construir_conhecimento(path_a: str, path_b: str) -> list[str]:
    """
    Lê os dois ficheiros .pl e devolve documentos RAG em linguagem simples e directa,
    optimizados para serem interpretados por um LLM de 3B parâmetros.
    Formato: "[sintoma(s)] → [nível]. [O que fazer]. [Porquê - em 1 frase]."
    """
    texto_a = _ler(path_a)
    texto_b = _ler(path_b)
    texto_total = texto_a + "\n" + texto_b

    sint_desc  = _extrair_mapa(texto_total, "sintoma")
    expl_regra = _extrair_mapa(texto_total, "explicacao_regra")
    expl_sint  = _extrair_mapa(texto_total, "explicacao")
    niveis     = _extrair_niveis(texto_total)
    regras_a   = _extrair_regras(texto_a)
    regras_b   = _extrair_regras(texto_b)

    docs = []

    # ── 1. Protocolo geral ──
    docs.append(
        "Protocolo SNS24: os sintomas são avaliados por ordem de gravidade.\n"
        "EMERGÊNCIA → ligar 112 imediatamente.\n"
        "MUITO URGENTE → ir à urgência hospitalar agora.\n"
        "URGENTE → consultar médico ou centro de saúde em 24 horas.\n"
        "POUCO URGENTE → tratar em casa, vigiar.\n"
        "SEM ALARME → vigiar em casa; ligar SNS24 (808 24 24 24) se piorar."
    )

    # ── 2. Regras da Parte A e B em formato simples ──
    for fonte, regras in [("A", regras_a), ("B", regras_b)]:
        for r in regras:
            nid  = r["nivel"]
            nome = niveis.get(nid, (nid, ""))[0]
            rec  = niveis.get(nid, ("", ""))[1]

            # Premissas em linguagem natural
            pres = []
            aus  = []
            for p in r["premissas"]:
                neg = re.match(r"nao\((\w+)\)", p)
                if neg:
                    aus.append(sint_desc.get(neg.group(1), neg.group(1)))
                else:
                    pres.append(sint_desc.get(p, p))

            if pres and aus:
                cond = f"{', '.join(pres)} (sem {', '.join(aus)})"
            elif pres:
                cond = ', '.join(pres)
            else:
                cond = "padrão geral"

            expl = expl_regra.get(r["id"], "")
            # Encurtar explicação: só a primeira frase
            expl_curta = expl.split(".")[0] + "." if expl else ""

            doc = f"{cond} → {nome}. {rec}."
            if expl_curta:
                doc += f" {expl_curta}"
            if fonte == "B":
                doc += " [padrão aprendido automaticamente]"
            docs.append(doc)

    # ── 3. Descrições dos sintomas (só os mais relevantes) ──
    # Agrupa por gravidade para o LLM ter contexto do que perguntar
    sint_grau = {
        "emergencia":    ["sem_respiracao", "sem_pulso", "resp_dificuldade",
                          "hemorragia", "inconsciente", "convulsoes"],
        "muito_urgente": ["dor_peito", "dor_irradia", "fala_dificil",
                          "fraqueza_lado", "confusao", "dor_abd"],
        "urgente":       ["febre_alta", "febre_bebe", "tosse_febre", "dor_persiste",
                          "vomitos", "diarreia", "dor_garganta"],
        "pouco_urgente": ["constipacao", "dor_leve", "febre_baixa", "mal_estar"],
    }
    for grau, sints in sint_grau.items():
        nome_grau = niveis.get(grau, (grau, ""))[0]
        linhas = []
        for s in sints:
            desc = sint_desc.get(s, s)
            expl = expl_sint.get(s, "")
            expl_curta = expl.split(".")[0] if expl else ""
            linha = f"  - {desc}"
            if expl_curta:
                linha += f": {expl_curta}"
            linhas.append(linha)
        docs.append(f"Sintomas que indicam {nome_grau}:\n" + "\n".join(linhas))

    n_total = len(docs)
    n_a     = len(regras_a)
    n_b     = len(regras_b)
    print(f"[RAG] Base construída: {n_total} documentos "
          f"({n_a} regras A + {n_b} regras B + grupos de sintomas)")
    return docs

# Constrói a base RAG e carrega as regras no arranque
CONHECIMENTO  = construir_conhecimento(KB_A, KB_B)
_kb_texto     = _ler(KB_A) + "\n" + _ler(KB_B)
REGRAS_TODAS  = _extrair_regras(_kb_texto)
NIVEIS_INFO   = _extrair_niveis(_kb_texto)   # id → (nome_display, recomendacao)

def _corrigir_acentos(texto: str) -> str:
    """Restaura acentos em texto vindo do Prolog (ficheiros sem UTF-8 acentuado)."""
    substituicoes = [
        ("evolucao", "evolução"), ("nao ", "não "), ("nao.", "não."),
        ("Nao ", "Não "), ("urgencia", "urgência"), ("Urgencia", "Urgência"),
        ("saude", "saúde"), ("Saude", "Saúde"), ("consulta", "consulta"),
        ("Marque", "Marque"), ("Autocuidados", "Autocuidados"),
        ("clinico", "clínico"), ("medico", "médico"), ("Medico", "Médico"),
        ("hospitalar", "hospitalar"), ("imediatamente", "imediatamente"),
    ]
    for original, corrigido in substituicoes:
        texto = texto.replace(original, corrigido)
    return texto


# ── RAG ENGINE ───────────────────────────────────────────────────────────────
class RAGEngine:
    def __init__(self, docs: list[str]):
        self.docs = docs
        self.vec  = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4),
                                    min_df=1, max_features=8000)
        self.mat  = self.vec.fit_transform(docs)

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        q   = self.vec.transform([query])
        sim = cosine_similarity(q, self.mat).flatten()
        idx = np.argsort(sim)[::-1][:top_k]
        return [self.docs[i] for i in idx if sim[i] > 0.01]

rag = RAGEngine(CONHECIMENTO)

# ── MAPEAMENTO DE SINTOMAS ───────────────────────────────────────────────────
SINTOMAS_KEYWORDS: dict[str, list[str]] = {
    "sem_respiracao":   ["não respira", "nao respira", "sem respiração", "parou de respirar",
                         "paragem respiratória", "apneia", "não está a respirar"],
    "sem_pulso":        ["sem pulso", "paragem cardíaca", "paragem cardiaca", "coração parou",
                         "sem batimento", "sem batimentos cardíacos"],
    "resp_dificuldade": ["dificuldade em respirar", "dificuldade a respirar", "falta de ar",
                         "dificuldade respiratória", "respirar com dificuldade", "respira mal",
                         "não consigo respirar", "não consegue respirar", "cor azulada",
                         "cianose", "falta de ar intensa", "falta de ar grave"],
    "hemorragia":       ["hemorragia", "a sangrar muito", "sangramento incontrolável",
                         "perda de sangue abundante", "muito sangue"],
    "inconsciente":     ["inconsciente", "não responde", "perdeu os sentidos", "desmaiou",
                         "perda de consciência", "sonolência marcada", "não acorda"],
    "convulsoes":       ["convulsões", "convulsoes", "convulsionar", "ataque epilético",
                         "tremores involuntários", "crise convulsiva", "está a convulsionar"],
    "dor_peito":        ["dor no peito", "aperto no peito", "pressão no peito",
                         "dor torácica", "dor no coração", "opressão no peito",
                         "dor peitoral", "peito a doer"],
    "dor_irradia":      ["irradia para o braço", "irradia para mandíbula", "irradia para costas",
                         "dor irradia", "irradiação", "dor que sobe para o braço",
                         "sobe para o braço", "vai para o braço"],
    "fala_dificil":     ["dificuldade em falar", "fala arrastada", "não consegue falar",
                         "dificuldade na fala", "fala difícil", "disartria",
                         "baralhado a falar", "falar está difícil"],
    "fraqueza_lado":    ["fraqueza num lado", "boca ao lado", "fraqueza unilateral",
                         "um lado do corpo", "braço não mexe", "perna não mexe",
                         "metade do corpo", "lado do corpo fraco"],
    "confusao":         ["confusão", "desorientado", "desorientação", "confuso",
                         "não sabe onde está", "alteração mental", "baralhado",
                         "não reconhece", "perdido", "atordoado"],
    "febre_alta":       ["febre alta", "febre acima de 39", "mais de 39 graus",
                         "temperatura muito alta", "febre elevada", "39°", "40°",
                         "39 graus", "40 graus", "febre de 39", "febre de 40"],
    "dor_abd":          ["dor abdominal", "dor de barriga", "barriga a doer muito",
                         "dor no abdómen", "abdómen rígido", "dor de estômago intensa",
                         "dor na barriga", "barriga a doer", "estômago a doer muito"],
    "febre_bebe":       ["bebé com febre", "bebe com febre", "recém-nascido com febre",
                         "filho bebé febre", "lactente com febre", "bebé tem febre"],
    "tosse_febre":      ["tosse com febre", "tosse e febre", "febre com tosse", "tosse febril",
                         "tosse e temperatura"],
    "dor_persiste":     ["dor que não passa", "dor persistente", "não cede à medicação",
                         "analgésico não ajuda", "paracetamol não passa", "dor que persiste",
                         "dor de cabeça que não passa", "dor forte que não cede"],
    "vomitos":          ["vómitos", "vomitar", "está a vomitar", "vomitou várias vezes",
                         "enjoos com vómito", "vomitou", "a vomitar"],
    "diarreia":         ["diarreia", "fezes líquidas", "diarreia grave", "dejecções líquidas",
                         "dejeções líquidas"],
    "dor_garganta":     ["dor de garganta", "garganta a doer", "dificuldade em engolir",
                         "garganta inflamada", "amígdalas", "engolir dói"],
    "constipacao":      ["constipado", "nariz entupido", "tosse ligeira", "ranho",
                         "sintomas de constipação", "resfriado", "pingo no nariz",
                         "nariz a pingar"],
    "dor_leve":         ["dor ligeira", "dor suave", "desconforto ligeiro", "dói um pouco",
                         "dor leve", "dor moderada", "dor de cabeça ligeira",
                         "dor de cabeça", "cefaleia"],
    "febre_baixa":      ["febre baixa", "temperatura ligeiramente elevada",
                         "febre de 37", "febre de 38", "37 graus", "37.5", "38 graus",
                         "temperatura a subir um pouco"],
    "mal_estar":        ["mal-estar", "mal estar", "indisposto", "não me sinto bem",
                         "cansado sem motivo", "indisposição geral", "sinto-me mal",
                         "não estou bem", "sinto mal estar"],
}

SINTOMAS_PT: dict[str, str] = {
    "sem_respiracao":   "Paragem respiratória",
    "sem_pulso":        "Paragem cardíaca",
    "resp_dificuldade": "Dificuldade respiratória grave",
    "hemorragia":       "Hemorragia abundante",
    "inconsciente":     "Inconsciência",
    "convulsoes":       "Convulsões",
    "dor_peito":        "Dor no peito",
    "dor_irradia":      "Dor com irradiação",
    "fala_dificil":     "Dificuldade na fala",
    "fraqueza_lado":    "Fraqueza num lado do corpo",
    "confusao":         "Confusão mental",
    "febre_alta":       "Febre alta (>39°C)",
    "dor_abd":          "Dor abdominal intensa",
    "febre_bebe":       "Febre em bebé (<3 meses)",
    "tosse_febre":      "Tosse com febre",
    "dor_persiste":     "Dor persistente sem alívio",
    "vomitos":          "Vómitos repetidos",
    "diarreia":         "Diarreia grave",
    "dor_garganta":     "Dor de garganta",
    "constipacao":      "Constipação",
    "dor_leve":         "Dor ligeira",
    "febre_baixa":      "Febre baixa (<38°C)",
    "mal_estar":        "Mal-estar geral",
}

SINTOMAS_EMERGENCIA = {"sem_respiracao", "sem_pulso", "resp_dificuldade",
                       "hemorragia", "inconsciente", "convulsoes"}

# Mapeamento sintoma → nível máximo esperado (para fallback se MYCIN falhar)
SINTOMAS_POR_NIVEL: dict[str, set] = {
    "emergencia":    {"sem_respiracao", "sem_pulso", "resp_dificuldade",
                      "hemorragia", "inconsciente", "convulsoes"},
    "muito_urgente": {"dor_peito", "dor_irradia", "fala_dificil",
                      "fraqueza_lado", "confusao", "dor_abd"},
    "urgente":       {"febre_alta", "febre_bebe", "tosse_febre",
                      "dor_persiste", "vomitos", "diarreia", "dor_garganta"},
    "pouco_urgente": {"constipacao", "dor_leve", "febre_baixa", "mal_estar"},
}
_ORDEM_NIVEIS = ["emergencia", "muito_urgente", "urgente", "pouco_urgente", "sem_alarme"]

# Pares mutuamente exclusivos: confirmar um nega automaticamente o outro
EXCLUSOES_MUTUAS: list[tuple] = [
    ("febre_alta", "febre_baixa"),   # temperatura >39 exclui <38 e vice-versa
]

# Dependências: se o pai é negado, o filho também é negado
# (tosse_febre = tosse + febre; sem febre não pode ser tosse_febre)
DEPENDENCIAS_NEGACAO: list[tuple] = [
    ("febre_alta", "tosse_febre"),   # nao(febre_alta) → nao(tosse_febre)
]


def nivel_por_sintomas(presentes: list) -> str:
    """Devolve o nível mais grave baseado apenas nos sintomas confirmados."""
    for nivel in _ORDEM_NIVEIS:
        if any(s in SINTOMAS_POR_NIVEL.get(nivel, set()) for s in presentes):
            return nivel
    return "sem_alarme"


def aplicar_exclusoes(sintomas: dict) -> None:
    """Propaga exclusões mútuas e dependências de negação."""
    for s1, s2 in EXCLUSOES_MUTUAS:
        if sintomas.get(s1) == "sim" and s2 not in sintomas:
            sintomas[s2] = "nao"
        elif sintomas.get(s2) == "sim" and s1 not in sintomas:
            sintomas[s1] = "nao"
    for pai, filho in DEPENDENCIAS_NEGACAO:
        if sintomas.get(pai) == "nao":
            sintomas[filho] = "nao"


DESCRICAO_PERGUNTA: dict[str, str] = {
    "sem_pulso":        "A pessoa tem pulso? Consegue sentir o coração a bater?",
    "hemorragia":       "Há sangramento abundante, difícil de controlar?",
    "sem_respiracao":   "A pessoa está a respirar normalmente?",
    "resp_dificuldade": "Sente falta de ar ou dificuldade a respirar?",
    "convulsoes":       "Teve convulsões ou tremores involuntários?",
    "inconsciente":     "Está consciente e a responder?",
    "confusao":         "Nota confusão mental ou desorientação?",
    "fala_dificil":     "Tem dificuldade em falar ou a fala está arrastada?",
    "fraqueza_lado":    "Sente fraqueza num lado do corpo ou boca ao lado?",
    "dor_peito":        "Tem dor ou aperto no peito?",
    "dor_irradia":      "A dor irradia para o braço, mandíbula ou costas?",
    "dor_abd":          "Tem dor abdominal intensa?",
    "febre_alta":       "Tem febre alta, acima de 39 graus?",
    "febre_bebe":       "É um bebé com menos de 3 meses com febre?",
    "tosse_febre":      "Tem tosse acompanhada de febre?",
    "dor_persiste":     "Tem alguma dor que não cede à medicação habitual?",
    "diarreia":         "Tem diarreia grave ou sinais de desidratação?",
    "dor_garganta":     "Tem dor de garganta com dificuldade em engolir?",
    "vomitos":          "Tem vómitos repetidos que impedem de beber líquidos?",
    "dor_leve":         "Tem alguma dor, mesmo que ligeira?",
    "febre_baixa":      "Tem febre baixa, entre 37 e 38 graus?",
    "constipacao":      "Tem sintomas de constipação, como nariz entupido ou tosse ligeira?",
    "mal_estar":        "Sente mal-estar geral ou indisposição?",
}

ORDEM_PROLOG = [
    "sem_pulso", "hemorragia", "sem_respiracao", "resp_dificuldade",
    "convulsoes", "inconsciente", "confusao", "fala_dificil",
    "fraqueza_lado", "dor_peito", "dor_irradia", "dor_abd",
    "febre_alta", "febre_bebe", "tosse_febre", "dor_persiste",
    "diarreia", "dor_garganta", "vomitos", "dor_leve",
    "febre_baixa", "constipacao", "mal_estar",
]

# ── UTILITÁRIOS DE CONVERSA ──────────────────────────────────────────────────

def e_resposta_simples(text: str) -> Optional[bool]:
    """Devolve True/False se a mensagem é um sim/não claro, None caso contrário."""
    t = text.lower().strip().rstrip(".,!? ")
    SIM = {"sim", "s", "é", "e", "tenho", "sinto", "sinto-me", "yes", "claro",
           "também", "tambem", "efetivamente", "efectivamente", "pois", "exactamente",
           "exatamente", "afirmativo", "com certeza", "certamente"}
    NAO = {"não", "nao", "n", "no", "nunca", "nem", "negativo",
           "não tenho", "nao tenho", "não sinto", "nao sinto",
           "não tive", "nao tive", "sem"}
    if t in SIM:
        return True
    if t in NAO:
        return False
    # Começa por palavra clara
    for w in ["sim ", "claro ", "tenho ", "sinto "]:
        if t.startswith(w):
            return True
    for w in ["não ", "nao ", "nunca "]:
        if t.startswith(w) and len(t) < 25:
            return False
    return None


def calcular_proximo_sintoma(sintomas: dict) -> Optional[str]:
    """
    Dado o estado actual dos sintomas conhecidos, devolve o sintoma mais informativo
    a perguntar a seguir, guiado pelas regras da base de conhecimento.

    Para cada regra activa (não eliminada, não resolvida), as suas premissas ainda
    desconhecidas recebem um score = CF * (1 + n_premissas_já_confirmadas).
    O sintoma com maior score acumulado é o mais discriminante.
    """
    from collections import defaultdict
    scores: defaultdict = defaultdict(float)

    for regra in REGRAS_TODAS:
        cf = regra["cf"]
        n_confirmadas = 0
        desconhecidos = []
        eliminada = False

        for p in regra["premissas"]:
            m_neg = re.match(r"nao\((\w+)\)", p)
            sint  = m_neg.group(1) if m_neg else p
            val   = sintomas.get(sint)

            if m_neg:
                # premissa nao(x): a regra precisa que x esteja ausente
                if val == "sim":
                    eliminada = True
                    break
                elif val == "nao":
                    n_confirmadas += 1
                else:
                    desconhecidos.append(sint)
            else:
                # premissa positiva: a regra precisa que x esteja presente
                if val == "nao":
                    eliminada = True
                    break
                elif val == "sim":
                    n_confirmadas += 1
                else:
                    desconhecidos.append(sint)

        if eliminada or not desconhecidos:
            continue

        peso = cf * (1 + n_confirmadas)
        for sint in desconhecidos:
            scores[sint] += peso

    return max(scores, key=scores.__getitem__) if scores else None


# ── MODELOS PYDANTIC ─────────────────────────────────────────────────────────
class MsgBody(BaseModel):
    session_id: Optional[str] = None
    message: str

# ── SESSÕES ──────────────────────────────────────────────────────────────────
sessions: dict = {}

# ── DETECÇÃO DE SINTOMAS ─────────────────────────────────────────────────────
def detectar_sintomas_keywords(text: str) -> dict:
    tl = text.lower()
    neg_words = ["não ", "nao ", "sem ", "nunca ", "nem ", "ausência de "]
    presentes, ausentes = [], []
    for sint, kws in SINTOMAS_KEYWORDS.items():
        for kw in kws:
            if kw in tl:
                idx     = tl.find(kw)
                ctx_pre = tl[max(0, idx - 35):idx]
                if any(neg in ctx_pre for neg in neg_words):
                    if sint not in ausentes:
                        ausentes.append(sint)
                else:
                    if sint not in presentes:
                        presentes.append(sint)
                break
    return {"presentes": presentes, "ausentes": ausentes}


async def extrair_sintomas_llm(text: str) -> dict:
    lista = "\n".join(f"- {k}: {v[0]}" for k, v in SINTOMAS_KEYWORDS.items())
    prompt = (
        f'Analisa o texto em português e diz quais sintomas médicos estão presentes ou ausentes.\n'
        f'Texto: "{text}"\n\n'
        f'Sintomas possíveis:\n{lista}\n\n'
        f'Responde APENAS com JSON válido:\n'
        f'{{"presentes": ["id1", ...], "ausentes": ["id2", ...]}}\n'
        f'Usa apenas os IDs da lista. Se não há sintomas claros: {{"presentes": [], "ausentes": []}}'
    )
    async with httpx.AsyncClient(timeout=25.0) as client:
        try:
            r = await client.post(
                f"{OLLAMA_URL}/generate",
                json={"model": MODEL, "prompt": prompt, "stream": False, "format": "json"},
            )
            r.raise_for_status()
            parsed = json.loads(r.json().get("response", "{}"))
            return {
                "presentes": [s for s in parsed.get("presentes", []) if s in SINTOMAS_KEYWORDS],
                "ausentes":  [s for s in parsed.get("ausentes",  []) if s in SINTOMAS_KEYWORDS],
            }
        except Exception:
            return detectar_sintomas_keywords(text)


# ── INTEGRAÇÃO PROLOG ────────────────────────────────────────────────────────
async def triagem_mycin(sintomas_presentes: list[str]) -> dict:
    async with httpx.AsyncClient(timeout=40.0) as client:
        try:
            r    = await client.post(f"{PROLOG_URL}/api/start")
            data = r.json()
            itr  = 0
            while data.get("type") == "pergunta" and itr < 30:
                itr  += 1
                sint  = data.get("sintoma", "")
                tipo  = "sim" if sint in sintomas_presentes else "nao"
                r     = await client.post(
                    f"{PROLOG_URL}/api/answer",
                    json={"sintoma": sint, "tipo": tipo, "certeza": 100},
                )
                data = r.json()
            return data
        except Exception as e:
            return {"type": "error", "error": str(e)}


# ── GERAÇÃO DE RESPOSTA ──────────────────────────────────────────────────────

async def _chamar_ollama(prompt: str, max_tokens: int = 200) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.post(
                f"{OLLAMA_URL}/generate",
                json={
                    "model":  MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": max_tokens,
                        "stop": ["Utilizador:", "Utente:", "\n\n\n"],
                    },
                },
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
        except Exception as e:
            return f"Ocorreu um erro: {e}"


async def gerar_resposta(session: dict, user_msg: str, resultado_prolog: Optional[dict],
                         prox_sint: Optional[str] = None) -> str:

    conf_list = [SINTOMAS_PT.get(s, s) for s, v in session["sintomas"].items() if v == "sim"]
    conf_txt  = ", ".join(conf_list) if conf_list else "nenhum"

    hist = session["history"][-4:]
    hist_txt = "\n".join(
        f"{'Utilizador' if m['role'] == 'user' else 'Assistente'}: {m['content']}"
        for m in hist if m["role"] != "system"
    )

    # ── Caso MYCIN: resultado final — template fixo, sem LLM ────────────────
    if resultado_prolog and resultado_prolog.get("type") == "resultado":
        nivel = resultado_prolog.get("nivel", "")
        rec   = _corrigir_acentos(resultado_prolog.get("recomendacao", ""))
        cf    = min(resultado_prolog.get("confianca_pct", 0), 95)
        sint_conf = conf_txt if conf_txt != "nenhum" else "os sintomas descritos"
        emergencia_aviso = "\n\n⚠️ **Ligue 112 (INEM) imediatamente.**" if "EMERG" in nivel.upper() else ""
        return (
            f"Com base nos sintomas que descreveu ({sint_conf}), a triagem está concluída.\n\n"
            f"**Nível: {nivel}** (confiança: {cf}%)\n\n"
            f"**Recomendação:** {rec}{emergencia_aviso}"
        )

    # ── Caso conversa: acknowledgment (LLM) + pergunta (código) ──────────────
    pergunta = DESCRICAO_PERGUNTA.get(prox_sint, "") if prox_sint else ""

    if pergunta:
        # LLM gera APENAS o acknowledgment — 1 frase neutra, sem recomendações clínicas
        ack_prompt = (
            f"SNS24. Português de Portugal.\n"
            f"O utilizador disse: \"{user_msg}\"\n"
            f"Escreve UMA frase curta e neutra a reconhecer o que disse (ex: 'Entendido.' ou 'Compreendo.').\n"
            f"PROIBIDO: diagnósticos, recomendações, mencionar 112, urgência ou gravidade.\n"
            f"Resposta (só a frase, sem aspas):"
        )
        ack = await _chamar_ollama(ack_prompt, max_tokens=30)
        # Remover qualquer recomendação clínica que o modelo possa ter gerado
        ack = re.sub(r"\?.*", "", ack).strip().rstrip(".,")
        ack = re.sub(r"(?i)(112|urgên|emergên|imediatamente|ligue|grave|sério).*", "", ack).strip().rstrip(".,")
        if not ack:
            ack = "Entendido"
        return f"{ack}. {pergunta}"
    else:
        # Motor esgotou perguntas — pede ao LLM para resumir e anunciar análise
        ctx_rag = "\n".join(f"- {d}" for d in rag.retrieve(user_msg, top_k=2))
        prompt = (
            f"SNS24. Português de Portugal. 2-3 frases.\n"
            f"Sintomas confirmados: {conf_txt}\n"
            f"Protocolo SNS24:\n{ctx_rag}\n\n"
            f"Conversa:\n{hist_txt}\n"
            f"Utilizador: {user_msg}\n"
            f"Resume o que sabes e diz que vais analisar a situação.\nAssistente:"
        )
        return await _chamar_ollama(prompt, max_tokens=150)


# ── ENDPOINTS ────────────────────────────────────────────────────────────────
@app.post("/api/chat/start")
async def start_chat():
    sid = str(uuid.uuid4())
    sessions[sid] = {
        "sintomas":         {},
        "history":          [],
        "triagem_feita":    False,
        "resultado_prolog": None,
        "ultima_pergunta":  None,   # sintoma sobre o qual se perguntou por último
        "n_trocas":         0,      # número de turnos de conversa
    }
    boas_vindas = (
        "Olá! Sou o assistente de triagem do SNS24. Estou aqui para o ajudar a perceber "
        "qual o serviço de saúde mais adequado para a sua situação.\n\n"
        "⚠️ Em caso de emergência grave, ligue sempre o **112**.\n\n"
        "Por favor, descreva os seus sintomas ou o que está a sentir."
    )
    sessions[sid]["history"].append({"role": "assistant", "content": boas_vindas})
    return {"session_id": sid, "message": boas_vindas}


@app.post("/api/chat/message")
async def chat_message(body: MsgBody):
    sid = body.session_id
    if not sid or sid not in sessions:
        raise HTTPException(status_code=400, detail="Sessão inválida. Inicie uma nova conversa.")

    session  = sessions[sid]
    user_msg = body.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Mensagem vazia.")

    session["history"].append({"role": "user", "content": user_msg})
    session["n_trocas"] += 1

    # 1. Se a mensagem é um sim/não simples à última pergunta, mapeá-la directamente
    resp_simples = e_resposta_simples(user_msg)
    if resp_simples is not None and session.get("ultima_pergunta"):
        sint_perguntado = session["ultima_pergunta"]
        if sint_perguntado not in session["sintomas"]:
            session["sintomas"][sint_perguntado] = "sim" if resp_simples else "nao"

    # 2. Detecção adicional: keywords + LLM (não sobrescreve o que já foi mapeado)
    # Ignorar LLM em respostas muito curtas (sim/não/talvez) — evita alucinações
    kw        = detectar_sintomas_keywords(user_msg)
    llm_extra = await extrair_sintomas_llm(user_msg) if len(user_msg.strip()) > 8 else {"presentes": [], "ausentes": []}

    for s in set(kw["presentes"] + llm_extra["presentes"]):
        if s not in session["sintomas"]:
            session["sintomas"][s] = "sim"
    for s in set(kw["ausentes"] + llm_extra["ausentes"]):
        if s not in session["sintomas"]:
            session["sintomas"][s] = "nao"

    # 2b. Aplicar exclusões mútuas (ex: febre_alta exclui febre_baixa)
    aplicar_exclusoes(session["sintomas"])

    # 3. Motor de regras: calcular a próxima pergunta mais informativa
    prox_sint = calcular_proximo_sintoma(session["sintomas"])

    # 4. Decidir se é altura de fazer triagem formal MYCIN
    has_emergency = any(session["sintomas"].get(s) == "sim" for s in SINTOMAS_EMERGENCIA)
    n_known       = sum(1 for v in session["sintomas"].values() if v in ("sim", "nao"))
    # Sintomas que justificam triagem antecipada mesmo com poucas respostas
    SINTOMAS_URGENTES = {"febre_alta", "febre_bebe", "dor_peito", "dor_abd",
                         "fala_dificil", "fraqueza_lado", "confusao", "dor_persiste"}
    has_urgente = any(session["sintomas"].get(s) == "sim" for s in SINTOMAS_URGENTES)
    deve_triagem  = (
        (has_emergency)
        or (has_urgente and n_known >= 2)
        or (prox_sint is None and n_known >= 2)
        or (session["n_trocas"] >= 6 and n_known >= 4)
    ) and not session["triagem_feita"]

    resultado_prolog = None
    if deve_triagem:
        presentes = [s for s, v in session["sintomas"].items() if v == "sim"]
        resultado_mycin = await triagem_mycin(presentes)
        session["triagem_feita"] = True   # sempre marcar — evita chamadas repetidas

        nivel_mycin    = resultado_mycin.get("nivel", "")
        nivel_esperado = nivel_por_sintomas(presentes)

        # Fallback: MYCIN falhou (servidor Prolog não disponível) ou resultado inválido
        if resultado_mycin.get("type") != "resultado":
            nome, rec = NIVEIS_INFO.get(nivel_esperado, (nivel_esperado, "Consulte um médico."))
            resultado_prolog = {
                "type":          "resultado",
                "nivel":         nome,
                "recomendacao":  rec,
                "confianca_pct": 65,
            }
        # Validar: MYCIN não pode ser mais grave do que os sintomas justificam
        elif nivel_mycin == "emergencia" and nivel_esperado not in ("emergencia",):
            nome, rec = NIVEIS_INFO.get(nivel_esperado, (nivel_esperado, "Consulte um médico."))
            resultado_prolog = {
                "type":          "resultado",
                "nivel":         nome,
                "recomendacao":  rec,
                "confianca_pct": 70,
            }
        else:
            resultado_prolog = resultado_mycin

        session["resultado_prolog"] = resultado_prolog

    # 5. Registar a próxima pergunta na sessão (para mapear sim/não no próximo turno)
    session["ultima_pergunta"] = prox_sint if not resultado_prolog else None

    resposta = await gerar_resposta(session, user_msg, resultado_prolog, prox_sint)

    sintomas_json = [
        {"id": s, "nome": SINTOMAS_PT.get(s, s), "presente": v == "sim"}
        for s, v in session["sintomas"].items()
    ]

    return {
        "message":          resposta,
        "sintomas":         sintomas_json,
        "triagem_feita":    session["triagem_feita"],
        "resultado_prolog": session["resultado_prolog"],
    }


@app.get("/api/chat/status")
async def status():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            r      = await client.get("http://localhost:11434/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            ready  = any(MODEL.split(":")[0] in m for m in models)
            return {"ollama": True, "models": models, "model_ready": ready, "model": MODEL}
        except Exception:
            return {"ollama": False, "models": [], "model_ready": False, "model": MODEL}


@app.get("/api/chat/kb_info")
async def kb_info():
    """Informação sobre a base de conhecimento RAG carregada."""
    return {
        "total_documentos": len(CONHECIMENTO),
        "ficheiros": [KB_A, KB_B],
        "preview": CONHECIMENTO[:3],
    }


# ── ARRANQUE ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  SNS24 Chatbot P2 - RAG + Ollama + MYCIN")
    print(f"  Modelo : {MODEL}")
    print(f"  API    : http://localhost:8081")
    print(f"  RAG    : {len(CONHECIMENTO)} documentos carregados")
    print(f"           (base_conhecimento_a.pl + base_conhecimento_b.pl)")
    print("=" * 55 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8081, reload=False)
