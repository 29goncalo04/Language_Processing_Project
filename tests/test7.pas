program BinarioParaInteiro;
type
  string = array[1..100] of CHAR;
var
    bin: string;
    i, valor, potencia: integer;
begin
    writeln('Introduza uma string binária:');
    readln(bin[1]);
    
    valor := 0;
    potencia := 1;
    for i := 100 downto 1 do
    begin
        if bin[i] = '1' then
            valor := valor + potencia;
        potencia := potencia * 2;
    end;
    writeln('O valor inteiro correspondente é: ', valor);
end.