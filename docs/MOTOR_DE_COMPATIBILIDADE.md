# Motor de compatibilidade

> Motor publicado na v2.5.0 e mantido na candidata v2.6.0. A última versão efetivamente publicada permanece v2.5.0 até a conclusão do processo de release.

O pacote `src/compatibility/` calcula a maior configuração eletricamente admissível para uma combinação de inversor e módulo sem depender do Tkinter. Ele foi separado da interface para poder ser reutilizado por uma matriz de compatibilidade, exportação CSV e futuras interfaces.

## Componentes

- `models.py`: modelos imutáveis de inversor, módulo, MPPT, opções e resultado.
- `engine.py`: compensação térmica, enumeração das configurações, otimização e fator limitante.
- `repository.py`: conversão dos registros de `src/optimus_sun.db` para os modelos do motor.
- `matrix.py`: seleções repetíveis, rótulos, ordenação e armazenamento das células calculadas.
- `csv_io.py`: serialização e leitura da representação visível da matriz, sem duplicar cálculos do motor.
- `__init__.py`: API pública do pacote.

## Entrada e saída

`analyze_compatibility()` recebe `InverterData`, `ModuleData` e `CompatibilityOptions`. O resultado contém, entre outros campos:

- quantidade total de módulos;
- potência DC em kW;
- percentual acima ou abaixo da potência nominal AC;
- fator limitante estruturado;
- indicação de corrente operacional ignorada;
- validade do resultado;
- strings e módulos por string em cada MPPT.

`compare_operating_current_modes()` executa a mesma análise no modo normal e no modo que ignora a corrente de operação. O segundo modo continua respeitando curto-circuito, tensões, entradas, strings, Full Load e sobrecarga.

## Estratégia de cálculo

1. Os valores do módulo são compensados termicamente entre 10 °C e 50 °C, usando as funções existentes em `optimus_lib.py`.
2. Para cada tipo de MPPT, são calculados os limites de strings por entrada, corrente de curto-circuito e corrente de operação.
3. São intersectadas as faixas de tensão de entrada, operação e, quando disponível, Full Load.
4. O motor enumera somente quantidades fisicamente possíveis de strings e módulos em série dentro desses limites.
5. Os grupos de MPPT são expandidos em MPPTs físicos e combinados por programação dinâmica.
6. A melhor configuração é a de maior quantidade total que não ultrapassa o limite de potência DC.

Em empates, o motor prefere a distribuição com menor diferença de quantidade entre MPPTs e, depois, o menor número total de strings.

Compensações, limites por MPPT e resultados são armazenados em caches limitados. Isso torna consultas repetidas praticamente imediatas e evita refazer trabalho quando uma matriz é revisitada. A interface provisória executa a geração fora da thread gráfica.

## Sobrecarga

Por padrão, o teto DC utiliza o percentual cadastrado no inversor. `custom_overload_percent` substitui esse valor somente no objeto de opções e não modifica o banco.

O percentual do resultado é calculado como:

```text
(potência DC / potência nominal AC - 1) × 100
```

Assim, resultados abaixo da potência nominal são negativos. O motor preserva o valor decimal; interfaces e exportadores podem arredondá-lo para apresentação.

## Dados ausentes

Campos obrigatórios com `None`, `-1`, zero ou valores inválidos não são transformados silenciosamente em compatibilidade zero. Nesses casos, o resultado possui `valid = False` e fator `MISSING_DATA`. Faixas de Full Load ausentes são tratadas como opcionais, preservando o comportamento atual do aplicativo.

Na matriz, uma quantidade zero válida é apresentada como `Não suporta | 0 | -`.
Já um resultado `MISSING_DATA` permanece `N/D | N/D | N/D`. Essa diferença é
somente visual: quantidade, validade, fator limitante e resultados técnicos
continuam estruturados e numéricos internamente.

## Política de flexibilização dos limites

A corrente máxima de operação é a única barreira que possui comparação
automática flexibilizada. O motor calcula o modo normal e o modo que ignora essa
corrente; somente quando o segundo produz uma quantidade válida maior ele passa
a ser o `display_result`.

Mesmo nesse modo continuam obrigatórios:

- corrente máxima de curto-circuito;
- quantidade física de entradas;
- faixa de tensão MPPT/operação;
- tensão máxima absoluta de entrada, com Voc corrigido por temperatura;
- Full Load e demais restrições configuradas;
- sobrecarga definida para cada ocorrência do inversor.

Não existe fallback para ignorar tensão MPPT, Voc máximo ou Isc máximo, nem
exceção automática por fabricante ou modelo.

Na matriz, uma quantidade zero válida é apresentada como `Não suporta | 0 | -`.
Já um resultado `MISSING_DATA` permanece `N/D | N/D | N/D`. Essa diferença é
somente visual: quantidade, validade, fator limitante e resultados técnicos
continuam estruturados e numéricos internamente.

## Política de flexibilização dos limites

A corrente máxima de operação é a única barreira que possui comparação
automática flexibilizada. O motor calcula o modo normal e o modo que ignora essa
corrente; somente quando o segundo produz uma quantidade válida maior ele passa
a ser o `display_result`.

Mesmo nesse modo continuam obrigatórios:

- corrente máxima de curto-circuito;
- quantidade física de entradas;
- faixa de tensão MPPT/operação;
- tensão máxima absoluta de entrada, com Voc corrigido por temperatura;
- Full Load e demais restrições configuradas;
- sobrecarga definida para cada ocorrência do inversor.

Não existe fallback para ignorar tensão MPPT, Voc máximo ou Isc máximo, nem
exceção automática por fabricante ou modelo.

## Estado da implementação

As três primeiras etapas entregam o motor, uma interface provisória de validação e intercâmbio CSV. A matriz permite:

- selecionar vários inversores e módulos ativos;
- repetir inversores com rótulos independentes;
- ordenar inversores pelo texto exibido e módulos manualmente;
- configurar sobrecarga cadastrada ou personalizada independentemente em cada ocorrência de inversor;
- inspecionar os dois modos de cada célula sem recalculá-la.
- exportar o `display_result` em UTF-8 com BOM e separador `;`;
- importar valores preservando linhas, colunas, ordem, repetições e `N/D`;
- associar manualmente equipamentos que não tiveram correspondência textual exata;
- recalcular valores importados somente por ação explícita do usuário.

As listas disponíveis na matriz contêm somente equipamentos ativos e são
ordenadas por fabricante e modelo. Se os dados elétricos de um cadastro ativo não
forem suficientes, o motor mantém o resultado inválido apresentado como `N/D`.

A primeira coluna da tabela mostra exclusivamente o texto da ocorrência. Esse
texto começa com o modelo e pode ser personalizado independentemente, inclusive
em repetições do mesmo ID. Fabricante e modelo real não são repetidos nessa
célula, mas permanecem disponíveis na estrutura interna e na tela de detalhes.

Quando ignorar a corrente de operação aumenta a quantidade e produz um resultado válido, a matriz usa esse resultado como `display_result`. Quantidade, potência e sobrecarga são sempre apresentadas a partir do mesmo objeto, com `↗` indicando o modo alternativo. Os resultados `normal` e `ignored` continuam preservados integralmente nos detalhes. Se não houver ganho ou se o resultado ignorando corrente for inválido, o resultado normal permanece como principal.

Valores importados são representados separadamente dos resultados técnicos do
motor. Assim, abrir um arquivo nunca inventa fator limitante, strings ou MPPTs e
nunca dispara cálculo silencioso. Os detalhes técnicos voltam a ficar
disponíveis depois que todos os equipamentos forem associados e a matriz for
recalculada. O contrato completo está em [CSV_MATRIZ.md](CSV_MATRIZ.md).

O cabeçalho e a coluna de inversores ainda rolam junto com o restante da matriz. Congelá-los permanece como melhoria visual futura.
