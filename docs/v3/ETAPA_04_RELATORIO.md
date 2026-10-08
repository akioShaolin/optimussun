# Etapa 04 — núcleo compartilhado de cálculos

Data da execução: 08/10/2026. Branch: `feature/v3.0.0`. A etapa foi realizada
sem alterar o SQLite operacional, o catálogo/schema MySQL, a migração, as
interfaces visuais ou a versão publicada.

## 1. Ponto de partida e baseline

Antes da extração foi criado o registro [ETAPA_04_BASELINE.md](ETAPA_04_BASELINE.md),
com resultados constantes para grupos homogêneos e heterogêneos, sobrecarga
cadastrada e personalizada, corrente operacional, plena carga, arredondamento e
dados ausentes. A suíte anterior à mudança terminou com 163 testes aprovados,
11 ignorados e 25 subtestes aprovados.

O inventário localizou:

- fórmulas escalares em `optimus_lib.py`;
- busca de fechamento de strings e fator limitante em
  `compatibility/engine.py`;
- preparação dos dados SQLite em `compatibility/repository.py`;
- orquestração, progresso e cancelamento em `compatibility/matrix.py`;
- uma segunda agregação de limites dentro de `optimus_sun.py`, usada pelos
  cartões e gráficos da aplicação principal.

As diferenças preexistentes estão reproduzidas na baseline. Em especial, a
matriz fecha strings fisicamente realizáveis, enquanto a tela principal mantém
tetos agregados. A opção antiga de ignorar plena carga também exclui o teto
operacional da projeção principal; isso não foi reinterpretado como defeito.

## 2. Organização implementada

O pacote `src/calculation_core/` não importa Tkinter, Matplotlib, SQLite,
PyMySQL ou HTTP:

| Arquivo | Responsabilidade |
| --- | --- |
| `models.py` | contratos imutáveis de entrada, opções, perfil, limites, resultado e ocorrências estruturadas |
| `math.py` | fórmulas escalares únicas de compensação térmica, limites de corrente, série e sobrecarga |
| `profiles.py` | resolução pura por seleção explícita ou por um único padrão válido |
| `engine.py` | validação, limites por MPPT, fechamento de strings, totais e fator limitante |
| `__init__.py` | API pública do núcleo |

`optimus_lib.py` conserva os nomes históricos, mas delega as fórmulas a
`calculation_core.math`. `compatibility/engine.py` conserva a API pública da
matriz e converte seus modelos v2 para os contratos do núcleo. O adaptador
`compatibility/legacy_main.py` projeta o resultado nos campos `calculos_cc`
consumidos pelos cartões e gráficos atuais.

Não há acesso MySQL nos clientes desktop. Os adaptadores atuais constroem um
perfil explícito de compatibilidade a partir dos campos CA legados e o marcam
como `LEGACY_CA_FIELDS`; eles não consultam nem escolhem arbitrariamente um dos
novos perfis migrados.

## 3. Contratos

### Entrada

`CalculationRequest` reúne:

- `InverterInput`: ID, fabricante, modelo, atividade, revisão/origem,
  classificações, sobrecarga e grupos MPPT;
- `ModuleInput`: ID, fabricante, modelo, atividade, revisão/origem, grandezas
  elétricas e coeficientes térmicos;
- `OutputProfile`: ID, inversor, tipo, modo, potência nominal/máxima/pico,
  tensões fase–fase/fase–neutro, correntes, atividade, padrão, revisão/origem;
- `CalculationOptions`: temperaturas, tolerâncias, sobrecarga personalizada e
  opções de corrente operacional/plena carga.

O núcleo recebe esses objetos prontos e nunca busca banco ou widget. A condição
de equipamento ativo pertence ao chamador: equipamento inativo válido pode ser
simulado pelo principal; a matriz continua filtrando ativos em seu repositório.
Perfil inativo nunca é calculável.

### Perfil de saída

`resolve_output_profile()` aplica somente uma seleção explícita válida ou um
único padrão válido. Não escolhe primeiro/menor/maior, não soma alternativas e
solicita escolha quando não existe padrão. `AC_OUTPUT` é elegível para
`ON-GRID`, `GRIDZERO` e `HYBRID`; `EPS_OUTPUT`, para `OFF-GRID` e `HYBRID`;
`AC_INPUT` é recusado como potência de saída. O perfil deve estar ativo,
pertencer ao inversor, identificar o modo e ter potência nominal positiva.

Potência nominal, máxima e de pico permanecem campos distintos. Tensões
fase–fase e fase–neutro são transportadas separadamente, sem conversão.

### Resultado

`CalculationResult` repete as identidades, revisões e origens efetivamente
usadas; registra perfil/modo e suas grandezas sem combiná-las; inclui opções e
sobrecarga efetiva, valores térmicos, limites e escolha por MPPT, limites totais,
quantidade, potência, sobrecarga, strings e fator limitante.

Falhas carregam `CalculationIssue` com código, severidade, campo e mensagem.
Dado estrutural ausente gera valores calculados `None`; não aparece como zero ou
compatibilidade válida. Quantidade zero é reservada para um contexto calculável
sem configuração positiva e recebe `NO_FEASIBLE_CONFIGURATION` e o fator físico
correspondente.

## 4. Dados desconhecidos e precisão

- Os adaptadores convertem `-1` somente nos campos legados opcionais já
  previstos: faixa de plena carga e tensão nominal de entrada. Não existe
  conversão genérica de negativos.
- Temperaturas e coeficientes negativos continuam válidos.
- Sobrecarga entra no contrato como percentual adicional (`50` significa 50%)
  e é convertida uma vez para fração na fórmula de potência.
- Correntes por MPPT não são divididas pelo número de entradas. O teste dedicado
  preserva literalmente limites de 130 A e 162,5 A.
- Quantidades usam `ceil` no mínimo de série e `floor` nos tetos; a busca e a
  comparação de quantidades são inteiras. Não há arredondamento intermediário
  da potência da matriz. A projeção principal conserva o `round(..., 1)` e o
  truncamento percentual históricos.
- A tolerância de potência permanece 0,5% quando informada pelo chamador. Nos
  testes, inteiros são exatos e valores de ponto flutuante usam a tolerância do
  `assertAlmostEqual` do Python.

Não foram adicionadas correções de eficiência, bateria ou temperatura além das
fórmulas existentes. `COEF_PMAX` continua apenas nos valores térmicos
descritivos do principal; a potência DC usa `WP`.

## 5. Uso mínimo sem interface

```python
from calculation_core import CalculationRequest, calculate

# inverter, module, profile e options são dataclasses já preenchidas pelo chamador.
result = calculate(CalculationRequest(inverter, module, profile, options))
if result.valid:
    print(result.quantity, result.dc_power_kw, result.mppt_results)
else:
    print([(issue.code.value, issue.field) for issue in result.issues])
```

Resolução explícita de perfil:

```python
from calculation_core import resolve_output_profile

resolution = resolve_output_profile(inverter, profiles, selected_profile_id=42)
if resolution.valid:
    result = calculate(CalculationRequest(inverter, module, resolution.profile, options))
```

## 6. Equivalência e diferenças controladas

Os oito casos congelados da matriz conservaram quantidade, potência, fator,
strings e módulos/string. Os testes históricos de `optimus_lib`, motor e matriz
continuaram aprovados. Um ensaio somente leitura no catálogo real confirmou,
para o par de IDs 203/117, 522 módulos no modo normal (`OPERATING_CURRENT`) e
527 ignorando corrente (`OVERLOAD_LIMIT`); a projeção principal retornou 522
módulos, 373,2 kW e dois grupos MPPT.

Os dois casos de aceitação históricos também foram repetidos: `SIW400G K025
W00 × WPV 610 H66MBN3` manteve 61 módulos, 37,21 kW, 48,84% e
`OVERLOAD_LIMIT`; `SIW200G M050 W1 × JAM66D42-570/MB` manteve zero módulos e
`OPERATING_CURRENT` no modo normal, e 13 módulos, 7,41 kW, 48,20% e
`OVERLOAD_LIMIT` ignorando corrente operacional.

Uma diferença intencional em relação à validação antiga foi tornada explícita:
quando a corrente operacional por MPPT está desconhecida, o modo normal falha
com dado ausente, mas o modo que explicitamente ignora somente essa corrente
pode calcular. Curto-circuito, tensão, entradas e potência continuam exigidos.
Isso elimina a exigência contraditória do campo que o usuário mandou ignorar,
sem fabricar um limite.

As divergências entre agregação principal e fechamento da matriz continuam
existindo somente nos adaptadores documentados; não houve mudança silenciosa de
regra para igualar telas conceitualmente diferentes.

## 7. Validação executada

- 61 testes focados do núcleo, adaptadores, fórmulas, motor e matriz, mais três
  subtestes, aprovados;
- regressão integral: 186 testes aprovados, 12 ignorados e 28 subtestes
  aprovados;
- cinco testes de regressão somente leitura do SQLite aprovados;
- compilação de `src`, `tools` e `tests` aprovada;
- importação do núcleo em processo isolado sem carregar Tkinter, Matplotlib,
  SQLite ou PyMySQL aprovada;
- `git diff --check` sem erros; os avisos exibidos referem-se apenas à política
  LF/CRLF já existente;
- SQLite antes/depois: integridade não modificada e SHA-256
  `d12c15cb337bfeac7b5afe405656ae538ade62ed2a6e5871a804724d2d04fc1a`.

Dos 12 testes ignorados, 11 são integrações MySQL protegidas por variável
explícita e um depende de Tk/Tcl, indisponível no interpretador do ambiente de
teste. O schema preenchido da Etapa 03 não foi limpo nem recarregado. Nenhuma
validação visual automatizada foi acrescentada. A GUI não foi aberta nesta
execução; sua estrutura de widgets, virtualização, progresso, cancelamento,
descarte, CSV, filtros e atalhos não foi alterada.

## 8. Preparação para a Etapa 05

Já usam o núcleo:

- aplicação principal, através da projeção `legacy_main`;
- matriz, através da API pública `compatibility`;
- funções escalares históricas, por wrappers em `optimus_lib`.

Ficam para etapas futuras, sem antecipação nesta entrega:

- adaptador do servidor para carregar os contratos a partir dos perfis MySQL;
- transporte HTTP/filas/autorização da Etapa 05;
- escolha visual dos perfis e migração dos clientes desktop para a API na Etapa
  07;
- eventual convergência de apresentação entre o teto agregado do principal e o
  fechamento de strings da matriz, somente com decisão funcional explícita.

Não surgiu nova decisão de negócio bloqueadora do núcleo. Continuam pendentes
as 369 referências de tensão, 112 revisões de perfis multimodo, três inversores
sem MPPT e a conferência do `H3-PRO-15.0`. Um perfil marcado como pronto não
substitui os dados elétricos necessários a cada cálculo.

