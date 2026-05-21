% Motor de inferencia MYCIN para triagem SNS24.
%
% Combinacao de CFs (AND = min; multiplas regras = formula MYCIN positiva):
%   CF1 + CF2 - (CF1 * CF2)
%   (so evidencia positiva chega aqui; CFs negativos bloqueiam regras ou
%    satisfazem premissas nao(S) via abs(), nunca entram na combinacao)

todos_niveis([sem_sintomas_alarme, pouco_urgente, urgente, muito_urgente, emergencia]).
limiar_saida(0.80).

% Usa ordem_sintomas_ml/1 (ML) se disponivel, senao recorre a ordem_sintomas/1 (manual).
obter_ordem_sintomas(Sintomas) :-
    ( predicate_property(ordem_sintomas_ml(_), defined) ->
        ordem_sintomas_ml(Sintomas)
    ;
        ordem_sintomas(Sintomas)
    ).

% ----------------------------------------------------------------
% PONTO DE ENTRADA
% diagnostico/1 devolve NivelId para guardar no CSV.
% ----------------------------------------------------------------
diagnostico(NivelId) :-
    nl,
    write('----------------------------------------------------'), nl,
    write('Triagem iniciada. O sistema ira fazer perguntas.'), nl,
    write('Primeiro responda se tem ou nao o sintoma:'), nl,
    write('  s. = SIM (tem o sintoma)'), nl,
    write('  n. = NAO (nao tem o sintoma)'), nl,
    write('  t. = NAO SEI (desconhecimento total, CF=0.0)'), nl,
    write('  p. = PORQUE esta pergunta?'), nl,
    write('De seguida, ser-lhe-a pedida a certeza de 0 a 100.'), nl,
    write('(Lembre-se: Terminar sempre as respostas com ponto final)'), nl,
    write('----------------------------------------------------'), nl,
    obter_ordem_sintomas(Sintomas),
    todos_niveis(Niveis),
    limiar_saida(Limiar),
    perguntar_sintomas(Sintomas, Niveis, Limiar, NivelId).

perguntar_sintomas([], Niveis, _, NivelId) :-
    calcular_scores_finais(Niveis, Scores),
    mostrar_resultado(Scores, NivelId).

perguntar_sintomas([S|Resto], Niveis, Limiar, NivelId) :-
    perguntar(S),
    ( atingiu_limiar_nivel(Limiar) ->
        calcular_scores_finais(Niveis, Scores),
        mostrar_resultado(Scores, NivelId)
    ;
        perguntar_sintomas(Resto, Niveis, Limiar, NivelId)
    ).

% Saida antecipada baseada no score COMBINADO de nivel (nao por regra isolada).
atingiu_limiar_nivel(Limiar) :-
    todos_niveis(Niveis),
    calcular_scores_finais(Niveis, Scores),
    member(_-CF, Scores),
    CF >= Limiar, !.

% ----------------------------------------------------------------
% MOTOR DE REGRAS
% ----------------------------------------------------------------

avaliar_regra(IdRegra, Nivel, CF_Final) :-
    regra(IdRegra, se(Sintomas), entao(Nivel), CF_BaseRegra),
    avaliar_premissas(Sintomas, 1.0, CF_Premissas),
    CF_Premissas > 0,
    CF_Final is CF_Premissas * CF_BaseRegra.

% AND sobre premissas: CF acumulado = min(CFs dos sintomas confirmados).
avaliar_premissas([], CF, CF).

avaliar_premissas([S|T], CF_Atual, CF_Final) :-
    \+ functor(S, nao, 1),
    facto(S, CF_Sintoma),
    CF_Sintoma > 0,
    NovoCF is min(CF_Atual, CF_Sintoma),
    avaliar_premissas(T, NovoCF, CF_Final).

% nao(S) e satisfeita quando S foi explicitamente negado (CF < 0).
avaliar_premissas([nao(S)|T], CF_Atual, CF_Final) :-
    facto(S, CF_Sintoma),
    CF_Sintoma < 0, !,
    NovoCF is min(CF_Atual, abs(CF_Sintoma)),
    avaliar_premissas(T, NovoCF, CF_Final).

% nao(S) falha se S nao foi negado (conservador).
avaliar_premissas([nao(_)|_], _, 0) :- !.

% CF <= 0 ou sintoma nao perguntado: regra nao dispara.
avaliar_premissas([S|_], _, 0) :-
    \+ functor(S, nao, 1), \+ facto(S, _).
avaliar_premissas([S|_], _, 0) :-
    \+ functor(S, nao, 1), facto(S, CF), CF =< 0.

% ----------------------------------------------------------------
% SCORES E COMBINACAO MYCIN
% ----------------------------------------------------------------

calcular_scores_finais([], []).
calcular_scores_finais([N|Ns], [N-CF_Final|Rest]) :-
    findall(CF, avaliar_regra(_, N, CF), ListaCFs),
    combinar_cfs(ListaCFs, CF_Final),
    calcular_scores_finais(Ns, Rest).

combinar_cfs([], 0.0).
combinar_cfs([CF], CF) :- !.
combinar_cfs([CF1, CF2 | T], Result) :-
    combinar_dois_cfs(CF1, CF2, CF_Comb),
    combinar_cfs([CF_Comb | T], Result).

combinar_dois_cfs(CF1, CF2, Res) :-
    CF1 > 0, CF2 > 0,
    Res is CF1 + CF2 - (CF1 * CF2).

% ----------------------------------------------------------------
% APRESENTACAO
% ----------------------------------------------------------------

score_maximo([N-S|Rest], BestN, BestS) :-
    score_maximo_aux(Rest, N, S, BestN, BestS).

score_maximo_aux([], BN, BS, BN, BS).
score_maximo_aux([N-S|Rest], CurN, CurS, BestN, BestS) :-
    ( S > CurS -> score_maximo_aux(Rest, N, S, BestN, BestS)
    ; score_maximo_aux(Rest, CurN, CurS, BestN, BestS) ).

barra_progresso(Score) :-
    Blocos is round(Score * 10),
    Vazios is 10 - Blocos,
    write('  ['),
    imprimir_n_vezes(Blocos, '#'),
    imprimir_n_vezes(Vazios, '-'),
    write('] ').

imprimir_n_vezes(0, _) :- !.
imprimir_n_vezes(N, C) :-
    N > 0, write(C),
    N1 is N - 1,
    imprimir_n_vezes(N1, C).

mostrar_resultado(Scores, NivelId) :-
    score_maximo(Scores, NivelId0, ScoreMax),
    ( ScoreMax < 0.05 -> NivelId = sem_sintomas_alarme ; NivelId = NivelId0 ),
    nivel(NivelId, NivelTexto, Recomendacao),
    Pct is round(ScoreMax * 100),
    nl,
    write('========================================'), nl,
    write('         RESULTADO DA TRIAGEM           '), nl,
    write('========================================'), nl,
    format('Nivel:        ~w~n', [NivelTexto]),
    format('Confianca:    ~w%~n', [Pct]),
    format('Recomendacao: ~w~n', [Recomendacao]),
    nl,
    write('Scores por nivel:'), nl,
    mostrar_scores(Scores, NivelId),
    nl,
    mostrar_justificacao_final(NivelId),
    write('========================================'), nl.

mostrar_scores([], _).
mostrar_scores([N-S|Rest], NivelRec) :-
    nivel(N, NT, _),
    Pct is round(S * 100),
    ( N = NivelRec ->
        format('  * ~w: ~w%~n', [NT, Pct]),
        barra_progresso(S), write('<- recomendado'), nl
    ;
        format('    ~w: ~w%~n', [NT, Pct]),
        barra_progresso(S), nl
    ),
    mostrar_scores(Rest, NivelRec).

mostrar_justificacao_final(sem_sintomas_alarme) :- !,
    write('Justificacao do Diagnostico:'), nl,
    write('  Nenhuma das regras de alarme foi activada.'), nl,
    write('  O nivel "SEM ALARME" foi atribuido por omissao (seguranca).'), nl.

mostrar_justificacao_final(NivelId) :-
    findall(CF-IdRegra,
            (avaliar_regra(IdRegra, NivelId, CF), CF > 0),
            RegrasAtivadas),
    ( RegrasAtivadas = [] ->
        write('Justificacao do Diagnostico:'), nl,
        write('  Nivel determinado por combinacao de evidencias fracas.'), nl
    ;
        keysort(RegrasAtivadas, ListaOrdenada),
        reverse(ListaOrdenada, RegrasDesc),
        RegrasDesc = [MaxCF-RegraPrincipal | OutrasRegras],
        regra(RegraPrincipal, se(Premissas), _, _),
        ( explicacao_regra(RegraPrincipal, ExplClinica) -> true
        ; ExplClinica = 'Regra gerada automaticamente por aprendizagem automatica (Parte B).'
        ),
        PctPrincipal is round(MaxCF * 100),
        write('Justificacao do Diagnostico:'), nl,
        format('  Regra principal [~w] activada com ~w% de certeza.~n',
               [RegraPrincipal, PctPrincipal]),
        write('  Premissas confirmadas: '), write(Premissas), nl,
        format('  Motivo clinico: ~w~n', [ExplClinica]),
        ( OutrasRegras \= [] ->
            nl,
            write('  Regras secundarias que tambem contribuiram:'), nl,
            mostrar_regras_secundarias(OutrasRegras)
        ;   true
        )
    ).

mostrar_regras_secundarias([]).
mostrar_regras_secundarias([CF-Id|Resto]) :-
    Pct is round(CF * 100),
    ( explicacao_regra(Id, Expl) ->
        format('    [~w] ~w% - ~w~n', [Id, Pct, Expl])
    ;
        format('    [~w] ~w%~n', [Id, Pct])
    ),
    mostrar_regras_secundarias(Resto).