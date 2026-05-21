% Grava os factos da sessao atual em triagens.csv para retreino do modelo ML.
% CF > 0 -> 1 (presente), CF <= 0 -> 0 (ausente).

% Ordem dos sintomas no CSV - deve coincidir com SINTOMAS em Python
sintomas_csv([
    sem_respiracao, sem_pulso, resp_dificuldade, hemorragia, inconsciente,
    convulsoes, dor_peito, dor_irradia, fala_dificil, fraqueza_lado,
    febre_alta, confusao, dor_abd, febre_bebe,
    tosse_febre, dor_persiste, vomitos, diarreia,
    dor_garganta, constipacao, dor_leve, febre_baixa, mal_estar
]).

guardar_triagem(NivelId) :-
    sintomas_csv(Sintomas),
    maplist(cf_para_bit, Sintomas, Bits),
    atom_string(NivelId, NivelStr),
    atomic_list_concat(Bits, ',', BitsCsv),
    atomic_list_concat([BitsCsv, NivelStr], ',', Linha),
    catch(
        escrever_linha_csv('triagens.csv', Linha),
        Err,
        format('[AVISO] Nao foi possivel guardar triagem no CSV: ~w~n', [Err])
    ).

cf_para_bit(Sintoma, 1) :- facto(Sintoma, CF), CF > 0, !.
cf_para_bit(_, 0).

escrever_linha_csv(Ficheiro, Linha) :-
    ( \+ exists_file(Ficheiro) ->
        sintomas_csv(Sintomas),
        maplist(atom_string, Sintomas, SintomasStr),
        atomic_list_concat(SintomasStr, ',', Cabecalho),
        atomic_list_concat([Cabecalho, 'nivel'], ',', CabecalhoCompleto),
        open(Ficheiro, write, Stream),
        writeln(Stream, CabecalhoCompleto),
        writeln(Stream, Linha),
        close(Stream)
    ;
        open(Ficheiro, append, Stream),
        writeln(Stream, Linha),
        close(Stream)
    ).