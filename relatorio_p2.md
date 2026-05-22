# Projeto 2 — Suporte à Decisão na Triagem SNS24 baseado em Chatbot, LLM e RAG

## 1. Introdução

O Projeto 2 (P2) tem como objetivo desenvolver um sistema inteligente de suporte à decisão (SISD) para triagem clínica, apresentado sob a forma de chatbot conversacional. O sistema apoia-se no modelo de linguagem de grande dimensão (LLM) Llama 3.2 (3B parâmetros), integrado através da plataforma Ollama, e combina-o com a técnica de Retrieval-Augmented Generation (RAG) e com o motor de inferência MYCIN desenvolvido no Projeto 1 (P1).

O chatbot permite que um utilizador descreva os seus sintomas em linguagem natural e recebe, no final da conversa, um resultado de triagem com nível de urgência e recomendação clínica, de forma análoga aos protocolos de triagem Altitude utilizados pelo serviço SNS24.

A integração com o P1 é direta: a base de conhecimento em Prolog (`base_conhecimento_a.pl` e `base_conhecimento_b.pl`) é reutilizada tanto para alimentar o módulo RAG como para alimentar o motor de inferência. O sistema é, portanto, uma extensão natural do trabalho anterior, adicionando uma camada de linguagem natural e um motor de diálogo estruturado.

---

## 2. Arquitetura do Sistema

O sistema é composto por quatro componentes principais que comunicam entre si através de HTTP:

| Componente | Tecnologia | Porta |
|---|---|---|
| Servidor de chatbot (backend Python) | FastAPI + Uvicorn | 8081 |
| Modelo de linguagem (LLM) | Ollama / Llama 3.2:3b | 11434 |
| Motor MYCIN em Prolog (P1) | Servidor HTTP Prolog | 8080 |
| Interface Web (frontend) | HTML/CSS/JS | — |

O fluxo de uma sessão de triagem é o seguinte:

1. O utilizador abre a interface web (`chatbot.html`) e inicia uma sessão via `POST /api/chat/start`, que devolve um identificador único de sessão (UUID).
2. Cada mensagem do utilizador é enviada via `POST /api/chat/message`. O servidor Python processa a mensagem: deteta sintomas, decide a próxima pergunta a fazer ou se é hora de fazer a triagem formal, e gera uma resposta em linguagem natural com o auxílio do LLM.
3. Quando os critérios de triagem são atingidos, o servidor tenta delegar ao motor MYCIN Prolog (P1, porta 8080). Caso este não esteja disponível, um motor MYCIN equivalente implementado em Python é utilizado como fallback.
4. O resultado final (nível de urgência, recomendação, fator de certeza) é formatado e enviado ao utilizador.

O servidor Python é também proxy do servidor Prolog, expondo os seus endpoints (`/api/start`, `/api/answer`, `/api/validate`) de modo a que o frontend possa comunicar com ambos através da mesma origem.

---

## 3. Base de Conhecimento e RAG

### 3.1 Processamento dos Ficheiros Prolog

No arranque do servidor, os ficheiros `base_conhecimento_a.pl` e `base_conhecimento_b.pl` são lidos e analisados via expressões regulares. São extraídas quatro estruturas de dados:

- **Sintomas** — `sintoma(id, 'Descrição')`: mapeamento de identificadores Prolog para descrições em linguagem natural.
- **Níveis de triagem** — `nivel(id, 'Nome', 'Recomendação')`: os cinco níveis do protocolo SNS24 (Emergência, Muito Urgente, Urgente, Pouco Urgente, Sem Alarme).
- **Regras de produção** — `regra(id, se([premissas]), entao(nivel), CF)`: a base de conhecimento completa com fatores de certeza.
- **Explicações** — `explicacao_regra(id, 'Texto')` e `explicacao(sintoma, 'Texto')`: texto clínico associado a cada regra e sintoma, gerado manualmente no P1.

### 3.2 Construção dos Documentos RAG

A partir dos dados extraídos, é construída uma coleção de documentos em linguagem natural simples, otimizados para serem interpretados por um LLM de 3B parâmetros. Cada documento segue o formato:

> `[condição(ões)] → [nível]. [O que fazer]. [Porquê — primeira frase da explicação clínica].`

São gerados três grupos de documentos:

1. **Protocolo geral** — uma descrição dos cinco níveis SNS24 e das respetivas ações.
2. **Uma entrada por regra de produção** (partes A e B) — as premissas são traduzidas para linguagem natural; negações (`nao(x)`) são expressas como "sem X"; as regras da Parte B são marcadas como `[padrão aprendido automaticamente]`.
3. **Grupos de sintomas por gravidade** — listas dos sintomas típicos de cada nível, com a respetiva explicação clínica resumida.

A coleção resultante contém tipicamente entre 60 e 80 documentos.

### 3.3 Motor TF-IDF e Recuperação

O módulo RAG é implementado com a classe `RAGEngine`, que utiliza um vectorizador TF-IDF com análise de n-gramas de caráter (`char_wb`, bigramas a tetragramas), com um vocabulário máximo de 8 000 características. A escolha de n-gramas de caráter, em vez de palavras completas, confere robustez a variações ortográficas, abreviaturas e erros de escrita — frequentes na linguagem natural clínica em português.

A recuperação é feita por similaridade de cosseno entre o vetor da consulta e a matriz de documentos. São devolvidos os `top_k=5` documentos com similaridade superior a 0.01. O contexto recuperado é injetado nos prompts enviados ao LLM quando este é chamado para gerar uma resposta livre (por exemplo, para resumir a situação antes de iniciar a triagem formal).

---

## 4. Deteção de Sintomas

### 4.1 Sistema de Keywords

A deteção de sintomas na mensagem do utilizador é feita através de um dicionário de keywords (`SINTOMAS_KEYWORDS`) que cobre 28 sintomas. Para cada sintoma, são definidas múltiplas expressões equivalentes em português corrente, incluindo variantes com e sem acentuação e formulações coloquiais. Por exemplo, `dor_peito` é detetado por expressões como "dor no peito", "aperto no peito", "pressão no peito", "dor torácica", "peito a doer", entre outras.

A deteção de negações é feita por análise de contexto: para cada keyword encontrada no texto, é inspecionada uma janela de 35 carateres anteriores à ocorrência. Se essa janela contiver palavras de negação ("não", "sem", "nunca", "ausência de"), o sintoma é marcado como ausente em vez de presente.

Este sistema determinou a decisão de **desativar** o LLM para a tarefa de extração de sintomas (ver 4.2), dado que o sistema de keywords demonstrou ser mais fiável e determinístico para as condições do projeto.

### 4.2 Limitações do LLM na Extração Estruturada

Embora exista uma função `extrair_sintomas_llm` que envia ao Ollama um prompt pedindo a identificação de sintomas em formato JSON, esta função não é invocada durante o fluxo normal. O motivo é a propensão do modelo Llama 3.2:3b para alucinações em tarefas de extração estruturada: o modelo gerava frequentemente sintomas não presentes no texto, confundia negações, ou devolvia JSON malformado. O sistema de keywords, sendo determinístico e construído manualmente com conhecimento do domínio, revelou-se significativamente mais robusto para este contexto.

### 4.3 Exclusões Mútuas e Propagação de Negações

Após a deteção de novos sintomas, é aplicada uma etapa de consistência lógica. O sistema define pares de sintomas **mutuamente exclusivos**: a confirmação de `febre_alta` (>39 °C) implica automaticamente a negação de `febre_baixa` (<38 °C), e vice-versa. Desta forma evita-se que a base de sintomas da sessão contenha contradições que comprometam a avaliação das regras.

---

## 5. Motor de Inferência MYCIN

### 5.1 Motor MYCIN em Python (Fallback)

O motor MYCIN foi originalmente implementado em Prolog no P1. Para garantir que o chatbot funciona mesmo quando o servidor Prolog não está disponível, foi desenvolvida uma implementação equivalente em Python (`triagem_mycin_python`).

O motor avalia todas as regras da base de conhecimento carregada em memória. Para cada regra, verifica se todas as premissas estão satisfeitas pelo conjunto de sintomas confirmados na sessão: premissas positivas (`sintoma`) requerem que o sintoma esteja marcado como presente; premissas negativas (`nao(sintoma)`) requerem que o sintoma esteja ausente ou não confirmado.

Quando uma regra dispara, o seu fator de certeza (CF) é combinado com o CF já acumulado para o mesmo nível, usando a fórmula padrão MYCIN:

$$CF_{combinado} = CF_1 + CF_2 \times (1 - CF_1)$$

Esta fórmula, derivada das probabilidades condicionais, garante que a combinação de múltiplas evidências independentes aumenta progressivamente a certeza sem ultrapassar 1.

No final, o nível mais grave que disparou (segundo a ordenação `emergencia > muito_urgente > urgente > pouco_urgente > sem_alarme`) é o resultado reportado, com o respetivo CF final expresso em percentagem.

### 5.2 Integração com o Servidor Prolog (P1)

Quando o servidor Prolog (P1) está disponível na porta 8080, o chatbot delega-lhe a triagem formal. O protocolo de comunicação é o mesmo definido no P1: o servidor Python envia `POST /api/start` para iniciar uma sessão Prolog, e responde iterativamente às perguntas do motor MYCIN Prolog enviando `POST /api/answer` com o valor (`"sim"` ou `"nao"`) para cada sintoma, até o Prolog devolver um resultado.

### 5.3 Garantia de Segurança Clínica

Após obter o resultado do Prolog, o motor Python é também executado em paralelo. Se o Python concluir um nível **mais grave** do que o Prolog, o resultado Python prevalece. Esta salvaguarda corrige uma assimetria do motor Prolog do P1, que seleciona a regra com o CF mais alto (e não necessariamente o nível mais grave): por exemplo, uma regra de `urgente` com CF 0.85 não deve suprimir uma regra de `muito_urgente` com CF 0.60.

---

## 6. Gestão da Conversa

### 6.1 Estado de Sessão

Cada sessão é identificada por um UUID e mantém em memória o seguinte estado:

- `sintomas` — dicionário `{id_sintoma: "sim" | "nao"}` com todos os sintomas avaliados.
- `history` — lista de mensagens da conversa (papel + conteúdo).
- `ultima_pergunta` — sintoma sobre o qual foi feita a última pergunta, para mapear corretamente respostas do tipo "sim"/"não" sem que o utilizador repita o nome do sintoma.
- `perguntas_feitas` — conjunto de sintomas já perguntados, para evitar repetições quando a resposta foi inconclusiva.
- `triagem_feita` — booleano que impede que a triagem seja executada mais de uma vez.
- `n_trocas` — contador de turnos de conversa.

### 6.2 Algoritmo de Seleção da Próxima Pergunta

O sistema não segue uma ordem fixa de perguntas. Em vez disso, a função `calcular_proximo_sintoma` escolhe dinamicamente o sintoma mais informativo a perguntar a seguir, tendo em conta o estado atual da sessão e as regras da base de conhecimento.

Para cada regra ainda ativa (não eliminada por uma premissa falsa, e com pelo menos uma premissa desconhecida), é calculado um score para cada sintoma desconhecido:

$$score = CF_{regra} \times 2^{n_{confirmadas}}$$

onde $n_{confirmadas}$ é o número de premissas da regra já confirmadas. O expoente cria um peso exponencial que favorece fortemente a **conclusão de regras com evidências parciais** em detrimento de abrir novas regras sem qualquer confirmação. Para regras cujas premissas estão todas por descobrir (e já existe pelo menos um sintoma confirmado na sessão), o peso é reduzido a $CF \times 0.2$, de modo a que uma regra em curso não seja interrompida por uma regra mais genérica com CF elevado.

O sintoma com o score acumulado mais alto entre todas as regras ativas é selecionado, excluindo os sintomas já perguntados.

### 6.3 Critérios de Disparo da Triagem

A triagem formal é desencadeada quando se verifica uma das seguintes condições:

- Está presente pelo menos um sintoma de emergência individual (`sem_respiracao`, `sem_pulso`, `resp_dificuldade`, `hemorragia`, `inconsciente`, `convulsoes`).
- Uma regra de emergência está completamente satisfeita pelos sintomas confirmados (por exemplo, `febre_alta` + `confusao` + `dor_abd` → sépsis, regra `r_em6`).
- Foram feitas 6 ou mais trocas e há pelo menos 4 sintomas avaliados (limite superior de conversa).
- Para sintomas urgentes, a triagem dispara quando há 5 ou mais sintomas avaliados e pelo menos 3 trocas de conversa, **desde que** nenhuma regra de emergência tenha ainda premissas por descobrir — garantindo que o sistema não encerra prematuramente quando uma regra de emergência ainda pode ser satisfeita.

### 6.4 Tratamento de Respostas Ambíguas

A função `e_resposta_simples` classifica cada mensagem como `True` (confirmação), `False` (negação) ou `None` (incerta). São reconhecidas variantes coloquiais de "sim" e "não" em português, incluindo expressões como "pois", "claro", "exatamente", "efetivamente" ou "negativo".

Respostas qualificadas — como "tenho febre, mas não acima de 39 graus" — são identificadas pela presença de conjunções adversativas após um confirmador, sendo classificadas como incertas (`None`) para evitar mapeamentos incorretos. Expressões de frequência intermitente ("às vezes", "de vez em quando") são tratadas da mesma forma, dado que a triagem clínica requer confirmação, não mera possibilidade.

Quando a resposta é incerta (`e_resposta_incerta`), o sintoma não é registado, mas é adicionado ao conjunto `perguntas_feitas` para não ser repetido.

---

## 7. Geração de Linguagem Natural com LLM

### 7.1 Modelo e Configuração

O LLM utilizado é o **Llama 3.2:3b**, executado localmente via **Ollama** (porta 11434). É um modelo compacto de 3B parâmetros, adequado para execução em hardware de consumo sem GPU dedicada. A temperatura é fixada em 0.1 para minimizar a variabilidade e reduzir o risco de alucinações. O número máximo de tokens gerados é limitado por caso de uso: 25 tokens para frases de reconhecimento intercalar, 35 tokens para a transição antes de uma pergunta clínica.

O LLM **não** é usado para inferência clínica nem para extração de sintomas. O seu papel é exclusivamente **linguístico**: tornar a conversa mais natural e empática, sem influenciar a lógica de triagem.

### 7.2 Prompts de Reconhecimento (Mid-Conversation)

Em cada turno de conversa, antes de colocar a próxima pergunta clínica, o LLM gera um breve reconhecimento contextual. O prompt descreve a situação do turno anterior (por exemplo, "o utilizador confirmou 'Febre alta (>39°C)'" ou "o utilizador não tem certeza sobre 'Dor no peito'") e pede uma frase empática de transição no registo formal do português europeu (uso de "si" em vez de "você").

O formato de saída esperado é fixo: `[frase empática]. [palavras de transição]:`, após o qual o sistema concatena a pergunta clínica pré-definida para o próximo sintoma. Exemplos típicos de saída:

> *"Entendido, obrigado por partilhar. Para continuar:"*
> *"Percebo, lamento que se sinta assim. Preciso também de saber:"*

### 7.3 Prompt de Introdução ao Resultado

Quando a triagem está concluída, o LLM gera uma única frase introdutória empática antes do resultado estruturado ser apresentado. O prompt instrui explicitamente o modelo a não revelar o nível, recomendações, nem qualquer referência clínica. O resultado (nível, recomendação, confiança) é inserido pelo servidor Python após a frase do LLM.

### 7.4 Pós-Processamento e Filtragem de Alucinações

A saída do LLM é sempre sujeita a pós-processamento antes de ser enviada ao utilizador:

1. **Remoção de perguntas** — qualquer fragmento a partir de "?" é eliminado (o LLM não deve antecipar a pergunta clínica seguinte).
2. **Filtragem de conteúdo clínico proibido** — expressões como "112", "urgência", "emergência", "imediatamente", "grave" são removidas do reconhecimento intercalar, para garantir que o LLM não influencia a perceção de gravidade antes do resultado formal.
3. **Deteção de antecipação do próximo sintoma** — antes de enviar a frase de transição, o sistema verifica se o texto gerado contém keywords associadas ao sintoma que vai ser perguntado a seguir. Se sim, a frase é substituída por um texto neutro fixo ("Entendido. Preciso também de saber"), evitando que o LLM "estrague" a pergunta ao revelá-la prematuramente.
4. **Correção de pronomes** — o modelo tende a usar o registo informal ("você", "estás", "tens", "podes"). Uma série de substituições por expressão regular corrige estes casos para o registo formal do português europeu ("si", "está", "tem", "pode").
5. **Limite de comprimento** — o texto é truncado a no máximo duas frases, prevenindo respostas desnecessariamente longas.

---

## 8. Interface Web

A interface de utilizador é uma página HTML de página única (`chatbot.html`), servida diretamente pelo servidor FastAPI. É implementada em HTML, CSS e JavaScript puro, sem dependências externas de framework.

A interface apresenta um painel de chat à esquerda e um painel lateral de diagnóstico à direita, que exibe em tempo real os sintomas já detetados na sessão (marcados como presentes ou ausentes), o status de ligação ao modelo Ollama, e o resultado final de triagem com o respetivo nível de urgência codificado por cor.

A comunicação com o servidor é feita através de dois endpoints principais:

- `POST /api/chat/start` — inicia uma nova sessão e recebe a mensagem de boas-vindas.
- `POST /api/chat/message` — envia uma mensagem do utilizador e recebe a resposta do sistema, o estado atual dos sintomas, e, quando disponível, o resultado de triagem.

O estado de ligação ao Ollama é monitorizado via `GET /api/chat/status`, que devolve a lista de modelos disponíveis e confirma se o modelo `llama3.2:3b` está carregado.

---

## 9. Conclusão

O sistema desenvolvido integra três paradigmas distintos de inteligência artificial: raciocínio baseado em regras (motor MYCIN / Prolog), recuperação de informação (RAG / TF-IDF) e geração de linguagem natural (LLM / Llama 3.2). A divisão de responsabilidades é clara: a lógica clínica e de inferência é inteiramente controlada pelo motor de regras e pela base de conhecimento do P1; o LLM é confinado à dimensão linguística da interação, com filtros que impedem que alucinações comprometam a segurança do resultado.

A principal limitação identificada é a capacidade do modelo Llama 3.2:3b em tarefas de extração estruturada, o que levou à decisão de o excluir do pipeline de deteção de sintomas em favor de um sistema determinístico baseado em keywords. Esta troca entre generalidade e fiabilidade é uma das tensões centrais na utilização de LLMs de dimensão reduzida em domínios de alto risco como a triagem clínica.
