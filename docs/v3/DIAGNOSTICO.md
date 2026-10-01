# Diagnóstico local — etapa 00

Data: 18/09/2026. Ambiente: Windows 11 Pro 10.0.22631; Python 3.13.3. Checkout inicial: `main` em `a9ef57a` (merge da v2.6.0), tag `v2.6.0` presente; criada `feature/v3.0.0` desse ponto. A única alteração pendente inicial era `src/optimus_sun.db`, preservada. `src/version.py` identifica a versão do código como `2.6.0`. Não havia `docs/v3/STATUS.md` nem `AGENTS.md` local encontrado. MySQL/VM não foram acessados: faltam ambiente de teste, versão do servidor e configuração de conexão; não é necessário para esta etapa.

## Snapshot SQLite e inventário

O snapshot foi criado pela API `sqlite3.Connection.backup` a partir de conexão `mode=ro`, sem escrita no banco de origem. Arquivo temporário: `%TEMP%/optimus-v3-stage00-c0e952ad555b46529f6c11a54e7b8038.db`. SHA-256 do snapshot: `317889cd875a5d2e8754206d57250930a0c0e05f147f12989c9ca85f3116dee8`. SHA-256 do arquivo de origem observado: `333b8f60c1bdc711c785db5b88041ebf8587dc2cbbc162f9de09f03743f91905`. Os hashes de arquivo diferem porque o backup cria outro arquivo físico; o snapshot é a referência lógica do inventário. `PRAGMA integrity_check = ok` e `PRAGMA foreign_key_check` sem ocorrências. Não se presumiu equivalência com o banco do GitHub ou da tag.

| Tabela local | Registros | ID mínimo–máximo | Colunas/tipos e relações relevantes |
| --- | ---: | --- | --- |
| `manufacturer` | 28 | 1–28 | `ID INTEGER`, `NAME TEXT`, `CATEGORY INTEGER`; sem FK/índice secundário. Categorias: 0=11, 1=15, 2=2. |
| `inverter` | 314 | 1–314 | Identidade `MODEL TEXT`, `MANUFACTURER_ID INTEGER`; grandezas físicas/CA em `REAL`/`INTEGER`; `OVERLOAD`, `NUMBER_OF_TRACKERS`, `NUMBER_OF_INPUTS`, `ACTIVE INTEGER`. FK fabricante `NO ACTION`; índices em fabricante e modelo. |
| `mppt` | 317 | 1–320 | `INVERTER_ID`, `MPPT_INDEX`, entradas/tensões `INTEGER`; `MAX_SHORT_CIRCUIT_CURRENT` e `MAX_OPERATING_CURRENT` `REAL`. FK inversor `CASCADE`; índice por inversor. |
| `module` | 418 | 1–418 | `MODEL TEXT`, fabricante, dimensões `REAL`, `WP INTEGER`, V/I/coefs `REAL`, classificações `TEXT`, `ACTIVE INTEGER`. FK fabricante `NO ACTION`; índices em fabricante/modelo. |
| `inverter_system` | 465 | 1–469 | `INVERTER_ID INTEGER`, `SYSTEM_TYPE TEXT`; FK inversor `CASCADE`, índice por inversor. |
| `inverter_communication` | 1.202 | 1–1212 | `INVERTER_ID INTEGER`, `COMMUNICATION_TYPE TEXT`; FK inversor **`NO ACTION`**, sem índice secundário encontrado. Diverge da proposta de cascata da v3. |
| `inverter_output_mode` | 366 | 1–369 | `INVERTER_ID INTEGER`, `OUTPUT_MODE TEXT`; FK inversor `CASCADE`, índice por inversor. |

São **sete** tabelas atuais; as quatro tabelas novas previstas no plano são saída CA, entrada CA, EPS e bateria. O catálogo tem 65 inversores e 35 módulos ativos; 249 inversores e 383 módulos inativos. Há 310 inversores com ao menos um grupo MPPT, portanto quatro sem grupo. O maior modelo de inversor tem 21 caracteres, de módulo 23, e nome de fabricante 12; existe um par duplicado `(MANUFACTURER_ID, MODEL)` em inversores. Não impor unicidade nova sem resolver esse legado.

`MPPT_INDEX=0` ocorre em 302 dos 317 grupos, mantendo a sentinela homogênea. Maior índice codificado: `2145` (`mppt.ID=257`, inversor 203); existem grupos com índices 3, 5, 6, 14 e 15. `MAX_OPERATING_CURRENT` varia de 10 a 185 A (27 valores distintos); `MAX_SHORT_CIRCUIT_CURRENT`, de 10 a 240 A (36 distintos). A corrente por string **não existe** no schema atual. Não inferir sua especificação.

Nos campos numéricos do snapshot, o único `-1` observado foi em `mppt.MAX_FULL_LOAD_VOLTAGE` (57), `MIN_FULL_LOAD_VOLTAGE` (57) e `RATED_INPUT_VOLTAGE` (37). Não foram observados `NULL` nas linhas existentes, apesar de várias colunas permitirem `NULL`; isso não autoriza converter todo `-1` genericamente. Sobrecarga cadastrada: 303 inversores com 50%, dez com 100%, um com 0%. Sistemas registrados: `ON-GRID` 311, `GRIDZERO` 70, `HYBRID` 63, `OFF-GRID` 21. São relações 1:N, não classes mutuamente exclusivas; há combinações como `HYBRID+OFF-GRID+ON-GRID`. Conferir a tabela de verdade antes de mapear saídas.

## Acoplamentos por arquivo/camada

| Área | Estado observado e impacto v3 |
| --- | --- |
| `src/optimus_sun.py` | Abre SQLite diretamente em consultas da GUI; cria `tk.Tk()` no módulo, `Toplevel`s e gráficos Matplotlib/TkAgg. Resolve banco externo por `sys.executable` quando congelado. Extrair acesso/casos de uso sem importar esta GUI no servidor. |
| `src/optimus_lib.py` | Funções matemáticas sem SQLite/Tk; base reutilizável do núcleo, mas validar contexto de perfil de saída antes de alterar cálculos. |
| `src/compatibility/` | `engine.py`/`models.py` concentram cálculo estruturado, `matrix.py` orquestra pares, `repository.py` conhece `sqlite3.Row`, SQL e uma potência nominal por inversor. `csv_io.py` depende do formato visível legado. Separar repositório e contrato de perfil, preservar importação CSV 2.6. |
| `src/catalog/` e `src/cadastros_db_gui.py` | `domain.py` contém validações, `repository.py` usa SQLite, `PRAGMA foreign_keys`, `?` e `COLLATE NOCASE`; `gui.py`/entry point usam Tk. Rascunhos e transações são base a preservar; perfis/flags e revisão otimista exigem novo contrato. |
| `src/equipment_search.py` / `_gui.py` | Consultas SQLite em modo leitura com `?`, `LIKE`/`COLLATE NOCASE`; GUI mantém seleção explícita e filtros independentes. Na v3 os critérios CA devem pertencer à mesma linha de saída e respostas atrasadas não podem confirmar equipamento. |
| `src/overload_control.py`, `src/focus_navigation.py` | Lógica de porcentagem e apoio ao foco já isolados; preservar significado de sobrecarga e Tab/Shift+Tab. |
| `tools/compatibility_matrix_gui.py` | Banco externo `mode=ro`; cálculo em `threading.Thread` e fila; renderização Tk na thread principal. Importação e alteração de seleção ainda chamam `_render_matrix()` sem callback e são totalmente síncronas. |
| `.spec` | `optimus_sun_v2_6_0.spec` reúne os três EXEs em `COLLECT` e copia `src/optimus_sun.db` para a raiz externa do pacote. O spec v2.5.0 e o histórico 2.3.8 existem; preservar, não reaproveitar SQLite como fallback operacional v3. |
| Testes | `test_catalog` e `test_equipment_search` criam SQLite temporário; `test_database_regression` lê diretamente `src/optimus_sun.db` em `mode=ro` e foi excluído da baseline da etapa 00. Testes de cálculo puro/CSV/matriz não escrevem no banco operacional. |

Dependências externas observadas: Matplotlib, Pillow e PyInstaller; Tkinter e SQLite vêm do Python instalado. Não há arquivo de dependências pinadas (`requirements`, `pyproject` ou Pipfile) no checkout. A stack FastAPI/SQLAlchemy/MySQL do plano ainda não foi adicionada.

## Matriz: hipótese a medir na etapa 01

O worker calcula fora do callback Tk e a GUI consulta a fila via `after(100)`. Porém `_render_matrix` remove widgets um a um, cria cabeçalhos de todos os módulos de forma síncrona, constrói três widgets por célula e atualiza a região de rolagem; no caminho assíncrono usa lote fixo de **oito linhas** com `after(1)`. O caminho sem callback, usado após importação e ao preservar matriz importada, renderiza todas as linhas síncronas. Isso identifica pontos de medição, **não prova** qual fase causa o atraso percebido. Não houve benchmark de desempenho nesta etapa.

Medição proposta: em banco/snapshot de teste, instrumentar leitura/preparação, tempo e quantidade por par no worker, limpeza, cabeçalhos, criação de células, atualização de scroll, p95/pior atraso de uma sonda `after`, duração total, pico de memória e resposta ao cancelamento. Registrar hardware/escala e repetir conjuntos 20×20, 100×100, largos e altos, ajustando por memória. Conferir equivalência numérica e CSV antes/depois. Nenhuma fórmula foi alterada nesta etapa.

## Baseline e riscos

Baseline executada com módulos de teste que usam dados temporários ou lógica pura, excluindo `test_database_regression`: **100 testes, OK** (`py -3 -X utf8 -B -m unittest -q ...`, com `tests` no `PYTHONPATH`). Houve mensagens Tk `invalid command name ... <lambda>` / `after script` ao destruir roots de testes; não mudaram o resultado, mas merecem isolamento na etapa 01. Uma primeira tentativa sem `tests` no import path falhou na coleta de `test_equipment_search` por `ModuleNotFoundError: test_catalog`; a repetição com path correto passou. Não houve teste de MySQL, API, VM nem medição visual da matriz.

Riscos concretos: banco local alterado fora do Git; duplicata de modelo/fabricante; quatro inversores sem MPPT; FK de comunicação diferente da cascata proposta; `MPPT_INDEX` codificado e sentinela 0; `-1` legado por campo; sobreposição de flags; potência CA única no `inverter`; perfis de saída inexistentes; renderização Tk potencialmente O(linhas×colunas) em widgets; ausência de testes MySQL e de versões de dependências fixadas. Não atribuir a um único risco a causa de falha sem reproduzir.

## Decisões abertas antes da etapa 02

1. Confirmar operação **sem modo offline**: clientes v3 dependem da API/VM. Se não for aceitável, o contrato precisa mudar antes de adaptar clientes.
2. Fechar a tabela de verdade das flags, sobretudo híbrido/off-grid/GRIDZERO, e quando uma saída CA ou EPS é utilizável. Não inventar saída de rede para off-grid.
3. Aprovar política de `NULL` por campo, dados mínimos de ativação versus rascunho e tratamento dos poucos `-1` reais; confirmar escala/precisão de DECIMAL e eficiências.
4. Definir `BATTERY_INDEX`: porta física a partir de 0 é proposta, mas alternativas por porta e unicidade ainda precisam de decisão.
5. Definir como representar modos de saída específicos de CA/EPS se o mesmo inversor os diferencia; hoje os modos são do inversor.
6. Decidir extensão necessária quando limites CC/full-load do datasheet dependem da tensão do perfil de saída. Não validar tal caso por equivalência presumida.
7. Fechar autorização de escrita e transporte seguro na rede interna com a TI antes de expor CRUD; definir estratégia de revisão/concorrência.

## Checklist manual para iniciar a etapa 01

- Confirmar que a matriz da v2.6.0 abre com o banco correto, sem mudar o arquivo operacional.
- Separar uma cópia de teste e registrar hardware, resolução e escala de tela.
- Reproduzir matriz pequena, 20×20, larga, alta e 100×100 se a memória permitir; anotar travamento, progresso, rolagem e cancelamento.
- Exportar o CSV de referência antes de mudanças e comparar resultados/linhas após a implementação da etapa 01.
- Distinguir tempo de cálculo, preparação, cabeçalhos, linhas e atraso do event loop; não concluir causa só pela aparência.
