% BASE DE CONHECIMENTO B - Triagem SNS24 (Gerada por ML)
% Gerado automaticamente em: 2026-05-01 19:03:07
% Dataset: triagens.csv (367 exemplos)
% Modelos: Random Forest (200 arvores), Decision Tree (max_depth=4)
% Filtros: CF >= 0.6, n_amostras >= 5

:- multifile regra/4.
:- multifile explicacao_regra/2.
:- discontiguous regra/4.
:- discontiguous explicacao_regra/2.

% Sintomas ordenados por feature importance (RF) + bonus clinico de prioridade.
ordem_sintomas_ml([
    sem_pulso, hemorragia, sem_respiracao, resp_dificuldade,
    convulsoes, inconsciente, confusao, fala_dificil,
    fraqueza_lado, dor_peito, dor_irradia, dor_abd,
    febre_alta, febre_bebe, tosse_febre, dor_persiste,
    diarreia, dor_garganta, vomitos, dor_leve,
    febre_baixa, constipacao, mal_estar
]).

% ----------------------------------------------------------------
% REGRAS GERADAS PELA DECISION TREE
% IDs dt_NNN distinguem-se dos r_XXX manuais da Parte A.
% O motor combina-as automaticamente via findall sobre regra/4.
% ----------------------------------------------------------------

% POUCO URGENTE
% CF=1.00, n=9
regra(dt_001, se([dor_leve, nao(febre_alta), mal_estar]), entao(pouco_urgente), 1.0).
explicacao_regra(dt_001, 'Padrao ML (POUCO URGENTE, confianca=100%, n=9): presenca de dor ligeira, mal-estar geral; ausencia de febre alta (>39C).').

% CF=0.76, n=18
regra(dt_002, se([dor_leve, nao(febre_alta), nao(mal_estar)]), entao(pouco_urgente), 0.76).
explicacao_regra(dt_002, 'Padrao ML (POUCO URGENTE, confianca=76%, n=18): presenca de dor ligeira; ausencia de febre alta (>39C), mal-estar geral.').

% SEM ALARME
% CF=0.89, n=14
regra(dt_003, se([nao(dor_leve), constipacao, febre_baixa]), entao(sem_sintomas_alarme), 0.89).
explicacao_regra(dt_003, 'Padrao ML (SEM ALARME, confianca=89%, n=14): presenca de constipacao, febre baixa; ausencia de dor ligeira.').

% CF=0.72, n=24
regra(dt_004, se([nao(dor_leve), nao(constipacao), mal_estar]), entao(sem_sintomas_alarme), 0.72).
explicacao_regra(dt_004, 'Padrao ML (SEM ALARME, confianca=72%, n=24): presenca de mal-estar geral; ausencia de dor ligeira, constipacao.').

