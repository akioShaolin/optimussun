# Etapa 04 — baseline anterior à extração

Registro obtido em 08/10/2026, antes de modificar o motor de compatibilidade ou
o fluxo de cálculo da aplicação principal. Os casos usam somente fixtures
controladas; os valores abaixo são constantes de referência e não são gerados
pelo núcleo novo.

## Regressão inicial

- suíte completa: 163 testes aprovados, 11 ignorados e 25 subtestes aprovados;
- `git diff --check`: sem erros (apenas avisos de conversão LF/CRLF já presentes);
- SHA-256 do SQLite operacional:
  `d12c15cb337bfeac7b5afe405656ae538ade62ed2a6e5871a804724d2d04fc1a`.

## Resultados congelados do motor da matriz

| Caso | Quantidade | Potência DC (kW) | Sobrecarga (%) | Fator | Strings | Módulos/string |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| homogêneo, sobrecarga cadastrada | 10 | 5,50 | 66,6666666667 | `OVERLOAD_LIMIT` | 1 | 10 |
| homogêneo, sobrecarga personalizada 50% | 9 | 4,50 | 50,0 | `OVERLOAD_LIMIT` | 1 | 9 |
| corrente operacional, modo normal | 19 | 10,45 | -89,55 | `OPERATING_CURRENT` | 1 | 19 |
| corrente operacional ignorada | 38 | 20,90 | -79,10 | `SHORT_CIRCUIT_CURRENT` | 2 | 19 |
| dois grupos heterogêneos | 37 | 20,35 | 1,750000000000007 | `OPERATING_CURRENT` | 3 | 7; 15 |
| plena carga aplicada | 0 | 0,00 | -100,0 | `FULL_LOAD_RANGE` | 0 | — |
| plena carga ignorada | 57 | 31,35 | -37,3 | `ALL_STRINGS_OCCUPIED` | 3 | 19 |
| potência do módulo ausente/inválida | 0 | 0,00 | 0,0 | `MISSING_DATA` | 0 | — |

O limite de potência usa tolerância exatamente como no legado e não se aplica
arredondamento intermediário antes da escolha da quantidade. Comparações de
ponto flutuante nos testes usam `assertAlmostEqual`; quantidades e strings são
comparadas exatamente.

## Diferenças preexistentes entre os fluxos

1. A matriz procura uma distribuição fisicamente realizável por MPPT e fecha
   strings inteiras. A tela principal calcula tetos agregados para alimentar
   seus cartões e gráficos; ela não executa a mesma otimização de fechamento.
2. Na tela principal, marcar **Ignorar faixa de carga máxima** retira também o
   teto agregado da faixa operacional da lista usada em `q_max_o`. No motor da
   matriz, `enforce_full_load=False` retira apenas a faixa de plena carga e
   preserva a faixa operacional MPPT. Este comportamento foi mantido pelo
   adaptador legado e não foi reinterpretado como correção funcional.
3. A tela principal arredonda a potência agregada em kW para uma casa decimal
   antes de truncar o percentual exibido. A matriz preserva a potência sem esse
   arredondamento e retorna sobrecarga em ponto flutuante.
4. O coeficiente `COEF_PMAX` participa dos valores térmicos descritivos da tela
   principal, mas a quantidade e a potência DC nominal continuam baseadas em
   `WP`, como no motor estruturado.

