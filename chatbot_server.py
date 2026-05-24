"""
P2 - SNS24 Chatbot com RAG + Ollama + Integração MYCIN
Porta: 8082  |  Modelo: llama3.2:3b
RAG: construído automaticamente a partir de base_conhecimento_a.pl + base_conhecimento_b.pl

Iniciar: python chatbot_server.py
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
                          "fraqueza_lado", "confusao", "dor_abd",
                          "reacao_alergica_grave", "dor_cabeca_subita"],
        "urgente":       ["febre_alta", "febre_bebe", "tosse_febre", "dor_persiste",
                          "vomitos", "diarreia", "dor_garganta",
                          "rigidez_nuca", "rash_petequial", "visao_alterada"],
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
# Mapeamento inverso: nome display (maiúsculas) → id Prolog
_NIVEL_NOME_PARA_ID = {nome.upper(): id_ for id_, (nome, _) in NIVEIS_INFO.items()}

EXPLICACOES_SINT = _extrair_mapa(_kb_texto, "explicacao")

# Ordem de colunas do triagens.csv (gerado pelo P1/P2)
CSV_SINTOMAS = [
    "sem_respiracao","sem_pulso","resp_dificuldade","hemorragia","inconsciente",
    "convulsoes","dor_peito","dor_irradia","fala_dificil","fraqueza_lado",
    "febre_alta","confusao","dor_abd","febre_bebe","tosse_febre","dor_persiste",
    "vomitos","diarreia","dor_garganta","constipacao","dor_leve","febre_baixa","mal_estar",
]
CSV_PATH = os.path.join(_DIR, "triagens.csv")

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


def salvar_triagem_csv(session: dict, resultado: dict) -> None:
    """Grava a triagem concluída em triagens.csv (append). Funciona mesmo em modo fallback Python."""
    nivel_id = resultado.get("nivel_id", "sem_sintomas_alarme")
    valores  = ["1" if session["sintomas"].get(s) == "sim" else "0" for s in CSV_SINTOMAS]
    linha    = ",".join(valores) + "," + nivel_id + "\n"
    try:
        with open(CSV_PATH, "a", encoding="utf-8") as f:
            f.write(linha)
        print(f"[CSV] Triagem gravada: {nivel_id}")
    except Exception as e:
        print(f"[CSV] Erro ao gravar triagem: {e}")


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
                         "dor peitoral", "peito a doer", "dor forte no peito",
                         "dor intensa no peito", "dor de peito", "dores no peito",
                         "peito dói", "peito doer"],
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
                         "39 graus", "40 graus", "febre de 39", "febre de 40",
                         "acima de 39", "mais de 39", "39.5", "40.5"],
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
                         "garganta inflamada", "amígdalas", "engolir dói",
                         "garganta dói", "garganta doi", "doi a garganta",
                         "doi me a garganta", "doi-me a garganta",
                         "dói a garganta", "dói-me a garganta",
                         "dói na garganta", "doi na garganta",
                         "dor na garganta", "dói garganta",
                         "um bocado a garganta", "bocado a garganta",
                         "garganta a doer um bocado", "garganta a doer um pouco"],
    "constipacao":      ["constipado", "nariz entupido", "tosse ligeira", "ranho",
                         "sintomas de constipação", "resfriado", "pingo no nariz",
                         "nariz a pingar", "tenho tosse", "sinto tosse", "com tosse",
                         "tosse seca", "tosse produtiva"],
    "dor_leve":         ["dor ligeira", "dor suave", "desconforto ligeiro", "dói um pouco",
                         "dor leve", "dor moderada", "dor de cabeça ligeira",
                         "dor de cabeça", "cefaleia",
                         "doi um bocado", "dói um bocado",
                         "doi me um bocado", "dói-me um bocado",
                         "dói-me um pouco", "doi me um pouco",
                         "um bocado a doer",
                         # expressões coloquiais de dor geral
                         "muitas dores", "muita dor", "só dores", "so dores",
                         "tenho dores", "sinto dores", "com dores",
                         "dores no corpo", "dores pelo corpo",
                         "dores generalizadas", "dores musculares",
                         "dores nos músculos", "dores nos musculos",
                         "muito dores", "bastantes dores",
                         "cheio de dores", "cheia de dores",
                         "dores em todo", "dores por todo"],
    "febre_baixa":      ["febre baixa", "temperatura ligeiramente elevada",
                         "febre de 37", "febre de 38", "37 graus", "37.5", "38 graus",
                         "temperatura a subir um pouco",
                         "febre mas não", "febre mas nao",
                         "febre, mas não", "febre, mas nao",
                         "febre ligeira", "febre moderada", "alguma febre",
                         "pouca febre", "um pouco de febre", "febre não alta",
                         "febre nao alta", "febre não muito", "febre nao muito",
                         "um bocado de febre", "bocado de febre",
                         "pouco de febre", "febrezinha"],
    "mal_estar":        ["mal-estar", "mal estar", "mau estar", "mau-estar",
                         "indisposto", "não me sinto bem",
                         "cansado sem motivo", "indisposição geral", "sinto-me mal",
                         "não estou bem", "sinto mal estar", "sinto mau estar",
                         "mal disposto", "mal-disposto", "indisposta", "mal disposta",
                         "sinto-me mal disposto", "meio indisposto",
                         "sinto-me indisposto", "sinto-me indisposta",
                         "não me sinto nada bem", "nao me sinto nada bem"],
    "rigidez_nuca":          ["rigidez da nuca", "nuca rígida", "pescoço rígido",
                              "não dobra a nuca", "nuca dura", "pescoço não dobra",
                              "não encosta o queixo ao peito", "nuca não dobra"],
    "rash_petequial":        ["manchas na pele que não desaparecem", "manchas vermelhas que não saem",
                              "manchas roxas na pele", "petéquias", "rash com febre",
                              "manchas hemorrágicas", "teste do copo", "manchas que ficam",
                              "manchas que não somem"],
    "reacao_alergica_grave": ["reação alérgica grave", "alergia grave", "inchaço da face",
                              "inchaço na língua", "inchaço na garganta", "lábios inchados",
                              "anafilaxia", "choque anafilático", "garganta a inchar",
                              "cara a inchar", "língua a inchar", "face inchada"],
    "dor_cabeca_subita":     ["pior dor de cabeça da vida", "dor de cabeça repentina muito forte",
                              "dor de cabeça muito intensa de repente", "dor de cabeça nunca igual",
                              "dor de cabeça explosiva", "dor de cabeça como nunca senti",
                              "dor de cabeça início súbito"],
    "visao_alterada":        ["perda de visão", "não vejo bem de repente", "visão turva de repente",
                              "visão dupla", "não consigo ver", "olho não vê", "visão a falhar",
                              "manchas na visão", "visão alterada de repente"],
}

SINTOMAS_PT: dict[str, str] = {
    "sem_respiracao":        "Paragem respiratória",
    "sem_pulso":             "Paragem cardíaca",
    "resp_dificuldade":      "Dificuldade respiratória grave",
    "hemorragia":            "Hemorragia abundante",
    "inconsciente":          "Inconsciência",
    "convulsoes":            "Convulsões",
    "dor_peito":             "Dor no peito",
    "dor_irradia":           "Dor com irradiação",
    "fala_dificil":          "Dificuldade na fala",
    "fraqueza_lado":         "Fraqueza num lado do corpo",
    "confusao":              "Confusão mental",
    "febre_alta":            "Febre alta (>39°C)",
    "dor_abd":               "Dor abdominal intensa",
    "febre_bebe":            "Febre em bebé (<3 meses)",
    "tosse_febre":           "Tosse com febre",
    "dor_persiste":          "Dor persistente sem alívio",
    "vomitos":               "Vómitos repetidos",
    "diarreia":              "Diarreia grave",
    "dor_garganta":          "Dor de garganta",
    "constipacao":           "Constipação",
    "dor_leve":              "Dores",
    "febre_baixa":           "Febre baixa (<38°C)",
    "mal_estar":             "Mal-estar geral",
    "rigidez_nuca":          "Rigidez da nuca",
    "rash_petequial":        "Rash petequial (manchas na pele)",
    "reacao_alergica_grave": "Reação alérgica grave / Anafilaxia",
    "dor_cabeca_subita":     "Dor de cabeça súbita e intensa",
    "visao_alterada":        "Alteração súbita da visão",
}

# Labels específicos para dor_leve consoante a localização descrita pelo utilizador.
# Cada entrada: (lista de keywords trigger, label a mostrar na sidebar).
# A primeira correspondência ganha; se nenhuma bater, mantém "Dores".
DOR_LEVE_LABELS: list[tuple] = [
    (["dor de cabeça", "dores de cabeça", "cefaleia", "dor na cabeça",
      "dói a cabeça", "doi a cabeça", "cabeça a doer"],          "Dor de cabeça"),
    (["dor nas costas", "dores nas costas", "dor na coluna",
      "costas a doer", "dor lombar"],                             "Dor nas costas"),
    (["dor muscular", "dores musculares", "músculos a doer",
      "dores nos músculos", "dores nos musculos"],                "Dores musculares"),
    (["dor nas pernas", "pernas a doer", "dor nas pernas",
      "dor nos membros", "membros a doer"],                       "Dores nos membros"),
    (["dor no pescoço", "pescoço a doer", "dor no pescoco"],      "Dor no pescoço"),
    (["dor no peito ligeira", "peito a doer ligeiramente"],        "Dor no peito (ligeira)"),
    (["dor de dentes", "dentes a doer", "dor dentária"],          "Dor de dentes"),
    (["dor nos ouvidos", "ouvidos a doer", "dor de ouvidos"],     "Dor de ouvidos"),
    (["dor nos olhos", "olhos a doer"],                           "Dor nos olhos"),
]

SINTOMAS_EMERGENCIA = {"sem_respiracao", "sem_pulso", "resp_dificuldade",
                       "hemorragia", "inconsciente", "convulsoes"}

# Mapeamento sintoma → nível máximo esperado (para fallback se MYCIN falhar)
SINTOMAS_POR_NIVEL: dict[str, set] = {
    "emergencia":    {"sem_respiracao", "sem_pulso", "resp_dificuldade",
                      "hemorragia", "inconsciente", "convulsoes"},
    "muito_urgente": {"dor_peito", "dor_irradia", "fala_dificil",
                      "fraqueza_lado", "confusao", "dor_abd",
                      "reacao_alergica_grave", "dor_cabeca_subita", "rash_petequial"},
    "urgente":       {"febre_alta", "febre_bebe", "tosse_febre",
                      "dor_persiste", "vomitos", "diarreia", "dor_garganta",
                      "rigidez_nuca", "visao_alterada"},
    "pouco_urgente": {"constipacao", "dor_leve", "febre_baixa", "mal_estar"},
}
_ORDEM_NIVEIS = ["emergencia", "muito_urgente", "urgente", "pouco_urgente", "sem_alarme"]

# Pares mutuamente exclusivos: confirmar um nega automaticamente o outro
EXCLUSOES_MUTUAS: list[tuple] = [
    ("febre_alta", "febre_baixa"),   # temperatura >39 exclui <38 e vice-versa
]

# Dependências: se o pai é negado, o filho também é negado.
# NOTA: febre_alta → tosse_febre foi REMOVIDO — tosse com febre baixa (37-38°C) é válido;
# negar tosse_febre automaticamente impedia detectar constipação com subfebrícula.
DEPENDENCIAS_NEGACAO: list[tuple] = []


def nivel_por_sintomas(presentes: list) -> str:
    """Devolve o nível mais grave avaliando primeiro as regras da base de conhecimento
    (combinações de sintomas) e só depois o mapeamento individual por sintoma.
    Isto garante que r_em6 (febre_alta+confusao+dor_abd → sépsis) é detectado
    mesmo quando o servidor Prolog não está disponível."""
    presentes_set = set(presentes)
    # 1. Verificar se alguma regra está completamente satisfeita (por ordem de gravidade)
    for nivel in _ORDEM_NIVEIS:
        for regra in REGRAS_TODAS:
            if regra["nivel"] != nivel:
                continue
            ok = True
            for p in regra["premissas"]:
                m_neg = re.match(r"nao\((\w+)\)", p)
                if m_neg:
                    if m_neg.group(1) in presentes_set: ok = False; break
                else:
                    if p not in presentes_set: ok = False; break
            if ok:
                return nivel
    # 2. Fallback: mapeamento individual
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
    "sem_pulso":             "A pessoa tem pulso? Consegue sentir o coração a bater?",
    "hemorragia":            "Há sangramento abundante, difícil de controlar?",
    "sem_respiracao":        "A pessoa está a respirar normalmente?",
    "resp_dificuldade":      "Sente falta de ar ou dificuldade a respirar?",
    "convulsoes":            "Teve convulsões ou tremores involuntários?",
    "inconsciente":          "Está consciente e a responder?",
    "confusao":              "Nota confusão mental ou desorientação?",
    "fala_dificil":          "Tem dificuldade em falar ou a fala está arrastada?",
    "fraqueza_lado":         "Sente fraqueza num lado do corpo ou boca ao lado?",
    "dor_peito":             "Tem dor ou aperto no peito?",
    "dor_irradia":           "A dor irradia para o braço, mandíbula ou costas?",
    "dor_abd":               "Tem dor abdominal intensa?",
    "febre_alta":            "Tem febre alta, acima de 39 graus?",
    "febre_bebe":            "É um bebé com menos de 3 meses com febre?",
    "tosse_febre":           "Tem tosse acompanhada de febre?",
    "dor_persiste":          "Tem alguma dor que não cede à medicação habitual?",
    "diarreia":              "Tem diarreia grave ou sinais de desidratação?",
    "dor_garganta":          "Tem dor de garganta com dificuldade em engolir?",
    "vomitos":               "Tem vómitos repetidos que impedem de beber líquidos?",
    "dor_leve":              "Tem alguma dor ou desconforto físico?",
    "febre_baixa":           "Tem febre baixa, entre 37 e 38 graus?",
    "constipacao":           "Tem sintomas de constipação, como nariz entupido ou tosse ligeira?",
    "mal_estar":             "Sente mal-estar geral ou indisposição?",
    "rigidez_nuca":          "Consegue encostar o queixo ao peito sem dificuldade, ou sente a nuca rígida?",
    "rash_petequial":        "Tem manchas vermelhas ou roxas na pele que não desaparecem quando se pressiona com um dedo?",
    "reacao_alergica_grave": "Teve alguma reação alérgica com inchaço da face, língua ou garganta?",
    "dor_cabeca_subita":     "Tem dor de cabeça muito intensa de início súbito, diferente de tudo o que já sentiu?",
    "visao_alterada":        "Tem alguma alteração súbita na visão, como visão turva, dupla ou perda de visão?",
}

ORDEM_PROLOG = [
    "sem_pulso", "hemorragia", "sem_respiracao", "resp_dificuldade",
    "reacao_alergica_grave", "convulsoes", "inconsciente", "confusao",
    "fala_dificil", "fraqueza_lado", "visao_alterada",
    "dor_peito", "dor_irradia", "dor_cabeca_subita", "dor_abd",
    "febre_alta", "rigidez_nuca", "rash_petequial",
    "febre_bebe", "tosse_febre", "dor_persiste",
    "diarreia", "dor_garganta", "vomitos", "dor_leve",
    "febre_baixa", "constipacao", "mal_estar",
]

# ── UTILITÁRIOS DE CONVERSA ──────────────────────────────────────────────────

def e_resposta_simples(text: str) -> Optional[bool]:
    """Devolve True/False se a mensagem é um sim/não claro, None caso contrário."""
    t = text.lower().strip().rstrip(".,!? ")
    # Normalizar vírgulas/ponto-e-vírgula → espaço (ex: "sim, a dor..." → "sim a dor...")
    t = re.sub(r"[,;]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    SIM = {"sim", "s", "é", "e", "tenho", "sinto", "sinto-me", "yes", "yep", "yha",
           "ya", "yeah", "claro", "também", "tambem", "efetivamente", "efectivamente",
           "pois", "exactamente", "exatamente", "afirmativo", "com certeza", "certamente",
           # intensificadores e afirmações indiretas — mapeados deterministicamente, sem LLM
           "muito", "bastante", "claramente", "definitivamente", "totalmente",
           "absolutamente", "obviamente", "óbvio", "obvio", "sem dúvida", "sem duvida",
           "tenho sim", "claro que sim",
           # afirmações suaves — tratadas como sim para não perder sintomas
           "acho que sim", "creio que sim", "parece que sim", "julgo que sim"}
    NAO = {"não", "nao", "n", "no", "nunca", "nem", "negativo",
           "não tenho", "nao tenho", "não sinto", "nao sinto",
           "não tive", "nao tive", "sem", "jamais",
           "de jeito nenhum", "de modo nenhum", "de maneira nenhuma"}
    if t in SIM:
        return True
    if t in NAO:
        return False
    # Qualificadores que invalidam uma resposta aparentemente positiva:
    # 1. Negação após conjunção adversativa ("tenho febre mas não acima de 39")
    # 2. Frequência intermitente ("sinto tonto de vez em quando") → incerteza
    _INVALIDA_SIM = {
        "mas não", "mas nao", "não acho", "nao acho", "mas não é", "mas nao e",
        "mas não tenho", "mas nao tenho", "não creio", "nao creio",
        "de vez em quando", "às vezes", "as vezes", "por vezes",
        "algumas vezes", "raramente", "ocasionalmente",
    }
    # Começa por palavra clara (com ou sem vírgula a seguir)
    for w in ["sim ", "claro ", "tenho ", "sinto ", "também ", "tambem ",
              "definitivamente ", "totalmente ", "absolutamente ", "claramente "]:
        if t.startswith(w):
            if any(q in t for q in _INVALIDA_SIM):
                return None   # resposta qualificada — tratar como incerta
            return True
    for w in ["não ", "nao ", "nunca "]:
        if t.startswith(w) and len(t) < 55:
            return False
    return None


_INCERTO_PALAVRAS = {
    "talvez", "não sei", "nao sei", "talvez sim", "talvez não", "talvez nao",
    "mais ou menos", "possivelmente", "não tenho a certeza", "nao tenho a certeza",
    "incerto", "incerta", "pode ser", "acho que não", "acho que nao",
    "não tenho certeza", "nao tenho certeza", "não tenho a certeza",
    # Frequência intermitente: sintoma presente "às vezes" não é confirmação clínica
    "de vez em quando", "às vezes", "as vezes", "por vezes",
    "algumas vezes", "raramente", "ocasionalmente", "de tempos em tempos",
}

def e_resposta_incerta(text: str) -> bool:
    """Verdade se a mensagem expressa incerteza (talvez/não sei/pode ser)."""
    t = text.lower().strip()
    return any(p in t for p in _INCERTO_PALAVRAS) and e_resposta_simples(text) is None


_PORQUE_PALAVRAS = {
    "porquê", "por quê", "por que", "porque me pergunta", "para que precisa",
    "para que quer saber", "pra que", "que tem a ver", "explica",
    "o que significa", "não entendo", "nao entendo",
    "não percebo", "nao percebo", "por que razão", "por que motivo",
    "porque?", "porque isso", "porque é que", "porque e que",
    "não compreendo", "nao compreendo", "pode explicar", "o que quer dizer",
}

def e_intencao_porque(text: str) -> bool:
    """Verdade se a mensagem é um pedido de explicação/justificação clínica."""
    t = text.lower().strip()
    return any(p in t for p in _PORQUE_PALAVRAS)


def _explicacao_sintoma(sint: str) -> str:
    """Devolve a explicação clínica do sintoma a partir da base de conhecimento."""
    return EXPLICACOES_SINT.get(
        sint,
        "Este sintoma é avaliado no nosso modelo clínico para afastar condições potencialmente graves.",
    )


def calcular_proximo_sintoma(sintomas: dict, perguntas_feitas: Optional[set] = None) -> Optional[str]:
    """
    Dado o estado actual dos sintomas conhecidos, devolve o sintoma mais informativo
    a perguntar a seguir, guiado pelas regras da base de conhecimento.

    Para cada regra activa (não eliminada, não resolvida), as suas premissas ainda
    desconhecidas recebem um score = CF * (1 + n_premissas_já_confirmadas).
    O sintoma com maior score acumulado é o mais discriminante.
    Sintomas já perguntados (mesmo sem resposta clara) são excluídos para evitar
    repetição.
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
                if val == "sim":
                    eliminada = True
                    break
                elif val == "nao":
                    n_confirmadas += 1
                else:
                    desconhecidos.append(sint)
            else:
                if val == "nao":
                    eliminada = True
                    break
                elif val == "sim":
                    n_confirmadas += 1
                else:
                    desconhecidos.append(sint)

        if eliminada or not desconhecidos:
            continue

        # Quando já há sintomas confirmados, "completar uma regra em curso"
        # vale muito mais do que "abrir uma regra nova sem evidências":
        # - n_confirmadas >= 1: peso exponencial (regra com evidências)
        # - n_confirmadas == 0 com sintomas já confirmados: peso reduzido (0.2×)
        #   → impede que febre_alta (8 regras independentes) bata dor_irradia
        #     (1 regra com dor_peito já confirmado)
        has_confirmed_sintoma = any(v == "sim" for v in sintomas.values())
        if n_confirmadas == 0 and has_confirmed_sintoma:
            peso = cf * 0.2
        else:
            peso = cf * (2 ** n_confirmadas)
        for sint in desconhecidos:
            scores[sint] += peso

    # Excluir sintomas já perguntados mas sem resposta clara
    if perguntas_feitas:
        for s in perguntas_feitas:
            scores.pop(s, None)

    return max(scores, key=scores.__getitem__) if scores else None


def tem_regra_emergencia_pendente(sintomas: dict) -> bool:
    """True se uma regra de emergência tem ≥2 premissas confirmadas e ≥1 desconhecida.
    Nesse caso a triagem não deve disparar — falta perguntar o sintoma restante que pode
    elevar o resultado para EMERGÊNCIA (ex: r_em6 com febre_alta+dor_abd mas confusao?)."""
    for regra in REGRAS_TODAS:
        if regra["nivel"] != "emergencia":
            continue
        n_conf, n_desc, eliminada = 0, 0, False
        for p in regra["premissas"]:
            m_neg = re.match(r"nao\((\w+)\)", p)
            sint  = m_neg.group(1) if m_neg else p
            val   = sintomas.get(sint)
            if m_neg:
                if val == "sim": eliminada = True; break
                elif val == "nao": n_conf += 1
                else: n_desc += 1
            else:
                if val == "nao": eliminada = True; break
                elif val == "sim": n_conf += 1
                else: n_desc += 1
        if not eliminada and n_conf >= 2 and n_desc >= 1:
            return True
    return False


def tem_regra_emergencia_satisfeita(sintomas: dict) -> bool:
    """True se alguma regra de emergência está completamente satisfeita pelos sintomas
    confirmados. Dispara triagem imediata mesmo sem sintomas individuais de emergência
    (ex: febre_alta + dor_abd + confusao → r_em6 → EMERGÊNCIA por sépsis)."""
    for regra in REGRAS_TODAS:
        if regra["nivel"] != "emergencia":
            continue
        satisfeita = True
        for p in regra["premissas"]:
            m_neg = re.match(r"nao\((\w+)\)", p)
            sint  = m_neg.group(1) if m_neg else p
            val   = sintomas.get(sint)
            if m_neg:
                if val == "sim": satisfeita = False; break   # nao(x) requer x ausente
            else:
                if val != "sim": satisfeita = False; break   # premissa positiva requer x=sim
        if satisfeita:
            return True
    return False


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


# ── MOTOR MYCIN PYTHON (fallback sem servidor Prolog) ────────────────────────

def _combinar_cf(cf1: float, cf2: float) -> float:
    """Fórmula MYCIN para combinar dois factores de certeza positivos."""
    return cf1 + cf2 * (1.0 - cf1)


def triagem_mycin_python(sintomas_presentes: list[str]) -> dict:
    """Motor MYCIN implementado em Python.
    Avalia todas as regras da base de conhecimento, combina os CFs com a fórmula
    MYCIN padrão e devolve o nível mais grave que disparou com a confiança real."""
    presentes = set(sintomas_presentes)
    cfs_por_nivel: dict[str, float] = {}

    for regra in REGRAS_TODAS:
        ok = True
        for p in regra["premissas"]:
            m_neg = re.match(r"nao\((\w+)\)", p)
            if m_neg:
                if m_neg.group(1) in presentes:
                    ok = False; break
            else:
                if p not in presentes:
                    ok = False; break
        if ok:
            n = regra["nivel"]
            cfs_por_nivel[n] = (
                _combinar_cf(cfs_por_nivel[n], regra["cf"])
                if n in cfs_por_nivel else regra["cf"]
            )

    if not cfs_por_nivel:
        # Nenhuma regra disparou — usar mapeamento individual
        nivel = nivel_por_sintomas(sintomas_presentes)
        nome, rec = NIVEIS_INFO.get(nivel, (nivel, "Consulte um médico."))
        return {"type": "resultado", "nivel": nome, "nivel_id": nivel,
                "recomendacao": rec, "confianca_pct": 50, "python_mycin": True}

    # Seleccionar o nível mais grave que disparou
    nivel_vencedor = next(n for n in _ORDEM_NIVEIS if n in cfs_por_nivel)
    cf_final = round(min(cfs_por_nivel[nivel_vencedor], 0.99) * 100)
    nome, rec = NIVEIS_INFO.get(nivel_vencedor, (nivel_vencedor, "Consulte um médico."))
    return {
        "type":          "resultado",
        "nivel":         nome,
        "nivel_id":      nivel_vencedor,
        "recomendacao":  rec,
        "confianca_pct": cf_final,
        "python_mycin":  True,
    }


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

    # ── Caso MYCIN: resultado final ──────────────────────────────────────────
    if resultado_prolog and resultado_prolog.get("type") == "resultado":
        nivel = resultado_prolog.get("nivel", "")
        rec   = _corrigir_acentos(resultado_prolog.get("recomendacao", ""))
        cf    = min(resultado_prolog.get("confianca_pct", 0), 95)
        sint_conf = conf_txt if conf_txt != "nenhum" else "os sintomas descritos"
        emergencia_aviso = "\n\n⚠️ **Ligue 112 (INEM) imediatamente.**" if "EMERG" in nivel.upper() else ""

        # Intro empática gerada por LLM — curta, sem revelar o resultado
        intro_prompt = (
            f"Assistente SNS24. Português de Portugal.\n"
            f"Acabaste de avaliar os sintomas de alguém após uma conversa.\n"
            f"Escreve UMA frase curta, profissional e empática a concluir a avaliação.\n"
            f"Exemplos: 'Obrigado pela sua colaboração.' / 'Analisei os seus sintomas com atenção.' / 'Avaliação concluída.'\n"
            f"PROIBIDO: revelar resultado, nível, recomendações, mencionar 112.\n"
            f"Resposta (só a frase, sem aspas):"
        )
        intro = await _chamar_ollama(intro_prompt, max_tokens=25)
        intro = re.sub(r"(?i)(112|urgên|emergên|imediatamente|ligue|nivel|nível|muito urgente|emergência).*", "", intro).strip()
        if not intro or len(intro) < 5:
            intro = "Obrigado pela sua colaboração."

        return (
            f"{intro}\n\n"
            f"Com base nos sintomas que descreveu ({sint_conf}), a triagem está concluída.\n\n"
            f"**Nível: {nivel}** (confiança: {cf}%)\n\n"
            f"**Recomendação:** {rec}{emergencia_aviso}"
        )

    # ── Caso conversa: acknowledgment contextual (LLM) + pergunta ────────────
    pergunta = DESCRICAO_PERGUNTA.get(prox_sint, "") if prox_sint else ""

    if pergunta:
        # Construir contexto do que aconteceu neste turno
        ultima = session.get("ultima_pergunta")
        resp_simples = e_resposta_simples(user_msg)
        if resp_simples is not None and ultima:
            sint_name = SINTOMAS_PT.get(ultima, ultima)
            situacao = f"confirmou '{sint_name}'" if resp_simples else f"disse que não tem '{sint_name}'"
        elif ultima and e_resposta_incerta(user_msg):
            sint_name = SINTOMAS_PT.get(ultima, ultima)
            situacao = f"não tem certeza sobre '{sint_name}'"
        else:
            situacao = f"disse: \"{user_msg[:80]}\""

        ack_prompt = (
            f"Assistente SNS24. Português de Portugal (usa 'si', 'seu', 'sua'; NUNCA 'você').\n"
            f"Situação: o utilizador {situacao}.\n\n"
            f"Escreve APENAS reconhecimento + transição. Formato obrigatório:\n"
            f"  [frase empática curta]. [palavras de transição]:\n"
            f"Exemplos:\n"
            f"  Entendido, obrigado por partilhar. Para continuar:\n"
            f"  Percebo, lamento que se sinta assim. Preciso também de saber:\n"
            f"  Compreendo. Para continuar a avaliação:\n"
            f"  Obrigado por me dizer isso. Diga-me também:\n"
            f"PROIBIDO: perguntas, diagnósticos, 112, urgência, emergência, gravidade, "
            f"recomendações, sintomas específicos, condições clínicas, nomes de doenças.\n"
            f"Resposta (só o texto, sem aspas, sem nova linha):"
        )
        ack = await _chamar_ollama(ack_prompt, max_tokens=35)
        # Limpar: remover perguntas e conteúdo proibido
        ack = re.sub(r"\?.*", "", ack).strip()
        ack = re.sub(r"(?i)(112|urgên|emergên|imediatamente|ligue|grave|sério|diagnóst).*", "", ack).strip()
        # Corrigir pronomes e formas verbais "tu" do LLM (deve usar "si"/"você")
        ack = re.sub(r"\bvocê\b", "si", ack, flags=re.IGNORECASE)
        ack = re.sub(r"\bestás\b", "está", ack)
        ack = re.sub(r"\btens\b", "tem", ack)
        ack = re.sub(r"\bpodes\b", "pode", ack)
        ack = re.sub(r"\bsabes\b", "sabe", ack)
        ack = re.sub(r"\bqueres\b", "quer", ack)
        ack = re.sub(r"\b(para|de) te\b", lambda m: m.group(1) + " si", ack)
        # Verificar se o LLM antecipou o próximo sintoma (alucinação clínica).
        # Usa as keywords canónicas do sintoma (min 4 chars) para detetar conjugações
        # e variações que o threshold de 6 chars na SINTOMAS_PT/DESCRICAO_PERGUNTA falharia
        # (ex: "febre"=5, "tosse"=5 não eram apanhados antes).
        if prox_sint and prox_sint in SINTOMAS_KEYWORDS:
            _stop_kw = {"com", "sem", "que", "não", "nao", "uma", "num", "por",
                        "para", "mais", "também", "preciso", "saber", "muito",
                        "assim", "ainda", "esta", "estar", "sinais", "grave",
                        "repet", "líqui", "beber", "ingerir"}
            _kws_prox: set = set()
            for kw_phrase in SINTOMAS_KEYWORDS[prox_sint]:
                for w in kw_phrase.split():
                    w_clean = w.lower().rstrip(".,!?")
                    if len(w_clean) >= 4 and w_clean not in _stop_kw:
                        _kws_prox.add(w_clean)
            if any(kw in ack.lower() for kw in _kws_prox):
                ack = "Entendido. Preciso também de saber"
        # Manter no máximo 2 frases (reconhecimento + transição)
        frases = re.split(r'(?<=[.!])\s+', ack)
        if len(frases) > 2:
            ack = " ".join(frases[:2])
        ack = ack.strip().rstrip(".,: ")
        if not ack or len(ack) < 4:
            ack = "Entendido. Preciso também de saber"
        return f"{ack}: {pergunta}"
    else:
        # Motor esgotou perguntas — LLM resume e anuncia análise
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
@app.get("/")
async def root():
    return FileResponse(os.path.join(_DIR, "interface.html"))


@app.get("/chatbot.html")
async def chatbot_html():
    return FileResponse(os.path.join(_DIR, "chatbot.html"))


# ── PROXY para o servidor Prolog (porta 8080) ─────────────────────────────────
@app.post("/api/start")
async def proxy_start(request: Request):
    body = await request.body()
    async with httpx.AsyncClient(timeout=40.0) as client:
        r = await client.post(f"{PROLOG_URL}/api/start", content=body,
                              headers={"Content-Type": "application/json"})
    return r.json()


@app.post("/api/answer")
async def proxy_answer(request: Request):
    body = await request.body()
    async with httpx.AsyncClient(timeout=40.0) as client:
        r = await client.post(f"{PROLOG_URL}/api/answer", content=body,
                              headers={"Content-Type": "application/json"})
    return r.json()


@app.post("/api/validate")
async def proxy_validate(request: Request):
    body = await request.body()
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{PROLOG_URL}/api/validate", content=body,
                              headers={"Content-Type": "application/json"})
    return r.json()


@app.post("/api/chat/start")
async def start_chat():
    sid = str(uuid.uuid4())
    sessions[sid] = {
        "sintomas":         {},
        "history":          [],
        "triagem_feita":    False,
        "resultado_prolog": None,
        "ultima_pergunta":  None,   # sintoma sobre o qual se perguntou por último
        "perguntas_feitas": set(),  # sintomas já perguntados (evita repetições)
        "n_trocas":         0,      # número de turnos de conversa
        "sintomas_labels":  {},     # labels específicos (ex: dor_leve → "Dor de cabeça")
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

    # Triagem já concluída — mostrar resultado armazenado sem reprocessar
    if session["triagem_feita"] and session.get("resultado_prolog"):
        rec   = _corrigir_acentos(session["resultado_prolog"].get("recomendacao", ""))
        nivel = session["resultado_prolog"].get("nivel", "")
        sintomas_json = [
            {"id": s, "nome": lbl, "presente": v == "sim"}
            for s, v in session["sintomas"].items()
            for lbl in (session.get("sintomas_labels", {}).get(s) or [SINTOMAS_PT.get(s, s)])
        ]
        return {
            "message": (
                f"A triagem já foi concluída. **{nivel}** — {rec}.\n\n"
                f"Se necessitar de uma nova avaliação, por favor inicie uma nova conversa."
            ),
            "sintomas":         sintomas_json,
            "triagem_feita":    True,
            "resultado_prolog": session["resultado_prolog"],
        }

    # 0. Porquê/pedido de explicação — responder com justificação clínica e repetir pergunta
    ultima_perg = session.get("ultima_pergunta")
    if e_intencao_porque(user_msg) and ultima_perg:
        expl     = _explicacao_sintoma(ultima_perg)
        pergunta = DESCRICAO_PERGUNTA.get(ultima_perg, "Pode responder à pergunta anterior?")
        resposta = f"Peço esta informação porque: {expl}\n\n{pergunta}"
        session["history"].append({"role": "assistant", "content": resposta})
        sintomas_json = [
            {"id": s, "nome": lbl, "presente": v == "sim"}
            for s, v in session["sintomas"].items()
            for lbl in (session.get("sintomas_labels", {}).get(s) or [SINTOMAS_PT.get(s, s)])
        ]
        return {"message": resposta, "sintomas": sintomas_json,
                "triagem_feita": False, "resultado_prolog": None}

    # 1. Se a mensagem é um sim/não simples à última pergunta, mapeá-la directamente
    resp_simples = e_resposta_simples(user_msg)
    # Salvaguarda: se resp_simples=True veio apenas do prefixo "tenho/sinto/..."
    # mas a deteção de keywords encontra um sintoma DIFERENTE de ultima_perg,
    # o utilizador está a descrever outra coisa ("tenho dor de cabeça" ≠ confirmar febre).
    if resp_simples is True and ultima_perg:
        kw_pre = detectar_sintomas_keywords(user_msg)
        outros = [s for s in kw_pre["presentes"] if s != ultima_perg]
        if outros:
            resp_simples = None  # tratar como descrição, não confirmação
    if resp_simples is not None and ultima_perg:
        if ultima_perg not in session["sintomas"]:
            session["sintomas"][ultima_perg] = "sim" if resp_simples else "nao"
        session["perguntas_feitas"].add(ultima_perg)
    elif ultima_perg:
        # Resposta livre, descritiva ou incerta — marcar como perguntada para não repetir.
        # Exceção: mensagens muito curtas com "?" são provavelmente pedidos de esclarecimento
        # não detetados por e_intencao_porque; não marcar para que a pergunta se repita.
        if not (len(user_msg.strip()) <= 20 and "?" in user_msg):
            session["perguntas_feitas"].add(ultima_perg)

    # 2. Detecção de sintomas via keywords (llama3.2:3b produz alucinações na
    # extração estruturada, por isso confiamos apenas nas keywords que são fiáveis)
    kw = detectar_sintomas_keywords(user_msg)
    for s in kw["presentes"]:
        if s not in session["sintomas"]:
            session["sintomas"][s] = "sim"
    # Labels específicos para dor_leve: acumular (não substituir) por localização
    if "dor_leve" in kw["presentes"] or session["sintomas"].get("dor_leve") == "sim":
        labels = session["sintomas_labels"].setdefault("dor_leve", [])
        tl = user_msg.lower()
        achou_especifico = False
        for kws, lbl in DOR_LEVE_LABELS:
            if any(k in tl for k in kws) and lbl not in labels:
                labels.append(lbl)
                achou_especifico = True
        # dor_leve recém-detectado sem localização específica → label genérico
        if "dor_leve" in kw["presentes"] and not achou_especifico and not labels:
            labels.append("Dores")
    for s in kw["ausentes"]:
        if s not in session["sintomas"]:
            session["sintomas"][s] = "nao"
        elif s == ultima_perg and session["sintomas"].get(s) == "sim" and resp_simples is True:
            # Override: keyword nega explicitamente o mesmo sintoma que a resposta
            # simples confirmou — ex: "tenho febre mas não acima de 39 graus"
            # → e_resposta_simples viu "tenho" → sim; keyword viu "não...acima de 39" → ausente
            # A keyword é mais específica: prevalece.
            session["sintomas"][s] = "nao"

    # 2b. Aplicar exclusões mútuas (ex: febre_alta exclui febre_baixa)
    aplicar_exclusoes(session["sintomas"])

    # 3+4. Early-exit absoluto para emergências completas; caso contrário, fluxo normal
    emerg_satisfeita = tem_regra_emergencia_satisfeita(session["sintomas"])
    if emerg_satisfeita and not session["triagem_feita"]:
        # Regra de emergência 100% satisfeita — triagem imediata, sem mais perguntas
        prox_sint    = None
        deve_triagem = True
    else:
        # 3. Motor de regras: calcular a próxima pergunta mais informativa
        prox_sint = calcular_proximo_sintoma(session["sintomas"], session["perguntas_feitas"])

        # 4. Decidir se é altura de fazer triagem formal MYCIN
        has_emergency = any(session["sintomas"].get(s) == "sim" for s in SINTOMAS_EMERGENCIA)
        n_known       = sum(1 for v in session["sintomas"].values() if v in ("sim", "nao"))
        SINTOMAS_URGENTES = {"febre_alta", "febre_bebe", "dor_peito", "dor_abd",
                             "fala_dificil", "fraqueza_lado", "confusao", "dor_persiste",
                             "reacao_alergica_grave", "dor_cabeca_subita", "rigidez_nuca"}
        has_urgente      = any(session["sintomas"].get(s) == "sim" for s in SINTOMAS_URGENTES)
        emerg_pendente   = tem_regra_emergencia_pendente(session["sintomas"])
        deve_triagem     = (
            (has_emergency or emerg_satisfeita)
            or (session["n_trocas"] >= 6 and n_known >= 4)
            or (not emerg_pendente and (
                (has_urgente and n_known >= 5 and session["n_trocas"] >= 3)
                or (prox_sint is None and n_known >= 3 and session["n_trocas"] >= 3)
            ))
        ) and not session["triagem_feita"]

    resultado_prolog = None
    if deve_triagem:
        presentes = [s for s, v in session["sintomas"].items() if v == "sim"]
        resultado_mycin = await triagem_mycin(presentes)
        session["triagem_feita"] = True   # sempre marcar — evita chamadas repetidas

        nivel_mycin    = resultado_mycin.get("nivel", "")
        nivel_esperado = nivel_por_sintomas(presentes)

        # Fallback: servidor Prolog não disponível — usar motor MYCIN Python
        if resultado_mycin.get("type") != "resultado":
            resultado_prolog = triagem_mycin_python(presentes)
        # Validar: Prolog não pode elevar para emergência sem justificação pelos sintomas
        elif nivel_mycin == "emergencia" and nivel_esperado not in ("emergencia",):
            resultado_prolog = triagem_mycin_python(presentes)
        else:
            # Garantir nivel_id (Prolog pode devolver ID "muito_urgente" ou display "MUITO URGENTE")
            if "nivel_id" not in resultado_mycin:
                raw = nivel_mycin.upper()
                resultado_mycin["nivel_id"] = (
                    nivel_mycin if nivel_mycin in NIVEIS_INFO
                    else _NIVEL_NOME_PARA_ID.get(raw, nivel_mycin)
                )
            # Piso de segurança clínica: o Prolog usa score_maximo (CF mais alto),
            # não o nível mais grave. Se o Python MYCIN (severity-first) devolver
            # um nível mais grave, prevalece — ex: vomitos(r_ur10, CF=0.60) não
            # pode perder para dor_leve(r_pu2, CF=0.65).
            resultado_python = triagem_mycin_python(presentes)
            nid_prolog  = resultado_mycin.get("nivel_id", "sem_alarme")
            nid_python  = resultado_python.get("nivel_id", "sem_alarme")
            idx_prolog  = _ORDEM_NIVEIS.index(nid_prolog)  if nid_prolog  in _ORDEM_NIVEIS else len(_ORDEM_NIVEIS)
            idx_python  = _ORDEM_NIVEIS.index(nid_python)  if nid_python  in _ORDEM_NIVEIS else len(_ORDEM_NIVEIS)
            resultado_prolog = resultado_python if idx_python < idx_prolog else resultado_mycin

        session["resultado_prolog"] = resultado_prolog
        salvar_triagem_csv(session, resultado_prolog)

    # 5. Registar a próxima pergunta na sessão (para mapear sim/não no próximo turno)
    # perguntas_feitas é marcado no turno seguinte, após resposta clara do utilizador
    if prox_sint and not resultado_prolog:
        session["ultima_pergunta"] = prox_sint
    else:
        session["ultima_pergunta"] = None

    resposta = await gerar_resposta(session, user_msg, resultado_prolog, prox_sint)

    sintomas_json = [
        {"id": s, "nome": lbl, "presente": v == "sim"}
        for s, v in session["sintomas"].items()
        for lbl in (session.get("sintomas_labels", {}).get(s) or [SINTOMAS_PT.get(s, s)])
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
    print(f"  API    : http://localhost:8082")
    print(f"  RAG    : {len(CONHECIMENTO)} documentos carregados")
    print(f"           (base_conhecimento_a.pl + base_conhecimento_b.pl)")
    print("=" * 55 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8082, reload=False)
