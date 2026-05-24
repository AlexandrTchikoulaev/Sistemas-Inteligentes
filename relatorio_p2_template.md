ºs



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












Índice
Índice	3
1. Introdução	1
1.1 Enquadramento	1
1.2 Objetivos	1
2. Execução do Projeto	2
2.1 Diagrama de Gantt	2
2.2 Distribuição de Trabalho	2
2.2.1 André Pinto	3
2.2.2 Alexandr Tchikoulaev	4
2.2.3 João Alves	5
2.2.4 Rui Silva	6
3. Evolução da Base de Conhecimento	7
3.1 Enquadramento e Motivação	7
3.2  Novos Sintomas	7
3.3 Novas Regras de Emergência	7
3.4 Novas Regras de Muito Urgente	8
3.5 Novas Regras para Quadros Pediátricos	8
3.6 Novas Regras de Pouco Urgente	9
3.7 Modificação de Regras Existentes	9
3.8 Remoção das Regras de Contra-Evidência (CF Negativos)	10
3.9 Atualização da Ordem de Questionamento	10
4. Sistema de Chatbot SNS24	11
4.1 Arquitetura do Sistema	11
4.2 Base de Conhecimento e Módulo RAG	11
4.3 Deteção de Sintomas	12
4.4 Motor de Inferência MYCIN	13
4.5 Gestão da Conversa	14
4.6 Geração de Linguagem Natural com LLM	15
4.7 Interface Web	16
5. Funcionalidades Avançadas	18
5.1 Garantia de Segurança Clínica	18
5.2 Intercepção de Pedidos de Explicação	18
5.3 Persistência Local de Triagens	18
6. Conclusões	19
6.1 Síntese	19
6.2 Discussão	19
6.3 Funcionamento do Trabalho em Grupo	20
Anexo A	21
base_conhecimento_a.pl:	21
chatbot_server.py:	31
chatbot.html:	72
exportar_kb.py:	92
kb_chatbot.txt:	93
Anexo B	101
Bibliografia	103


1. Introdução
1.1 Enquadramento
Este projeto foi desenvolvido pelo Grupo 4 no âmbito da unidade curricular de Sistemas Inteligentes de Apoio à Decisão da Licenciatura em Ciência de Dados na Universidade do Minho.
O Projeto 2 tem como objetivo estender o Sistema Baseado em Conhecimento desenvolvido no Projeto 1, ao acrescentar uma camada de interação em linguagem natural sob a forma de chatbot conversacional.
O sistema integra o LLM Llama 3.2, executado localmente através da plataforma Ollama, com a técnica de Retrieval-Augmented Generation e com o motor de inferência MYCIN em Prolog do Projeto 1. A integração com o P1 é direta: a base de conhecimento em Prolog é reutilizada tanto para alimentar o módulo RAG como para alimentar o motor de inferência.
O sistema é uma extensão natural do trabalho anterior, com uma camada de linguagem natural e um motor de diálogo estruturado que permite ao utilizador descrever os seus sintomas de forma coerente.
A pertinência desta abordagem no contexto do SNS24 é imediata: uma interface conversacional reduz a barreira de utilização relativamente ao formulário estruturado do Projeto 1, tornando o sistema acessível a utilizadores sem literacia informática e o uso de um LLM local garante que nenhum dado clínico do utilizador abandona o dispositivo.
1.2 Objetivos
O principal objetivo deste projeto é desenvolver um chatbot de triagem médica que permita ao utilizador descrever os seus sintomas em linguagem natural e receber no final da conversa o resultado da triagem com o nível de urgência e a recomendação clínica.
De forma mais específica, pretende-se:
Construir um módulo RAG que indexe automaticamente toda a base de conhecimento Prolog para suporte à geração de respostas pelo LLM;
Desenvolver um motor de diálogo estruturado que seleciona de forma dinâmica as perguntas mais informativas de forma a colocar em cada turno da conversa;
Integrar o motor MYCIN do P1 (Prolog) com um motor MYCIN equivalente em Python;
Criar uma interface web conversacional moderna que apresente o resultado de triagem de forma clara e justificada.
2. Execução do Projeto
2.1 Diagrama de Gantt

figura 1: Diagrama de Gantt do Projeto 2
2.2 Distribuição de Trabalho
A execução deste projeto decorreu em continuidade do Projeto 1, o que permitiu ao grupo partir de uma base técnica consolidada para distribuir o trabalho em função às competências demonstradas na primeira fase.
A estratégia adotada foi de manter a mesma divisão por especialização: cada elemento assumiu a responsabilidade pelas componentes diretamente relacionadas com o seu contributo no P1, garantindo continuidade e coerência técnica.
Tal como anteriormente, o sucesso do sistema depende da integração constante entre as diferentes frentes de desenvolvimento. O motor de diálogo, o RAG, o LLM e a interface web avançaram em paralelo, mas exigiram sincronização frequente para garantir compatibilidade de interfaces e coerência clínica dos resultados.

2.2.1 André Pinto
O meu contributo no Projeto 2 centrou-se na evolução da base de conhecimento clínico, que no Projeto 1 tinha ficado implementada com vinte e oito regras e vinte e três sintomas. A análise dos casos de teste utilizados durante o desenvolvimento do P1 mostrou que poderiam ser adicionados vários cenários importantes na base de conhecimento original. 
Para suprir estas lacunas, adicionei cinco novos sintomas à base, que permitiram formular quatro novas regras de emergência e quatro novas regras de muito urgente. Acrescentei também cinco regras que permitem distinguir de forma correta situações com vómitos, diarreia ou ambos os sintomas ao mesmo tempo. Esta separação é importante porque cada situação pode apresentar diferentes riscos de desidratação e exigir cuidados diferentes.
Além disso, adicionei três regras classificadas como pouco urgente para evitar que casos virais simples fossem avaliados com prioridade demasiado elevada, algo que acontecia frequentemente nos testes informais realizados ao P1. Modifiquei ainda duas regras existentes para incluir condições de negação que corrigiam resultados incorretos no contexto da constipação. 
A decisão com maior impacto foi a remoção integral das treze regras de contra-evidência com CF negativo que a versão original continha. Estas regras introduziram um risco de segurança clínica inaceitável: em teoria, a presença de um sintoma como mal_estar poderia reduzir o CF de emergência de um doente com paragem respiratória. As novas regras com premissas nao(x) cumprem a mesma função de diferenciação clínica de forma positiva e controlada.
Por fim, atualizei o predicado ordem_sintomas/1 para incluir os cinco novos sintomas nas posições adequadas, de modo a que o motor Prolog do P1 os questione na sequência clinicamente correta.
Código desenvolvido:
base_conhecimento_a.pl - expansão de 28 para 36 regras, adição de 5 sintomas, remoção de 13 contra-evidências, modificação de r_ur5/r_ur6, atualização de ordem_sintomas/1.

2.2.2 Alexandr Tchikoulaev
A minha participação no Projeto centrou-se no desenvolvimento do módulo RAG, que constitui a espinha dorsal da integração entre o conhecimento clínico formalizado em Prolog e o modelo de linguagem.
Após ser definida a arquitetura de quatro componentes - servidor Python (FastAPI), modelo LLM (Ollama), motor Prolog (P1) e interface web - e o protocolo de comunicação entre eles, que garantiu a independência entre a lógica clínica e a camada de linguagem (o LLM nunca tem acesso direto ao motor de inferência, sendo o resultado clínico sempre determinado pelo MYCIN) desenvolvi o parser Prolog. Este sistema atua no arranque do servidor e lê automaticamente os ficheiros base_conhecimento_a.pl e base_conhecimento_b.pl e extrai as quatro estruturas de dados necessárias: sintomas, níveis de triagem, regras de produção e explicações. A partir destas estruturas, implementei a construção automática da coleção de documentos RAG em linguagem natural composta por três grupos de documentos (protocolo geral SNS24, uma entrada por regra de produção, grupos de sintomas por gravidade) e o motor TF-IDF com análise de n-gramas de caráter que indexa e recupera os documentos mais relevantes para cada mensagem do utilizador. A escolha de n-gramas de caráter, em vez de palavras completas, conferiu robustez a variações ortográficas, abreviaturas e erros de escrita, frequentes na linguagem natural clínica em português.
Código desenvolvido:
chatbot_server.py - parser Prolog (_extrair_mapa, parse_rules_pl), construção dos documentos RAG (_build_rag_docs), classe RAGEngine (vectorizador TF-IDF, método retrieve)
2.2.3 João Alves
A minha participação centrou-se no desenvolvimento da camada de interação com o utilizador, tanto a interface web do chatbot como a integração com o modelo de linguagem e na funcionalidade de intercepção de pedidos de explicação.
Desenvolvi o frontend chatbot.html como uma Single Page Application em HTML, CSS e JavaScript puro, sem dependências externas. A interface apresenta um painel de chat à esquerda e um painel lateral de diagnóstico à direita, que exibe em tempo real os sintomas já detetados na sessão (marcados como presentes ou ausentes), o status de ligação ao modelo Ollama e o resultado final de triagem com o respetivo nível de urgência codificado por cor. A comunicação com o servidor é feita de forma assíncrona através de dois endpoints principais.
No que respeita ao LLM, implementei os três tipos de prompts utilizados pelo sistema: o prompt de reconhecimento contextual intercalar, que gera uma frase empática de transição antes de cada pergunta clínica; o prompt de introdução ao resultado final, que enquadra emocionalmente o diagnóstico sem o antecipar; e a lógica de pós-processamento que filtra alucinações, corrige pronomes para o registo formal do português europeu, remove referências clínicas proibidas e omite respostas desnecessariamente longas. Implementei também a funcionalidade de interseção de pedidos de explicação, que deteta intenções como "porque precisas de saber?" e responde com a justificação clínica do sintoma antes de repetir a pergunta.
Código desenvolvido:
chatbot.html - interface web completa (chat, painel de diagnóstico, comunicação assíncrona)
chatbot_server.py - funções gerar_acknowledgment, gerar_intro_resultado, pós-processamento LLM, e_intencao_porque, gestão do endpoint /api/chat/message para pedidos de explicação

2.2.4 Rui Silva
A minha contribuição no Projeto 2 centrou-se nas componentes de inferência clínica e de deteção de sintomas, as duas componentes que determinam diretamente a qualidade e segurança do resultado da triagem.
Desenvolvi o sistema de deteção de sintomas por keywords, que cobre 28 sintomas com múltiplas expressões equivalentes em português corrente para cada um, incluindo variantes com e sem acentuação e formulações coloquiais. Implementei a deteção de negações por janela de contexto, a aplicação de exclusões mútuas para garantir consistência lógica entre sintomas relacionados, e a classificação de respostas como confirmação, negação ou incerta através da função e_resposta_simples, incluindo intensificadores absolutos e respostas qualificadas com conjunções adversativas.
Implementei o motor MYCIN em Python como alternativa ao servidor Prolog do P1, avaliando todas as regras da base de conhecimento carregada em memória com a fórmula de combinação de CFs compatível com o MYCIN original. Desenvolvi o algoritmo de seleção dinâmica da próxima pergunta, que calcula um score exponencial CF 2nconfirmadas para cada sintoma desconhecido em cada regra ativa, favorecendo a conclusão de regras com evidências parciais. Implementei os critérios de disparo da triagem e a salvaguarda de segurança clínica que garante que o nível mais grave entre o Prolog e o Python é sempre o resultado reportado. Implementei também a persistência automática de triagens em triagens.csv independentemente da disponibilidade do servidor Prolog.
Código desenvolvido:
chatbot_server.py - SINTOMAS_KEYWORDS, extrair_sintomas_keywords, e_resposta_simples, e_resposta_incerta, triagem_mycin_python, calcular_proximo_sintoma, calcular_scores_sessao, critérios de triagem, salvar_triagem_csv


3. Evolução da Base de Conhecimento
3.1 Enquadramento e Motivação
No contexto do Projeto 2, a base de conhecimento foi revista e expandida relativamente à versão entregue no Projeto 1. As alterações têm dois objetivos: aumentar a cobertura clínica do sistema para padrões de doenças que a versão original não detetava e tornar o raciocínio mais preciso, ao remover mecanismos que se revelaram problemáticos durante os testes.
A versão original continha vinte e oito regras de produção, vinte e três sintomas e treze regras de contra-evidência com CF negativo. A análise dos casos de teste durante o desenvolvimento do chatbot revelou várias situações graves que não estavam representadas na base de conhecimento original. Além disso foram identificadas regras que podiam gerar respostas contraditórias que poderiam criar riscos na avaliação dos casos, no qual a nova arquitetura permitiu eliminar esse problema de forma segura. 
3.2  Novos Sintomas
Foram adicionados cinco sintomas que não existiam na versão original:
            Identificador
                                Descrição
            rigidez_nuca
Rigidez da nuca - não consegue encostar o queixo ao peito.
           rash_petequial
Manchas vermelhas ou roxas na pele que não desaparecem à pressão.
    reacao_alergica_grave
Reação alérgica grave com inchaço da face, língua ou garganta.
       dor_cabeca_subita
Dor de cabeça muito intensa de início súbito - "pior da vida".
            visao_alterada
Alteração súbita da visão num ou ambos os olhos.

Estes sintomas cobrem quatro síndromes de alto risco que ficavam sem representação. A sua adição foi necessária para que as novas regras de emergência e muito urgentes que foram descritas nas secções seguintes para que pudessem ser formuladas.
3.3 Novas Regras de Emergência
Foram acrescentadas quatro regras de emergência que combinam sintomas em padrões clínicos:
  Regra
                     Premissas
 CF
          Justificação clínica
  r_em8
         resp_dificuldade + febre_alta
0.87
Suspeita de pneumonia grave ou sépsis respiratória com risco de falência iminente.
  r_em9
           febre_alta + rigidez_nuca
0.92
Padrão clássico de meningite bacteriana - emergência neurológica.
  r_em10
           febre_alta + rash_petequial
0.95
Sinal de alerta de meningococcemia - progressão para choque em horas.
  r_em11
resp_dificuldade + reacao_alergica_grave
0.93
Anafilaxia com compromisso da via aérea - 
requer adrenalina e 112.

O CF elevado destas regras reflete a sua alta especificidade: cada combinação de sintomas aponta para um único quadro clínico com risco de vida imediato, o que justifica a adoção de um nível de confiança próximo da certeza máxima.
3.4 Novas Regras de Muito Urgente
Quatro novas regras foram adicionadas ao nível muito urgente, que cobrem padrões neurológicos e cardiológicos que a versão original não continha:
  Regra
Premissas
CF
                Justificação clínica
r_mu10
confusao + febre_alta + nao(dor_abd)
0.85
Padrão de meningite/encefalite - sem dor abdominal afasta sépsis (r_em6).
r_mu11
          reacao_alergica_grave
0.80
Pode evoluir para anafilaxia - requer avaliação 
hospitalar imediata.
r_mu12
             dor_cabeca_subita
0.85
Sinal clássico de hemorragia subaracnoideia por rotura
de aneurisma.
r_mu13
       visao_alterada + fala_dificil
0.90
Padrão BE-FAST completo de AVC - alta certeza diagnóstica.

A regra r_mu10 é particularmente relevante do ponto de vista do raciocínio: introduz a negação de dor_abd como premissa para distinguir entre regras. Sem esta distinção, um doente com confusão e febre mas sem dor abdominal não teria um resultado correto.
3.5 Novas Regras para Quadros Pediátricos
Foram acrescentadas cinco regras que refinam a triagem de quadros gastrointestinais e pediátricos:
Regra
            Premissas
CF
       Nível
                  Justificação
r_ur10
vomitos + nao(diarreia)
0.60
     Urgente
Desidratação por via gástrica isolada - pode exigir reposição IV.
r_ur11
dor_garganta + febre_alta
0.75
     Urgente
Suspeita de amigdalite bacteriana com risco de abscesso.
r_ur12
febre_bebe + vomitos + nao(diarreia)
0.80
Muito Urgente
Bebé com reservas limitadas - risco de desidratação rápida.
r_ur13
diarreia + nao(vomitos)
0.55
     Urgente
Diarreia grave implica desidratação; sem vómitos há margem 
para hidratação oral vigiada.
r_ur14
visao_alterada
0.60
     Urgente
AVC, glaucoma agudo ou oclusão retiniana - risco de cegueira permanente.

A lógica comum a r_ur10/r_ur13 e a r_ur12 é a separação das vias de perda de líquidos: vómitos e diarreia em simultâneo já tinham regra própria; as novas regras cobrem os casos onde apenas uma das vias está comprometida, de forma a garantir a triagem adequada, mesmo nesses cenários.
3.6 Novas Regras de Pouco Urgente
Foram adicionadas três regras que servem para evitar a sobreavaliação de quadros virais benignos:
Regra
         Premissas
CF
                        Justificação
r_pu5
constipacao + dor_garganta + nao(febre_alta)
0.72
Quadro viral típico - dor de garganta no contexto 
de constipação sem febre alta não justifica urgência.
r_pu6
febre_baixa + mal_estar + nao(dor_abd)
0.68
Infeção viral autolimitada - a ausência de dor abdominal 
afasta complicações.
r_pu7
constipacao + dor_persiste + nao(febre_alta)
0.65
Cefaleia/mialgia gripal - dor que não cede no contexto
de constipação é gripal, não urgência.

Estas regras interagem diretamente com as modificações às regras r_ur5 e r_ur6, descritas na secção seguinte: em conjunto criam caminhos de raciocínio que diferenciam o mesmo sintoma consoante o contexto clínico.
3.7 Modificação de Regras Existentes
Duas regras foram modificadas para adicionar condições de negação que corrigiam classificações incorretas:
r_ur5 - Dor persistente:
Versão original: se([dor_persiste]) → urgente (CF 0.40);
Versão atual: se([dor_persiste, nao(constipacao)]) → urgente (CF 0.40).
Sem esta modificação, uma cefaleia ou uma mialgia gripal que não cedia ao paracetamol era classificada como urgente. O contexto de constipação indica que a dor tem origem viral e não requer consulta de urgência.
r_ur6 - Dor de garganta:
Versão original: se([dor_garganta]) → urgente (CF 0.55);
Versão atual: se([dor_garganta, nao(constipacao)]) → urgente (CF 0.55).
Analogamente, a dor de garganta isolada deve ser urgente apenas quando não está inserida num quadro de constipação. Com constipação, a regra r_pu5 classifica-a como pouco urgente se não houver febre alta. Sem a condição nao(constipacao) em r_ur6, as duas regras disputavam o mesmo caso e o motor reportava urgente por ter um CF mais alto.
3.8 Remoção das Regras de Contra-Evidência (CF Negativos)
A versão original continha treze regras com CF negativo que penalizavam os níveis mais graves quando sintomas leves estavam presentes. Por exemplo, a presença de dor_leve reduzia o CF de emergência em 0.70 e o de muito urgente em 0.55.
Estas regras foram integralmente removidas por duas razões:
Segurança clínica: Um CF negativo pode em teoria baixar o resultado final abaixo de um limiar e esconder uma emergência real. Se, por exemplo, um doente tem uma paragem respiratória (r_em1, CF 0.95) mas menciona também que tem um ligeiro mal-estar (r_c_em4, CF −0.45), a fórmula MYCIN combinaria os dois valores e o resultado de emergência seria atenuado este comportamento é clinicamente inaceitável;
Substituição por condições negadas: As regras com premissas nao(x) cumprem a mesma função de forma segura e explícita. Em vez de penalizar um nível grave quando um sintoma leve está presente, as regras agora só disparam para um nível leve quando a ausência de sintomas graves é confirmada. O raciocínio é positivo e controlado, não subtrativo.
3.9 Atualização da Ordem de Questionamento
O predicado ordem_sintomas/1, que define a sequência de perguntas no motor Prolog do P1, foi atualizado para incluir os cinco novos sintomas nas posições adequadas:
reacao_alergica_grave foi inserida imediatamente após convulsoes;
visao_alterada e dor_cabeca_subita foram colocadas após os sinais de AVC clássicos para completar o rastreio neurológico antes de passar para sintomas de menor gravidade;
rigidez_nuca e rash_petequial foram colocados após a febre_alta porque a sua relevância clínica depende da presença de febre e a combinação deve ser avaliada em sequência.
4. Sistema de Chatbot SNS24
4.1 Arquitetura do Sistema
O sistema é composto por quatro componentes principais que comunicam entre si:
                    Componente
Tecnologia
Porta
Servidor de chatbot (backend Python)
FastAPI + Uvicorn
8081
Modelo de linguagem (LLM)
Ollama / Llama 3.2:3b
11434
Motor MYCIN em Prolog (P1)
Servidor HTTP Prolog
8080
Interface Web (frontend)
HTML/CSS/JS
   -

O fluxo de uma sessão de triagem é o seguinte:
O utilizador abre a interface web e inicia uma sessão via POST /api/chat/start, que devolve um identificador único de sessão;
Cada mensagem do utilizador é enviada via POST /api/chat/message. O servidor Python processa a mensagem: deteta sintomas, decide a próxima pergunta a fazer ou se é hora de realizar a triagem formal, e gera uma resposta em linguagem natural com o auxílio do LLM;
Quando os critérios de triagem são atingidos, o servidor tenta delegar ao motor MYCIN Prolog. Caso este não esteja disponível, um motor MYCIN equivalente implementado em Python é utilizado como alternativa;
O resultado final é formatado e enviado ao utilizador.
O servidor Python é também proxy do servidor Prolog, expondo os seus endpoints (/api/start, /api/answer, /api/validate) de modo a que o frontend possa comunicar com ambos através da mesma origem.
A divisão de responsabilidades entre os componentes é clara e intencional: a lógica clínica e de inferência é inteiramente controlada pelo motor de regras e pela base de conhecimento Prolog; o LLM é confinado à dimensão linguística da interação, com filtros que impedem que eventuais alucinações comprometam a segurança do resultado.
4.2 Base de Conhecimento e Módulo RAG
No arranque do servidor, os ficheiros base_conhecimento_a.pl e base_conhecimento_b.pl são lidos e analisados via expressões regulares. São extraídas quatro estruturas de dados:
Sintomas - sintoma(id, 'Descrição'): mapeamento de identificadores Prolog para descrições em linguagem natural;
Níveis de triagem - nivel(id, 'Nome', 'Recomendação'): os cinco níveis do protocolo SNS24 (Emergência, Muito Urgente, Urgente, Pouco Urgente, Sem Alarme);
Regras de produção - regra(id, se([premissas]), entao(nivel), CF): a base de conhecimento completa com fatores de certeza;
Explicações - explicacao_regra(id, 'Texto') e explicacao(sintoma, 'Texto'): texto clínico associado a cada regra e sintoma.
A partir dos dados extraídos, é construída uma coleção de documentos em linguagem natural simples, otimizados para serem interpretados por um LLM de 3B parâmetros. Cada documento segue o formato:
[condição(ões)] → [nível]. [O que fazer]. [Porquê - primeira frase da explicação clínica].
São gerados três grupos de documentos:
Protocolo geral - uma descrição dos cinco níveis SNS24 e das respetivas ações recomendadas;
Uma entrada por regra de produção (partes A e B) - as premissas são traduzidas para linguagem natural; negações (nao(x)) são expressas como "sem X"; as regras da Parte B são marcadas como [padrão aprendido automaticamente];
Grupos de sintomas por gravidade - listas dos sintomas típicos de cada nível, com a respetiva explicação clínica resumida.
A coleção resultante contém tipicamente entre 60 e 80 documentos.
O módulo RAG é implementado com a classe RAGEngine, que utiliza um vectorizador TF-IDF com análise de n-gramas de caráter, com um vocabulário máximo de 8 000 características. A escolha de n-gramas de caráter, em vez de palavras completas, confere robustez a variações ortográficas, abreviaturas e erros de escrita, frequentes na linguagem natural clínica em português.
A recuperação é feita por similaridade de cosseno entre o vetor da consulta e a matriz de documentos. São devolvidos os top_k=5 documentos com similaridade superior a 0.01. O contexto recuperado é injetado nos prompts enviados ao LLM quando este é chamado para gerar respostas livres contextuais.
4.3 Deteção de Sintomas
A deteção de sintomas na mensagem do utilizador é feita através de um dicionário de keywords que cobre 28 sintomas. Para cada sintoma, são definidas múltiplas expressões equivalentes em português corrente, incluindo variantes com e sem acentuação e formulações coloquiais. Por exemplo, dor_peito é detetado por expressões como "dor no peito", "aperto no peito", "pressão no peito", "dor torácica", "peito a doer", entre outras.
A deteção de negações é feita por análise de contexto: para cada keyword encontrada no texto, é inspecionada uma janela de 35 carateres anteriores à ocorrência. Se essa janela contiver palavras de negação ("não", "sem", "nunca", "ausência de"), o sintoma é marcado como ausente em vez de presente.
Este sistema determinou a decisão de desativar o LLM para a tarefa de extração de sintomas: o sistema de keywords demonstrou ser mais fiável e determinístico, enquanto o modelo Llama 3.2:3b gerava frequentemente sintomas não presentes no texto, confundia negações, ou devolvia JSON malformado.
Embora exista uma função extrair_sintomas_llm que envia ao Ollama um prompt pedindo a identificação de sintomas em formato JSON, esta função não é invocada durante o fluxo normal. A propensão do modelo Llama 3.2:3b para alucinações em tarefas de extração estruturada desde a geração de sintomas não presentes no texto, confusão de negações e JSON malformado, tornou o sistema de keywords significativamente mais robusto para este contexto de domínio especializado.
Após a deteção de novos sintomas, é aplicada uma etapa de consistência lógica. O sistema define pares de sintomas mutuamente exclusivos: a confirmação de febre_alta (>39 °C) implica automaticamente a negação de febre_baixa (<38 °C), e vice-versa. Desta forma evita-se que a base de sintomas da sessão contenha contradições que comprometam a avaliação das regras.
4.4 Motor de Inferência MYCIN
O motor MYCIN foi originalmente implementado em Prolog no P1. Para garantir que o chatbot funciona mesmo quando o servidor Prolog não está disponível, foi desenvolvida uma implementação equivalente em Python.
O motor avalia todas as regras da base de conhecimento carregada em memória. Para cada regra, verifica se todas as premissas estão satisfeitas pelo conjunto de sintomas confirmados na sessão: premissas positivas requerem que o sintoma esteja marcado como presente; premissas negativas requerem que o sintoma esteja ausente ou não confirmado.
Quando uma regra dispara, o seu fator de certeza é combinado com o CF já acumulado para o mesmo nível, usando a fórmula padrão MYCIN:
CFcombinado=CF1+CF2(1-CF1)
Esta fórmula garante que a combinação de múltiplas evidências independentes aumenta progressivamente a certeza sem ultrapassar 1. No final, o nível mais grave que disparou é o resultado reportado, com o respectivo CF final expresso em percentagem.
Quando o servidor Prolog está disponível na porta 8080, o chatbot delega-lhe a triagem formal. O protocolo de comunicação é o mesmo definido no P1: o servidor Python envia POST /api/start para iniciar uma sessão Prolog, e responde iterativamente às perguntas do motor MYCIN Prolog enviando POST /api/answer com o valor ("sim" ou "nao") para cada sintoma, até o Prolog devolver um resultado.
4.5 Gestão da Conversa
Cada sessão é identificada por um UUID e mantém em memória o seguinte estado:
sintomas - dicionário {id_sintoma: "sim" | "nao"} com todos os sintomas avaliados;
history - lista de mensagens da conversa (papel + conteúdo);
ultima_pergunta - sintoma sobre o qual foi feita a última pergunta, para mapear corretamente respostas do tipo "sim"/"não" sem que o utilizador repita o nome do sintoma;
perguntas_feitas - conjunto de sintomas já perguntados. Um sintoma é adicionado a este conjunto apenas depois de o utilizador responder de forma clara, não no momento em que a pergunta é seleccionada. Esta distinção evita que uma mensagem não reconhecida "queime" um sintoma antes de o utilizador ter tido oportunidade de responder;
triagem_feita - booleano que impede que a triagem seja executada mais de uma vez;
n_trocas - contador de turnos de conversa;
Para decidir a próxima pergunta, o sistema não segue uma ordem fixa de perguntas. Em vez disso, a função calcular_proximo_sintoma escolhe dinamicamente o sintoma mais informativo a perguntar a seguir, tendo em conta o estado atual da sessão e as regras da base de conhecimento.
Para cada regra ainda ativa ou seja, que não foi eliminada por uma premissa falsa e com pelo menos uma premissa desconhecida, é calculado um score para cada sintoma desconhecido:
score=CFregra2nconfirmadas
onde nconfirmadas é o número de premissas da regra já confirmadas. O expoente cria um peso exponencial que favorece fortemente a conclusão de regras com evidências parciais em detrimento de abrir novas regras sem qualquer confirmação. Para regras cujas premissas estão todas por descobrir e já existe pelo menos um sintoma confirmado na sessão, o peso é reduzido a CF0.2, de modo a que uma regra em curso não seja interrompida por uma regra mais genérica com CF elevado.
O sintoma com o score acumulado mais alto entre todas as regras ativas é selecionado, excluindo os sintomas já perguntados.
A triagem formal é desencadeada quando se verifica uma das seguintes condições:
Está presente pelo menos um sintoma de emergência individual (sem_respiracao, sem_pulso, resp_dificuldade, hemorragia, inconsciente, convulsoes);
Uma regra de emergência está completamente satisfeita pelos sintomas confirmados. Neste caso é aplicado um early-exit absoluto: a triagem é desencadeada de imediato, sem calcular a próxima pergunta clínica nem atualizar ultima_pergunta ou perguntas_feitas. Este mecanismo separa-se explicitamente do fluxo normal para garantir que nenhuma pergunta adicional seja colocada quando já existe uma emergência confirmada;
Foram feitas 6 ou mais trocas e há pelo menos 4 sintomas avaliados;
Para sintomas urgentes, a triagem dispara quando há 5 ou mais sintomas avaliados e pelo menos 3 trocas de conversa, desde que nenhuma regra de emergência tenha ainda premissas por descobrir.
De modo a tratar respostas ambíguas, a função e_resposta_simples classifica cada mensagem como True, False ou None. São reconhecidas variantes coloquiais de "sim" e "não" em português, incluindo expressões como "pois", "claro", "exatamente", "efetivamente" ou "negativo".
Respostas qualificadas como "tenho febre, mas não acima de 39 graus" são identificadas pela presença de conjunções adversativas após um confirmador, sendo classificadas como incertas para evitar mapeamentos incorretos. O vocabulário de confirmações foi também estendido com intensificadores absolutos: respostas como "muito", "bastante", "definitivamente", "absolutamente", "sem dúvida" são mapeadas diretamente como True sem recorrer ao LLM, com latência nula.
Quando a resposta é incerta, o sintoma não é registado, mas é adicionado ao conjunto perguntas_feitas.
4.6 Geração de Linguagem Natural com LLM
O LLM utilizado é o Llama 3.2:3b, executado localmente via Ollama. É um modelo compacto de 3B parâmetros, adequado para execução em hardware de consumo sem GPU dedicada. A temperatura é fixada em 0.1 para minimizar a variabilidade e reduzir o risco de alucinações. O número máximo de tokens gerados é limitado por caso de uso: 25 tokens para frases de reconhecimento intercalar, 35 tokens para a transição antes de uma pergunta clínica.
O LLM não é usado para inferência clínica nem para extração de sintomas. O seu papel é exclusivamente linguístico: tornar a conversa mais natural e empática, sem influenciar a lógica de triagem.
Em cada turno de conversa, antes de colocar a próxima pergunta clínica, o LLM gera um breve reconhecimento contextual. O prompt descreve a situação do turno anterior (por exemplo, "o utilizador confirmou 'Febre alta (>39°C)'" ou "o utilizador não tem certeza sobre 'Dor no peito'") e pede uma frase empática de transição no registo formal do português europeu.
O formato de saída esperado é fixo: [frase empática]. [palavras de transição]:, após o qual o sistema concatena a pergunta clínica pré-definida para o próximo sintoma.
Quando a triagem está concluída, o LLM gera uma única frase introdutória empática antes do resultado estruturado ser apresentado. O prompt instrui explicitamente o modelo a não revelar o nível, recomendações, nem qualquer referência clínica. O resultado (nível, recomendação, confiança) é inserido pelo servidor Python após a frase do LLM.
A saída do LLM é sempre sujeita a pós-processamento antes de ser enviada ao utilizador:
Remoção de perguntas - qualquer fragmento a partir de "?" é eliminado isto porque o LLM não deve antecipar a pergunta clínica seguinte;
Filtragem de conteúdo clínico proibido - expressões como "112", "urgência", "emergência", "imediatamente", "grave" são removidas do reconhecimento intercalar, para garantir que o LLM não influencia a perceção de gravidade antes do resultado formal;
Deteção de antecipação do próximo sintoma - se o texto gerado contiver keywords associadas ao sintoma que vai ser perguntado a seguir, a frase é substituída por um texto neutro fixo;
Correção de pronomes - o modelo tende a usar o registo informal. Substituições por expressão regular corrigem estes casos para o registo formal do português europeu;
Limite de comprimento - o texto é truncado a no máximo duas frases.
4.7 Interface Web
A interface de utilizador é uma página HTML de página única, servida diretamente pelo servidor FastAPI. É implementada em HTML, CSS e JavaScript puro, sem dependências externas de framework.

figura 3: Interface Web do Chatbot SNS24
A interface apresenta um painel de chat à esquerda e um painel lateral de diagnóstico à direita, que exibe em tempo real os sintomas já detectados na sessão, o status de ligação ao modelo Ollama, e o resultado final de triagem com o respetivo nível de urgência codificado por cor.
A comunicação com o servidor é feita através de dois endpoints principais:
POST /api/chat/start - inicia uma nova sessão e recebe a mensagem de boas-vindas;
POST /api/chat/message - envia uma mensagem do utilizador e recebe a resposta do sistema, o estado atual dos sintomas, e, quando disponível, o resultado de triagem.
O estado de ligação ao Ollama é monitorizado via GET /api/chat/status, que devolve a lista de modelos disponíveis e confirma se o modelo llama3.2:3b está carregado.

5. Funcionalidades Avançadas
5.1 Garantia de Segurança Clínica
Após obter o resultado do motor Prolog, o motor Python também é executado em paralelo. Se o Python concluir um nível mais grave do que o Prolog, o resultado obtido no Python prevalece. Esta salvaguarda corrige uma assimetria do motor Prolog do P1, que seleciona a regra com o CF mais alto e não necessariamente o nível mais grave: por exemplo, uma regra de urgente com CF 0.85 não deve suprimir uma regra de muito_urgente com CF 0.60.
Esta camada de segurança garante que o sistema nunca subestime a gravidade clínica de um caso por um artefacto do motor de inferência. A decisão de incluir esta salvaguarda foi motivada por testes informais em que o servidor Prolog retornava como urgente em casos onde o motor Python identificava corretamente muito_urgente devido a uma regra com CF inferior mas nível mais grave
5.2 Intercepção de Pedidos de Explicação
Quando o utilizador questiona a pertinência de uma questão, o sistema deteta o pedido de explicação em vez de uma resposta ao sintoma. A justificação clínica é obtida diretamente da base de conhecimento Prolog através do predicado explicacao(sintoma, 'Texto'), armazenado no dicionário EXPLICACOES_SINT, que detalha a relevância médica do sintoma no contexto da triagem.
Após exibir este esclarecimento, o sistema repete a pergunta clínica anterior sem avançar para o próximo sintoma ou modificar o estado da sessão, mantendo as variáveis ultima_pergunta e perguntas_feitas intactas. Desta forma, o fluxo de triagem não é alterado e o utilizador tem a oportunidade de responder à pergunta original com o contexto e esclarecimento adequados.
5.3 Persistência Local de Triagens
Na versão original do Projeto 1, a persistência de dados em triagens.csv estava acoplada ao estado dinâmico facto/2 do Prolog, impossibilitando a gravação no modo alternativo Python. Para resolver isto, implementou-se a função salvar_triagem_csv, que é invocada pelo servidor Python no final de cada triagem; a função converte o dicionário session["sintomas"] numa linha binária estruturada, adiciona-a em modo append e grava o identificador Prolog do nível vencedor para garantir a compatibilidade com o pipeline de treino do P1 Parte B.
Esta implementação fecha o ciclo de aprendizagem contínua do P1: as sessões do chatbot P2 passam a alimentar diretamente o mesmo triagens.csv que o pipeline de aprendizagem automática do P1 utiliza para gerar as novas regras em base_conhecimento_b.pl.
6. Conclusões
6.1 Síntese
Este projeto materializou-se no desenvolvimento de um chatbot de triagem clínica que integra três paradigmas distintos de inteligência artificial: raciocínio baseado em regras, recuperação de informação e geração de linguagem natural. A solução é uma extensão direta e coerente do Projeto 1. Reutiliza toda a base de conhecimento clínico, o motor de inferência e o pipeline de aprendizagem automática, adicionando uma camada de linguagem natural que torna o sistema acessível a todos os utilizadores.
A divisão de responsabilidades entre componentes é clara e clinicamente segura: a lógica de inferência é inteiramente controlada pelo motor de regras; o LLM é confinado à dimensão linguística da interação, com filtros que impedem que alucinações comprometam a segurança do resultado. A base de conhecimento foi expandida de 28 para 36 regras, com cobertura de síndromes críticas, que antes estavam ausentes, e as treze regras de contra-evidência com CF negativo foram substituídas por um mecanismo mais seguro baseado em premissas negadas.
6.2 Discussão
A principal tensão no desenvolvimento foi o uso de um LLM reduzido (Llama 3.2:3b) num domínio de alto risco. O modelo revelou-se adequado para gerar frases empáticas curtas, mas insatisfatório na extração estruturada de sintomas. Por isso, foi excluído do pipeline de deteção em favor de um sistema determinístico baseado em keywords, uma escolha pragmática entre generalidade e fiabilidade em contextos clínicos. A arquitetura tira partido do LLM onde ele é robusto (geração de linguagem) e afasta-o de onde falha (extração clínica), combinando a naturalidade conversacional da IA com a fiabilidade de um sistema especialista baseado em regras.
As maiores dificuldades residiram na gestão do estado da sessão em contexto assíncrono, garantindo que ambiguidades, pedidos de explicação ou mensagens não reconhecidas não corrompam o fluxo da triagem, e na calibração dos gatilhos de disparo, que devem ser sensíveis a emergências sem encerrar a conversa prematuramente.
O sistema cumpre todos os objetivos do Projeto 2. A integração com o P1 é completa: a base de conhecimento é reutilizada, as triagens alimentam o ficheiro `triagens.csv` e o servidor Prolog (P1) funciona como motor primário de inferência. O grupo autoavalia o projeto com 18 valores.
6.3 Funcionamento do Trabalho em Grupo
O trabalho em grupo decorreu em continuidade natural do Projeto 1, com a mesma distribuição de responsabilidades e o mesmo modelo de colaboração. A definição de interfaces entre componentes no início do desenvolvimento permitiu que as quatro frentes avançassem em paralelo com conflitos técnicos mínimos.
As situações que exigiram maior coordenação foram a calibração dos critérios de disparo da triagem, que dependem simultaneamente do estado dos sintomas e do contador de trocas da conversa, e a filtragem de alucinações do LLM, cujos casos extremos foram identificados durante os testes da interface mas exigiram ajustes na lógica de prompt.
No que respeita à autodiferenciação, o grupo considera que todos os elementos contribuíram de forma ativa e proporcional às responsabilidades atribuídas, pelo que as avaliações individuais propostas são as seguintes:
                    Nome
Número
  Avaliação Proposta
          Alexandr Tchikoulaev
A103625
              18
                André Pinto
A106825
              18
                 João Alves
A102394
              18
                  Rui Silva
A106831
              18


Anexo A
base_conhecimento_a.pl:
:- multifile regra/4.
:- multifile explicacao_regra/2.
:- discontiguous regra/4.
:- discontiguous explicacao_regra/2.
:- discontiguous explicacao/2.


% ----------------------------------------------------------------
% SINTOMAS
% ----------------------------------------------------------------
sintoma(sem_respiracao,   'Paragem respiratoria (nao respira de todo)').
sintoma(sem_pulso,        'Paragem cardiaca (sem pulso detectavel)').
sintoma(resp_dificuldade, 'Falta de ar grave (nao consegue falar ou cor azulada)').
sintoma(hemorragia,       'Hemorragia abundante e incontrolavel').
sintoma(inconsciente,     'Alteracao da consciencia (nao responde ou sonolencia marcada)').
sintoma(convulsoes,       'Convulsoes ou contracoes involuntarias do corpo').
sintoma(dor_peito,        'Dor no centro do peito ha mais de 10 minutos').
sintoma(dor_irradia,      'A dor irradia para o braco, mandibula ou costas').
sintoma(fala_dificil,     'Dificuldade subita em falar ou fala arrastada').
sintoma(fraqueza_lado,    'Fraqueza subita num so lado do corpo ou boca ao lado').
sintoma(confusao,         'Confusao mental ou desorientacao subita').
sintoma(dor_abd,          'Dor abdominal muito intensa e persistente').
sintoma(febre_bebe,       'Febre em bebe com menos de 3 meses').
sintoma(febre_alta,       'Febre acima de 39 graus Celsius').
sintoma(tosse_febre,      'Tosse acompanhada de febre').
sintoma(dor_persiste,     'Dor moderada que nao cede a medicacao').
sintoma(vomitos,          'Vomitos repetidos que impedem ingerir liquidos').
sintoma(diarreia,         'Diarreia grave com sinais de desidratacao').
sintoma(dor_garganta,     'Dor de garganta com dificuldade em engolir').
sintoma(constipacao,      'Sintomas de constipacao (tosse ligeira, nariz entupido)').
sintoma(dor_leve,         'Dor ligeira controlada com medicacao habitual').
sintoma(febre_baixa,      'Febre baixa, abaixo de 38 graus Celsius').
sintoma(mal_estar,        'Mal-estar geral sem sintomas especificos').
sintoma(rigidez_nuca,          'Rigidez da nuca (nao consegue encostar o queixo ao peito)').
sintoma(rash_petequial,        'Manchas vermelhas ou roxas na pele que nao desaparecem a pressao').
sintoma(reacao_alergica_grave, 'Reacao alergica grave com inchaço da face, lingua ou garganta').
sintoma(dor_cabeca_subita,     'Dor de cabeca muito intensa de inicio subito (pior da vida)').
sintoma(visao_alterada,        'Alteracao subita da visao num ou ambos os olhos').


% ----------------------------------------------------------------
% NIVEIS DE TRIAGEM
% ----------------------------------------------------------------
nivel(emergencia,          'EMERGENCIA',    'Ligue 112 (INEM) imediatamente').
nivel(muito_urgente,       'MUITO URGENTE', 'Dirija-se a urgencia hospitalar agora').
nivel(urgente,             'URGENTE',       'Marque consulta no centro de saude em 24h').
nivel(pouco_urgente,       'POUCO URGENTE', 'Autocuidados em casa, vigiar evolucao').
nivel(sem_sintomas_alarme, 'SEM ALARME',    'Vigiar; contactar SNS24 se piorar').


% ----------------------------------------------------------------
% REGRAS DE PRODUCAO
% CF: 0.40-0.65 sugestivo, 0.70-0.85 sindrome tipica, 0.90+ certeza alta.
% Regras com N+1 sintomas devem ter CF >= regra de N (mais sintomas = mais certeza).
% ----------------------------------------------------------------


% EMERGENCIA
regra(r_em1, se([sem_respiracao]),   entao(emergencia), 0.95).
regra(r_em2, se([sem_pulso]),        entao(emergencia), 0.95).
regra(r_em3, se([resp_dificuldade]), entao(emergencia), 0.85).
regra(r_em4, se([hemorragia]),       entao(emergencia), 0.85).
regra(r_em5, se([inconsciente]),     entao(emergencia), 0.85).
% Convulsoes activas: comprometem via aerea, protocolo SNS24 indica 112.
regra(r_em7, se([convulsoes]),       entao(emergencia), 0.85).
% Triada septica classica.
regra(r_em6, se([febre_alta, confusao, dor_abd]), entao(emergencia), 0.88).


% MUITO URGENTE
regra(r_mu1, se([dor_peito, dor_irradia]),     entao(muito_urgente), 0.90).
regra(r_mu2, se([dor_peito]),                  entao(muito_urgente), 0.60).
regra(r_mu3, se([fala_dificil]),               entao(muito_urgente), 0.80).
regra(r_mu4, se([fraqueza_lado]),              entao(muito_urgente), 0.80).
% dor_abd sem febre: afasta sepsis mas pode ser abdomen agudo.
regra(r_mu6, se([dor_abd, nao(febre_alta)]),   entao(muito_urgente), 0.60).
% Confusao subita e muito_urgente com ou sem febre; r_em6 prevalece se tambem houver dor_abd.
regra(r_mu7, se([confusao]),                   entao(muito_urgente), 0.80).
% Padrao FAST completo: dois sinais AVC em simultaneo.
regra(r_mu8, se([fala_dificil, fraqueza_lado]), entao(muito_urgente), 0.92).
% Febre + dor_abd sem confusao: r_em6 nao dispara, pode ser cirurgico/infeccioso.
regra(r_mu9, se([febre_alta, dor_abd]),        entao(muito_urgente), 0.72).


% URGENTE
regra(r_ur1, se([febre_bebe]),                              entao(urgente), 0.90).
regra(r_ur2, se([febre_alta, tosse_febre]),                 entao(urgente), 0.80).
regra(r_ur3, se([vomitos, diarreia]),                       entao(urgente), 0.75).
regra(r_ur4, se([febre_alta]),                              entao(urgente), 0.50).
% dor_persiste sem constipacao: dor que nao cede a analgesicos precisa de reavaliacao medica
% com constipacao: cefaleia/mialgia gripal nao resolvida => pouco_urgente (r_pu7)
regra(r_ur5, se([dor_persiste, nao(constipacao)]),          entao(urgente), 0.40).
% dor_garganta sem constipacao: suspeita de amigdalite bacteriana ou abscesso
regra(r_ur6, se([dor_garganta, nao(constipacao)]),          entao(urgente), 0.55).
% Bebe com febre + perda de liquidos por dupla via: risco critico de desidratacao.
regra(r_ur7, se([febre_bebe, vomitos, diarreia]),           entao(muito_urgente), 0.88).
regra(r_ur8, se([febre_alta, tosse_febre, dor_persiste]),   entao(urgente), 0.85).
% Dor_abd sem sintomas GI afasta gastroenterite; sugere origem cirurgica/urologica.
regra(r_ur9, se([dor_abd, nao(vomitos), nao(diarreia)]),    entao(urgente), 0.80).


% Vomitos sem diarreia: desidratacao por via gastrica, sem dupla perda de liquidos
regra(r_ur10, se([vomitos, nao(diarreia)]),              entao(urgente),       0.60).
% Diarreia grave sem vomitos: ainda assim urgente pois a definicao ja implica desidratacao
regra(r_ur13, se([diarreia, nao(vomitos)]),              entao(urgente),       0.55).
% Dor de garganta com febre alta: suspeita de amigdalite bacteriana
regra(r_ur11, se([dor_garganta, febre_alta]),            entao(urgente),       0.75).
% Bebe com vomitos e sem diarreia: reservas do lactente esgotam-se rapidamente
regra(r_ur12, se([febre_bebe, vomitos, nao(diarreia)]),  entao(muito_urgente), 0.80).


% Alteracao subita da visao isolada: urgente (AVC, glaucoma agudo, oclusao retiniana)
regra(r_ur14, se([visao_alterada]),                          entao(urgente),       0.60).


% Confusao + febre alta sem dor abdominal: padrao de meningite ou encefalite (nao sepsis)
regra(r_mu10, se([confusao, febre_alta, nao(dor_abd)]),  entao(muito_urgente), 0.85).
% Reacao alergica grave sem dificuldade respiratoria: pode evoluir para anafilaxia
regra(r_mu11, se([reacao_alergica_grave]),                   entao(muito_urgente), 0.80).
% Hemorragia subaracnoideia: pior dor de cabeca da vida de inicio subito
regra(r_mu12, se([dor_cabeca_subita]),                       entao(muito_urgente), 0.85).
% BE-FAST completo: alteracao da visao + dificuldade na fala
regra(r_mu13, se([visao_alterada, fala_dificil]),            entao(muito_urgente), 0.90).
% Dificuldade respiratoria com febre alta: suspeita de pneumonia grave ou sepsis respiratoria
regra(r_em8,  se([resp_dificuldade, febre_alta]),         entao(emergencia),    0.87).
% Meningite bacteriana: febre alta + rigidez da nuca
regra(r_em9,  se([febre_alta, rigidez_nuca]),               entao(emergencia),   0.92).
% Meningococcemia: rash petequial com febre alta
regra(r_em10, se([febre_alta, rash_petequial]),             entao(emergencia),   0.95).
% Anafilaxia: dificuldade respiratoria com reacao alergica grave
regra(r_em11, se([resp_dificuldade, reacao_alergica_grave]), entao(emergencia),  0.93).


% POUCO URGENTE
regra(r_pu1, se([constipacao]),           entao(pouco_urgente), 0.70).
regra(r_pu2, se([dor_leve]),              entao(pouco_urgente), 0.65).
regra(r_pu3, se([febre_baixa]),           entao(pouco_urgente), 0.60).
regra(r_pu4, se([dor_leve, mal_estar]),   entao(pouco_urgente), 0.70).


% Gripe tipica sem febre alta: quadro viral tratavel em casa
regra(r_pu5, se([constipacao, dor_garganta, nao(febre_alta)]), entao(pouco_urgente), 0.72).
% Febre baixa com mal-estar geral sem dor abdominal: viral autolimitado
regra(r_pu6, se([febre_baixa, mal_estar, nao(dor_abd)]),       entao(pouco_urgente), 0.68).
% Constipacao com dor que nao cede: cefaleia/mialgia gripal; nao requer urgencia
regra(r_pu7, se([constipacao, dor_persiste, nao(febre_alta)]), entao(pouco_urgente), 0.65).


% SEM ALARME
regra(r_sa1, se([mal_estar]),                    entao(sem_sintomas_alarme), 0.55).
% Intencionalmente sem_alarme: motor combina com r_pu1 e reporta pouco_urgente.
regra(r_sa2, se([constipacao, febre_baixa]),     entao(sem_sintomas_alarme), 0.65).


% ----------------------------------------------------------------
% EXPLICACOES DAS REGRAS (exibidas no resultado final)
% ----------------------------------------------------------------


% Emergencia
explicacao_regra(r_em1, 'Paragem respiratoria requer suporte basico de vida imediato.').
explicacao_regra(r_em2, 'Paragem cardiaca necessita de reanimacao e chamada ao 112.').
explicacao_regra(r_em3, 'Falta de ar grave e coloracao azulada indicam hipoxia severa.').
explicacao_regra(r_em4, 'Hemorragias activas podem levar a choque hipovolemico.').
explicacao_regra(r_em5, 'Alteracao de consciencia profunda sugere lesao ou doenca grave.').
explicacao_regra(r_em7, 'Convulsoes activas comprometem a via aerea, causam hipoxia e indicam emergencia neurologica. O protocolo SNS24 indica chamada imediata ao 112.').
explicacao_regra(r_em6, 'Febre alta + confusao + dor abdominal e o triade classica de sepsis, infeccao disseminada com risco de falencia multiorganica imediata.').
explicacao_regra(r_em9,  'Febre alta com rigidez da nuca e o sinal classico de meningite bacteriana, infeccao do sistema nervoso central com risco de vida imediato e sequelas graves.').
explicacao_regra(r_em10, 'Rash petequial com febre e o sinal de alerta de meningococcemia, septicemia meningococica com progressao rapida para choque e falencia multiorganica em horas.').
explicacao_regra(r_em11, 'Dificuldade respiratoria com reacao alergica grave indica anafilaxia, emergencia imunologica com risco de obstrucao total da via aerea que requer adrenalina e chamada ao 112.').


% Muito urgente
explicacao_regra(r_mu1, 'Dor no peito com irradiacao e o quadro classico de enfarte do miocardio.').
explicacao_regra(r_mu2, 'Dor no peito isolada pode ser cardiaca, requerendo avaliacao muito urgente.').
explicacao_regra(r_mu3, 'Dificuldade repentina na fala e um sinal de alerta de Acidente Vascular Cerebral (AVC).').
explicacao_regra(r_mu4, 'Fraqueza unilateral do corpo e fortemente indicativa de AVC.').
explicacao_regra(r_mu6, 'Dor abdominal intensa sem febre pode significar abdomen agudo (ex: apendicite, colica renal). A ausencia de febre nao afasta a urgencia cirurgica.').
explicacao_regra(r_mu7, 'A confusao mental subita indica grave alteracao neurologica, metabolica ou infecciosa, independentemente de existir febre. Febre alta + confusao sem dor abdominal pode indicar meningite ou encefalite. Se tambem existir dor abdominal, aplica-se r_em6 (sepsis, emergencia).').
explicacao_regra(r_mu8, 'Dificuldade na fala combinada com fraqueza unilateral e o padrao FAST classico de AVC, a combinacao eleva a certeza diagnostica acima de cada sinal isolado.').
explicacao_regra(r_mu9, 'Febre alta associada a dor abdominal intensa, na ausencia de confusao, pode indicar infeccao com foco cirurgico (apendicite com febre, colecistite aguda, pielonefrite grave). Requer avaliacao hospitalar urgente.').


% Urgente
explicacao_regra(r_ur1, 'A febre em bebes menores de 3 meses e sempre um sinal de alerta (sistema imunitario imaturo).').
explicacao_regra(r_ur2, 'Febre alta combinada com tosse levanta a suspeita de pneumonia.').
explicacao_regra(r_ur3, 'Vomitos e diarreia simultaneos acarretam um alto risco de desidratacao.').
explicacao_regra(r_ur4, 'Febre alta persistente requer investigacao de foco infeccioso.').
explicacao_regra(r_ur5, 'Dor moderada que nao cede a medicacao habitual, sem contexto de constipacao, precisa de reavaliacao medica para despiste de origem inflamatoria ou lesiva.').
explicacao_regra(r_ur6, 'Dor de garganta sem contexto de constipacao pode indicar amigdalite bacteriana ou abscesso periamigdalino, com risco de compromisso da via aerea. Com constipacao, e quadro viral benigno (ver r_pu5).').
explicacao_regra(r_ur7, 'Bebe febril com perda de liquidos por vomitos E diarreia enfrenta risco critico de desidratacao severa. As reservas de um lactente esgotam-se em horas. Este quadro justifica ida imediata a urgencia hospitalar.').
explicacao_regra(r_ur8, 'Febre alta com tosse e dor que nao cede a analgesicos aponta para infeccao respiratoria profunda (ex: pneumonia bacteriana), que pode necessitar de antibioterapia urgente.').
explicacao_regra(r_ur9, 'Dor abdominal sem vomitos nem diarreia afasta a gastroenterite como causa. A ausencia de sintomas gastrointestinais com dor intensa sugere origem cirurgica ou urologica (apendicite, colica renal ou colecistite) que requer avaliacao medica presencial urgente.').
explicacao_regra(r_ur10, 'Vomitos repetidos sem diarreia comprometem a hidratacao por via gastrica isolada. A incapacidade de ingerir liquidos pode exigir reposicao intravenosa.').
explicacao_regra(r_ur13, 'Diarreia grave ja implica, por definicao, sinais de desidratacao. Sem vomitos ha margem para hidratacao oral supervisionada, mas a vigilancia medica e necessaria.').
explicacao_regra(r_ur11, 'Dor de garganta associada a febre alta levanta suspeita de amigdalite bacteriana por estreptococo, que pode exigir antibioterapia e avaliar o risco de abscesso.').
explicacao_regra(r_ur12, 'Bebe febril com vomitos repetidos enfrenta risco elevado de desidratacao rapida. As reservas de um lactente esgotam-se em poucas horas, justificando avaliacao hospitalar urgente mesmo sem diarreia simultanea.').
explicacao_regra(r_ur14, 'Alteracao subita da visao pode indicar AVC, oclusao da arteria central da retina, glaucoma agudo ou outras emergencias oftalmologicas com risco de cegueira permanente se nao tratadas a tempo.').
explicacao_regra(r_mu10, 'Confusao mental associada a febre alta sem dor abdominal e o padrao clinico de meningite bacteriana ou encefalite viral. Estas infeccoes do sistema nervoso central sao emergencias neurologicas mesmo sem o quadro abdominal de sepsis.').
explicacao_regra(r_mu11, 'Reacao alergica grave com inchaço da face ou garganta pode evoluir rapidamente para anafilaxia com compromisso da via aerea, pelo que requer avaliacao hospitalar imediata.').
explicacao_regra(r_mu12, 'Dor de cabeca de inicio subito e muito intensa, descrita como a pior da vida, e o sinal classico de hemorragia subaracnoideia por rotura de aneurisma cerebral. Requer TAC cerebral urgente.').
explicacao_regra(r_mu13, 'Alteracao da visao associada a dificuldade na fala completa o padrao BE-FAST de AVC, elevando significativamente a certeza diagnostica e justificando avaliacao hospitalar imediata.').
explicacao_regra(r_em8, 'Dificuldade respiratoria grave com febre alta levanta a suspeita de pneumonia severa ou sepsis de foco pulmonar, ambas com risco de falencia respiratoria iminente e indicacao para avaliacao hospitalar imediata.').


% Pouco urgente / sem alarme
explicacao_regra(r_pu1, 'Sintomas gripais ligeiros devem ser autotratados com repouso.').
explicacao_regra(r_pu2, 'Dores ligeiras que cedem a medicacao nao requerem idas urgentes ao hospital.').
explicacao_regra(r_pu3, 'Febres baixas sao normalmente autolimitadas e respondem a antipireticos em casa.').
explicacao_regra(r_pu4, 'Mal-estar com dor ligeira e controlada consolida um quadro benigno, o medico de familia e o destino adequado, nao a urgencia hospitalar.').
explicacao_regra(r_pu5,  'Constipacao com dor de garganta sem febre alta enquadra-se num quadro viral tipico, tratavel em casa com analgesicos e repouso. Nao justifica ida a urgencia.').
explicacao_regra(r_pu6,  'Febre baixa com mal-estar geral sem dor abdominal e o quadro mais frequente de infeção viral autolimitada, sem necessidade de urgencia. Medicacao de venda livre e repouso sao suficientes.').
explicacao_regra(r_pu7,  'Cefaleias e mialgias gripais que nao cedem ao paracetamol sao frequentes nas infecoes virais das vias respiratorias. No contexto de constipacao, nao sao indicacao de urgencia.').
explicacao_regra(r_sa1, 'O mal-estar geral sem alarmes deve ser apenas vigiado em casa.').
explicacao_regra(r_sa2, 'Constipacao com febre baixa e o quadro viral autolimitado mais tipico, medicacao de venda livre e habitualmente suficiente.').


% ----------------------------------------------------------------
% EXPLICACOES DOS SINTOMAS (resposta ao comando "p." do utilizador)
% ----------------------------------------------------------------
explicacao(sem_respiracao,   'A ausencia de respiracao e a emergencia medica mais critica, exigindo inicio imediato de Suporte Basico de Vida.').
explicacao(sem_pulso,        'A paragem cardiaca requer reanimacao imediata para tentar restabelecer o fluxo sanguineo ao cerebro.').
explicacao(resp_dificuldade, 'A dificuldade grave em respirar pode indicar falencia respiratoria, o que representa um risco imediato de vida.').
explicacao(hemorragia,       'A perda rapida e incontrolavel de sangue pode levar rapidamente ao choque hipovolemico.').
explicacao(inconsciente,     'A perda de consciencia indica grave sofrimento cerebral, podendo ser trauma, AVC ou intoxicacao.').
explicacao(convulsoes,       'As convulsoes activas comprometem a via aerea, causam hipoxia e indicam uma emergencia neurologica aguda que requer chamada imediata ao 112.').
explicacao(dor_peito,        'A dor no peito e o sintoma primario de alerta para avaliar a hipotese de um Enfarte do Miocardio (ataque cardiaco).').
explicacao(dor_irradia,      'A irradiacao da dor no peito para os membros ou costas e um padrao que reforca muito a suspeita de origem cardiaca.').
explicacao(fala_dificil,     'A dificuldade subita em articular palavras e um dos principais sinais de alerta de um possivel AVC.').
explicacao(fraqueza_lado,    'A perda de forca num dos lados do corpo e um sintoma neurologico classico de isquemia ou hemorragia cerebral.').
explicacao(confusao,         'A confusao mental subita pode ser sinal de infeccao grave (meningite, sepsis), falta de oxigenio ou alteracao neurologica abrupta. Com febre alta, o risco aumenta significativamente.').
explicacao(dor_abd,          'Dores abdominais subitas e muito intensas podem indicar condicoes agudas graves, como apendicite ou perfuracao de orgaos. Associada a febre alta, o risco cirurgico aumenta.').
explicacao(febre_bebe,       'Os bebes tem um sistema imunitario imaturo, pelo que a febre requer sempre avaliacao medica urgente para despiste de infeccoes.').
explicacao(febre_alta,       'Febres muito elevadas (acima de 39 graus) sugerem infeccoes que podem requerer intervencao medica ou antibioticos. Associada a confusao ou dor abdominal, a urgencia aumenta.').
explicacao(tosse_febre,      'A tosse associada a febre levanta a forte suspeita de infeccoes respiratorias, como a pneumonia.').
explicacao(dor_persiste,     'Uma dor que nao cede a medicacao de alivio habitual sugere um quadro inflamatorio ou lesivo que necessita de diagnostico formal.').
explicacao(vomitos,          'A incapacidade repetida de reter liquidos no estomago leva rapidamente a desidratacao severa.').
explicacao(diarreia,         'A perda de grandes volumes de liquidos pelos intestinos comporta um alto risco de desidratacao e desequilibrio electrolitico.').
explicacao(dor_garganta,     'Se acompanhada de grande dificuldade em engolir, pode indicar abscesso periamigdalino ou epiglotite, infeccoes que ameacam bloquear a via aerea.').
explicacao(constipacao,      'Sintomas tipicos de constipacao ajudam a enquadrar o quadro como uma provavel infeccao viral benigna, sem gravidade.').
explicacao(dor_leve,         'Dores de baixa intensidade e facilmente controlaveis geralmente nao indicam problemas com os seus orgaos vitais.').
explicacao(febre_baixa,      'Temperaturas moderadas sao a resposta natural de defesa do corpo a pequenas agressoes virais ou inflamatorias.').
explicacao(mal_estar,        'Sentir-se indisposto de forma vaga, sem sinais de alarme, ajuda-nos a confirmar a ausencia de quadros clinicos urgentes.').
explicacao(rigidez_nuca,          'A rigidez da nuca e um sinal de irritacao meningea. Com febre alta, e o sinal classico de meningite bacteriana, uma emergencia neurologica com risco de vida imediato.').
explicacao(rash_petequial,        'Manchas na pele que nao desaparecem a pressao com febre sao o sinal classico de meningococcemia, infeccao fulminante e potencialmente fatal em horas.').
explicacao(reacao_alergica_grave, 'Inchaço da face, labios, lingua ou garganta apos exposicao a alergeno pode evoluir para anafilaxia, emergencia que requer adrenalina imediata e chamada ao 112.').
explicacao(dor_cabeca_subita,     'Uma dor de cabeca de inicio subito descrita como a mais intensa de sempre levanta a suspeita de hemorragia subaracnoideia por rotura de aneurisma cerebral, que requer avaliacao de emergencia.').
explicacao(visao_alterada,        'A perda ou alteracao subita da visao pode indicar AVC, oclusao da arteria central da retina ou outras causas vasculares graves que requerem avaliacao urgente.').
explicacao(_, 'Este sintoma e avaliado no nosso modelo clinico para afastar condicoes potencialmente graves.').


% ----------------------------------------------------------------
% ORDEM DE QUESTIONAMENTO
% febre_alta antes de confusao e dor_abd para r_em6/r_mu9 dispararem mais cedo.
% ----------------------------------------------------------------
ordem_sintomas([
    sem_respiracao, sem_pulso, resp_dificuldade, hemorragia, inconsciente,
    convulsoes, reacao_alergica_grave,
    dor_peito, dor_irradia, fala_dificil, fraqueza_lado,
    visao_alterada, dor_cabeca_subita,
    febre_alta, rigidez_nuca, rash_petequial, confusao, dor_abd, febre_bebe,
    tosse_febre, dor_persiste, vomitos, diarreia,
    dor_garganta, constipacao, dor_leve, febre_baixa, mal_estar
]).

chatbot_server.py:
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
                         "garganta inflamada", "amígdalas", "engolir dói"],
    "constipacao":      ["constipado", "nariz entupido", "tosse ligeira", "ranho",
                         "sintomas de constipação", "resfriado", "pingo no nariz",
                         "nariz a pingar", "tenho tosse", "sinto tosse", "com tosse",
                         "tosse seca", "tosse produtiva"],
    "dor_leve":         ["dor ligeira", "dor suave", "desconforto ligeiro", "dói um pouco",
                         "dor leve", "dor moderada", "dor de cabeça ligeira",
                         "dor de cabeça", "cefaleia"],
    "febre_baixa":      ["febre baixa", "temperatura ligeiramente elevada",
                         "febre de 37", "febre de 38", "37 graus", "37.5", "38 graus",
                         "temperatura a subir um pouco",
                         "febre mas não", "febre mas nao",
                         "febre ligeira", "febre moderada", "alguma febre",
                         "pouca febre", "um pouco de febre", "febre não alta",
                         "febre nao alta", "febre não muito", "febre nao muito"],
    "mal_estar":        ["mal-estar", "mal estar", "indisposto", "não me sinto bem",
                         "cansado sem motivo", "indisposição geral", "sinto-me mal",
                         "não estou bem", "sinto mal estar", "mal disposto",
                         "mal-disposto", "indisposta", "mal disposta",
                         "sinto-me mal disposto", "meio indisposto"],
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
    "dor_leve":              "Dor ligeira",
    "febre_baixa":           "Febre baixa (<38°C)",
    "mal_estar":             "Mal-estar geral",
    "rigidez_nuca":          "Rigidez da nuca",
    "rash_petequial":        "Rash petequial (manchas na pele)",
    "reacao_alergica_grave": "Reação alérgica grave / Anafilaxia",
    "dor_cabeca_subita":     "Dor de cabeça súbita e intensa",
    "visao_alterada":        "Alteração súbita da visão",
}


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
# NOTA: febre_alta → tosse_febre foi REMOVIDO - tosse com febre baixa (37-38°C) é válido;
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
    "dor_leve":              "Tem alguma dor, mesmo que ligeira?",
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
           # intensificadores e afirmações indiretas - mapeados deterministicamente, sem LLM
           "muito", "bastante", "claramente", "definitivamente", "totalmente",
           "absolutamente", "obviamente", "óbvio", "obvio", "sem dúvida", "sem duvida",
           "tenho sim", "claro que sim"}
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
                return None   # resposta qualificada - tratar como incerta
            return True
    for w in ["não ", "nao ", "nunca "]:
        if t.startswith(w) and len(t) < 55:
            return False
    return None




_INCERTO_PALAVRAS = {
    "talvez", "não sei", "nao sei", "talvez sim", "talvez não", "talvez nao",
    "mais ou menos", "possivelmente", "não tenho a certeza", "nao tenho a certeza",
    "incerto", "incerta", "pode ser", "acho que sim", "acho que não", "acho que nao",
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
    Nesse caso a triagem não deve disparar - falta perguntar o sintoma restante que pode
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
        # Nenhuma regra disparou - usar mapeamento individual
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


        # Intro empática gerada por LLM - curta, sem revelar o resultado
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
        # Motor esgotou perguntas - LLM resume e anuncia análise
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


    # Triagem já concluída - mostrar resultado armazenado sem reprocessar
    if session["triagem_feita"] and session.get("resultado_prolog"):
        rec   = _corrigir_acentos(session["resultado_prolog"].get("recomendacao", ""))
        nivel = session["resultado_prolog"].get("nivel", "")
        sintomas_json = [
            {"id": s, "nome": SINTOMAS_PT.get(s, s), "presente": v == "sim"}
            for s, v in session["sintomas"].items()
        ]
        return {
            "message": (
                f"A triagem já foi concluída. **{nivel}** - {rec}.\n\n"
                f"Se necessitar de uma nova avaliação, por favor inicie uma nova conversa."
            ),
            "sintomas":         sintomas_json,
            "triagem_feita":    True,
            "resultado_prolog": session["resultado_prolog"],
        }


    # 0. Porquê/pedido de explicação - responder com justificação clínica e repetir pergunta
    ultima_perg = session.get("ultima_pergunta")
    if e_intencao_porque(user_msg) and ultima_perg:
        expl     = _explicacao_sintoma(ultima_perg)
        pergunta = DESCRICAO_PERGUNTA.get(ultima_perg, "Pode responder à pergunta anterior?")
        resposta = f"Peço esta informação porque: {expl}\n\n{pergunta}"
        session["history"].append({"role": "assistant", "content": resposta})
        sintomas_json = [{"id": s, "nome": SINTOMAS_PT.get(s, s), "presente": v == "sim"}
                         for s, v in session["sintomas"].items()]
        return {"message": resposta, "sintomas": sintomas_json,
                "triagem_feita": False, "resultado_prolog": None}


    # 1. Se a mensagem é um sim/não simples à última pergunta, mapeá-la directamente
    resp_simples = e_resposta_simples(user_msg)
    if resp_simples is not None and ultima_perg:
        if ultima_perg not in session["sintomas"]:
            session["sintomas"][ultima_perg] = "sim" if resp_simples else "nao"
        session["perguntas_feitas"].add(ultima_perg)  # marcar como feita só após resposta clara
    elif e_resposta_incerta(user_msg) and ultima_perg:
        # Resposta incerta ("talvez", "não sei") - não regista o sintoma,
        # mas marca como perguntado para não repetir a mesma questão
        session["perguntas_feitas"].add(ultima_perg)


    # 2. Detecção de sintomas via keywords (llama3.2:3b produz alucinações na
    # extração estruturada, por isso confiamos apenas nas keywords que são fiáveis)
    kw = detectar_sintomas_keywords(user_msg)
    for s in kw["presentes"]:
        if s not in session["sintomas"]:
            session["sintomas"][s] = "sim"
    for s in kw["ausentes"]:
        if s not in session["sintomas"]:
            session["sintomas"][s] = "nao"
        elif s == ultima_perg and session["sintomas"].get(s) == "sim" and resp_simples is True:
            # Override: keyword nega explicitamente o mesmo sintoma que a resposta
            # simples confirmou - ex: "tenho febre mas não acima de 39 graus"
            # → e_resposta_simples viu "tenho" → sim; keyword viu "não...acima de 39" → ausente
            # A keyword é mais específica: prevalece.
            session["sintomas"][s] = "nao"


    # 2b. Aplicar exclusões mútuas (ex: febre_alta exclui febre_baixa)
    aplicar_exclusoes(session["sintomas"])


    # 3+4. Early-exit absoluto para emergências completas; caso contrário, fluxo normal
    emerg_satisfeita = tem_regra_emergencia_satisfeita(session["sintomas"])
    if emerg_satisfeita and not session["triagem_feita"]:
        # Regra de emergência 100% satisfeita - triagem imediata, sem mais perguntas
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
        session["triagem_feita"] = True   # sempre marcar - evita chamadas repetidas


        nivel_mycin    = resultado_mycin.get("nivel", "")
        nivel_esperado = nivel_por_sintomas(presentes)


        # Fallback: servidor Prolog não disponível - usar motor MYCIN Python
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
            # um nível mais grave, prevalece - ex: vomitos(r_ur10, CF=0.60) não
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

chatbot.html:
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SNS24 – Chatbot P2 (RAG + LLM)</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }


:root {
  --green:       #059669;
  --green-light: #d1fae5;
  --green-mid:   #10b981;
  --green-dark:  #065f46;
  --bg:          #f0fdf4;
  --surface:     #ffffff;
  --surface2:    #f8fafc;
  --border:      #e2e8f0;
  --border2:     #cbd5e1;
  --text:        #0f172a;
  --text-mid:    #475569;
  --text-dim:    #94a3b8;
  --mono:        'IBM Plex Mono', monospace;
  --sans:        'DM Sans', sans-serif;
  --c-em:    #dc2626;
  --c-mu:    #ea580c;
  --c-ur:    #d97706;
  --c-pu:    #2563eb;
  --c-sa:    #059669;
  --purple:  #7c3aed;
}


html, body {
  width: 100%; height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  overflow: hidden;
}


/* ── Topbar ── */
#topbar {
  background: var(--surface);
  border-bottom: 1.5px solid var(--border);
  display: flex; align-items: center; gap: 14px;
  padding: 0 24px; height: 60px;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
}
.logo { display: flex; align-items: center; gap: 10px; }
.logo-icon {
  width: 34px; height: 34px; background: var(--purple); border-radius: 9px;
  display: flex; align-items: center; justify-content: center; font-size: 17px;
}
.logo-text  { font-size: 14px; font-weight: 800; color: var(--text); }
.logo-text span { color: var(--purple); }
.logo-sub   { font-size: 10.5px; color: var(--text-dim); font-weight: 500; margin-top: 1px; }
.spacer { flex: 1; }


.back-btn {
  font-family: var(--sans); font-size: 12.5px; font-weight: 700;
  padding: 7px 16px; border-radius: 8px;
  border: 1.5px solid var(--border2); color: var(--text-mid);
  background: var(--surface2); cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 6px; transition: all .13s;
}
.back-btn:hover { border-color: var(--green); color: var(--green); background: var(--green-light); }


.status-pill {
  display: flex; align-items: center; gap: 6px;
  border-radius: 20px; padding: 4px 12px;
  font-size: 11px; font-weight: 600; border: 1px solid;
}
.status-pill.ok    { background: var(--green-light); border-color: #a7f3d0; color: var(--green-dark); }
.status-pill.warn  { background: #fef9c3;            border-color: #fcd34d; color: #92400e; }
.status-pill.err   { background: #fff5f5;            border-color: #fca5a5; color: var(--c-em); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.ok   .status-dot { background: var(--green); animation: blink 2s infinite; }
.warn .status-dot { background: #d97706; }
.err  .status-dot { background: var(--c-em); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }


/* ── Layout ── */
#app {
  display: flex; padding-top: 60px;
  height: 100vh; overflow: hidden;
}


/* ── Sidebar ── */
#sidebar {
  width: 270px; flex-shrink: 0;
  background: var(--surface); border-right: 1.5px solid var(--border);
  display: flex; flex-direction: column; overflow-y: auto;
}
.sb-sec { padding: 14px 16px; border-bottom: 1px solid var(--border); }
.sb-lbl {
  font-size: 9.5px; font-weight: 700; letter-spacing: 1.5px;
  text-transform: uppercase; color: var(--text-dim); margin-bottom: 10px;
}


/* Sobre o sistema */
.about-box {
  font-size: 11.5px; color: var(--text-mid); line-height: 1.65;
}
.about-tag {
  display: inline-block; font-size: 10px; font-weight: 700;
  padding: 2px 8px; border-radius: 5px; margin-bottom: 6px;
  background: #ede9fe; color: var(--purple); border: 1px solid #c4b5fd;
}


/* Sintomas */
#sint-list { display: flex; flex-direction: column; gap: 5px; }
.sint-item {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 8px; border-radius: 7px; font-size: 11.5px; font-weight: 500;
}
.sint-pres { background: #f0fdf4; color: #15803d; border: 1px solid #a7f3d0; }
.sint-aus  { background: #f8fafc; color: var(--text-dim); border: 1px solid var(--border); text-decoration: line-through; }
.sint-dot  { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.sint-pres .sint-dot { background: var(--green); }
.sint-aus  .sint-dot { background: var(--border2); }
.sint-empty { font-size: 11.5px; color: var(--text-dim); padding: 4px 0; }


/* Resultado MYCIN */
#resultado-box { padding: 14px 16px; }
.res-card {
  border-radius: 11px; padding: 12px 14px; border: 2px solid;
}
.res-nivel { font-size: 13px; font-weight: 800; margin-bottom: 3px; }
.res-rec   { font-size: 11.5px; font-weight: 500; color: var(--text-mid); line-height: 1.5; }
.res-cf    { font-family: var(--mono); font-size: 20px; font-weight: 700; margin-top: 8px; }
.res-cf-lbl{ font-size: 9px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase;
             color: var(--text-dim); }
.res-mycin-badge {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 9.5px; font-weight: 700; padding: 2px 8px; border-radius: 5px;
  background: #ede9fe; color: var(--purple); border: 1px solid #c4b5fd; margin-top: 8px;
}
.res-vazio { font-size: 11.5px; color: var(--text-dim); }


/* ── Feed principal ── */
#main {
  flex: 1; display: flex; flex-direction: column;
  overflow: hidden; min-width: 0;
}


#feed {
  flex: 1; overflow-y: auto; padding: 24px 28px;
  display: flex; flex-direction: column; gap: 14px;
}


/* Mensagens */
.msg-wrap { display: flex; }
.msg-wrap.user { justify-content: flex-end; }
.msg-wrap.bot  { justify-content: flex-start; }


.msg-bubble {
  max-width: 72%; padding: 12px 16px;
  border-radius: 16px; font-size: 14px; line-height: 1.65; font-weight: 500;
}
.msg-wrap.user .msg-bubble {
  background: var(--purple); color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-wrap.bot .msg-bubble {
  background: var(--surface); border: 1.5px solid var(--border);
  color: var(--text); border-bottom-left-radius: 4px;
  box-shadow: 0 1px 6px rgba(0,0,0,.06);
}
.msg-wrap.bot .msg-bubble.emergency {
  border-color: var(--c-em); background: #fff5f5;
}


/* Typing indicator */
.typing-wrap { display: flex; gap: 10px; align-items: center; }
.typing-bubble {
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: 16px; border-bottom-left-radius: 4px;
  padding: 14px 18px; display: flex; gap: 5px; align-items: center;
  box-shadow: 0 1px 6px rgba(0,0,0,.06);
}
.dot-anim {
  width: 7px; height: 7px; border-radius: 50%; background: var(--text-dim);
  animation: bounce 1.2s infinite;
}
.dot-anim:nth-child(2) { animation-delay: .15s; }
.dot-anim:nth-child(3) { animation-delay: .30s; }
@keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }


/* Avatar */
.avatar {
  width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
  background: #ede9fe; border: 1.5px solid #c4b5fd; margin-top: 2px;
}
.msg-wrap.user { gap: 10px; }
.msg-wrap.bot  { gap: 10px; }


/* Card boas-vindas */
.welcome-card {
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: 14px; padding: 20px 22px;
  box-shadow: 0 2px 10px rgba(0,0,0,.06);
}
.welcome-title { font-size: 18px; font-weight: 800; margin-bottom: 6px; }
.welcome-sub   { font-size: 13px; color: var(--text-mid); line-height: 1.6; }
.welcome-badges { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 14px; }
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11.5px; font-weight: 600; padding: 4px 11px; border-radius: 20px; border: 1px solid;
}
.badge-purple { background: #ede9fe; border-color: #c4b5fd; color: var(--purple); }
.badge-green  { background: var(--green-light); border-color: #a7f3d0; color: var(--green-dark); }
.badge-orange { background: #fff7ed; border-color: #fdba74; color: #9a3412; }


/* ── Input area ── */
#input-area {
  background: var(--surface); border-top: 1.5px solid var(--border);
  padding: 14px 28px 16px;
  box-shadow: 0 -2px 12px rgba(0,0,0,.06);
  display: flex; flex-direction: column; gap: 10px;
}


#input-row { display: flex; gap: 10px; align-items: flex-end; }


#msg-input {
  flex: 1; font-family: var(--sans); font-size: 14px;
  padding: 11px 16px; border: 1.5px solid var(--border2);
  border-radius: 12px; outline: none; resize: none;
  line-height: 1.5; min-height: 46px; max-height: 120px;
  transition: border-color .15s;
  background: var(--surface2);
}
#msg-input:focus { border-color: var(--purple); background: #fff; }
#msg-input::placeholder { color: var(--text-dim); }
#msg-input:disabled { opacity: .5; cursor: not-allowed; }


#btn-send {
  font-family: var(--sans); font-size: 13px; font-weight: 700;
  padding: 11px 22px; border-radius: 12px;
  background: var(--purple); color: #fff; border: none; cursor: pointer;
  transition: all .13s; white-space: nowrap;
  display: flex; align-items: center; gap: 7px;
  box-shadow: 0 2px 8px rgba(124,58,237,.3);
}
#btn-send:hover:not(:disabled) { background: #6d28d9; transform: translateY(-1px); }
#btn-send:disabled { opacity: .4; cursor: not-allowed; transform: none; }


#btn-start {
  width: 100%; font-family: var(--sans); font-size: 14px; font-weight: 700;
  padding: 13px; border-radius: 12px;
  background: var(--purple); color: #fff; border: none; cursor: pointer;
  transition: all .13s; display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 2px 10px rgba(124,58,237,.3);
}
#btn-start:hover { background: #6d28d9; transform: translateY(-1px); }


/* Marcação de emergência no feed */
.sys-err {
  font-size: 12px; color: var(--c-em); font-weight: 600;
  padding: 6px 12px; background: #fff5f5; border: 1px solid #fca5a5;
  border-radius: 8px; display: flex; align-items: center; gap: 7px;
}


/* Animações */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.msg-wrap { animation: slideUp .2s ease; }
</style>
</head>
<body>


<header id="topbar">
  <div class="logo">
    <div class="logo-icon">🤖</div>
    <div>
      <div class="logo-text">SNS<span>24</span> Chatbot</div>
      <div class="logo-sub">Projeto 2 · RAG + LLM (Ollama) + MYCIN</div>
    </div>
  </div>
  <div class="spacer"></div>
  <div class="status-pill warn" id="status-pill">
    <div class="status-dot"></div>
    <span id="status-txt">A verificar…</span>
  </div>
  <a class="back-btn" href="/">
    ← Triagem Clássica (P1)
  </a>
</header>


<div id="app">
  <aside id="sidebar">
    <div class="sb-sec">
      <div class="sb-lbl">Sistema P2</div>
      <div class="about-box">
        <div class="about-tag">RAG + LLM</div>
        <br>
        Chatbot conversacional com <strong>Retrieval Augmented Generation</strong>
        sobre os protocolos Altitude SNS24.<br><br>
        Motor <strong>MYCIN</strong> (Parte A) integrado para validação formal do diagnóstico.
      </div>
    </div>


    <div class="sb-sec" style="flex:1">
      <div class="sb-lbl">Sintomas Detetados</div>
      <div id="sint-list">
        <div class="sint-empty">Nenhum sintoma identificado ainda.</div>
      </div>
    </div>


    <div id="resultado-box">
      <div class="sb-lbl">Resultado MYCIN</div>
      <div class="res-vazio" id="resultado-content">
        Aguarda resposta completa.
      </div>
    </div>
  </aside>


  <main id="main">
    <div id="feed">
      <div class="welcome-card">
        <div class="welcome-title">🤖 Chatbot de Triagem SNS24</div>
        <div class="welcome-sub">
          Este chatbot usa um <strong>Modelo de Linguagem (LLM)</strong> aumentado com
          <strong>RAG</strong> sobre os protocolos clínicos Altitude do SNS24,
          e valida o diagnóstico com o motor <strong>MYCIN</strong> da Parte A.
        </div>
        <div class="welcome-badges">
          <span class="badge badge-purple">🧠 llama3.2:3b via Ollama</span>
          <span class="badge badge-green">📚 RAG · Protocolos Altitude</span>
          <span class="badge badge-orange">⚙️ Motor MYCIN integrado</span>
        </div>
      </div>
    </div>


    <div id="input-area">
      <button id="btn-start" onclick="iniciarChat()">
        💬 &nbsp;Iniciar Conversa com o Assistente
      </button>
      <div id="input-row" style="display:none">
        <textarea id="msg-input" placeholder="Descreva os seus sintomas…" rows="1"
                  onkeydown="handleKey(event)" oninput="autoResize(this)" disabled></textarea>
        <button id="btn-send" onclick="enviar()" disabled>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
          Enviar
        </button>
      </div>
    </div>
  </main>
</div>


<script>
const API = 'http://localhost:8081';
let sessionId = null;
let busy      = false;


// ── STATUS ──────────────────────────────────────────────────────────────────
async function verificarStatus() {
  const pill = document.getElementById('status-pill');
  const txt  = document.getElementById('status-txt');
  try {
    const r = await fetch(`${API}/api/chat/status`);
    const d = await r.json();
    if (d.ollama && d.model_ready) {
      pill.className = 'status-pill ok';
      txt.textContent = `${d.model} · pronto`;
    } else if (d.ollama) {
      pill.className = 'status-pill warn';
      txt.textContent = 'Modelo não encontrado';
      mostrarErro(`Modelo "${d.model || 'llama3.2:3b'}" não encontrado. Corra: ollama pull llama3.2:3b`);
    } else {
      pill.className = 'status-pill err';
      txt.textContent = 'Ollama offline';
      mostrarErro('Ollama não está a correr. Inicie com: ollama serve');
    }
  } catch {
    pill.className = 'status-pill err';
    txt.textContent = 'Chatbot offline';
    mostrarErro('Servidor chatbot offline. Inicie com: python chatbot_server.py');
  }
}


// ── INICIAR ──────────────────────────────────────────────────────────────────
async function iniciarChat() {
  document.getElementById('btn-start').style.display = 'none';
  document.getElementById('input-row').style.display  = 'flex';


  setBusy(true);
  adicionarTyping();
  try {
    const r = await fetch(`${API}/api/chat/start`, {method:'POST'});
    const d = await r.json();
    removerTyping();
    sessionId = d.session_id;
    adicionarMsgBot(d.message);
    setBusy(false);
  } catch {
    removerTyping();
    mostrarErro('Não foi possível iniciar. Verifique se o chatbot_server.py está a correr.');
    setBusy(false);
    document.getElementById('btn-start').style.display = 'block';
    document.getElementById('input-row').style.display  = 'none';
  }
}


// ── ENVIAR ───────────────────────────────────────────────────────────────────
async function enviar() {
  if (busy || !sessionId) return;
  const inp = document.getElementById('msg-input');
  const msg = inp.value.trim();
  if (!msg) return;


  adicionarMsgUser(msg);
  inp.value = '';
  autoResize(inp);
  setBusy(true);
  adicionarTyping();


  try {
    const r = await fetch(`${API}/api/chat/message`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session_id: sessionId, message: msg}),
    });
    const d = await r.json();
    removerTyping();
    adicionarMsgBot(d.message);
    atualizarSintomas(d.sintomas || []);
    if (d.resultado_prolog) mostrarResultado(d.resultado_prolog);
  } catch(e) {
    removerTyping();
    mostrarErro('Erro de comunicação: ' + e.message);
  }
  setBusy(false);
}


function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }
}


function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}


// ── UI ───────────────────────────────────────────────────────────────────────
function setBusy(v) {
  busy = v;
  document.getElementById('msg-input').disabled = v;
  document.getElementById('btn-send').disabled   = v;
}


function scrollBottom() {
  const f = document.getElementById('feed');
  requestAnimationFrame(() => f.scrollTop = f.scrollHeight);
}


function esc(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}


function md(text) {
  // Markdown mínimo: bold, itálico, listas, parágrafos
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');
}


function adicionarMsgUser(txt) {
  const f    = document.getElementById('feed');
  const wrap = document.createElement('div');
  wrap.className = 'msg-wrap user';
  wrap.innerHTML = `<div class="msg-bubble">${esc(txt)}</div>`;
  f.appendChild(wrap);
  scrollBottom();
}


function adicionarMsgBot(txt) {
  const f    = document.getElementById('feed');
  const wrap = document.createElement('div');
  const isEm = /112|emergência|chame o 112|ligue o 112/i.test(txt);
  wrap.className = 'msg-wrap bot';
  wrap.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="msg-bubble${isEm ? ' emergency' : ''}">${md(txt)}</div>`;
  f.appendChild(wrap);
  scrollBottom();
}


function adicionarTyping() {
  const f    = document.getElementById('feed');
  const wrap = document.createElement('div');
  wrap.className = 'msg-wrap bot';
  wrap.id        = 'typing-ind';
  wrap.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="typing-bubble">
      <div class="dot-anim"></div>
      <div class="dot-anim"></div>
      <div class="dot-anim"></div>
    </div>`;
  f.appendChild(wrap);
  scrollBottom();
}


function removerTyping() {
  const el = document.getElementById('typing-ind');
  if (el) el.remove();
}


function mostrarErro(msg) {
  const f = document.getElementById('feed');
  const d = document.createElement('div');
  d.className = 'sys-err';
  d.innerHTML = `⚠️ ${esc(msg)}`;
  f.appendChild(d);
  scrollBottom();
}


// ── SIDEBAR: SINTOMAS ────────────────────────────────────────────────────────
function atualizarSintomas(sintomas) {
  const el = document.getElementById('sint-list');
  const presentes = (sintomas || []).filter(s => s.presente);
  if (!presentes.length) {
    el.innerHTML = '<div class="sint-empty">Nenhum sintoma identificado ainda.</div>';
    return;
  }
  el.innerHTML = presentes.map(s => `
    <div class="sint-item sint-pres">
      <div class="sint-dot"></div>
      <span>${esc(s.nome)}</span>
    </div>`).join('');
}


// ── SIDEBAR: RESULTADO MYCIN ─────────────────────────────────────────────────
const NIVEL_CORES = {
  emergencia:          {cor:'#dc2626', bg:'#fff5f5', label:'🔴 EMERGÊNCIA'},
  muito_urgente:       {cor:'#ea580c', bg:'#fff7ed', label:'🟠 MUITO URGENTE'},
  urgente:             {cor:'#d97706', bg:'#fffbeb', label:'🟡 URGENTE'},
  pouco_urgente:       {cor:'#2563eb', bg:'#eff6ff', label:'🔵 POUCO URGENTE'},
  sem_sintomas_alarme: {cor:'#059669', bg:'#f0fdf4', label:'🟢 SEM ALARME'},
};


function mostrarResultado(res) {
  const el = document.getElementById('resultado-content');
  if (!res || res.type !== 'resultado') {
    el.innerHTML = '<div class="res-vazio">Motor MYCIN: sem resultado disponível.</div>';
    return;
  }
  const nid = res.nivel_id && NIVEL_CORES[res.nivel_id] ? res.nivel_id : null;
  const c   = nid ? NIVEL_CORES[nid] : {cor:'#6b7280', bg:'#f9fafb', label: res.nivel || '-'};
  const cfLabel = res.python_mycin
    ? `${res.confianca_pct || 0}% <span style="font-weight:400;font-size:11px">(motor Python - Prolog indisponível)</span>`
    : `${res.confianca_pct || 0}%`;
  el.innerHTML = `
    <div class="res-card" style="border-color:${c.cor};background:${c.bg}">
      <div class="res-nivel" style="color:${c.cor}">${c.label}</div>
      <div class="res-rec">${esc(res.recomendacao || '')}</div>
      <div class="res-cf" style="color:${c.cor}">${cfLabel}</div>
      <div class="res-cf-lbl">Confiança MYCIN</div>
      <div class="res-mycin-badge">⚙️ Motor MYCIN (Parte A)</div>
    </div>`;
}


// ── INIT ─────────────────────────────────────────────────────────────────────
verificarStatus();
setInterval(verificarStatus, 30000);
</script>
</body>
</html>

exportar_kb.py:
"""
Exporta a base de conhecimento RAG do chatbot para kb_chatbot.txt.
Usa exactamente a mesma função construir_conhecimento() do chatbot_server.py.


Uso: python exportar_kb.py
"""
from chatbot_server import construir_conhecimento, KB_A, KB_B


docs = construir_conhecimento(KB_A, KB_B)


output = "BASE DE CONHECIMENTO RAG - SNS24 CHATBOT\n"
output += "Gerado automaticamente a partir de base_conhecimento_a.pl + base_conhecimento_b.pl\n"
output += "=" * 60 + "\n\n"


for i, doc in enumerate(docs, 1):
    output += f"[{i}]\n{doc}\n\n" + "-" * 60 + "\n\n"


with open("kb_chatbot.txt", "w", encoding="utf-8") as f:
    f.write(output)


print(f"Exportado: kb_chatbot.txt ({len(docs)} documentos)")

kb_chatbot.txt:
BASE DE CONHECIMENTO RAG - SNS24 CHATBOT
Gerado automaticamente a partir de base_conhecimento_a.pl + base_conhecimento_b.pl
============================================================

[1]
Protocolo SNS24: os sintomas são avaliados por ordem de gravidade.
EMERGÊNCIA → ligar 112 imediatamente.
MUITO URGENTE → ir à urgência hospitalar agora.
URGENTE → consultar médico ou centro de saúde em 24 horas.
POUCO URGENTE → tratar em casa, vigiar.
SEM ALARME → vigiar em casa; ligar SNS24 (808 24 24 24) se piorar.

------------------------------------------------------------

[2]
Paragem respiratoria (nao respira de todo) → EMERGENCIA. Ligue 112 (INEM) imediatamente. Paragem respiratoria requer suporte basico de vida imediato.

------------------------------------------------------------

[3]
Paragem cardiaca (sem pulso detectavel) → EMERGENCIA. Ligue 112 (INEM) imediatamente. Paragem cardiaca necessita de reanimacao e chamada ao 112.

------------------------------------------------------------

[4]
Falta de ar grave (nao consegue falar ou cor azulada) → EMERGENCIA. Ligue 112 (INEM) imediatamente. Falta de ar grave e coloracao azulada indicam hipoxia severa.

------------------------------------------------------------

[5]
Hemorragia abundante e incontrolavel → EMERGENCIA. Ligue 112 (INEM) imediatamente. Hemorragias activas podem levar a choque hipovolemico.

------------------------------------------------------------

[6]
Alteracao da consciencia (nao responde ou sonolencia marcada) → EMERGENCIA. Ligue 112 (INEM) imediatamente. Alteracao de consciencia profunda sugere lesao ou doenca grave.

------------------------------------------------------------

[7]
Convulsoes ou contracoes involuntarias do corpo → EMERGENCIA. Ligue 112 (INEM) imediatamente. Convulsoes activas comprometem a via aerea, causam hipoxia e indicam emergencia neurologica.

------------------------------------------------------------

[8]
Febre acima de 39 graus Celsius, Confusao mental ou desorientacao subita, Dor abdominal muito intensa e persistente → EMERGENCIA. Ligue 112 (INEM) imediatamente. Febre alta + confusao + dor abdominal e o triade classica de sepsis, infeccao disseminada com risco de falencia multiorganica imediata.

------------------------------------------------------------

[9]
Dor no centro do peito ha mais de 10 minutos, A dor irradia para o braco, mandibula ou costas → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Dor no peito com irradiacao e o quadro classico de enfarte do miocardio.

------------------------------------------------------------

[10]
Dor no centro do peito ha mais de 10 minutos → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Dor no peito isolada pode ser cardiaca, requerendo avaliacao muito urgente.

------------------------------------------------------------

[11]
Dificuldade subita em falar ou fala arrastada → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Dificuldade repentina na fala e um sinal de alerta de Acidente Vascular Cerebral (AVC).

------------------------------------------------------------

[12]
Fraqueza subita num so lado do corpo ou boca ao lado → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Fraqueza unilateral do corpo e fortemente indicativa de AVC.

------------------------------------------------------------

[13]
Dor abdominal muito intensa e persistente (sem Febre acima de 39 graus Celsius) → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Dor abdominal intensa sem febre pode significar abdomen agudo (ex: apendicite, colica renal).

------------------------------------------------------------

[14]
Confusao mental ou desorientacao subita → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. A confusao mental subita indica grave alteracao neurologica, metabolica ou infecciosa, independentemente de existir febre.

------------------------------------------------------------

[15]
Dificuldade subita em falar ou fala arrastada, Fraqueza subita num so lado do corpo ou boca ao lado → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Dificuldade na fala combinada com fraqueza unilateral e o padrao FAST classico de AVC, a combinacao eleva a certeza diagnostica acima de cada sinal isolado.

------------------------------------------------------------

[16]
Febre acima de 39 graus Celsius, Dor abdominal muito intensa e persistente → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Febre alta associada a dor abdominal intensa, na ausencia de confusao, pode indicar infeccao com foco cirurgico (apendicite com febre, colecistite aguda, pielonefrite grave).

------------------------------------------------------------

[17]
Febre em bebe com menos de 3 meses → URGENTE. Marque consulta no centro de saude em 24h. A febre em bebes menores de 3 meses e sempre um sinal de alerta (sistema imunitario imaturo).

------------------------------------------------------------

[18]
Febre acima de 39 graus Celsius, Tosse acompanhada de febre → URGENTE. Marque consulta no centro de saude em 24h. Febre alta combinada com tosse levanta a suspeita de pneumonia.

------------------------------------------------------------

[19]
Vomitos repetidos que impedem ingerir liquidos, Diarreia grave com sinais de desidratacao → URGENTE. Marque consulta no centro de saude em 24h. Vomitos e diarreia simultaneos acarretam um alto risco de desidratacao.

------------------------------------------------------------

[20]
Febre acima de 39 graus Celsius → URGENTE. Marque consulta no centro de saude em 24h. Febre alta persistente requer investigacao de foco infeccioso.

------------------------------------------------------------

[21]
Dor moderada que nao cede a medicacao → URGENTE. Marque consulta no centro de saude em 24h. Dor que nao cede aos analgesicos precisa de reavaliacao medica.

------------------------------------------------------------

[22]
Dor de garganta com dificuldade em engolir → URGENTE. Marque consulta no centro de saude em 24h. Dificuldade em engolir acompanhada de dor pode indicar infeccao severa na garganta ou abscesso periamigdalino, com risco de compromisso da via aerea.

------------------------------------------------------------

[23]
Febre em bebe com menos de 3 meses, Vomitos repetidos que impedem ingerir liquidos, Diarreia grave com sinais de desidratacao → MUITO URGENTE. Dirija-se a urgencia hospitalar agora. Bebe febril com perda de liquidos por vomitos E diarreia enfrenta risco critico de desidratacao severa.

------------------------------------------------------------

[24]
Febre acima de 39 graus Celsius, Tosse acompanhada de febre, Dor moderada que nao cede a medicacao → URGENTE. Marque consulta no centro de saude em 24h. Febre alta com tosse e dor que nao cede a analgesicos aponta para infeccao respiratoria profunda (ex: pneumonia bacteriana), que pode necessitar de antibioterapia urgente.

------------------------------------------------------------

[25]
Dor abdominal muito intensa e persistente (sem Vomitos repetidos que impedem ingerir liquidos, Diarreia grave com sinais de desidratacao) → URGENTE. Marque consulta no centro de saude em 24h. Dor abdominal sem vomitos nem diarreia afasta a gastroenterite como causa.

------------------------------------------------------------

[26]
Sintomas de constipacao (tosse ligeira, nariz entupido) → POUCO URGENTE. Autocuidados em casa, vigiar evolucao. Sintomas gripais ligeiros devem ser autotratados com repouso.

------------------------------------------------------------

[27]
Dor ligeira controlada com medicacao habitual → POUCO URGENTE. Autocuidados em casa, vigiar evolucao. Dores ligeiras que cedem a medicacao nao requerem idas urgentes ao hospital.

------------------------------------------------------------

[28]
Febre baixa, abaixo de 38 graus Celsius → POUCO URGENTE. Autocuidados em casa, vigiar evolucao. Febres baixas sao normalmente autolimitadas e respondem a antipireticos em casa.

------------------------------------------------------------

[29]
Dor ligeira controlada com medicacao habitual, Mal-estar geral sem sintomas especificos → POUCO URGENTE. Autocuidados em casa, vigiar evolucao. Mal-estar com dor ligeira e controlada consolida um quadro benigno, o medico de familia e o destino adequado, nao a urgencia hospitalar.

------------------------------------------------------------

[30]
Mal-estar geral sem sintomas especificos → SEM ALARME. Vigiar; contactar SNS24 se piorar. O mal-estar geral sem alarmes deve ser apenas vigiado em casa.

------------------------------------------------------------

[31]
Sintomas de constipacao (tosse ligeira, nariz entupido), Febre baixa, abaixo de 38 graus Celsius → SEM ALARME. Vigiar; contactar SNS24 se piorar. Constipacao com febre baixa e o quadro viral autolimitado mais tipico, medicacao de venda livre e habitualmente suficiente.

------------------------------------------------------------

[32]
Dor ligeira controlada com medicacao habitual, Mal-estar geral sem sintomas especificos (sem Febre acima de 39 graus Celsius) → POUCO URGENTE. Autocuidados em casa, vigiar evolucao. Padrao ML (POUCO URGENTE, confianca=100%, n=9): presenca de dor ligeira, mal-estar geral; ausencia de febre alta (>39C). [padrão aprendido automaticamente]

------------------------------------------------------------

[33]
Dor ligeira controlada com medicacao habitual (sem Febre acima de 39 graus Celsius, Mal-estar geral sem sintomas especificos) → POUCO URGENTE. Autocuidados em casa, vigiar evolucao. Padrao ML (POUCO URGENTE, confianca=76%, n=18): presenca de dor ligeira; ausencia de febre alta (>39C), mal-estar geral. [padrão aprendido automaticamente]

------------------------------------------------------------

[34]
Sintomas de constipacao (tosse ligeira, nariz entupido), Febre baixa, abaixo de 38 graus Celsius (sem Dor ligeira controlada com medicacao habitual) → SEM ALARME. Vigiar; contactar SNS24 se piorar. Padrao ML (SEM ALARME, confianca=89%, n=14): presenca de constipacao, febre baixa; ausencia de dor ligeira. [padrão aprendido automaticamente]

------------------------------------------------------------

[35]
Mal-estar geral sem sintomas especificos (sem Dor ligeira controlada com medicacao habitual, Sintomas de constipacao (tosse ligeira, nariz entupido)) → SEM ALARME. Vigiar; contactar SNS24 se piorar. Padrao ML (SEM ALARME, confianca=72%, n=24): presenca de mal-estar geral; ausencia de dor ligeira, constipacao. [padrão aprendido automaticamente]

------------------------------------------------------------

[36]
Sintomas que indicam EMERGENCIA:
  - Paragem respiratoria (nao respira de todo): A ausencia de respiracao e a emergencia medica mais critica, exigindo inicio imediato de Suporte Basico de Vida
  - Paragem cardiaca (sem pulso detectavel): A paragem cardiaca requer reanimacao imediata para tentar restabelecer o fluxo sanguineo ao cerebro
  - Falta de ar grave (nao consegue falar ou cor azulada): A dificuldade grave em respirar pode indicar falencia respiratoria, o que representa um risco imediato de vida
  - Hemorragia abundante e incontrolavel: A perda rapida e incontrolavel de sangue pode levar rapidamente ao choque hipovolemico
  - Alteracao da consciencia (nao responde ou sonolencia marcada): A perda de consciencia indica grave sofrimento cerebral, podendo ser trauma, AVC ou intoxicacao
  - Convulsoes ou contracoes involuntarias do corpo: As convulsoes activas comprometem a via aerea, causam hipoxia e indicam uma emergencia neurologica aguda que requer chamada imediata ao 112

------------------------------------------------------------

[37]
Sintomas que indicam MUITO URGENTE:
  - Dor no centro do peito ha mais de 10 minutos: A dor no peito e o sintoma primario de alerta para avaliar a hipotese de um Enfarte do Miocardio (ataque cardiaco)
  - A dor irradia para o braco, mandibula ou costas: A irradiacao da dor no peito para os membros ou costas e um padrao que reforca muito a suspeita de origem cardiaca
  - Dificuldade subita em falar ou fala arrastada: A dificuldade subita em articular palavras e um dos principais sinais de alerta de um possivel AVC
  - Fraqueza subita num so lado do corpo ou boca ao lado: A perda de forca num dos lados do corpo e um sintoma neurologico classico de isquemia ou hemorragia cerebral
  - Confusao mental ou desorientacao subita: A confusao mental subita pode ser sinal de infeccao grave (meningite, sepsis), falta de oxigenio ou alteracao neurologica abrupta
  - Dor abdominal muito intensa e persistente: Dores abdominais subitas e muito intensas podem indicar condicoes agudas graves, como apendicite ou perfuracao de orgaos

------------------------------------------------------------

[38]
Sintomas que indicam URGENTE:
  - Febre acima de 39 graus Celsius: Febres muito elevadas (acima de 39 graus) sugerem infeccoes que podem requerer intervencao medica ou antibioticos
  - Febre em bebe com menos de 3 meses: Os bebes tem um sistema imunitario imaturo, pelo que a febre requer sempre avaliacao medica urgente para despiste de infeccoes
  - Tosse acompanhada de febre: A tosse associada a febre levanta a forte suspeita de infeccoes respiratorias, como a pneumonia
  - Dor moderada que nao cede a medicacao: Uma dor que nao cede a medicacao de alivio habitual sugere um quadro inflamatorio ou lesivo que necessita de diagnostico formal
  - Vomitos repetidos que impedem ingerir liquidos: A incapacidade repetida de reter liquidos no estomago leva rapidamente a desidratacao severa
  - Diarreia grave com sinais de desidratacao: A perda de grandes volumes de liquidos pelos intestinos comporta um alto risco de desidratacao e desequilibrio electrolitico
  - Dor de garganta com dificuldade em engolir: Se acompanhada de grande dificuldade em engolir, pode indicar abscesso periamigdalino ou epiglotite, infeccoes que ameacam bloquear a via aerea

------------------------------------------------------------

[39]
Sintomas que indicam POUCO URGENTE:
  - Sintomas de constipacao (tosse ligeira, nariz entupido): Sintomas tipicos de constipacao ajudam a enquadrar o quadro como uma provavel infeccao viral benigna, sem gravidade
  - Dor ligeira controlada com medicacao habitual: Dores de baixa intensidade e facilmente controlaveis geralmente nao indicam problemas com os seus orgaos vitais
  - Febre baixa, abaixo de 38 graus Celsius: Temperaturas moderadas sao a resposta natural de defesa do corpo a pequenas agressoes virais ou inflamatorias
  - Mal-estar geral sem sintomas especificos: Sentir-se indisposto de forma vaga, sem sinais de alarme, ajuda-nos a confirmar a ausencia de quadros clinicos urgentes

------------------------------------------------------------


Anexo B
CONTRATO DE GRUPO Projecto 2 - Sistemas Inteligentes de Apoio à Decisão Universidade do Minho, Escola de Ciências - Semestre 2 2025/2026
Elementos do Grupo
Nome
Número
Alexandr Tchikoulaev
A103625
André Pinto
A106825
João Alves
A102394
Rui Silva
A106831


1. Compromisso de Participação
Todos os elementos do grupo comprometem-se a participar activamente no desenvolvimento do projecto, contribuindo para a análise do problema, aquisição de conhecimento e desenvolvimento técnico das componentes que lhes forem atribuídas.
2. Meios de Comunicação
A comunicação entre os elementos do grupo é realizada através de mensagens no WhatsApp para assuntos do dia-a-dia e através de reuniões em formato online via Discord para discussões mais estruturadas.
3. Reuniões
O grupo estabelece uma reunião semanal após a aula prática, destinada a sincronizar o progresso de cada elemento, identificar bloqueios e definir as tarefas para a semana seguinte.
4. Resolução de Incumprimento
Caso um elemento não cumpra as tarefas acordadas, o grupo abordará directamente o elemento em questão na reunião seguinte, identificando o problema e estabelecendo um prazo para a conclusão do trabalho em falta até à reunião subsequente.
5. Assinaturas
Ao assinar este documento, cada elemento confirma que leu, compreendeu e aceita os termos aqui estabelecidos.
 
Alexandr Tchikoulaev Alexandr Tchikoulaev Data: // 20-2-2026
André Pinto André Pinto Data: // 20-2-2026
João Alves João Alves Data: // 20-2-2026
Rui Silva Rui Silva Data: // 20-2-2026


Bibliografia
[1] Shortliffe, E.H. (1976). Computer-Based Medical Consultations: MYCIN. Elsevier.
[2] Russell, S. e Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4.ª ed.). Pearson.
[3] SNS24 (2024). Protocolos de Triagem Altitude - Fluxogramas de Sintomas. Serviço Nacional de Saúde.
[4] Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825–2830.
[5] Witten, I.H., Frank, E. e Hall, M.A. (2011). Data Mining: Practical Machine Learning Tools and Techniques (3.ª ed.). Morgan Kaufmann.
[6] Covington, M.A. (1994). Natural Language Processing for Prolog Programmers. Prentice Hall.
[7] Meta AI (2024). Llama 3.2: Multilingual Large Language Models. Meta AI Research.
[8] Ollama (2024). Ollama - Run Large Language Models Locally. Documentação oficial em https://ollama.com.
[9] FastAPI (2024). FastAPI - Modern, Fast Web Framework for Building APIs with Python. Documentação oficial em https://fastapi.tiangolo.com.
