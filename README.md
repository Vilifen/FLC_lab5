## Лабораторная работа 3. Разработка синтаксического анализатора (парсера)

# Цель работы.
Изучить назначение и принципы работы синтаксического анализатора в структуре компилятора. Спроектировать грамматику, построить соответствующую схему метода анализа грамматики и выполнить программную реализацию парсера с нейтрализацией синтаксических ошибок методом Айронса. Интегрировать разработанный модуль в ранее созданный графический интерфейс языкового процессора.

# Сведения об авторе.
Лабораторную работу сделала студентка группы АВТ-313 Федулова В.В.

# Вариант задания.
103. Цикл while на языке PHP
     
while ($i < 10) {
    $i++;
};

while ($counter < 5) {
    $counter++;
    $counter++;
};

# Разработка грамматики (полное определение разработанной грамматики).

1) <START> ->  'while' <WHILE>
2)  <WHILE> -> ‘(‘ <LPARENTHESIS>
3)  <LPARENTHESIS> -> '$' <ID_OUTSIDE>
4)  <ID_OUTSIDE> -> letter <ID_OUTSIDE>
5)  <ID_OUTSIDE> -> letter <ID_OUTSIDE> | digit <ID_OUTSIDE> | ‘_’ <ID_OUTSIDE> | <RELATION_OPERATION>
6)  <RELATION_OPERATION> -> ‘<’ <SMALLER> | ‘>’ <BIGGER> | ‘<=’ <SMALLER_OR_EQUAL> | ‘>=’ <BIGGER_OR_EQUAL> | ‘==’ <EQUAL> | ‘!=’ <NOT_EQUAL>
7)  <RELATION_OPERATION> -> '$' <ID_OUTSIDE*>
8)  <ID_OUTSIDE*> -> letter <ID_OUTSIDE*>
9)  <ID_OUTSIDE*> -> letter <ID_OUTSIDE*> | digit <ID_OUTSIDE*> | ‘_’ <ID_OUTSIDE*>
10)  <ID_OUTSIDE*> -> <OPERAND> | ‘)’ <RPARENTHESIS>
11)  <OPERAND> -> ‘&&’ <OPERAND_AND> | ‘||’ <OPERAND_OR>
12)  <OPERAND> -> <ID_OUTSIDE>
<RPARENTHESIS> -> ‘{’ <LBRACE>
13) <LBRACE> -> ''$' <ID_INSIDE>
14) <ID_INSIDE> -> letter <ID_INSIDE>
15) <ID_INSIDE> -> letter <ID_INSIDE> | digit <ID_INSIDE> | ‘_’ <ID_INSIDE> | ‘++’ <INCREMENT> | ‘--’ <DECREMENT>
16)  <INCREMENT> | <DECREMENT>  -> ‘;’ <SEMICOLON>
17) <SEMICOLON> -> ‘}’ <RBRACE>
18) <RBRACE> -> ‘;’ <SEMICOLON>


# Классификация грамматики (по Хомскому).

# Метод анализа

# Диагностика и нейтрализация синтаксических ошибок.

# Тестовые примеры