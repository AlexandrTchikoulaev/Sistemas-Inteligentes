% facto(Sintoma, CF)
%   CF = 1.0    -> presente com certeza total
%   CF = -1.0   -> negado
%   0 < CF < 1  -> grau de certeza parcial

:- dynamic facto/2.

limpar :- retractall(facto(_, _)).