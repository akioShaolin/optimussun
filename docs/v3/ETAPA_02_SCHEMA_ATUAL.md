# Etapa 02 — schema SQLite atual

Levantamento em 01/10/2026, na branch `feature/v3.0.0`. Fonte primária: catálogo `sqlite_master` e pragmas do arquivo `src/optimus_sun.db`, aberto com URI `mode=ro`. Este documento descreve o estado atual; a proposta futura está separada em [ETAPA_02_DICIONARIO_DADOS.md](ETAPA_02_DICIONARIO_DADOS.md).

## Integridade e objetos

- `PRAGMA integrity_check`: `ok`.
- `PRAGMA foreign_key_check`: nenhuma ocorrência.
- 7 tabelas de domínio, 7 índices explícitos, nenhuma view e nenhum trigger.
- Nenhuma restrição `UNIQUE` explícita.
- Todas as PKs usam `INTEGER PRIMARY KEY AUTOINCREMENT`; no `PRAGMA table_info`, a PK pode aparecer com `notnull=0`, mas a identidade `INTEGER PRIMARY KEY` continua não nula na prática.
- As FKs sem cláusula explícita usam `ON UPDATE NO ACTION` e `ON DELETE NO ACTION`.

| Tabela | Linhas | Finalidade atual |
| --- | ---: | --- |
| `manufacturer` | 28 | Fabricantes e categoria de equipamento. |
| `inverter` | 314 | Identidade, características, cinco grandezas de saída CA, sobrecarga e totais agregados. |
| `mppt` | 317 | Grupos de MPPT e seus limites CC. |
| `module` | 418 | Identidade e características elétricas/mecânicas dos módulos. |
| `inverter_system` | 465 | Tipos/capacidades de sistema associados ao inversor. |
| `inverter_communication` | 1.202 | Meios de comunicação declarados para o inversor. |
| `inverter_output_mode` | 366 | Modos de saída associados diretamente ao inversor. |

## `manufacturer`

```sql
CREATE TABLE manufacturer(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL,
    CATEGORY INTEGER CHECK (CATEGORY IN (0, 1, 2)) DEFAULT 0
)
```

`CATEGORY`: 0=inversores, 1=módulos, 2=ambos, confirmado pela GUI e pelas consultas. O `CHECK` é estrutural para o significado numérico atual. Não há índice ou unicidade de nome. Não existem nomes repetidos sem diferenciar maiúsculas/minúsculas no snapshot.

## `inverter`

| Campo | Tipo / nulabilidade / default atuais | Unidade/semântica e uso real |
| --- | --- | --- |
| `ID` | `INTEGER PK AUTOINCREMENT` | Identidade persistida, usada por todas as tabelas filhas. |
| `MODEL` | `TEXT NOT NULL` | Modelo; busca, ordenação, cadastro e apresentação. |
| `MANUFACTURER_ID` | `INTEGER NOT NULL` | FK para fabricante; busca/cadastro. |
| `DIM_WIDTH`, `DIM_HEIGHT`, `DIM_DEPTH` | `REAL NULL DEFAULT -1` | mm; cadastro e ficha, não entram no cálculo FV atual. |
| `DIM_WEIGHT` | `REAL NULL DEFAULT -1` | kg; cadastro e ficha. |
| `MAX_OPERATING_TEMPERATURE`, `MIN_OPERATING_TEMPERATURE` | `INTEGER NULL`, sem default | °C; cadastro/ficha. Temperatura negativa pode ser válida. |
| `COOLING_MODE`, `PROTECTION_DEGREE`, `TOPOLOGY` | `TEXT NOT NULL` | Cadastro/ficha; o domínio valida presença, não vocabulário rígido. |
| `RATED_ACTIVE_POWER` | `INTEGER NULL DEFAULT -1` | W; potência nominal única do inversor, usada no cálculo de sobrecarga, busca, matriz e detalhes. |
| `MAX_ACTIVE_POWER` | `INTEGER NULL DEFAULT -1` | W; busca, cadastro e apresentação; não é potência nominal do motor. |
| `RATED_OUTPUT_VOLTAGE` | `REAL NULL DEFAULT -1` | Vac; busca, cartão e detalhes. |
| `RATED_OUTPUT_CURRENT`, `MAX_OUTPUT_CURRENT` | `REAL NULL DEFAULT -1` | Aac; filtros e detalhes. |
| `OVERLOAD` | `INTEGER NULL DEFAULT -1` | percentual adicional; `50` significa 50%. Sessão pode substituir sem gravar. |
| `NUMBER_OF_TRACKERS` | `INTEGER NULL DEFAULT -1` | quantidade física de MPPTs; valida grupos, decodifica `MPPT_INDEX` e alimenta cálculos/apresentação. |
| `NUMBER_OF_INPUTS` | `INTEGER NULL DEFAULT -1` | total agregado de entradas; validado contra grupos MPPT e usado no cálculo/apresentação. |
| `ACTIVE` | `INTEGER NOT NULL`, sem default, `CHECK (ACTIVE IN (0,1))` | booleano de catálogo. Principal lista ativos/inativos; matriz filtra ativos. |

DDL adicional: FK `MANUFACTURER_ID → manufacturer.ID`, sem cascata. Índices `idx_inverter_manufacturer_id` e `idx_inverter_model`, ambos B-tree não únicos. Há uma duplicidade real de `(MANUFACTURER_ID, MODEL)`: fabricante 1, modelo `SIW200H M037 W00`, IDs 147 e 253. Não existe check numérico além de `ACTIVE`.

As cinco grandezas CA (`RATED_ACTIVE_POWER` até `MAX_OUTPUT_CURRENT`) são tratadas pelo código como um único perfil implícito e serão candidatas à separação documental em `inverter_ac_output`; hoje filtros combinam diretamente colunas da mesma linha `inverter`.

## `mppt`

| Campo | Tipo / nulabilidade / default atuais | Unidade/semântica e uso real |
| --- | --- | --- |
| `ID` | `INTEGER PK AUTOINCREMENT` | Identidade do grupo. |
| `INVERTER_ID` | `INTEGER NOT NULL` | FK para inversor. |
| `MPPT_INDEX` | `INTEGER NULL DEFAULT 0` | Codifica posições físicas: `0` significa grupo homogêneo que cobre todos os MPPTs; grupos heterogêneos usam produto de primos correspondentes às posições. Não é ordinal simples. |
| `NUMBER_OF_INPUTS` | `INTEGER NULL DEFAULT -1` | entradas **por MPPT** daquele grupo; multiplicado pela quantidade de posições para validar o total do inversor. |
| `MAX_INPUT_VOLTAGE` | `INTEGER NULL DEFAULT -1` | Vcc, tensão máxima absoluta de entrada. |
| `MIN_STARTUP_VOLTAGE` | `INTEGER NULL DEFAULT -1` | Vcc, tensão mínima de partida. |
| `MAX_OPERATING_VOLTAGE`, `MIN_OPERATING_VOLTAGE` | `INTEGER NULL DEFAULT -1` | Vcc, faixa operacional MPPT; usada no limite de módulos em série. |
| `MAX_FULL_LOAD_VOLTAGE`, `MIN_FULL_LOAD_VOLTAGE` | `INTEGER NULL DEFAULT -1` | Vcc, faixa de plena carga; usada quando essa restrição não é ignorada. |
| `RATED_INPUT_VOLTAGE` | `INTEGER NULL DEFAULT -1` | Vcc, nominal CC; cadastro/apresentação, não utilizado pelo motor atual. |
| `MAX_SHORT_CIRCUIT_CURRENT` | `REAL NULL DEFAULT -1` | Acc por MPPT/grupo, usada no limite de strings por Isc. |
| `MAX_OPERATING_CURRENT` | `REAL NULL DEFAULT -1` | Acc por MPPT/grupo, usada no limite de strings por corrente operacional. Não há corrente por string no schema. |

FK `INVERTER_ID → inverter.ID ON DELETE CASCADE`; `ON UPDATE NO ACTION`. Índice não único `idx_mppt_inverter_id`. Não há checks ou unicidade. Existem 302 linhas com `MPPT_INDEX=0`; maior valor codificado 2145. Sentinelas `-1`: 57 em cada limite Full Load e 37 em tensão nominal. Nenhum outro `-1`, `NULL`, vazio ou `N/D` foi observado no snapshot. O código trata grandezas ausentes com regras próprias; não se pode derivar corrente por string dividindo corrente do MPPT por entradas.

## `module`

| Campo | Tipo / nulabilidade / default atuais | Unidade/semântica e uso real |
| --- | --- | --- |
| `ID` | `INTEGER PK AUTOINCREMENT` | Identidade persistida. |
| `MODEL` | `TEXT NOT NULL` | Busca, ordenação, cadastro e apresentação. |
| `MANUFACTURER_ID` | `INTEGER NOT NULL` | FK para fabricante. |
| `DIM_WIDTH`, `DIM_HEIGHT`, `DIM_DEPTH` | `REAL NULL DEFAULT -1` | mm; cadastro/ficha. |
| `DIM_WEIGHT` | `REAL NULL DEFAULT -1` | kg; cadastro/ficha. |
| `WP` | `INTEGER NULL DEFAULT -1` | Wp/W; potência nominal usada no cálculo, busca, matriz e apresentação. |
| `VMPP` | `REAL NULL DEFAULT -1` | Vcc; cálculo de série após compensação térmica. |
| `IMPP` | `REAL NULL DEFAULT -1` | Acc; cálculo de strings por corrente operacional. |
| `VOC` | `REAL NULL DEFAULT -1` | Vcc; limite máximo de série após compensação térmica. |
| `ISC` | `REAL NULL DEFAULT -1` | Acc; limite de strings por curto-circuito após compensação térmica. |
| `SOLAR_CELLS` | `TEXT NULL`, check fechado | Tecnologia/material; filtro, cadastro e ficha. |
| `CELL_TYPE` | `TEXT NULL`, check fechado | Tipo de célula; filtro, cadastro e ficha. |
| `SURFACE_TYPE` | `TEXT NULL`, check fechado | Superfície; filtro, cadastro e ficha. |
| `COEF_PMAX` | `REAL NULL DEFAULT -0.35` | %/°C; cálculo de potência compensada. |
| `COEF_VOC` | `REAL NULL DEFAULT -0.3` | %/°C; usado como aproximação atual para compensar Voc e Vmpp. |
| `COEF_ISC` | `REAL NULL DEFAULT 0.05` | %/°C; usado como aproximação atual para Isc e Impp. |
| `ACTIVE` | `INTEGER NOT NULL`, sem default, check 0/1 | booleano de catálogo; matriz seleciona somente ativos. |

Checks fechados: `SOLAR_CELLS IN ('MONOCRISTALINO','POLICRISTALINO')`, `CELL_TYPE IN ('FULL CELL','HALF CELL')`, `SURFACE_TYPE IN ('MONOFACIAL','BIFACIAL')`; check estrutural `ACTIVE IN (0,1)`. FK fabricante sem cascata. Índices não únicos por fabricante e modelo. Não há duplicidade de fabricante+modelo no snapshot. Os coeficientes negativos são valores físicos legítimos, não sentinelas.

## Relações textuais do inversor

| Tabela | Colunas | FK / índice | Check atual | Uso real |
| --- | --- | --- | --- | --- |
| `inverter_system` | `ID`, `INVERTER_ID NOT NULL`, `SYSTEM_TYPE TEXT NULL` | FK inversor `ON DELETE CASCADE`; índice em `INVERTER_ID` | `ON-GRID`, `OFF-GRID`, `GRIDZERO`, `HYBRID` | Busca, cadastro, ficha e classificação implícita das capacidades. |
| `inverter_communication` | `ID`, `INVERTER_ID NULL`, `COMMUNICATION_TYPE TEXT NULL` | FK inversor sem cascata; **sem índice** | `DISPLAY`, `RS485`, `WIFI`, `LED`, `USB`, `4G` | Busca, cadastro e ficha. A ausência de cascata pode bloquear exclusão do pai se FKs estiverem habilitadas; diverge das outras relações. |
| `inverter_output_mode` | `ID`, `INVERTER_ID NOT NULL`, `OUTPUT_MODE TEXT NULL` | FK inversor `ON DELETE CASCADE`; índice em `INVERTER_ID` | `THREE_PHASE_FOUR_WIRE`, `THREE_PHASE_THREE_WIRE`, `SINGLE_PHASE` | Busca, cadastro e ficha. Atualmente é associação direta e não catálogo global. |

Não há pares duplicados `(INVERTER_ID, valor)` nessas três tabelas, mas também não existe `UNIQUE` que impeça duplicatas futuras. Os três checks são vocabulários fechados. O cadastro e a busca repetem esses vocabulários no código; valores como CAN, RS232, Ethernet, GPRS e Split Phase não cabem no SQLite atual sem mudança de schema.

## Checks atuais

| Categoria | Check | Proposta preliminar para revisão |
| --- | --- | --- |
| Estrutural | `manufacturer.CATEGORY IN (0,1,2)` | Manter enquanto a categoria continuar numérica com esses três significados. |
| Estrutural | `inverter.ACTIVE IN (0,1)`; `module.ACTIVE IN (0,1)` | Manter como booleano/coerência estrutural no MySQL. |
| Vocabulário | três classificações de módulo | Remover check fechado; aplicação sugere/canonicaliza e preserva desconhecidos. |
| Vocabulário | `SYSTEM_TYPE` | Remover check fechado; regras condicionais ficam no serviço. |
| Vocabulário | `COMMUNICATION_TYPE` | Remover check fechado; aplicação oferece sugestões extensíveis. |
| Vocabulário | `OUTPUT_MODE` | O papel da tabela muda na proposta: catálogo global sem enum rígido. |

Contagem: nove expressões `CHECK` no DDL (categoria, dois ACTIVE, três classificações do módulo e três relações). Não há checks de positividade, faixas físicas, coerência entre mínimo/máximo ou presença de filhos; essas regras são parcial ou totalmente tratadas na aplicação.

## Sentinelas e ambiguidades

- Defaults `-1` estão declarados em muitas grandezas, embora no snapshot só ocorram nos três campos MPPT listados. Testes exercitam `-1` também para módulo e sobrecarga. A semântica é implícita e varia por consumidor.
- `MPPT_INDEX=0` **não é desconhecido**: é sentinela estrutural válida de grupo homogêneo.
- `ACTIVE=0` e `CATEGORY=0` são valores válidos, não ausência. `OVERLOAD=0` ocorre em um inversor e pode ser válido.
- Não foram encontrados `NULL`, strings vazias nem `N/D` armazenados nas linhas atuais. Isso não elimina a nulabilidade declarada no schema.
- `src/optimus_sun.py` contém uma chave de estrutura chamada `RATED_OUTPUT_VOLTAGE` no bloco MPPT onde o schema usa `RATED_INPUT_VOLTAGE`; o carregamento/cálculo efetivo não usa esse nominal. É uma inconsistência nominal legada a não transportar silenciosamente.
- Dimensões, proteção, refrigeração, topologia e classificações são cadastro/apresentação. As grandezas CA alimentam busca/apresentação; `RATED_ACTIVE_POWER` também alimenta o cálculo. MPPT e grandezas elétricas/térmicas do módulo alimentam diretamente o motor.

## Efeito esperado no código, sem alteração nesta etapa

O acesso atual depende de `sqlite3`, placeholders `?`, `PRAGMA`, `COLLATE NOCASE` e `sqlite3.Row` em `optimus_sun.py`, `equipment_search.py`, `catalog/repository.py`, `compatibility/repository.py`, ferramentas e testes. A separação de perfis exigirá mudar DTOs/repositórios e tornar a saída parte explícita do contexto de cálculo. O cadastro deverá substituir as listas 1:N atuais por catálogo/perfis coerentes; busca CA deve aplicar critérios à mesma linha de perfil. Fórmulas em `optimus_lib.py` e `compatibility/engine.py` não precisam conhecer SQL, mas hoje recebem uma única potência nominal derivada de `inverter.RATED_ACTIVE_POWER`.
