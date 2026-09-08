# Motor de compatibilidade

> Funcionalidade em desenvolvimento para a futura v2.5.0. A versão publicada do Optimus Sun permanece v2.3.8.

O pacote `src/compatibility/` calcula a maior configuração eletricamente admissível para uma combinação de inversor e módulo sem depender do Tkinter. Ele foi separado da interface para poder ser reutilizado por uma matriz de compatibilidade, exportação CSV e futuras interfaces.

## Componentes

- `models.py`: modelos imutáveis de inversor, módulo, MPPT, opções e resultado.
- `engine.py`: compensação térmica, enumeração das configurações, otimização e fator limitante.
- `repository.py`: conversão dos registros de `src/optimus_sun.db` para os modelos do motor.
- `matrix.py`: seleções repetíveis, rótulos, ordenação e armazenamento das células calculadas.
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

## Estado da implementação

As duas primeiras etapas entregam o motor e uma interface provisória de validação. A matriz permite:

- selecionar vários inversores e módulos ativos;
- repetir inversores com rótulos independentes;
- ordenar inversores pelo texto exibido e módulos manualmente;
- configurar sobrecarga cadastrada ou personalizada independentemente em cada ocorrência de inversor;
- inspecionar os dois modos de cada célula sem recalculá-la.

Quando ignorar a corrente de operação aumenta a quantidade e produz um resultado válido, a matriz usa esse resultado como `display_result`. Quantidade, potência e sobrecarga são sempre apresentadas a partir do mesmo objeto, com `↗` indicando o modo alternativo. Os resultados `normal` e `ignored` continuam preservados integralmente nos detalhes. Se não houver ganho ou se o resultado ignorando corrente for inválido, o resultado normal permanece como principal.

Ainda não estão implementados:

- exportação e importação CSV;
- associação manual de equipamentos importados.

O cabeçalho e a coluna de inversores ainda rolam junto com o restante da matriz. Congelá-los permanece como melhoria visual futura.
