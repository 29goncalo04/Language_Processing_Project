{exemplo 7 mas com erros semânticos}
program BinarioParaInteiro;
type
    mystring = array[1..100] of CHAR;

function BinToInt(bin: mystring; len: boolean): integer;  { Erro semântico: parâmetro 'len' declarado como BOOLEAN, mas usado no FOR como INTEGER }
var
    i, valor, potencia: integer;
begin
    valor := true;                 { Erro semântico: atribuição a 'valor' (INTEGER) recebe BOOLEAN}
    potencia := 1.0;               { Erro semântico: atribuição a 'potencia' (INTEGER) recebe REAL}
    for i := len downto 1 do        { Erro semântico: variável de controlo do FOR 'len' não é INTEGER, mas BOOLEAN }
    begin
        if bin[i] = '1' then
            valor := valor + potencia;
        potencia := potencia * 2
    end;
    BinToInt := valor
end;

var
    bin: mystring;
    len, resultado: integer;
    ch: char;
    valido: boolean;
begin
    writeln('Introduza uma string binária terminada por um ponto (ex: 10101.):');

    length := 0;                    { Erro semântico: 'length' não declarado}
    valido := 5;                   { Erro semântico: atribuição a 'valido' (BOOLEAN) recebe INTEGER}
    read(ch);

    { Lê carácter a carácter até encontrar '.' ou erro }
    while (ch <> '.') and (valido) do
    begin
        len := len + 1;             { Erro semântico: somar INTEGER com BOOLEAN}
        if len <= 100 then
        begin
            if (ch = '0') or (ch = '1') then
                bin[len] := ch
            else
                valido := false
        end
        else
            valido := false;  
        if valido then
            read(ch);
    end;

    { Se tudo foi válido, converte binário para inteiro }
    if valido then
    begin
        { Chama a função que converte o binário para inteiro }
        resultado := BinToInt(bin, len);
        writeln('O valor inteiro correspondente é: ', resultado)
    end
    else
        writeln('Erro: string inválida (tamanho >100 ou carácteres não binários).');
end.