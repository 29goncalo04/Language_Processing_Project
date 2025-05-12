{exemplo 0 inventado mas com erros semânticos}

PROGRAM Test;
VAR
    x, y: INTEGER;
    flag: BOOLEAN;      { ERRO: variável nunca inicializada antes de usar }
BEGIN
    x := 10;
    y := x DIV 2.5;      { ERRO: DIV requer ambos operandos inteiros, mas recebeu 2.5 real }
    y := x MOD flag;     { ERRO: MOD requer dois inteiros, mas flag é boolean }
    
    IF real(x, y) > 5.123 THEN
        { ERRO: real() (cast) espera exactamente 1 argumento, aqui foram 2 }
        WRITE('Maior que cinco');
    
    IF y IN x THEN       { ERRO: IN requer conjunto à direita, mas x é integer }
        WRITE(y);
    
    IF flag > 0 THEN     { ERRO: não se pode comparar boolean com integer }
        WRITE('Flag é verdadeiro');
    
    WRITELN(z);          { ERRO: uso de variável não declarada 'z' }
END.