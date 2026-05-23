{exemplo 2 do enunciado}
program Maior3;

var
    num1, num2, num3, maior: Integer;

begin
    { Ler 3 números }
    WriteLn('Introduza o primeiro número: ');
    ReadLn(num1);

    WriteLn('Introduza o segundo número: ');
    ReadLn(num2);

    WriteLn('Introduza o terceiro número: ');
    ReadLn(num3);

    { Calcular o maior }
    if num1 > num2 then
        if num1 > num3 then
            maior := num1
        else maior := num3
    else
        if num2 > num3 then
            maior := num2
        else maior := num3;
        
    { Escrever o resultado }
    WriteLn('O maior é: ', maior)
end.