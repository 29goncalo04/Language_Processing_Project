{exemplo 5 mas com erros semânticos}

program SomaArray;
var
    numeros: array[1..a] of integer;   {variável 'a' não declarada}
    i, soma: integer;
begin
    soma := 0;
    writeln('Introduza 5 números inteiros:');
    for i := 0 to 4 do  (* Erro semântico: índice fora dos limites definidos do array (1..5) *)
    begin
        readln(numeros[i]);  (* Erro semântico: acesso fora dos limites do array *)
        soma := soma + i;    (* Erro semântico: soma o índice em vez do número lido *)
    end;
    writeln('A soma dos números é: ', numeros);  (* Erro semântico: tentativa de imprimir um array diretamente *)
end.