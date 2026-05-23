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

## 3. Evolução da Base de Conhecimento (Parte A)

No contexto do P2, a base de conhecimento `base_conhecimento_a.pl` foi revista e expandida relativamente à versão entregue no P1. As alterações têm dois objetivos: aumentar a cobertura clínica do sistema para padrões de doença grave que a versão original não detetava, e tornar o raciocínio mais preciso eliminando mecanismos que se revelaram problemáticos em teste.

### 3.1 Novos Sintomas

Foram adicionados cinco sintomas que não existiam na versão original:

| Identificador | Descrição |
|---|---|
| `rigidez_nuca` | Rigidez da nuca — não consegue encostar o queixo ao peito |
| `rash_petequial` | Manchas vermelhas ou roxas na pele que não desaparecem à pressão |
| `reacao_alergica_grave` | Reação alérgica grave com inchaço da face, língua ou garganta |
| `dor_cabeca_subita` | Dor de cabeça muito intensa de início súbito — "pior da vida" |
| `visao_alterada` | Alteração súbita da visão num ou ambos os olhos |

Estes sintomas cobrem quatro síndromes de alto risco que ficavam sem representação: meningite bacteriana e meningococcemia (os dois primeiros), anafilaxia (terceiro), hemorragia subaracnoideia (quarto) e AVC com envolvimento da visão (quinto). A sua adição foi necessária para que as novas regras de emergência e muito urgente descritas abaixo pudessem ser formuladas.

### 3.2 Novas Regras de Emergência

Foram acrescentadas quatro regras de emergência que combinam sintomas em padrões clínicos reconhecidos:

| Regra | Premissas | CF | Justificação clínica |
|---|---|---|---|
| `r_em8` | `resp_dificuldade` + `febre_alta` | 0.87 | Suspeita de pneumonia grave ou sépsis respiratória com risco de falência iminente |
| `r_em9` | `febre_alta` + `rigidez_nuca` | 0.92 | Padrão clássico de meningite bacteriana — emergência neurológica |
| `r_em10` | `febre_alta` + `rash_petequial` | 0.95 | Sinal de alerta de meningococcemia — progressão para choque em horas |
| `r_em11` | `resp_dificuldade` + `reacao_alergica_grave` | 0.93 | Anafilaxia com compromisso da via aérea — requer adrenalina e 112 |

O CF elevado destas regras (0.87–0.95) reflete a sua alta especificidade: cada combinação de sintomas aponta para um único quadro clínico com risco de vida imediato.

### 3.3 Novas Regras de Muito Urgente

Quatro novas regras foram adicionadas ao nível muito urgente, cobrindo padrões neurológicos e cardiológicos que a versão original também não contemplava:

| Regra | Premissas | CF | Justificação clínica |
|---|---|---|---|
| `r_mu10` | `confusao` + `febre_alta` + `nao(dor_abd)` | 0.85 | Padrão de meningite/encefalite — sem dor abdominal afasta sépsis (r_em6) |
| `r_mu11` | `reacao_alergica_grave` | 0.80 | Pode evoluir para anafilaxia — requer avaliação hospitalar imediata |
| `r_mu12` | `dor_cabeca_subita` | 0.85 | Sinal clássico de hemorragia subaracnoideia por rotura de aneurisma |
| `r_mu13` | `visao_alterada` + `fala_dificil` | 0.90 | Padrão BE-FAST completo de AVC — alta certeza diagnóstica |

A regra `r_mu10` é particularmente relevante do ponto de vista do raciocínio: introduz a negação de `dor_abd` como premissa para distinguir meningite/encefalite (muito urgente) de sépsis (emergência — regra `r_em6`). Sem esta distinção, um doente com confusão e febre mas sem dor abdominal não seria corretamente escalado.

### 3.4 Novas Regras de Urgente e Muito Urgente para Situações Pediátricas e GI

Foram acrescentadas cinco regras que refinam a triagem de quadros gastrointestinais e pediátricos:

| Regra | Premissas | CF | Nível | Justificação |
|---|---|---|---|---|
| `r_ur10` | `vomitos` + `nao(diarreia)` | 0.60 | Urgente | Desidratação por via gástrica isolada — pode exigir reposição IV |
| `r_ur11` | `dor_garganta` + `febre_alta` | 0.75 | Urgente | Suspeita de amigdalite bacteriana com risco de abscesso |
| `r_ur12` | `febre_bebe` + `vomitos` + `nao(diarreia)` | 0.80 | Muito Urgente | Bebé com reservas limitadas — risco de desidratação rápida |
| `r_ur13` | `diarreia` + `nao(vomitos)` | 0.55 | Urgente | Diarreia grave implica desidratação; sem vómitos há margem para hidratação oral vigiada |
| `r_ur14` | `visao_alterada` | 0.60 | Urgente | AVC, glaucoma agudo ou oclusão retiniana — risco de cegueira permanente |

A lógica comum a `r_ur10`/`r_ur13` e `r_ur12` é a separação das vias de perda de líquidos: vómitos e diarreia em simultâneo já tinham regra própria (`r_ur3`); as novas regras cobrem os casos onde apenas uma das vias está comprometida, garantindo triagem adequada mesmo nesses cenários.

### 3.5 Novas Regras de Pouco Urgente

Foram adicionadas três regras que servem para **evitar a sobreavaliação** (over-triage) de quadros virais benignos:

| Regra | Premissas | CF | Justificação |
|---|---|---|---|
| `r_pu5` | `constipacao` + `dor_garganta` + `nao(febre_alta)` | 0.72 | Quadro viral típico — dor de garganta no contexto de constipação sem febre alta não justifica urgência |
| `r_pu6` | `febre_baixa` + `mal_estar` + `nao(dor_abd)` | 0.68 | Infeção viral autolimitada — a ausência de dor abdominal afasta complicações |
| `r_pu7` | `constipacao` + `dor_persiste` + `nao(febre_alta)` | 0.65 | Cefaleia/mialgia gripal — dor que não cede no contexto de constipação é gripal, não urgência |

Estas regras interagem diretamente com as modificações às regras `r_ur5` e `r_ur6` descritas a seguir: em conjunto, criam caminhos de raciocínio que diferenciam o mesmo sintoma (por exemplo, dor de garganta) consoante o contexto clínico completo.

### 3.6 Modificação de Regras Existentes

Duas regras foram modificadas para adicionar condições de negação que corrigiam classificações incorretas:

**`r_ur5` — Dor persistente:**
- Versão original: `se([dor_persiste])` → urgente (CF 0.40)
- Versão atual: `se([dor_persiste, nao(constipacao)])` → urgente (CF 0.40)

Sem esta modificação, uma cefaleia ou mialgia gripal que não cedia ao paracetamol era classificada como urgente. O contexto de constipação indica que a dor tem origem viral e não requer consulta de urgência — é este caso que a nova regra `r_pu7` trata.

**`r_ur6` — Dor de garganta:**
- Versão original: `se([dor_garganta])` → urgente (CF 0.55)
- Versão atual: `se([dor_garganta, nao(constipacao)])` → urgente (CF 0.55)

Analogamente, a dor de garganta isolada deve ser urgente apenas quando não está inserida num quadro de constipação. Com constipação, a regra `r_pu5` classifica-a como pouco urgente se não houver febre alta. Sem a condição `nao(constipacao)` em `r_ur6`, as duas regras disputavam o mesmo caso e o motor reportava urgente por ter um CF mais alto.

### 3.7 Remoção das Regras de Contra-Evidência (CF Negativos)

A versão original continha 13 regras com CF negativo (`r_c_em1` a `r_c_ur3`) que penalizavam os níveis mais graves quando sintomas benignos estavam presentes. Por exemplo, a presença de `dor_leve` reduzia o CF de emergência em 0.70 e o de muito urgente em 0.55.

Estas regras foram **integralmente removidas** por duas razões:

1. **Segurança**: Um CF negativo pode, em teoria, baixar o resultado final abaixo de um limiar e esconder uma emergência real. Se um doente tem uma paragem respiratória (`r_em1`, CF 0.95) mas menciona também que tem um ligeiro mal-estar (`r_c_em4`, CF −0.45), a fórmula MYCIN combinaria os dois valores e o resultado de emergência seria atenuado — comportamento clinicamente inaceitável.

2. **Substituição por condições negadas**: As novas regras com premissas `nao(x)` cumprem a mesma função de forma segura e explícita. Em vez de penalizar um nível grave quando um sintoma benigno está presente, as regras agora só disparam para um nível benigno quando a ausência de sintomas graves é confirmada. O raciocínio é positivo e controlado, não subtrativo.

### 3.8 Atualização da Ordem de Questionamento

A predicado `ordem_sintomas/1`, que define a sequência de perguntas no motor Prolog do P1, foi atualizada para incluir os cinco novos sintomas nas posições adequadas:

- `reacao_alergica_grave` foi inserida imediatamente após `convulsoes` — porque pode evoluir rapidamente para anafilaxia e deve ser avaliada cedo.
- `visao_alterada` e `dor_cabeca_subita` foram colocadas após os sinais de AVC clássicos (`fala_dificil`, `fraqueza_lado`) — completando o rastreio neurológico antes de passar para sintomas de menor gravidade.
- `rigidez_nuca` e `rash_petequial` foram colocadas imediatamente após `febre_alta` — porque a sua relevância clínica depende da presença de febre e a combinação deve ser avaliada em sequência.

---

## 4. Base de Conhecimento e RAG

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

## 5. Deteção de Sintomas

### 4.1 Sistema de Keywords

A deteção de sintomas na mensagem do utilizador é feita através de um dicionário de keywords (`SINTOMAS_KEYWORDS`) que cobre 28 sintomas. Para cada sintoma, são definidas múltiplas expressões equivalentes em português corrente, incluindo variantes com e sem acentuação e formulações coloquiais. Por exemplo, `dor_peito` é detetado por expressões como "dor no peito", "aperto no peito", "pressão no peito", "dor torácica", "peito a doer", entre outras.

A deteção de negações é feita por análise de contexto: para cada keyword encontrada no texto, é inspecionada uma janela de 35 carateres anteriores à ocorrência. Se essa janela contiver palavras de negação ("não", "sem", "nunca", "ausência de"), o sintoma é marcado como ausente em vez de presente.

Este sistema determinou a decisão de **desativar** o LLM para a tarefa de extração de sintomas (ver 5.2), dado que o sistema de keywords demonstrou ser mais fiável e determinístico para as condições do projeto.

### 4.2 Limitações do LLM na Extração Estruturada

Embora exista uma função `extrair_sintomas_llm` que envia ao Ollama um prompt pedindo a identificação de sintomas em formato JSON, esta função não é invocada durante o fluxo normal. O motivo é a propensão do modelo Llama 3.2:3b para alucinações em tarefas de extração estruturada: o modelo gerava frequentemente sintomas não presentes no texto, confundia negações, ou devolvia JSON malformado. O sistema de keywords, sendo determinístico e construído manualmente com conhecimento do domínio, revelou-se significativamente mais robusto para este contexto.

### 4.3 Exclusões Mútuas e Propagação de Negações

Após a deteção de novos sintomas, é aplicada uma etapa de consistência lógica. O sistema define pares de sintomas **mutuamente exclusivos**: a confirmação de `febre_alta` (>39 °C) implica automaticamente a negação de `febre_baixa` (<38 °C), e vice-versa. Desta forma evita-se que a base de sintomas da sessão contenha contradições que comprometam a avaliação das regras.

---

## 6. Motor de Inferência MYCIN

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

## 7. Gestão da Conversa

### 6.1 Estado de Sessão

Cada sessão é identificada por um UUID e mantém em memória o seguinte estado:

- `sintomas` — dicionário `{id_sintoma: "sim" | "nao"}` com todos os sintomas avaliados.
- `history` — lista de mensagens da conversa (papel + conteúdo).
- `ultima_pergunta` — sintoma sobre o qual foi feita a última pergunta, para mapear corretamente respostas do tipo "sim"/"não" sem que o utilizador repita o nome do sintoma.
- `perguntas_feitas` — conjunto de sintomas já perguntados. Um sintoma é adicionado a este conjunto **apenas depois de o utilizador responder de forma clara** (sim, não ou incerto) — não no momento em que a pergunta é selecionada. Esta distinção evita que uma mensagem não reconhecida (como um pedido de explicação) "queime" um sintoma antes de o utilizador ter tido oportunidade de responder.
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
- Uma regra de emergência está completamente satisfeita pelos sintomas confirmados (por exemplo, `febre_alta` + `confusao` + `dor_abd` → sépsis, regra `r_em6`). Neste caso é aplicado um **early-exit absoluto**: a triagem é desencadeada de imediato, sem calcular a próxima pergunta clínica nem atualizar `ultima_pergunta` ou `perguntas_feitas`. Este mecanismo separa-se explicitamente do fluxo normal para garantir que nenhuma pergunta adicional seja colocada quando já existe uma emergência confirmada.
- Foram feitas 6 ou mais trocas e há pelo menos 4 sintomas avaliados (limite superior de conversa).
- Para sintomas urgentes, a triagem dispara quando há 5 ou mais sintomas avaliados e pelo menos 3 trocas de conversa, **desde que** nenhuma regra de emergência tenha ainda premissas por descobrir — garantindo que o sistema não encerra prematuramente quando uma regra de emergência ainda pode ser satisfeita.

### 6.4 Tratamento de Respostas Ambíguas

A função `e_resposta_simples` classifica cada mensagem como `True` (confirmação), `False` (negação) ou `None` (incerta). São reconhecidas variantes coloquiais de "sim" e "não" em português, incluindo expressões como "pois", "claro", "exatamente", "efetivamente" ou "negativo".

Respostas qualificadas — como "tenho febre, mas não acima de 39 graus" — são identificadas pela presença de conjunções adversativas após um confirmador, sendo classificadas como incertas (`None`) para evitar mapeamentos incorretos. Expressões de frequência intermitente ("às vezes", "de vez em quando") são tratadas da mesma forma, dado que a triagem clínica requer confirmação, não mera possibilidade.

O vocabulário de confirmações foi também estendido com **intensificadores absolutos**: respostas como "muito", "bastante", "claramente", "definitivamente", "totalmente", "absolutamente", "sem dúvida" ou "tenho sim" são mapeadas diretamente como `True` sem recorrer ao LLM. Esta extensão é implementada de forma determinística — por dicionário e expressões regulares — com latência nula, evitando uma chamada extra ao Ollama por cada turno de conversa.

Quando a resposta é incerta (`e_resposta_incerta`), o sintoma não é registado, mas é adicionado ao conjunto `perguntas_feitas` para não ser repetido.

### 6.5 Intercepção de Pedidos de Explicação

Durante a conversa, o utilizador pode questionar a pertinência de uma pergunta clínica com mensagens como "porquê precisas de saber?", "não percebo", "o que significa isso?" ou "por que motivo me pergunta isto?". Em vez de tratar estas mensagens como respostas ao sintoma em avaliação, o sistema deteta a intenção de pedido de explicação (`e_intencao_porque`) e responde com a justificação clínica correspondente.

A justificação é obtida diretamente da base de conhecimento Prolog: o predicado `explicacao(sintoma, 'Texto')`, já existente em `base_conhecimento_a.pl`, é extraído no arranque do servidor e armazenado no dicionário `EXPLICACOES_SINT`. Para cada sintoma há uma explicação textual que descreve a relevância clínica do sintoma no contexto da triagem (por exemplo, para `dor_peito`: *"A dor no peito é o sintoma primário de alerta para avaliar a hipótese de um Enfarte do Miocárdio"*).

Após exibir a explicação, o sistema **repete a pergunta clínica anterior** sem avançar para o próximo sintoma. O estado de sessão não é modificado: `ultima_pergunta` mantém-se inalterado e `perguntas_feitas` não é atualizado. Desta forma, o utilizador tem oportunidade de responder com contexto adequado.

### 6.6 Persistência Local de Triagens

No P1, a gravação de triagens no ficheiro `triagens.csv` era feita exclusivamente através do endpoint `/api/validate` do servidor Prolog, que dependia do estado de `facto/2` da sessão Prolog ativa. Esta dependência tornava a persistência inoperante em modo fallback Python.

Foi implementada a função `salvar_triagem_csv`, que é invocada pelo servidor Python sempre que uma triagem é concluída — independentemente de ter sido realizada pelo motor Prolog ou pelo motor Python. A função converte o dicionário `session["sintomas"]` numa linha binária (0/1 por sintoma), seguindo a mesma ordem de colunas do `triagens.csv` existente, e escreve-a em modo append. A coluna `nivel` recebe o identificador Prolog do nível vencedor (por exemplo, `urgente`, `muito_urgente`), garantindo compatibilidade com o pipeline de treino do P1 Parte B.

---

## 8. Geração de Linguagem Natural com LLM

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

## 9. Interface Web

A interface de utilizador é uma página HTML de página única (`chatbot.html`), servida diretamente pelo servidor FastAPI. É implementada em HTML, CSS e JavaScript puro, sem dependências externas de framework.

A interface apresenta um painel de chat à esquerda e um painel lateral de diagnóstico à direita, que exibe em tempo real os sintomas já detetados na sessão (marcados como presentes ou ausentes), o status de ligação ao modelo Ollama, e o resultado final de triagem com o respetivo nível de urgência codificado por cor.

A comunicação com o servidor é feita através de dois endpoints principais:

- `POST /api/chat/start` — inicia uma nova sessão e recebe a mensagem de boas-vindas.
- `POST /api/chat/message` — envia uma mensagem do utilizador e recebe a resposta do sistema, o estado atual dos sintomas, e, quando disponível, o resultado de triagem.

O estado de ligação ao Ollama é monitorizado via `GET /api/chat/status`, que devolve a lista de modelos disponíveis e confirma se o modelo `llama3.2:3b` está carregado.

---

## 10. Conclusão

O sistema desenvolvido integra três paradigmas distintos de inteligência artificial: raciocínio baseado em regras (motor MYCIN / Prolog), recuperação de informação (RAG / TF-IDF) e geração de linguagem natural (LLM / Llama 3.2). A divisão de responsabilidades é clara: a lógica clínica e de inferência é inteiramente controlada pelo motor de regras e pela base de conhecimento do P1; o LLM é confinado à dimensão linguística da interação, com filtros que impedem que alucinações comprometam a segurança do resultado.

Relativamente à versão inicial do P2, foram introduzidas quatro melhorias ao orquestrador de diálogo: intercepção de pedidos de explicação com resposta clínica contextual (reutilizando `explicacao/2` da base Prolog); reconhecimento de intensificadores como afirmações sem chamada adicional ao LLM; early-exit absoluto quando uma regra de emergência está completamente satisfeita; e persistência automática de triagens em `triagens.csv` independentemente da disponibilidade do servidor Prolog. Foi também corrigido um bug de gestão de estado em que um sintoma era marcado como "já perguntado" no momento da seleção, em vez de apenas após resposta clara do utilizador.

A principal limitação identificada é a capacidade do modelo Llama 3.2:3b em tarefas de extração estruturada, o que levou à decisão de o excluir do pipeline de deteção de sintomas em favor de um sistema determinístico baseado em keywords. Esta troca entre generalidade e fiabilidade é uma das tensões centrais na utilização de LLMs de dimensão reduzida em domínios de alto risco como a triagem clínica.
