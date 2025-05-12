{exemplo 7 do enunciado mas sem length e string (porque não existe em Pascal Standard) e com funções}

program BinarioParaInteiro;
type
    mystring = array[1..100] of CHAR;

function BinToInt(bin: mystring; len: integer): integer;
var
    i, valor, potencia: integer;
begin
    valor := 0;
    potencia := 1;
    for i := len downto 1 do
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

    len := 0;
    valido := true;
    read(ch);

    { Lê carácter a carácter até encontrar '.' ou erro }
    while (ch <> '.') and (valido) do
    begin
        len := len + 1;
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