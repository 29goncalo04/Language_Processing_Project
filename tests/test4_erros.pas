{exemplo 4 mas com erros semânticos}

program NumeroPrimo;
var
    num, i: integer;
    primo: boolean;
begin
    writeln('Introduza um número inteiro positivo:');
    readln(num);

    primo := true;

    { ERRO semântico: atribuição de boolean a integer }
    i := primo;

    { ERRO semântico: operador DIV requer operandos inteiros, mas 2.5 é real }
    while (i <= (num div 2.5)) and primo do
    begin
        { ERRO semântico: comparação entre integer e boolean }
        if (num mod i) = primo then
            primo := false;
        { ERRO semântico: atribuição de integer a boolean }
        primo := num;
        { ERRO semântico: soma boolean + integer não faz sentido }
        i := i + primo;
    end;

    { ERRO semântico: comparação integer > boolean não permitida }
    if num > primo then
        writeln(num, ' é um número primo')
    else
        writeln(num, ' não é um número primo')
end.