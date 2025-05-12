{exemplo 6 do enunciado mas sem length e string (porque não existe em Pascal Standard)}

program BinarioParaInteiro;

type
  mystring = array[1..100] of CHAR;
  
var
  bin: mystring;
  i, valor, potencia, len: integer;
  input: mystring;
  ch: char;
  valido: boolean;
  
begin
  writeln('Introduza uma string binária terminada por um ponto (ex: 10101.):');
  readln(input); 
  len := 0;
  valido := true;
  i := 1;
  ch:='a';

  { percorre a string até ao '.' ou erro ou mais de 100 }
  while (i <= 100) and (ch<>'.') do
  begin
    ch := input[i];

    if (ch = '0') or (ch = '1') then
    begin
      len := len + 1;
      bin[len] := ch;
    end;

    i := i + 1;
  end;
  
  { se não terminou com '.', também é erro }
  if input[i-1] <> '.' then
    valido := false;

  if valido then
  begin
    valor := 0;
    potencia := 1;

    for i := len downto 1 do
    begin
      if bin[i] = '1' then
        valor := valor + potencia;
      potencia := potencia * 2;
    end;

    writeln('O valor inteiro correspondente é: ', valor);
  end
  else
    writeln('Erro: string inválida (tamanho >100 ou carácteres não binários).');
end.