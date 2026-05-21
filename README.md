# SNS24 — Sistema de Triagem Inteligente

Sistema de triagem clínica SNS24 com motor de inferência MYCIN (SWI-Prolog), aprendizagem automática (scikit-learn) e chatbot RAG com Ollama.

---

## Estrutura do Projeto

```
├── Parte A+B — Motor MYCIN + ML
│   ├── base_conhecimento_a.pl   — regras clínicas manuais (30 regras)
│   ├── base_conhecimento_b.pl   — regras geradas por ML (gerado automaticamente)
│   ├── base_dados.pl            — memória de trabalho da sessão
│   ├── sistema_inferencia.pl    — motor MYCIN central
│   ├── server.pl                — servidor HTTP + API REST (porta 8080)
│   ├── interface.html           — frontend web da triagem
│   ├── main.pl                  — orquestrador CLI
│   ├── interface.pl             — interface de terminal
│   ├── guardar_triagem.pl       — persistência em triagens.csv
│   ├── gerar_dataset.py         — geração do dataset sintético inicial
│   └── treinar_exportar.py      — treino dos modelos ML e exportação Prolog
│
└── Parte 2 — Chatbot RAG
    ├── chatbot_server.py        — servidor FastAPI (porta 8081)
    ├── chatbot.html             — interface web do chatbot
    └── Exemplo Chat/            — exemplos de implementação RAG alternativa
```

---

## Pré-requisitos

| Ferramenta | Versão recomendada | Como instalar |
|---|---|---|
| [SWI-Prolog](https://www.swi-prolog.org/download/stable) | 9.x | Instalador oficial |
| Python | 3.10+ | [python.org](https://www.python.org) |
| [Ollama](https://ollama.com) | mais recente | Instalador oficial |

---

## Instalação (uma vez)

### 1. Dependências Python

```bash
pip install -r requirements_p2.txt
```

Ou manualmente:

```bash
pip install pandas scikit-learn fastapi uvicorn[standard] httpx numpy
```

### 2. Modelo Ollama

```bash
ollama pull llama3.2:3b
```

### 3. Gerar dataset e treinar modelos ML

```bash
# Gera triagens.csv com ~365 exemplos sintéticos a partir das regras da Parte A
python gerar_dataset.py

# Treina Random Forest + Decision Tree e exporta base_conhecimento_b.pl
python treinar_exportar.py
```

Depois deste passo o ficheiro `base_conhecimento_b.pl` fica disponível e o sistema está pronto a usar.

---

## Modo Web (recomendado)

### Passo 1 — Iniciar o servidor Prolog

```bash
swipl server.pl
```

O servidor inicia na **porta 8080**. Para parar, escrever `q.` na consola.

### Passo 2 — Abrir a interface

Abrir o browser em:

```
http://localhost:8080
```

Ou abrir o ficheiro `interface.html` diretamente no browser (faz os pedidos ao servidor local).

### Retreinar o modelo ML (modo web)

Depois de acumular triagens em `triagens.csv`, executar numa consola separada:

```bash
python treinar_exportar.py
```

Depois, na consola do SWI-Prolog onde o servidor está a correr:

```prolog
?- recarregar_base_b.
```

Isto recarrega o modelo sem reiniciar o servidor.

---

## Modo CLI (terminal)

```bash
swipl main.pl
```

Dentro do SWI-Prolog:

```prolog
?- iniciar.
```

Responder às perguntas com:
- `s.` — Sim (pede grau de certeza em %)
- `n.` — Não (pede grau de certeza em %)
- `t.` — Talvez / não sei
- `p.` — Porquê esta pergunta?

O retreino ML acontece automaticamente no final de cada triagem.

---

## Parte 2 — Chatbot RAG

O chatbot usa Ollama com RAG construído automaticamente a partir das bases de conhecimento Prolog.

### Pré-requisito: servidor Prolog a correr

O chatbot integra com o motor MYCIN. Garantir que o servidor da Parte 1 está ativo:

```bash
swipl server.pl   # porta 8080
```

### Iniciar o chatbot

```bash
python chatbot_server.py
```

O servidor inicia na **porta 8081**. Abrir no browser:

```
http://localhost:8081
```

Ou abrir `chatbot.html` diretamente.

---

## Fluxo completo de uma triagem (modo web)

```
Browser → POST /api/start  → servidor escolhe ordem de sintomas (ML ou manual)
        → POST /api/answer  → motor MYCIN avalia todas as regras A+B em paralelo
        ↓ (repete até score ≥ 0.80 ou fim dos sintomas)
        → POST /api/validate → guarda em triagens.csv automaticamente
```

Os scores MYCIN atualizam em tempo real na sidebar a cada resposta.

---

## Ficheiros gerados automaticamente

| Ficheiro | Gerado por | Função |
|---|---|---|
| `triagens.csv` | `guardar_triagem.pl` | Dataset para retreino ML |
| `base_conhecimento_b.pl` | `treinar_exportar.py` | Regras ML em formato Prolog |

Não editar `base_conhecimento_b.pl` à mão — é sobrescrito em cada retreino.

---

## Resolução de problemas

**`swipl` não é reconhecido**: adicionar o SWI-Prolog ao PATH do sistema (normalmente `C:\Program Files\swipl\bin` no Windows).

**Ollama não responde**: verificar se o serviço está ativo com `ollama list`. Se não, iniciar com `ollama serve`.

**`base_conhecimento_b.pl` não existe**: correr `python gerar_dataset.py` e depois `python treinar_exportar.py` antes de iniciar o Prolog.

**Porta 8080 ocupada**: verificar com `netstat -ano | findstr :8080` (Windows) e terminar o processo que a ocupa.

---

> Este sistema é educativo e não substitui avaliação médica.  
> Em emergência: **112** | Dúvidas: **SNS24 — 808 24 24 24**
