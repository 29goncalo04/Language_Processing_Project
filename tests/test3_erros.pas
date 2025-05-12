{exemplo 3 mas com erros semânticos}

program Fatorial;
var
    n, i, fat: integer;
begin
    writeln('Introduza um número inteiro positivo:');
    readln(n);

    { ERRO semântico: variável 'fat' usada antes de inicialização }
    if fat > 0 then
        writeln('Fat já inicializado');

    { ERRO semântico: atribuição de carácter a integer }
    i := '1';

    for i := 1 to n do
        fat := fat * i;

    { ERRO semântico: operador '/' produz real, não pode atribuir a integer }
    fat := fat / 2;

    { ERRO semântico: indexar inteiro como se fosse array }
    fat := fat[1];

    writeln('Fatorial de ', n, ': ', fat);
end.