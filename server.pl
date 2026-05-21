% SNS24 Triagem HTTP Server
%
% Uso: swipl server.pl   <- abre http://localhost:8080
%      Para parar: escrever q + Enter no mesmo terminal
%
% Endpoints:
%   POST /api/start    - inicia triagem, devolve primeira pergunta
%   POST /api/answer   - responde sintoma, devolve pergunta ou resultado
%   POST /api/validate - guarda triagem no CSV (online learning)

:- use_module(library(http/thread_httpd)).
:- use_module(library(http/http_dispatch)).
:- use_module(library(http/http_json)).
:- use_module(library(http/http_files)).

server_dir(Dir) :-
    (   source_file(Src),
        file_base_name(Src, 'server.pl'),
        file_directory_name(Src, Dir)
    ->  true
    ;   working_directory(Dir, Dir)
    ).

:- server_dir(SD),
   atomic_list_concat([SD, '/base_dados.pl'], P1),
   ( exists_file(P1) -> consult(P1)
   ; format(user_error, '[ERRO] Nao encontrado: ~w~n', [P1]) ).

:- server_dir(SD),
   atomic_list_concat([SD, '/base_conhecimento_a.pl'], P2),
   ( exists_file(P2) -> consult(P2)
   ; format(user_error, '[ERRO] Nao encontrado: ~w~n', [P2]) ).

:- server_dir(SD),
   atomic_list_concat([SD, '/guardar_triagem.pl'], P3),
   ( exists_file(P3) -> consult(P3)
   ; format(user_error, '[AVISO] guardar_triagem.pl nao encontrado.~n', []) ).

:- server_dir(SD),
   atomic_list_concat([SD, '/sistema_inferencia.pl'], P4),
   ( exists_file(P4) -> consult(P4)
   ; format(user_error, '[ERRO] Nao encontrado: ~w~n', [P4]) ).

:- server_dir(SD),
   atomic_list_concat([SD, '/base_conhecimento_b.pl'], P5),
   ( exists_file(P5) ->
       consult(P5),
       format(user_error, '[Parte B] Base ML carregada.~n', [])
   ;   format(user_error, '[Parte B] base_conhecimento_b.pl nao encontrada (opcional).~n', [])
   ).

:- dynamic session_sintomas/1.

% ----------------------------------------------------------------
% ROTAS HTTP
% ----------------------------------------------------------------

:- http_handler(root(.),               serve_index,   []).
:- http_handler(root('interface.html'), serve_index,   []).
:- http_handler(root('chatbot.html'),   serve_chatbot, []).
:- http_handler(root(api/start),    handle_start,    [method(post)]).
:- http_handler(root(api/answer),   handle_answer,   [method(post)]).
:- http_handler(root(api/validate), handle_validate, [method(post)]).

serve_chatbot(Request) :-
    server_dir(Dir),
    atomic_list_concat([Dir, '/chatbot.html'], P),
    http_reply_file(P, [unsafe(true)], Request).

serve_index(Request) :-
    server_dir(Dir),
    atomic_list_concat([Dir, '/interface.html'], P),
    http_reply_file(P, [unsafe(true)], Request).

% POST /api/start
% with_output_to suprime qualquer write/nl dos modulos para nao poluir o socket HTTP.
handle_start(_Request) :-
    catch(
        with_output_to(string(_),
            with_mutex(sns_mutex, (
                limpar,
                obter_ordem_sintomas(Sintomas),
                retractall(session_sintomas(_)),
                assertz(session_sintomas(Sintomas)),
                proximo_passo(Resp)
            ))
        ),
        Err,
        ( term_string(Err, ErrS), Resp = _{type:"error", message:ErrS} )
    ),
    reply_json_dict(Resp).

% POST /api/answer
% Body JSON: { "sintoma": "dor_peito", "tipo": "sim"|"nao"|"talvez", "certeza": 0-100 }
handle_answer(Request) :-
    catch(
        handle_answer_safe(Request),
        Err,
        ( term_string(Err, ErrS), reply_json_dict(_{type:"error", message:ErrS}) )
    ).

handle_answer_safe(Request) :-
    http_read_json_dict(Request, Dict, []),

    get_dict(sintoma, Dict, SR),
    ( atom(SR) -> SA = SR ; atom_string(SA, SR) ),

    ( get_dict(tipo, Dict, TR) ->
        ( atom(TR) -> Tipo = TR ; atom_string(Tipo, TR) )
    ;   Tipo = sim ),

    ( get_dict(certeza, Dict, CertR) ->
        ( number(CertR) -> Cert = CertR ; atom_number(CertR, Cert) )
    ;   Cert = 100.0 ),

    tipo_para_cf(Tipo, Cert, CFInterno),

    catch(
        with_output_to(string(_),
            with_mutex(sns_mutex, (
                retractall(facto(SA, _)),
                assertz(facto(SA, CFInterno)),

                ( session_sintomas([_|Resto]) ->
                    retractall(session_sintomas(_)),
                    assertz(session_sintomas(Resto))
                ;   retractall(session_sintomas(_)),
                    assertz(session_sintomas([]))
                ),

                todos_niveis(Niveis),
                calcular_scores_finais(Niveis, Scores),
                score_max_val(Scores, MaxCF),
                limiar_saida(Limiar),
                session_sintomas(Resto2),

                ( (Resto2 = [] ; MaxCF >= Limiar) ->
                    construir_resultado(Scores, Resp)
                ;
                    proximo_passo(Resp)
                )
            ))
        ),
        Err2,
        ( term_string(Err2, ErrS2), Resp = _{type:"error", message:ErrS2} )
    ),
    reply_json_dict(Resp).

% sim -> CF positivo, nao -> CF negativo (activa premissas nao(S)), talvez -> 0.
tipo_para_cf(sim,    Cert, CF) :- !, CF is  Cert / 100.0.
tipo_para_cf(nao,    Cert, CF) :- !, CF is -(Cert / 100.0).
tipo_para_cf(talvez, _,    0.0) :- !.
tipo_para_cf(_,      _,    0.0).

% POST /api/validate
% Body JSON: { "nivel_id": "urgente", "validacao": "confirmado"|"corrigido"|"skip", "nivel_correto": "..." }
handle_validate(Request) :-
    catch(
        handle_validate_safe(Request),
        Err,
        ( term_string(Err, ErrS), reply_json_dict(_{ok: false, message: ErrS}) )
    ).

handle_validate_safe(Request) :-
    http_read_json_dict(Request, Dict, []),
    
    get_dict(nivel_id, Dict, NIR),
    ( atom(NIR) -> NId = NIR ; atom_string(NId, NIR) ),
    
    catch(
        with_output_to(string(_),
            with_mutex(sns_mutex, guardar_triagem(NId))
        ),
        ErrG,
        format(user_error, '[AVISO] guardar_triagem falhou: ~w~n', [ErrG])
    ),
    
    atom_string(NId, NStr),
    reply_json_dict(_{ok: true, nivel: NStr, guardado: true}).

% ----------------------------------------------------------------
% PROXIMO PASSO / PERGUNTA / RESULTADO
% ----------------------------------------------------------------

proximo_passo(Resp) :-
    ( session_sintomas([S|_]) ->
        construir_pergunta(S, Resp)
    ;
        todos_niveis(Niveis),
        calcular_scores_finais(Niveis, Scores),
        construir_resultado(Scores, Resp)
    ).

construir_pergunta(S, Resp) :-
    ( sintoma(S, D0)    -> atom_string(D0, Desc) ; atom_string(S, Desc) ),
    ( explicacao(S, E0) -> atom_string(E0, Expl) ; Expl = "" ),
    atom_string(S, SStr),
    todos_niveis(Niveis),
    calcular_scores_finais(Niveis, Scores),
    scores_para_json(Scores, nenhum, ScoresJ),
    Resp = _{type:"pergunta", sintoma:SStr, descricao:Desc, explicacao:Expl, scores:ScoresJ}.

construir_resultado(Scores, Resp) :-
    score_maximo(Scores, NivelId0, ScoreMax),
    ( ScoreMax < 0.05 -> NivelId = sem_sintomas_alarme ; NivelId = NivelId0 ),
    nivel(NivelId, NivelTxt0, Rec0),
    atom_string(NivelId,   NivelIdStr),
    atom_string(NivelTxt0, NivelTxt),
    atom_string(Rec0, Rec),
    Pct is round(ScoreMax * 100),

    scores_para_json(Scores, NivelId, ScoresJ),
    construir_justificacao(NivelId, JustJ),

    findall(S-CF0, (facto(S, CF0), CF0 > 0, sintoma(S, _)), SintsCF),
    maplist(sint_json, SintsCF, SintsJ),

    Resp = _{
        type:          "resultado",
        nivel_id:      NivelIdStr,
        nivel:         NivelTxt,
        recomendacao:  Rec,
        confianca_pct: Pct,
        scores:        ScoresJ,
        justificacao:  JustJ,
        sintomas:      SintsJ
    }.

scores_para_json([], _, []).
scores_para_json([N-CF|T], NivelRec, [J|JT]) :-
    nivel(N, NT0, _),
    atom_string(N, NStr),
    atom_string(NT0, NT),
    P is round(CF * 100),
    ( N == NivelRec -> Rec = true ; Rec = false ),
    J = _{nivel_id:NStr, nivel_txt:NT, score_pct:P, recomendado:Rec},
    scores_para_json(T, NivelRec, JT).

sint_json(S-CF, J) :-
    ( sintoma(S, D0) -> atom_string(D0, Desc) ; atom_string(S, Desc) ),
    Pct is round(CF * 100),
    J = _{desc:Desc, cf_pct:Pct}.

% ----------------------------------------------------------------
% JUSTIFICACAO JSON
% ----------------------------------------------------------------

construir_justificacao(sem_sintomas_alarme, J) :- !,
    J = _{
        tipo:               "sem_alarme",
        texto:              "Nenhuma das regras de alarme foi activada. O nivel SEM ALARME foi atribuido por omissao (seguranca).",
        regra_principal:    "",
        certeza_pct:        0,
        premissas:          [],
        explicacao:         "",
        regras_secundarias: []
    }.

construir_justificacao(NivelId, J) :-
    findall(CF-IdR, (avaliar_regra(IdR, NivelId, CF), CF > 0), Regras),
    ( Regras = [] ->
        J = _{
            tipo:               "fraco",
            texto:              "Nivel determinado por combinacao de evidencias fracas.",
            regra_principal:    "",
            certeza_pct:        0,
            premissas:          [],
            explicacao:         "",
            regras_secundarias: []
        }
    ;
        keysort(Regras, Ord),
        reverse(Ord, [MaxCF-RPrincipal|Outras]),
        regra(RPrincipal, se(Premissas), _, _),
        ( explicacao_regra(RPrincipal, ExplA) ->
            atom_string(ExplA, Expl)
        ;   Expl = "Regra gerada automaticamente (Parte B - ML)."
        ),
        atom_string(RPrincipal, RStr),
        PctP is round(MaxCF * 100),
        maplist(premissa_json, Premissas, PremJ),
        maplist(regra_sec_json, Outras, OutrasJ),
        J = _{
            tipo:               "detalhe",
            texto:              "",
            regra_principal:    RStr,
            certeza_pct:        PctP,
            premissas:          PremJ,
            explicacao:         Expl,
            regras_secundarias: OutrasJ
        }
    ).

premissa_json(nao(S), J) :- !,
    ( sintoma(S, D0) -> atom_string(D0, Desc) ; atom_string(S, Desc) ),
    J = _{presente: false, desc: Desc}.
premissa_json(S, J) :-
    ( sintoma(S, D0) -> atom_string(D0, Desc) ; atom_string(S, Desc) ),
    J = _{presente: true, desc: Desc}.

regra_sec_json(CF-Id, J) :-
    Pct is round(CF * 100),
    atom_string(Id, IdStr),
    ( explicacao_regra(Id, E0) -> atom_string(E0, EStr) ; EStr = "" ),
    J = _{id:IdStr, certeza_pct:Pct, explicacao:EStr}.

% ----------------------------------------------------------------
% UTILIDADES
% ----------------------------------------------------------------

score_max_val([], 0.0).
score_max_val([_-CF|T], Max) :-
    score_max_val(T, M2),
    Max is max(CF, M2).

% ----------------------------------------------------------------
% ARRANQUE
% ----------------------------------------------------------------

:- initialization(main, main).

main :-
    Port = 8080,
    http_server(http_dispatch, [port(Port)]),
    format("~n========================================~n"),
    format("  SNS24 Triagem - Parte A + Parte B~n"),
    format("  http://localhost:~w~n", [Port]),
    format("========================================~n"),
    format("  Para parar: escreva  q  e prima Enter~n"),
    format("========================================~n~n"),
    aguardar_parar.

% Bloqueia a thread principal a aguardar q/quit/exit/etc.
aguardar_parar :-
    read_line_to_string(user_input, Linha),
    (   Linha == end_of_file
    ->  halt(0)
    ;   string_lower(Linha, LinhaLow),
        (   member(LinhaLow, ["q","quit","parar","stop","exit","sair"])
        ->  format("~nServidor parado. Porta ~w libertada.~n", [8080]),
            halt(0)
        ;   aguardar_parar
        )
    ).