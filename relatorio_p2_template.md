

Universidade do Minho
Escola de Ciências




Projeto 2
Sistemas Inteligentes de Apoio à Decisão

Alexandr Tchikoulaev A103625
André Pinto A106825
João Alves A102394
Rui Silva A106831




Trabalho efetuado sob a orientação de
André Agostinho Granja Silva Oliveira
Manuel Filipe Vieira Torres Santos




Maio 2026




---

# Índice

1. Introdução ............................................................... 1
   - 1.1. Enquadramento .................................................... 1
   - 1.2. Objetivos ......................................................... 1
2. Execução do Projeto ...................................................... 2
   - 2.1. Diagrama de Gantt ................................................. 2
   - 2.2. Distribuição de Trabalho .......................................... 2
3. Evolução da Base de Conhecimento ......................................... 7
   - 3.1. Enquadramento e Motivação ......................................... 7
   - 3.2. Novos Sintomas .................................................... 7
   - 3.3. Novas Regras de Emergência ........................................ 8
   - 3.4. Novas Regras de Muito Urgente ..................................... 8
   - 3.5. Novas Regras de Urgente e Pediátricas ............................. 9
   - 3.6. Novas Regras de Pouco Urgente ..................................... 9
   - 3.7. Modificação de Regras Existentes .................................. 9
   - 3.8. Remoção das Regras de Contra-Evidência ............................ 10
   - 3.9. Atualização da Ordem de Questionamento ............................ 10
4. Sistema de Chatbot SNS24 ................................................. 11
   - 4.1. Arquitetura do Sistema ............................................ 11
   - 4.2. Base de Conhecimento e Módulo RAG ................................. 12
   - 4.3. Deteção de Sintomas ............................................... 13
   - 4.4. Motor de Inferência MYCIN ......................................... 14
   - 4.5. Gestão da Conversa ................................................ 15
   - 4.6. Geração de Linguagem Natural com LLM .............................. 17
   - 4.7. Interface Web ..................................................... 18
5. Funcionalidades Avançadas ................................................ 19
   - 5.1. Garantia de Segurança Clínica ..................................... 19
   - 5.2. Intercepção de Pedidos de Explicação .............................. 19
   - 5.3. Persistência Local de Triagens .................................... 20
6. Conclusões ............................................................... 21
   - 6.1. Síntese ........................................................... 21
   - 6.2. Discussão ......................................................... 21
   - 6.3. Funcionamento do Trabalho em Grupo ................................ 22
Anexo A ..................................................................... 23
Anexo B ..................................................................... 70
Bibliografia ................................................................ 71

---

## 1. Introdução

### 1.1. Enquadramento

Este projeto foi desenvolvido pelo Grupo 4 (Alexandr Tchikoulaev, André Pinto, João Alves e Rui Silva) no âmbito da unidade curricular de Sistemas Inteligentes de Apoio à Decisão da Licenciatura em Ciência de Dados na Universidade do Minho.
O Projeto 2 tem como objetivo estender o Sistema Baseado em Conhecimento desenvolvido no Projeto 1, adicionando uma camada de interação em linguagem natural sob a forma de chatbot conversacional. O sistema integra o modelo de linguagem de grande dimensão (LLM) Llama 3.2 (3B parâmetros), executado localmente através da plataforma Ollama, com a técnica de Retrieval-Augmented Generation (RAG) e com o motor de inferência MYCIN já implementado em Prolog no Projeto 1.
A integração com o P1 é direta: a base de conhecimento em Prolog (`base_conhecimento_a.pl` e `base_conhecimento_b.pl`) é reutilizada tanto para alimentar o módulo RAG como para alimentar o motor de inferência. O sistema é, portanto, uma extensão natural do trabalho anterior, adicionando uma camada de linguagem natural e um motor de diálogo estruturado que permite ao utilizador descrever os seus sintomas em português corrente.
A pertinência desta abordagem no contexto do SNS24 é imediata: uma interface conversacional reduz a barreira de utilização relativamente ao formulário estruturado do Projeto 1, tornando o sistema acessível a utilizadores sem literacia informática, e o uso de um LLM local garante que nenhum dado clínico do utilizador abandona o dispositivo.

### 1.2. Objetivos

O principal objetivo deste projeto é desenvolver um chatbot de triagem médica que permita ao utilizador descrever os seus sintomas em linguagem natural e receber, no final da conversa, um resultado de triagem com nível de urgência e recomendação clínica.

De forma mais específica, pretende-se:

- Expandir a base de conhecimento `base_conhecimento_a.pl` com novos sintomas e regras clínicas identificadas durante os testes do P1
- Construir um módulo RAG que indexe automaticamente toda a base de conhecimento Prolog para suporte à geração de respostas pelo LLM
- Implementar um sistema determinístico de deteção de sintomas em linguagem natural, robusto a variações ortográficas e expressões coloquiais
- Desenvolver um motor de diálogo estruturado que selecione dinamicamente as perguntas mais informativas a colocar em cada turno de conversa
- Integrar o motor MYCIN do P1 (Prolog) com um motor MYCIN equivalente implementado em Python como salvaguarda
- Criar uma interface web conversacional moderna que apresente o resultado de triagem de forma clara e justificada

---

## 2. Execução do Projeto

### 2.1. Diagrama de Gantt

figura 1: Diagrama de Gantt do Projeto 2

### 2.2. Distribuição de Trabalho

A execução deste projeto decorreu em continuidade do Projeto 1, o que permitiu ao grupo partir de uma base técnica consolidada e distribuir o trabalho em função das competências demonstradas na primeira fase. A estratégia adotada foi manter a mesma divisão por especialização: cada elemento assumiu a responsabilidade pelas componentes diretamente relacionadas com o seu contributo no P1, garantindo continuidade e coerência técnica. Tal como anteriormente, o sucesso do sistema dependeu de integração constante entre as diferentes frentes de desenvolvimento — o motor de diálogo, o RAG, o LLM e a interface web avançaram em paralelo, mas exigiram sincronização frequente para garantir compatibilidade de interfaces e coerência clínica dos resultados.

#### 2.2.1. Alexandr Tchikoulaev

O meu contributo no Projeto 2 centrou-se na evolução da base de conhecimento clínico, que no Projeto 1 tinha ficado limitada a vinte e oito regras e vinte e três sintomas. A análise dos casos de triagem testados durante o desenvolvimento do P1 revelou diversas lacunas clinicamente significativas: padrões de meningite bacteriana, anafilaxia, hemorragia subaracnoideia e AVC com envolvimento da visão não tinham representação na base de conhecimento original.

Para colmatar estas lacunas, adicionei cinco novos sintomas à base (`rigidez_nuca`, `rash_petequial`, `reacao_alergica_grave`, `dor_cabeca_subita`, `visao_alterada`), que permitiram formular quatro novas regras de emergência e quatro novas regras de muito urgente. Acrescentei ainda cinco regras para quadros gastrointestinais e pediátricos que separavam correctamente os cenários de vómitos isolados, diarreia isolada e ambos em simultâneo — distinção clinicamente relevante pois implica diferentes riscos de desidratação e diferentes vias de reposição. Adicionei três regras de pouco urgente destinadas especificamente a evitar a sobreavaliação de quadros virais benignos, que constituíam o erro mais frequente nos testes informais do P1. Modifiquei ainda duas regras existentes (`r_ur5` e `r_ur6`) para incluir condições de negação que corrigiam classificações incorretas no contexto de constipação.

A decisão com maior impacto arquitetural foi a remoção integral das treze regras de contra-evidência com CF negativo que a versão original continha. Estas regras introduziam um risco de segurança clínica inaceitável: em teoria, a presença de um sintoma benigno como `mal_estar` podia atenuar o CF de emergência de um doente com paragem respiratória. As novas regras com premissas `nao(x)` cumprem a mesma função de diferenciação clínica de forma positiva e controlada.

Por fim, atualizei o predicado `ordem_sintomas/1` para incluir os cinco novos sintomas nas posições adequadas, de modo a que o motor Prolog do P1 os questione na sequência clinicamente correcta.

Código desenvolvido:
- `base_conhecimento_a.pl` — expansão de 28 para 36 regras, adição de 5 sintomas, remoção de 13 contra-evidências, modificação de `r_ur5`/`r_ur6`, atualização de `ordem_sintomas/1`

#### 2.2.2. André Pinto

A minha participação no Projeto 2 centrou-se no desenho da arquitetura global do sistema e no desenvolvimento do módulo RAG, que constitui a espinha dorsal da integração entre o conhecimento clínico formalizado em Prolog e o modelo de linguagem.

Defini a arquitetura de quatro componentes — servidor Python (FastAPI), modelo LLM (Ollama), motor Prolog (P1) e interface web — e o protocolo de comunicação entre eles. Esta decisão arquitetural garantiu a independência entre a lógica clínica e a camada de linguagem: o LLM nunca tem acesso direto ao motor de inferência, sendo o resultado clínico sempre determinado pelo MYCIN.

Desenvolvi o parser Prolog que, no arranque do servidor, lê automaticamente os ficheiros `base_conhecimento_a.pl` e `base_conhecimento_b.pl` e extrai as quatro estruturas de dados necessárias: sintomas, níveis de triagem, regras de produção e explicações. A partir destas estruturas, implementei a construção automática da coleção de documentos RAG em linguagem natural — três grupos de documentos (protocolo geral SNS24, uma entrada por regra de produção, grupos de sintomas por gravidade) — e o motor TF-IDF com análise de n-gramas de caráter (`char_wb`, bigramas a tetragramas) que indexa e recupera os documentos mais relevantes para cada mensagem do utilizador. A escolha de n-gramas de caráter, em vez de palavras completas, conferiu robustez a variações ortográficas, abreviaturas e erros de escrita, frequentes na linguagem natural clínica em português.

Código desenvolvido:
- `chatbot_server.py` — parser Prolog (`_extrair_mapa`, `parse_rules_pl`), construção dos documentos RAG (`_build_rag_docs`), classe `RAGEngine` (vectorizador TF-IDF, método `retrieve`)

#### 2.2.3. João Alves

A minha participação centrou-se no desenvolvimento da camada de interação com o utilizador — tanto a interface web do chatbot como a integração com o modelo de linguagem — e na funcionalidade de intercepção de pedidos de explicação.

Desenvolvi o frontend `chatbot.html` como uma Single Page Application em HTML, CSS e JavaScript puro, sem dependências externas. A interface apresenta um painel de chat à esquerda e um painel lateral de diagnóstico à direita, que exibe em tempo real os sintomas já detetados na sessão (marcados como presentes ou ausentes), o status de ligação ao modelo Ollama e o resultado final de triagem com o respetivo nível de urgência codificado por cor. A comunicação com o servidor é feita de forma assíncrona através de dois endpoints principais (`POST /api/chat/start` e `POST /api/chat/message`).

No que respeita ao LLM, implementei os três tipos de prompts utilizados pelo sistema: o prompt de reconhecimento contextual intercalar, que gera uma frase empática de transição antes de cada pergunta clínica; o prompt de introdução ao resultado final, que enquadra emocionalmente o diagnóstico sem o antecipar; e a lógica de pós-processamento que filtra alucinações, corrige pronomes para o registo formal do português europeu, remove referências clínicas proibidas e trunca respostas desnecessariamente longas. Implementei também a funcionalidade de intercepção de pedidos de explicação, que deteta intenções como "porquê precisas de saber?" e responde com a justificação clínica do sintoma antes de repetir a pergunta.

Código desenvolvido:
- `chatbot.html` — interface web completa (chat, painel de diagnóstico, comunicação assíncrona)
- `chatbot_server.py` — funções `gerar_acknowledgment`, `gerar_intro_resultado`, pós-processamento LLM, `e_intencao_porque`, gestão do endpoint `/api/chat/message` para pedidos de explicação

#### 2.2.4. Rui Silva

A minha contribuição no Projeto 2 centrou-se nas componentes de inferência clínica e de deteção de sintomas — as duas componentes que determinam directamente a qualidade e segurança do resultado de triagem.

Desenvolvi o sistema de deteção de sintomas por keywords, que cobre 28 sintomas com múltiplas expressões equivalentes em português corrente para cada um, incluindo variantes com e sem acentuação e formulações coloquiais. Implementei a deteção de negações por janela de contexto (35 carateres anteriores à ocorrência), a aplicação de exclusões mútuas para garantir consistência lógica entre sintomas relacionados (`febre_alta`/`febre_baixa`), e a classificação de respostas como confirmação, negação ou incerta através da função `e_resposta_simples`, incluindo intensificadores absolutos e respostas qualificadas com conjunções adversativas.

Implementei o motor MYCIN em Python (`triagem_mycin_python`) como alternativa ao servidor Prolog do P1, avaliando todas as regras da base de conhecimento carregada em memória com a fórmula de combinação de CFs compatível com o MYCIN original. Desenvolvi o algoritmo de seleção dinâmica da próxima pergunta (`calcular_proximo_sintoma`), que calcula um score exponencial `CF × 2^n_confirmadas` para cada sintoma desconhecido em cada regra ativa, favorecendo a conclusão de regras com evidências parciais. Implementei os critérios de disparo da triagem (sintomas de emergência individuais, regras de emergência completamente satisfeitas, early-exit absoluto, limites de turnos) e a salvaguarda de segurança clínica que garante que o nível mais grave entre o Prolog e o Python é sempre o resultado reportado. Implementei também a persistência automática de triagens em `triagens.csv` independentemente da disponibilidade do servidor Prolog.

Código desenvolvido:
- `chatbot_server.py` — `SINTOMAS_KEYWORDS`, `extrair_sintomas_keywords`, `e_resposta_simples`, `e_resposta_incerta`, `triagem_mycin_python`, `calcular_proximo_sintoma`, `calcular_scores_sessao`, critérios de triagem, `salvar_triagem_csv`

---

## 3. Evolução da Base de Conhecimento

### 3.1. Enquadramento e Motivação

No contexto do Projeto 2, a base de conhecimento `base_conhecimento_a.pl` foi revista e expandida relativamente à versão entregue no Projeto 1. As alterações têm dois objetivos complementares: aumentar a cobertura clínica do sistema para padrões de doença grave que a versão original não detetava, e tornar o raciocínio mais preciso eliminando mecanismos que se revelaram problemáticos durante os testes.

A versão original continha vinte e oito regras de produção, vinte e três sintomas e treze regras de contra-evidência com CF negativo. A análise de casos de triagem durante o desenvolvimento do chatbot revelou quatro síndromes de alto risco sem representação — meningite bacteriana, meningococcemia, anafilaxia e hemorragia subaracnoideia — e identificou a presença de regras de contra-evidência como um risco de segurança clínica que a nova arquitetura permite eliminar de forma segura.

### 3.2. Novos Sintomas

Foram adicionados cinco sintomas que não existiam na versão original:

| Identificador | Descrição |
|---|---|
| `rigidez_nuca` | Rigidez da nuca — não consegue encostar o queixo ao peito |
| `rash_petequial` | Manchas vermelhas ou roxas na pele que não desaparecem à pressão |
| `reacao_alergica_grave` | Reação alérgica grave com inchaço da face, língua ou garganta |
| `dor_cabeca_subita` | Dor de cabeça muito intensa de início súbito — "pior da vida" |
| `visao_alterada` | Alteração súbita da visão num ou ambos os olhos |

Estes sintomas cobrem quatro síndromes de alto risco que ficavam sem representação: meningite bacteriana e meningococcemia (os dois primeiros), anafilaxia (terceiro), hemorragia subaracnoideia (quarto) e AVC com envolvimento da visão (quinto). A sua adição foi necessária para que as novas regras de emergência e muito urgente descritas nas secções seguintes pudessem ser formuladas.

### 3.3. Novas Regras de Emergência

Foram acrescentadas quatro regras de emergência que combinam sintomas em padrões clínicos reconhecidos:

| Regra | Premissas | CF | Justificação clínica |
|---|---|---|---|
| `r_em8` | `resp_dificuldade` + `febre_alta` | 0.87 | Suspeita de pneumonia grave ou sépsis respiratória com risco de falência iminente |
| `r_em9` | `febre_alta` + `rigidez_nuca` | 0.92 | Padrão clássico de meningite bacteriana — emergência neurológica |
| `r_em10` | `febre_alta` + `rash_petequial` | 0.95 | Sinal de alerta de meningococcemia — progressão para choque em horas |
| `r_em11` | `resp_dificuldade` + `reacao_alergica_grave` | 0.93 | Anafilaxia com compromisso da via aérea — requer adrenalina e 112 |

O CF elevado destas regras (0.87–0.95) reflete a sua alta especificidade: cada combinação de sintomas aponta para um único quadro clínico com risco de vida imediato, o que justifica a adoção de um limiar de confiança próximo da certeza máxima.

### 3.4. Novas Regras de Muito Urgente

Quatro novas regras foram adicionadas ao nível muito urgente, cobrindo padrões neurológicos e cardiológicos que a versão original não contemplava:

| Regra | Premissas | CF | Justificação clínica |
|---|---|---|---|
| `r_mu10` | `confusao` + `febre_alta` + `nao(dor_abd)` | 0.85 | Padrão de meningite/encefalite — sem dor abdominal afasta sépsis (r_em6) |
| `r_mu11` | `reacao_alergica_grave` | 0.80 | Pode evoluir para anafilaxia — requer avaliação hospitalar imediata |
| `r_mu12` | `dor_cabeca_subita` | 0.85 | Sinal clássico de hemorragia subaracnoideia por rotura de aneurisma |
| `r_mu13` | `visao_alterada` + `fala_dificil` | 0.90 | Padrão BE-FAST completo de AVC — alta certeza diagnóstica |

A regra `r_mu10` é particularmente relevante do ponto de vista do raciocínio: introduz a negação de `dor_abd` como premissa para distinguir meningite/encefalite (muito urgente) de sépsis (emergência — regra `r_em6`). Sem esta distinção, um doente com confusão e febre mas sem dor abdominal não seria correctamente escalado.

### 3.5. Novas Regras de Urgente e Muito Urgente para Quadros Pediátricos e GI

Foram acrescentadas cinco regras que refinam a triagem de quadros gastrointestinais e pediátricos:

| Regra | Premissas | CF | Nível | Justificação |
|---|---|---|---|---|
| `r_ur10` | `vomitos` + `nao(diarreia)` | 0.60 | Urgente | Desidratação por via gástrica isolada — pode exigir reposição IV |
| `r_ur11` | `dor_garganta` + `febre_alta` | 0.75 | Urgente | Suspeita de amigdalite bacteriana com risco de abscesso |
| `r_ur12` | `febre_bebe` + `vomitos` + `nao(diarreia)` | 0.80 | Muito Urgente | Bebé com reservas limitadas — risco de desidratação rápida |
| `r_ur13` | `diarreia` + `nao(vomitos)` | 0.55 | Urgente | Diarreia grave implica desidratação; sem vómitos há margem para hidratação oral vigiada |
| `r_ur14` | `visao_alterada` | 0.60 | Urgente | AVC, glaucoma agudo ou oclusão retiniana — risco de cegueira permanente |

A lógica comum a `r_ur10`/`r_ur13` e `r_ur12` é a separação das vias de perda de líquidos: vómitos e diarreia em simultâneo já tinham regra própria (`r_ur3`); as novas regras cobrem os casos onde apenas uma das vias está comprometida, garantindo triagem adequada mesmo nesses cenários.

### 3.6. Novas Regras de Pouco Urgente

Foram adicionadas três regras que servem para evitar a sobreavaliação de quadros virais benignos:

| Regra | Premissas | CF | Justificação |
|---|---|---|---|
| `r_pu5` | `constipacao` + `dor_garganta` + `nao(febre_alta)` | 0.72 | Quadro viral típico — dor de garganta no contexto de constipação sem febre alta não justifica urgência |
| `r_pu6` | `febre_baixa` + `mal_estar` + `nao(dor_abd)` | 0.68 | Infeção viral autolimitada — a ausência de dor abdominal afasta complicações |
| `r_pu7` | `constipacao` + `dor_persiste` + `nao(febre_alta)` | 0.65 | Cefaleia/mialgia gripal — dor que não cede no contexto de constipação é gripal, não urgência |

Estas regras interagem directamente com as modificações às regras `r_ur5` e `r_ur6` descritas na secção seguinte: em conjunto, criam caminhos de raciocínio que diferenciam o mesmo sintoma (por exemplo, dor de garganta) consoante o contexto clínico completo.

### 3.7. Modificação de Regras Existentes

Duas regras foram modificadas para adicionar condições de negação que corrigiam classificações incorretas:

**`r_ur5` — Dor persistente:**
- Versão original: `se([dor_persiste])` → urgente (CF 0.40)
- Versão atual: `se([dor_persiste, nao(constipacao)])` → urgente (CF 0.40)

Sem esta modificação, uma cefaleia ou mialgia gripal que não cedia ao paracetamol era classificada como urgente. O contexto de constipação indica que a dor tem origem viral e não requer consulta de urgência — é este caso que a nova regra `r_pu7` trata.

**`r_ur6` — Dor de garganta:**
- Versão original: `se([dor_garganta])` → urgente (CF 0.55)
- Versão atual: `se([dor_garganta, nao(constipacao)])` → urgente (CF 0.55)

Analogamente, a dor de garganta isolada deve ser urgente apenas quando não está inserida num quadro de constipação. Com constipação, a regra `r_pu5` classifica-a como pouco urgente se não houver febre alta. Sem a condição `nao(constipacao)` em `r_ur6`, as duas regras disputavam o mesmo caso e o motor reportava urgente por ter um CF mais alto.

### 3.8. Remoção das Regras de Contra-Evidência (CF Negativos)

A versão original continha treze regras com CF negativo (`r_c_em1` a `r_c_ur3`) que penalizavam os níveis mais graves quando sintomas benignos estavam presentes. Por exemplo, a presença de `dor_leve` reduzia o CF de emergência em 0.70 e o de muito urgente em 0.55.

Estas regras foram integralmente removidas por duas razões:

1. **Segurança clínica**: Um CF negativo pode, em teoria, baixar o resultado final abaixo de um limiar e esconder uma emergência real. Se um doente tem uma paragem respiratória (`r_em1`, CF 0.95) mas menciona também que tem um ligeiro mal-estar (`r_c_em4`, CF −0.45), a fórmula MYCIN combinaria os dois valores e o resultado de emergência seria atenuado — comportamento clinicamente inaceitável.

2. **Substituição por condições negadas**: As novas regras com premissas `nao(x)` cumprem a mesma função de forma segura e explícita. Em vez de penalizar um nível grave quando um sintoma benigno está presente, as regras agora só disparam para um nível benigno quando a ausência de sintomas graves é confirmada. O raciocínio é positivo e controlado, não subtrativo.

### 3.9. Atualização da Ordem de Questionamento

O predicado `ordem_sintomas/1`, que define a sequência de perguntas no motor Prolog do P1, foi atualizado para incluir os cinco novos sintomas nas posições adequadas:

- `reacao_alergica_grave` foi inserida imediatamente após `convulsoes` — porque pode evoluir rapidamente para anafilaxia e deve ser avaliada cedo.
- `visao_alterada` e `dor_cabeca_subita` foram colocadas após os sinais de AVC clássicos (`fala_dificil`, `fraqueza_lado`) — completando o rastreio neurológico antes de passar para sintomas de menor gravidade.
- `rigidez_nuca` e `rash_petequial` foram colocadas imediatamente após `febre_alta` — porque a sua relevância clínica depende da presença de febre e a combinação deve ser avaliada em sequência.

---

## 4. Sistema de Chatbot SNS24

### 4.1. Arquitetura do Sistema

O sistema é composto por quatro componentes principais que comunicam entre si através de HTTP:

| Componente | Tecnologia | Porta |
|---|---|---|
| Servidor de chatbot (backend Python) | FastAPI + Uvicorn | 8081 |
| Modelo de linguagem (LLM) | Ollama / Llama 3.2:3b | 11434 |
| Motor MYCIN em Prolog (P1) | Servidor HTTP Prolog | 8080 |
| Interface Web (frontend) | HTML/CSS/JS | — |

figura 2: Arquitetura do Sistema de Chatbot SNS24

O fluxo de uma sessão de triagem é o seguinte:

1. O utilizador abre a interface web (`chatbot.html`) e inicia uma sessão via `POST /api/chat/start`, que devolve um identificador único de sessão (UUID).
2. Cada mensagem do utilizador é enviada via `POST /api/chat/message`. O servidor Python processa a mensagem: deteta sintomas, decide a próxima pergunta a fazer ou se é hora de realizar a triagem formal, e gera uma resposta em linguagem natural com o auxílio do LLM.
3. Quando os critérios de triagem são atingidos, o servidor tenta delegar ao motor MYCIN Prolog (P1, porta 8080). Caso este não esteja disponível, um motor MYCIN equivalente implementado em Python é utilizado como alternativa.
4. O resultado final (nível de urgência, recomendação, fator de certeza) é formatado e enviado ao utilizador.

O servidor Python é também proxy do servidor Prolog, expondo os seus endpoints (`/api/start`, `/api/answer`, `/api/validate`) de modo a que o frontend possa comunicar com ambos através da mesma origem.

A divisão de responsabilidades entre os componentes é clara e intencional: a lógica clínica e de inferência é inteiramente controlada pelo motor de regras e pela base de conhecimento Prolog; o LLM é confinado à dimensão linguística da interação, com filtros que impedem que eventuais alucinações comprometam a segurança do resultado.

### 4.2. Base de Conhecimento e Módulo RAG

#### Processamento dos Ficheiros Prolog

No arranque do servidor, os ficheiros `base_conhecimento_a.pl` e `base_conhecimento_b.pl` são lidos e analisados via expressões regulares. São extraídas quatro estruturas de dados:

- **Sintomas** — `sintoma(id, 'Descrição')`: mapeamento de identificadores Prolog para descrições em linguagem natural.
- **Níveis de triagem** — `nivel(id, 'Nome', 'Recomendação')`: os cinco níveis do protocolo SNS24 (Emergência, Muito Urgente, Urgente, Pouco Urgente, Sem Alarme).
- **Regras de produção** — `regra(id, se([premissas]), entao(nivel), CF)`: a base de conhecimento completa com fatores de certeza.
- **Explicações** — `explicacao_regra(id, 'Texto')` e `explicacao(sintoma, 'Texto')`: texto clínico associado a cada regra e sintoma.

#### Construção dos Documentos RAG

A partir dos dados extraídos, é construída uma coleção de documentos em linguagem natural simples, otimizados para serem interpretados por um LLM de 3B parâmetros. Cada documento segue o formato:

> `[condição(ões)] → [nível]. [O que fazer]. [Porquê — primeira frase da explicação clínica].`

São gerados três grupos de documentos:

1. **Protocolo geral** — uma descrição dos cinco níveis SNS24 e das respetivas ações recomendadas.
2. **Uma entrada por regra de produção** (partes A e B) — as premissas são traduzidas para linguagem natural; negações (`nao(x)`) são expressas como "sem X"; as regras da Parte B são marcadas como `[padrão aprendido automaticamente]`.
3. **Grupos de sintomas por gravidade** — listas dos sintomas típicos de cada nível, com a respetiva explicação clínica resumida.

A coleção resultante contém tipicamente entre 60 e 80 documentos.

#### Motor TF-IDF e Recuperação

O módulo RAG é implementado com a classe `RAGEngine`, que utiliza um vectorizador TF-IDF com análise de n-gramas de caráter (`char_wb`, bigramas a tetragramas), com um vocabulário máximo de 8 000 características. A escolha de n-gramas de caráter, em vez de palavras completas, confere robustez a variações ortográficas, abreviaturas e erros de escrita — frequentes na linguagem natural clínica em português.

A recuperação é feita por similaridade de cosseno entre o vetor da consulta e a matriz de documentos. São devolvidos os `top_k=5` documentos com similaridade superior a 0.01. O contexto recuperado é injetado nos prompts enviados ao LLM quando este é chamado para gerar respostas livres contextuais.

### 4.3. Deteção de Sintomas

#### Sistema de Keywords

A deteção de sintomas na mensagem do utilizador é feita através de um dicionário de keywords (`SINTOMAS_KEYWORDS`) que cobre 28 sintomas. Para cada sintoma, são definidas múltiplas expressões equivalentes em português corrente, incluindo variantes com e sem acentuação e formulações coloquiais. Por exemplo, `dor_peito` é detetado por expressões como "dor no peito", "aperto no peito", "pressão no peito", "dor torácica", "peito a doer", entre outras.

A deteção de negações é feita por análise de contexto: para cada keyword encontrada no texto, é inspecionada uma janela de 35 carateres anteriores à ocorrência. Se essa janela contiver palavras de negação ("não", "sem", "nunca", "ausência de"), o sintoma é marcado como ausente em vez de presente.

Este sistema determinou a decisão de desativar o LLM para a tarefa de extração de sintomas: o sistema de keywords demonstrou ser mais fiável e determinístico, enquanto o modelo Llama 3.2:3b gerava frequentemente sintomas não presentes no texto, confundia negações, ou devolvia JSON malformado.

#### Limitações do LLM na Extração Estruturada

Embora exista uma função `extrair_sintomas_llm` que envia ao Ollama um prompt pedindo a identificação de sintomas em formato JSON, esta função não é invocada durante o fluxo normal. A propensão do modelo Llama 3.2:3b para alucinações em tarefas de extração estruturada — geração de sintomas não presentes no texto, confusão de negações, JSON malformado — tornou o sistema de keywords significativamente mais robusto para este contexto de domínio especializado.

#### Exclusões Mútuas e Propagação de Negações

Após a deteção de novos sintomas, é aplicada uma etapa de consistência lógica. O sistema define pares de sintomas mutuamente exclusivos: a confirmação de `febre_alta` (>39 °C) implica automaticamente a negação de `febre_baixa` (<38 °C), e vice-versa. Desta forma evita-se que a base de sintomas da sessão contenha contradições que comprometam a avaliação das regras.

### 4.4. Motor de Inferência MYCIN

#### Motor MYCIN em Python (Alternativa)

O motor MYCIN foi originalmente implementado em Prolog no P1. Para garantir que o chatbot funciona mesmo quando o servidor Prolog não está disponível, foi desenvolvida uma implementação equivalente em Python (`triagem_mycin_python`).

O motor avalia todas as regras da base de conhecimento carregada em memória. Para cada regra, verifica se todas as premissas estão satisfeitas pelo conjunto de sintomas confirmados na sessão: premissas positivas requerem que o sintoma esteja marcado como presente; premissas negativas (`nao(sintoma)`) requerem que o sintoma esteja ausente ou não confirmado.

Quando uma regra dispara, o seu fator de certeza (CF) é combinado com o CF já acumulado para o mesmo nível, usando a fórmula padrão MYCIN:

$$CF_{combinado} = CF_1 + CF_2 \times (1 - CF_1)$$

Esta fórmula garante que a combinação de múltiplas evidências independentes aumenta progressivamente a certeza sem ultrapassar 1. No final, o nível mais grave que disparou é o resultado reportado, com o respetivo CF final expresso em percentagem.

#### Integração com o Servidor Prolog (P1)

Quando o servidor Prolog (P1) está disponível na porta 8080, o chatbot delega-lhe a triagem formal. O protocolo de comunicação é o mesmo definido no P1: o servidor Python envia `POST /api/start` para iniciar uma sessão Prolog, e responde iterativamente às perguntas do motor MYCIN Prolog enviando `POST /api/answer` com o valor (`"sim"` ou `"nao"`) para cada sintoma, até o Prolog devolver um resultado.

### 4.5. Gestão da Conversa

#### Estado de Sessão

Cada sessão é identificada por um UUID e mantém em memória o seguinte estado:

- `sintomas` — dicionário `{id_sintoma: "sim" | "nao"}` com todos os sintomas avaliados.
- `history` — lista de mensagens da conversa (papel + conteúdo).
- `ultima_pergunta` — sintoma sobre o qual foi feita a última pergunta, para mapear correctamente respostas do tipo "sim"/"não" sem que o utilizador repita o nome do sintoma.
- `perguntas_feitas` — conjunto de sintomas já perguntados. Um sintoma é adicionado a este conjunto **apenas depois de o utilizador responder de forma clara** — não no momento em que a pergunta é seleccionada. Esta distinção evita que uma mensagem não reconhecida (como um pedido de explicação) "queime" um sintoma antes de o utilizador ter tido oportunidade de responder.
- `triagem_feita` — booleano que impede que a triagem seja executada mais de uma vez.
- `n_trocas` — contador de turnos de conversa.

#### Algoritmo de Seleção da Próxima Pergunta

O sistema não segue uma ordem fixa de perguntas. Em vez disso, a função `calcular_proximo_sintoma` escolhe dinamicamente o sintoma mais informativo a perguntar a seguir, tendo em conta o estado atual da sessão e as regras da base de conhecimento.

Para cada regra ainda ativa (não eliminada por uma premissa falsa, e com pelo menos uma premissa desconhecida), é calculado um score para cada sintoma desconhecido:

$$score = CF_{regra} \times 2^{n_{confirmadas}}$$

onde $n_{confirmadas}$ é o número de premissas da regra já confirmadas. O expoente cria um peso exponencial que favorece fortemente a conclusão de regras com evidências parciais em detrimento de abrir novas regras sem qualquer confirmação. Para regras cujas premissas estão todas por descobrir (e já existe pelo menos um sintoma confirmado na sessão), o peso é reduzido a $CF \times 0.2$, de modo a que uma regra em curso não seja interrompida por uma regra mais genérica com CF elevado.

O sintoma com o score acumulado mais alto entre todas as regras ativas é seleccionado, excluindo os sintomas já perguntados.

#### Critérios de Disparo da Triagem

A triagem formal é desencadeada quando se verifica uma das seguintes condições:

- Está presente pelo menos um sintoma de emergência individual (`sem_respiracao`, `sem_pulso`, `resp_dificuldade`, `hemorragia`, `inconsciente`, `convulsoes`).
- Uma regra de emergência está completamente satisfeita pelos sintomas confirmados (por exemplo, `febre_alta` + `confusao` + `dor_abd` → sépsis, regra `r_em6`). Neste caso é aplicado um **early-exit absoluto**: a triagem é desencadeada de imediato, sem calcular a próxima pergunta clínica nem atualizar `ultima_pergunta` ou `perguntas_feitas`. Este mecanismo separa-se explicitamente do fluxo normal para garantir que nenhuma pergunta adicional seja colocada quando já existe uma emergência confirmada.
- Foram feitas 6 ou mais trocas e há pelo menos 4 sintomas avaliados (limite superior de conversa).
- Para sintomas urgentes, a triagem dispara quando há 5 ou mais sintomas avaliados e pelo menos 3 trocas de conversa, desde que nenhuma regra de emergência tenha ainda premissas por descobrir.

#### Tratamento de Respostas Ambíguas

A função `e_resposta_simples` classifica cada mensagem como `True` (confirmação), `False` (negação) ou `None` (incerta). São reconhecidas variantes coloquiais de "sim" e "não" em português, incluindo expressões como "pois", "claro", "exatamente", "efetivamente" ou "negativo".

Respostas qualificadas — como "tenho febre, mas não acima de 39 graus" — são identificadas pela presença de conjunções adversativas após um confirmador, sendo classificadas como incertas para evitar mapeamentos incorretos. O vocabulário de confirmações foi também estendido com intensificadores absolutos: respostas como "muito", "bastante", "definitivamente", "absolutamente", "sem dúvida" são mapeadas directamente como `True` sem recorrer ao LLM, com latência nula.

Quando a resposta é incerta (`e_resposta_incerta`), o sintoma não é registado, mas é adicionado ao conjunto `perguntas_feitas` para não ser repetido.

### 4.6. Geração de Linguagem Natural com LLM

#### Modelo e Configuração

O LLM utilizado é o **Llama 3.2:3b**, executado localmente via **Ollama** (porta 11434). É um modelo compacto de 3B parâmetros, adequado para execução em hardware de consumo sem GPU dedicada. A temperatura é fixada em 0.1 para minimizar a variabilidade e reduzir o risco de alucinações. O número máximo de tokens gerados é limitado por caso de uso: 25 tokens para frases de reconhecimento intercalar, 35 tokens para a transição antes de uma pergunta clínica.

O LLM **não** é usado para inferência clínica nem para extração de sintomas. O seu papel é exclusivamente **linguístico**: tornar a conversa mais natural e empática, sem influenciar a lógica de triagem.

#### Prompts de Reconhecimento (Mid-Conversation)

Em cada turno de conversa, antes de colocar a próxima pergunta clínica, o LLM gera um breve reconhecimento contextual. O prompt descreve a situação do turno anterior (por exemplo, "o utilizador confirmou 'Febre alta (>39°C)'" ou "o utilizador não tem certeza sobre 'Dor no peito'") e pede uma frase empática de transição no registo formal do português europeu (uso de "si" em vez de "você").

O formato de saída esperado é fixo: `[frase empática]. [palavras de transição]:`, após o qual o sistema concatena a pergunta clínica pré-definida para o próximo sintoma.

#### Prompt de Introdução ao Resultado

Quando a triagem está concluída, o LLM gera uma única frase introdutória empática antes do resultado estruturado ser apresentado. O prompt instrui explicitamente o modelo a não revelar o nível, recomendações, nem qualquer referência clínica. O resultado (nível, recomendação, confiança) é inserido pelo servidor Python após a frase do LLM.

#### Pós-Processamento e Filtragem de Alucinações

A saída do LLM é sempre sujeita a pós-processamento antes de ser enviada ao utilizador:

1. **Remoção de perguntas** — qualquer fragmento a partir de "?" é eliminado (o LLM não deve antecipar a pergunta clínica seguinte).
2. **Filtragem de conteúdo clínico proibido** — expressões como "112", "urgência", "emergência", "imediatamente", "grave" são removidas do reconhecimento intercalar, para garantir que o LLM não influencia a perceção de gravidade antes do resultado formal.
3. **Deteção de antecipação do próximo sintoma** — se o texto gerado contiver keywords associadas ao sintoma que vai ser perguntado a seguir, a frase é substituída por um texto neutro fixo.
4. **Correção de pronomes** — o modelo tende a usar o registo informal ("você", "estás", "tens"). Substituições por expressão regular corrigem estes casos para o registo formal do português europeu ("si", "está", "tem").
5. **Limite de comprimento** — o texto é truncado a no máximo duas frases.

### 4.7. Interface Web

A interface de utilizador é uma página HTML de página única (`chatbot.html`), servida directamente pelo servidor FastAPI. É implementada em HTML, CSS e JavaScript puro, sem dependências externas de framework.

figura 3: Interface Web do Chatbot SNS24

A interface apresenta um painel de chat à esquerda e um painel lateral de diagnóstico à direita, que exibe em tempo real os sintomas já detetados na sessão (marcados como presentes ou ausentes), o status de ligação ao modelo Ollama, e o resultado final de triagem com o respetivo nível de urgência codificado por cor.

A comunicação com o servidor é feita através de dois endpoints principais:

- `POST /api/chat/start` — inicia uma nova sessão e recebe a mensagem de boas-vindas.
- `POST /api/chat/message` — envia uma mensagem do utilizador e recebe a resposta do sistema, o estado atual dos sintomas, e, quando disponível, o resultado de triagem.

O estado de ligação ao Ollama é monitorizado via `GET /api/chat/status`, que devolve a lista de modelos disponíveis e confirma se o modelo `llama3.2:3b` está carregado.

---

## 5. Funcionalidades Avançadas

### 5.1. Garantia de Segurança Clínica

Após obter o resultado do motor Prolog, o motor Python é também executado em paralelo. Se o Python concluir um nível **mais grave** do que o Prolog, o resultado Python prevalece. Esta salvaguarda corrige uma assimetria do motor Prolog do P1, que seleciona a regra com o CF mais alto (e não necessariamente o nível mais grave): por exemplo, uma regra de `urgente` com CF 0.85 não deve suprimir uma regra de `muito_urgente` com CF 0.60.

Esta camada de segurança garante que o sistema nunca subestima a gravidade clínica de um caso por um artefacto do motor de inferência. A decisão de incluir esta salvaguarda foi motivada por testes informais em que o servidor Prolog retornava `urgente` em casos onde o motor Python identificava corretamente `muito_urgente` devido a uma regra com CF inferior mas nível mais grave.

### 5.2. Intercepção de Pedidos de Explicação

Durante a conversa, o utilizador pode questionar a pertinência de uma pergunta clínica com mensagens como "porquê precisas de saber?", "não percebo", "o que significa isso?" ou "por que motivo me pergunta isto?". Em vez de tratar estas mensagens como respostas ao sintoma em avaliação, o sistema deteta a intenção de pedido de explicação (`e_intencao_porque`) e responde com a justificação clínica correspondente.

A justificação é obtida directamente da base de conhecimento Prolog: o predicado `explicacao(sintoma, 'Texto')`, já existente em `base_conhecimento_a.pl`, é extraído no arranque do servidor e armazenado no dicionário `EXPLICACOES_SINT`. Para cada sintoma há uma explicação textual que descreve a relevância clínica do sintoma no contexto da triagem (por exemplo, para `dor_peito`: *"A dor no peito é o sintoma primário de alerta para avaliar a hipótese de um Enfarte do Miocárdio"*).

Após exibir a explicação, o sistema **repete a pergunta clínica anterior** sem avançar para o próximo sintoma. O estado de sessão não é modificado: `ultima_pergunta` mantém-se inalterado e `perguntas_feitas` não é atualizado. Desta forma, o utilizador tem oportunidade de responder com contexto adequado.

### 5.3. Persistência Local de Triagens

No P1, a gravação de triagens no ficheiro `triagens.csv` dependia do estado de `facto/2` da sessão Prolog ativa, tornando a persistência inoperante em modo alternativa Python.

Foi implementada a função `salvar_triagem_csv`, que é invocada pelo servidor Python sempre que uma triagem é concluída — independentemente de ter sido realizada pelo motor Prolog ou pelo motor Python. A função converte o dicionário `session["sintomas"]` numa linha binária (0/1 por sintoma), seguindo a mesma ordem de colunas do `triagens.csv` existente, e escreve-a em modo append. A coluna `nivel` recebe o identificador Prolog do nível vencedor (por exemplo, `urgente`, `muito_urgente`), garantindo compatibilidade com o pipeline de treino do Projeto 1 Parte B.

Esta implementação fecha o ciclo de aprendizagem contínua do P1: as sessões do chatbot P2 alimentam o mesmo `triagens.csv` que o pipeline de aprendizagem automática do P1 utiliza para gerar novas regras em `base_conhecimento_b.pl`.

---

## 6. Conclusões

### 6.1. Síntese

O presente projeto materializou-se no desenvolvimento de um chatbot de triagem clínica que integra três paradigmas distintos de inteligência artificial: raciocínio baseado em regras (motor MYCIN em Prolog e Python), recuperação de informação (RAG com TF-IDF) e geração de linguagem natural (LLM Llama 3.2:3b). A solução é uma extensão directa e coerente do Projeto 1 — reutiliza toda a base de conhecimento clínico, o motor de inferência e o pipeline de aprendizagem automática, adicionando uma camada de linguagem natural que torna o sistema acessível a utilizadores sem literacia informática.

A divisão de responsabilidades entre componentes é clara e clinicamente segura: a lógica de inferência é inteiramente controlada pelo motor de regras; o LLM é confinado à dimensão linguística da interação, com filtros que impedem que alucinações comprometam a segurança do resultado. A base de conhecimento foi expandida de 28 para 36 regras, com cobertura de síndromes críticos anteriormente ausentes, e as treze regras de contra-evidência com CF negativo foram substituídas por um mecanismo mais seguro baseado em premissas negadas.

### 6.2. Discussão

A principal tensão identificada no desenvolvimento foi a utilização de um LLM de dimensão reduzida (3B parâmetros) num domínio de alto risco. O modelo Llama 3.2:3b demonstrou ser adequado para a geração de frases empáticas curtas, mas insatisfatório para extração estruturada de sintomas — o que levou à decisão de o excluir do pipeline de deteção em favor de um sistema determinístico baseado em keywords. Esta troca entre generalidade e fiabilidade é uma das tensões centrais na utilização de LLMs de dimensão reduzida em contextos clínicos.

A arquitectura desenvolvida resolve esta tensão de forma pragmática: o LLM é utilizado onde é robusto (geração de linguagem empática) e excluído onde falha (extração de informação clínica estruturada). O resultado é um sistema que combina a naturalidade conversacional de um assistente LLM com a fiabilidade determinística de um sistema especialista baseado em regras.

As principais dificuldades residiram na gestão do estado de sessão em contexto assíncrono — garantir que respostas ambíguas, pedidos de explicação e mensagens não reconhecidas não corrompem o fluxo de triagem — e na calibração dos critérios de disparo da triagem, que devem ser suficientemente sensíveis para não perder emergências mas suficientemente conservadores para não encerrar a conversa prematuramente.

O sistema cumpre a totalidade dos objetivos propostos para o Projeto 2. A integração com o P1 é completa: a base de conhecimento é reutilizada, as triagens do chatbot alimentam o `triagens.csv` do P1, e o servidor Prolog do P1 é o motor primário de inferência quando disponível. O grupo autoavalia o projeto com 18 valores.

### 6.3. Funcionamento do Trabalho em Grupo

O trabalho em grupo decorreu em continuidade natural do Projeto 1, com a mesma distribuição de responsabilidades e o mesmo modelo de colaboração. A definição de interfaces entre componentes no início do desenvolvimento — protocolo de comunicação HTTP, formato das mensagens de sessão, dicionário de sintomas partilhado — permitiu que as quatro frentes avançassem em paralelo com conflitos técnicos mínimos.

As situações que exigiram maior coordenação foram a calibração dos critérios de disparo da triagem, que dependem simultaneamente do estado dos sintomas (componente do Rui) e do contador de trocas da conversa (componente do André), e a filtragem de alucinações do LLM, cujos casos extremos foram identificados durante os testes da interface (componente do João) mas exigiram ajustes na lógica de prompt (também componente do João).

No que respeita à autodiferenciação, o grupo considera que todos os elementos contribuíram de forma ativa e proporcional às responsabilidades atribuídas, pelo que as avaliações individuais propostas são as seguintes:

| Nome | Número | Avaliação Proposta |
|---|---|---|
| Alexandr Tchikoulaev | A103625 | 18 |
| André Pinto | A106825 | 18 |
| João Alves | A102394 | 18 |
| Rui Silva | A106831 | 18 |

---

## Anexo A

**chatbot_server.py** (excerto principal):

```python
"""
P2 - SNS24 Chatbot com RAG + Ollama + Integração MYCIN
Porta: 8081  |  Modelo: llama3.2:3b
RAG: construído automaticamente a partir de base_conhecimento_a.pl + base_conhecimento_b.pl

Iniciar: python chatbot_server.py
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx, json, uuid, re, os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
import uvicorn

app = FastAPI(title="SNS24 Chatbot P2")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

OLLAMA_URL = "http://localhost:11434/api"
MODEL      = "llama3.2:3b"
PROLOG_URL = "http://localhost:8080"

_DIR = os.path.dirname(os.path.abspath(__file__))
KB_A = os.path.join(_DIR, "base_conhecimento_a.pl")
KB_B = os.path.join(_DIR, "base_conhecimento_b.pl")

# ── CLASSE RAG ───────────────────────────────────────────────────────────────

class RAGEngine:
    def __init__(self, docs: list[str]):
        self.docs = docs
        self.vec  = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4),
                                    max_features=8000)
        self.mat  = self.vec.fit_transform(docs) if docs else None

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        if self.mat is None:
            return []
        q   = self.vec.transform([query])
        sim = cosine_similarity(q, self.mat)[0]
        idx = np.argsort(sim)[::-1][:top_k]
        return [self.docs[i] for i in idx if sim[i] > 0.01]

# ── MOTOR MYCIN PYTHON (alternativa ao Prolog) ───────────────────────────────

def triagem_mycin_python(sintomas: dict, regras: list) -> tuple[str, float]:
    scores: dict[str, float] = {}

    def combinar(cf1: float, cf2: float) -> float:
        if cf1 >= 0 and cf2 >= 0:
            return cf1 + cf2 * (1 - cf1)
        if cf1 <= 0 and cf2 <= 0:
            return cf1 + cf2 * (1 + cf1)
        return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)) + 1e-9)

    for r in regras:
        premissas, nivel, cf_regra = r["premissas"], r["nivel"], r["cf"]
        ok = True
        for p in premissas:
            if p.startswith("nao("):
                s = p[4:-1]
                if sintomas.get(s) == "sim":
                    ok = False; break
            else:
                if sintomas.get(p) != "sim":
                    ok = False; break
        if ok:
            scores[nivel] = combinar(scores.get(nivel, 0.0), cf_regra)

    ORDEM = ["emergencia", "muito_urgente", "urgente",
             "pouco_urgente", "sem_sintomas_alarme"]
    for nivel in ORDEM:
        if scores.get(nivel, 0) > 0:
            return nivel, round(scores[nivel] * 100, 1)
    return "sem_sintomas_alarme", 0.0

# ── ALGORITMO DE SELEÇÃO DA PRÓXIMA PERGUNTA ─────────────────────────────────

def calcular_proximo_sintoma(sintomas: dict, regras: list,
                              perguntas_feitas: set) -> Optional[str]:
    scores: dict[str, float] = {}
    tem_confirmado = any(v == "sim" for v in sintomas.values())

    for r in regras:
        premissas, cf = r["premissas"], r["cf"]
        pos = [p for p in premissas if not p.startswith("nao(")]
        neg = [p[4:-1] for p in premissas if p.startswith("nao(")]

        eliminada = any(sintomas.get(s) == "nao" for s in neg
                        if sintomas.get(s) == "sim")
        eliminada = eliminada or any(sintomas.get(s) == "sim"
                                     for s in neg)
        if eliminada:
            continue

        confirmadas = sum(1 for s in pos if sintomas.get(s) == "sim")
        desconhecidos = [s for s in pos
                         if sintomas.get(s) is None
                         and s not in perguntas_feitas]
        if not desconhecidos:
            continue

        if confirmadas == 0 and tem_confirmado:
            peso = cf * 0.2
        else:
            peso = cf * (2 ** confirmadas)

        for s in desconhecidos:
            scores[s] = scores.get(s, 0) + peso

    if not scores:
        return None
    return max(scores, key=scores.__getitem__)
```

---

## Anexo B

**base_conhecimento_a.pl** (regras novas adicionadas no P2):

```prolog
% ----------------------------------------------------------------
% NOVOS SINTOMAS (adicionados no P2)
% ----------------------------------------------------------------
sintoma(rigidez_nuca,        'Rigidez da nuca — nao consegue encostar o queixo ao peito').
sintoma(rash_petequial,      'Manchas vermelhas ou roxas na pele que nao desaparecem a pressao').
sintoma(reacao_alergica_grave,'Reacao alergica grave com inchaco da face, lingua ou garganta').
sintoma(dor_cabeca_subita,   'Dor de cabeca muito intensa de inicio subito — "pior da vida"').
sintoma(visao_alterada,      'Alteracao subita da visao num ou ambos os olhos').


% NOVAS REGRAS DE EMERGENCIA
regra(r_em8,  se([resp_dificuldade, febre_alta]),         entao(emergencia),    0.87).
regra(r_em9,  se([febre_alta, rigidez_nuca]),             entao(emergencia),    0.92).
regra(r_em10, se([febre_alta, rash_petequial]),           entao(emergencia),    0.95).
regra(r_em11, se([resp_dificuldade, reacao_alergica_grave]), entao(emergencia), 0.93).

% NOVAS REGRAS DE MUITO URGENTE
regra(r_mu10, se([confusao, febre_alta, nao(dor_abd)]),  entao(muito_urgente), 0.85).
regra(r_mu11, se([reacao_alergica_grave]),                entao(muito_urgente), 0.80).
regra(r_mu12, se([dor_cabeca_subita]),                   entao(muito_urgente), 0.85).
regra(r_mu13, se([visao_alterada, fala_dificil]),         entao(muito_urgente), 0.90).

% NOVAS REGRAS DE URGENTE (quadros GI e pediátricos)
regra(r_ur10, se([vomitos, nao(diarreia)]),                         entao(urgente),       0.60).
regra(r_ur11, se([dor_garganta, febre_alta]),                       entao(urgente),       0.75).
regra(r_ur12, se([febre_bebe, vomitos, nao(diarreia)]),             entao(muito_urgente), 0.80).
regra(r_ur13, se([diarreia, nao(vomitos)]),                         entao(urgente),       0.55).
regra(r_ur14, se([visao_alterada]),                                 entao(urgente),       0.60).

% NOVAS REGRAS DE POUCO URGENTE (anti-sobreavaliação)
regra(r_pu5, se([constipacao, dor_garganta, nao(febre_alta)]),      entao(pouco_urgente), 0.72).
regra(r_pu6, se([febre_baixa, mal_estar, nao(dor_abd)]),            entao(pouco_urgente), 0.68).
regra(r_pu7, se([constipacao, dor_persiste, nao(febre_alta)]),      entao(pouco_urgente), 0.65).

% REGRAS MODIFICADAS (adicionada condição nao(constipacao))
% r_ur5: versão original era se([dor_persiste])
regra(r_ur5, se([dor_persiste, nao(constipacao)]),   entao(urgente), 0.40).
% r_ur6: versão original era se([dor_garganta])
regra(r_ur6, se([dor_garganta, nao(constipacao)]),   entao(urgente), 0.55).

% ORDEM DE QUESTIONAMENTO ATUALIZADA (inclui 5 novos sintomas)
ordem_sintomas([
    sem_respiracao, sem_pulso, resp_dificuldade, hemorragia, inconsciente,
    convulsoes, reacao_alergica_grave,
    dor_peito, dor_irradia, fala_dificil, fraqueza_lado,
    visao_alterada, dor_cabeca_subita,
    febre_alta, rigidez_nuca, rash_petequial,
    confusao, dor_abd, febre_bebe,
    tosse_febre, dor_persiste, vomitos, diarreia,
    dor_garganta, constipacao, dor_leve, febre_baixa, mal_estar
]).
```

---

## Bibliografia

[1] Shortliffe, E.H. (1976). *Computer-Based Medical Consultations: MYCIN*. Elsevier.

[2] Russell, S. e Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4.ª ed.). Pearson.

[3] SNS24 (2024). *Protocolos de Triagem Altitude — Fluxogramas de Sintomas*. Serviço Nacional de Saúde.

[4] Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

[5] Witten, I.H., Frank, E. e Hall, M.A. (2011). *Data Mining: Practical Machine Learning Tools and Techniques* (3.ª ed.). Morgan Kaufmann.

[6] Covington, M.A. (1994). *Natural Language Processing for Prolog Programmers*. Prentice Hall.

[7] Meta AI (2024). *Llama 3.2: Multilingual Large Language Models*. Meta AI Research.

[8] Ollama (2024). *Ollama — Run Large Language Models Locally*. Documentação oficial em https://ollama.com.

[9] FastAPI (2024). *FastAPI — Modern, Fast Web Framework for Building APIs with Python*. Documentação oficial em https://fastapi.tiangolo.com.
