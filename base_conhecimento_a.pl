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
regra(r_ur5, se([dor_persiste]),                            entao(urgente), 0.40).
regra(r_ur6, se([dor_garganta]),                            entao(urgente), 0.55).
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

% Confusao + febre alta sem dor abdominal: padrao de meningite ou encefalite (nao sepsis)
regra(r_mu10, se([confusao, febre_alta, nao(dor_abd)]),  entao(muito_urgente), 0.85).
% Dificuldade respiratoria com febre alta: suspeita de pneumonia grave ou sepsis respiratoria
regra(r_em8,  se([resp_dificuldade, febre_alta]),         entao(emergencia),    0.87).

% POUCO URGENTE
regra(r_pu1, se([constipacao]),           entao(pouco_urgente), 0.70).
regra(r_pu2, se([dor_leve]),              entao(pouco_urgente), 0.65).
regra(r_pu3, se([febre_baixa]),           entao(pouco_urgente), 0.60).
regra(r_pu4, se([dor_leve, mal_estar]),   entao(pouco_urgente), 0.70).

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
explicacao_regra(r_ur5, 'Dor que nao cede aos analgesicos precisa de reavaliacao medica.').
explicacao_regra(r_ur6, 'Dificuldade em engolir acompanhada de dor pode indicar infeccao severa na garganta ou abscesso periamigdalino, com risco de compromisso da via aerea.').
explicacao_regra(r_ur7, 'Bebe febril com perda de liquidos por vomitos E diarreia enfrenta risco critico de desidratacao severa. As reservas de um lactente esgotam-se em horas. Este quadro justifica ida imediata a urgencia hospitalar.').
explicacao_regra(r_ur8, 'Febre alta com tosse e dor que nao cede a analgesicos aponta para infeccao respiratoria profunda (ex: pneumonia bacteriana), que pode necessitar de antibioterapia urgente.').
explicacao_regra(r_ur9, 'Dor abdominal sem vomitos nem diarreia afasta a gastroenterite como causa. A ausencia de sintomas gastrointestinais com dor intensa sugere origem cirurgica ou urologica (apendicite, colica renal ou colecistite) que requer avaliacao medica presencial urgente.').
explicacao_regra(r_ur10, 'Vomitos repetidos sem diarreia comprometem a hidratacao por via gastrica isolada. A incapacidade de ingerir liquidos pode exigir reposicao intravenosa.').
explicacao_regra(r_ur13, 'Diarreia grave ja implica, por definicao, sinais de desidratacao. Sem vomitos ha margem para hidratacao oral supervisionada, mas a vigilancia medica e necessaria.').
explicacao_regra(r_ur11, 'Dor de garganta associada a febre alta levanta suspeita de amigdalite bacteriana por estreptococo, que pode exigir antibioterapia e avaliar o risco de abscesso.').
explicacao_regra(r_ur12, 'Bebe febril com vomitos repetidos enfrenta risco elevado de desidratacao rapida. As reservas de um lactente esgotam-se em poucas horas, justificando avaliacao hospitalar urgente mesmo sem diarreia simultanea.').
explicacao_regra(r_mu10, 'Confusao mental associada a febre alta sem dor abdominal e o padrao clinico de meningite bacteriana ou encefalite viral. Estas infeccoes do sistema nervoso central sao emergencias neurologicas mesmo sem o quadro abdominal de sepsis.').
explicacao_regra(r_em8, 'Dificuldade respiratoria grave com febre alta levanta a suspeita de pneumonia severa ou sepsis de foco pulmonar, ambas com risco de falencia respiratoria iminente e indicacao para avaliacao hospitalar imediata.').

% Pouco urgente / sem alarme
explicacao_regra(r_pu1, 'Sintomas gripais ligeiros devem ser autotratados com repouso.').
explicacao_regra(r_pu2, 'Dores ligeiras que cedem a medicacao nao requerem idas urgentes ao hospital.').
explicacao_regra(r_pu3, 'Febres baixas sao normalmente autolimitadas e respondem a antipireticos em casa.').
explicacao_regra(r_pu4, 'Mal-estar com dor ligeira e controlada consolida um quadro benigno, o medico de familia e o destino adequado, nao a urgencia hospitalar.').
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
explicacao(_, 'Este sintoma e avaliado no nosso modelo clinico para afastar condicoes potencialmente graves.').

% ----------------------------------------------------------------
% ORDEM DE QUESTIONAMENTO
% febre_alta antes de confusao e dor_abd para r_em6/r_mu9 dispararem mais cedo.
% ----------------------------------------------------------------
ordem_sintomas([
    sem_respiracao, sem_pulso, resp_dificuldade, hemorragia, inconsciente,
    convulsoes, dor_peito, dor_irradia, fala_dificil, fraqueza_lado,
    febre_alta, confusao, dor_abd, febre_bebe,
    tosse_febre, dor_persiste, vomitos, diarreia,
    dor_garganta, constipacao, dor_leve, febre_baixa, mal_estar
]).