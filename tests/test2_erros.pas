{exemplo 2 mas com erros semânticos}

program Maior3;

var
    num1, num2, num3, maior: Integer;
    flag: Boolean;           { ERRO: variável flag nunca é inicializada antes de usar }

begin
    WriteLn('Introduza o primeiro número: ');
    ReadLn(num1);

    WriteLn('Introduza o segundo número: ');
    ReadLn(num2);

    WriteLn('Introduza o terceiro número: ');
    ReadLn(num3);

    if num1 > num2 then
        if num1 > num3 then
            maior := num1
        else 
            maior := num3
    else
        if num2 > num3 then
            maior := num2
        else 
            maior := num3;

    { ERRO semântico: usar variável não inicializada flag numa expressão }
    if flag then
        maior := num1;

    { ERRO semântico: atribuição de tipo incompatível (real → integer) }
    maior := 3.14;

    { ERRO semântico: comparação entre integer e boolean }
    if num1 > flag then
        maior := num2;

    { ERRO semântico: usar variável inexistente }
    if num4 > num1 then
        maior := num4;

    WriteLn('O maior é: ', maior)
end.