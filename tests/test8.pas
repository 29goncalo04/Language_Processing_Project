program BinarioParaInteiro;

function BinToInt(bin: array[1..100] of CHAR): integer;
var
    i, valor, potencia: integer;
begin
    valor := 0;
    potencia := 1;

    for i := 100 downto 1 do
    begin
        if bin[i] = '1' then
            valor := valor + potencia;
        potencia := potencia * 2;
    end;

    BinToInt := valor;
end;

var
    bin: array[1..100] of CHAR;
    valor: integer;
begin
    writeln('Introduza uma string binária:');
    readln(bin);
    valor := BinToInt(bin);
    
    writeln('O valor inteiro correspondente é: ', valor);
end.