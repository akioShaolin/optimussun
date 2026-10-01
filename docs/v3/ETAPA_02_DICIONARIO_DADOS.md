# Etapa 02 — dicionário de dados proposto para a v3

Proposta documental em 01/10/2026 para a futura persistência MySQL do Optimus Sun v3. Este arquivo não é DDL executável e não autoriza migração. O inventário fiel do SQLite existente está em [ETAPA_02_SCHEMA_ATUAL.md](ETAPA_02_SCHEMA_ATUAL.md).

## Convenções propostas

- Engine: `InnoDB`; charset `utf8mb4`; collation Unicode case-insensitive a definir na implementação.
- Identificadores: `INT UNSIGNED AUTO_INCREMENT`. O volume atual e o crescimento previsível não justificam `BIGINT` para catálogos; a aplicação não deve depender do tamanho físico do ID.
- `MPPT_INDEX`: `BIGINT UNSIGNED`, pois preserva a codificação atual por produto de primos e pode crescer muito mais rapidamente que a quantidade de linhas.
- Grandezas físicas usam `DECIMAL`, evitando aproximações binárias de `FLOAT`. As precisões abaixo são propostas conservadoras e devem ser confrontadas com os datasheets antes do DDL definitivo.
- Potência em W, tensão em V, corrente em A, dimensões em mm, massa em kg, temperatura em °C, tempo em ms e percentuais em pontos percentuais (`50.000` significa 50%).
- Dado técnico desconhecido é `NULL`. Zero só representa zero real; `-1` não será sentinela genérica.
- Nomes SQL permanecem em inglês e `snake_case` no futuro DDL. Neste documento, nomes aparecem em maiúsculas para facilitar o paralelo com o SQLite atual.
- `ACTIVE` só existe onde desativar sem apagar tem significado de negócio. Tabelas filhas puramente descritivas não recebem a coluna por padrão.
- Regras de coerência entre perfis, campos obrigatórios para ativação e capacidades por tipo de sistema ficam no serviço de domínio. O banco mantém integridade referencial e invariantes estruturais locais.

## Visão das relações

```text
manufacturer 1 ── N inverter 1 ── N mppt
                           ├────── N inverter_ac_output ── N:1 inverter_output_mode
                           ├────── N inverter_ac_input
                           ├────── N inverter_eps_output ─ N:1 inverter_output_mode
                           ├────── N inverter_battery
                           ├────── N inverter_system
                           └────── N inverter_communication

manufacturer 1 ── N module
```

Um perfil elétrico é uma linha coerente: os valores usados juntos devem vir da mesma linha. A presença do perfil declara suporte àquela interface; não haverá tabela-ponte redundante de capacidades.

## 1. `manufacturer`

Mantém fabricantes de inversores, módulos ou ambos.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade. |
| `NAME` | `TEXT` | `VARCHAR(150)` | não | Nome exibido e pesquisável. |
| `CATEGORY` | `INTEGER` | `TINYINT UNSIGNED` | não / `0` | 0=inversor, 1=módulo, 2=ambos; `CHECK (CATEGORY IN (0,1,2))`. |

Índices: `INDEX(NAME)`. A unicidade de nome depende da política de canonicalização pendente. Exclusão deve ser `RESTRICT` enquanto houver equipamentos associados.

## 2. `inverter`

Identidade e propriedades comuns do inversor. As cinco grandezas CA legadas deixam esta tabela e passam a compor perfis em `inverter_ac_output`.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade. |
| `MODEL` | `TEXT` | `VARCHAR(255)` | não | Modelo comercial. |
| `MANUFACTURER_ID` | `INTEGER` | `INT UNSIGNED` FK | não | Fabricante; exclusão `RESTRICT`. |
| `DIM_WIDTH` | `REAL` | `DECIMAL(10,2)` | sim / `NULL` | Largura em mm. |
| `DIM_HEIGHT` | `REAL` | `DECIMAL(10,2)` | sim / `NULL` | Altura em mm. |
| `DIM_DEPTH` | `REAL` | `DECIMAL(10,2)` | sim / `NULL` | Profundidade em mm. |
| `DIM_WEIGHT` | `REAL` | `DECIMAL(10,3)` | sim / `NULL` | Massa em kg. |
| `MAX_OPERATING_TEMPERATURE` | `INTEGER` | `DECIMAL(6,2)` | sim / `NULL` | Limite superior; pode ser negativo. |
| `MIN_OPERATING_TEMPERATURE` | `INTEGER` | `DECIMAL(6,2)` | sim / `NULL` | Limite inferior; pode ser negativo. |
| `COOLING_MODE` | `TEXT` | `VARCHAR(150)` | sim / `NULL` | Descrição extensível. |
| `PROTECTION_DEGREE` | `TEXT` | `VARCHAR(100)` | sim / `NULL` | Grau IP/NEMA ou equivalente. |
| `TOPOLOGY` | `TEXT` | `VARCHAR(150)` | sim / `NULL` | Topologia declarada. |
| `OVERLOAD` | `INTEGER` | `DECIMAL(7,3)` | sim / `NULL` | Sobrecarga CC cadastrada em %. |
| `NUMBER_OF_TRACKERS` | `INTEGER` | `SMALLINT UNSIGNED` | sim / `NULL` | Total físico de MPPTs. |
| `NUMBER_OF_INPUTS` | `INTEGER` | `SMALLINT UNSIGNED` | sim / `NULL` | Total físico de entradas CC. |
| `MAX_EFFICIENCY` | — (novo) | `DECIMAL(6,3)` | sim / `NULL` | Eficiência máxima em %. |
| `EURO_EFFICIENCY` | — (novo) | `DECIMAL(6,3)` | sim / `NULL` | Eficiência europeia em %. |
| `ACTIVE` | `INTEGER` | `BOOLEAN` | não / `FALSE` | Disponibilidade no catálogo. |
| `ROW_VERSION` | — (novo) | `INT UNSIGNED` | não / `1` | Concorrência otimista; incremento pelo serviço. |

Campos removidos do pai: `RATED_ACTIVE_POWER`, `MAX_ACTIVE_POWER`, `RATED_OUTPUT_VOLTAGE`, `RATED_OUTPUT_CURRENT` e `MAX_OUTPUT_CURRENT`. Índices: `(MANUFACTURER_ID, MODEL)`, `MODEL` e `ACTIVE`. Não se propõe `UNIQUE(MANUFACTURER_ID, MODEL)` enquanto a duplicidade real não for conciliada.

Checks locais: dimensões, massa, sobrecarga e eficiências não negativas quando presentes; eficiências no intervalo 0–100; mínimo de temperatura não maior que máximo quando ambos existirem. A completude necessária para ativar um inversor pertence ao domínio.

## 3. `mppt`

Preserva grupos de MPPT e a semântica existente de `MPPT_INDEX`. Correntes por MPPT e por string tornam-se grandezas independentes.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade do grupo. |
| `INVERTER_ID` | `INTEGER` | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `MPPT_INDEX` | `INTEGER` | `BIGINT UNSIGNED` | não / `0` | `0`=grupo homogêneo; demais valores preservam produto de primos. |
| `NUMBER_OF_INPUTS` | `INTEGER` | `SMALLINT UNSIGNED` | sim / `NULL` | Entradas por MPPT do grupo. |
| `MAX_INPUT_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Tensão CC máxima absoluta. |
| `MIN_STARTUP_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Tensão mínima de partida. |
| `MAX_OPERATING_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Faixa MPPT, limite superior. |
| `MIN_OPERATING_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Faixa MPPT, limite inferior. |
| `MAX_FULL_LOAD_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Plena carga, limite superior. |
| `MIN_FULL_LOAD_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Plena carga, limite inferior. |
| `RATED_INPUT_VOLTAGE` | `INTEGER` | `DECIMAL(10,3)` | sim / `NULL` | Tensão CC nominal. |
| `MAX_SHORT_CIRCUIT_CURRENT_PER_MPPT` | `REAL` (`MAX_SHORT_CIRCUIT_CURRENT`) | `DECIMAL(10,3)` | sim / `NULL` | Limite Isc agregado do MPPT. |
| `MAX_SHORT_CIRCUIT_CURRENT_PER_STRING` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Limite Isc de cada entrada/string; nunca derivado por divisão. |
| `MAX_OPERATING_CURRENT_PER_MPPT` | `REAL` (`MAX_OPERATING_CURRENT`) | `DECIMAL(10,3)` | sim / `NULL` | Limite operacional agregado do MPPT. |
| `MAX_OPERATING_CURRENT_PER_STRING` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Limite operacional de cada entrada/string; nunca derivado. |

Índice em `INVERTER_ID`; exclusão do inversor em cascata. Não se propõe unicidade automática de `(INVERTER_ID, MPPT_INDEX)` até validar todos os padrões heterogêneos e a edição de grupos. Checks locais impedem grandezas negativas e garantem mínimos não maiores que máximos quando ambos estiverem presentes.

## 4. `module`

Catálogo de módulos fotovoltaicos.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade. |
| `MODEL` | `TEXT` | `VARCHAR(255)` | não | Modelo comercial. |
| `MANUFACTURER_ID` | `INTEGER` | `INT UNSIGNED` FK | não | Fabricante; exclusão `RESTRICT`. |
| `DIM_WIDTH`, `DIM_HEIGHT`, `DIM_DEPTH` | `REAL` | `DECIMAL(10,2)` | sim / `NULL` | Dimensões em mm. |
| `DIM_WEIGHT` | `REAL` | `DECIMAL(10,3)` | sim / `NULL` | Massa em kg. |
| `WP` | `INTEGER` | `DECIMAL(12,2)` | sim / `NULL` | Potência nominal em Wp. |
| `VMPP`, `VOC` | `REAL` | `DECIMAL(10,3)` | sim / `NULL` | Tensões CC em V. |
| `IMPP`, `ISC` | `REAL` | `DECIMAL(10,3)` | sim / `NULL` | Correntes CC em A. |
| `SOLAR_CELLS` | `TEXT` | `VARCHAR(100)` | sim / `NULL` | Material/tecnologia, sem enum fechado. |
| `CELL_TYPE` | `TEXT` | `VARCHAR(100)` | sim / `NULL` | Tipo de célula, sem enum fechado. |
| `SURFACE_TYPE` | `TEXT` | `VARCHAR(100)` | sim / `NULL` | Superfície, sem enum fechado. |
| `COEF_PMAX`, `COEF_VOC`, `COEF_ISC` | `REAL` | `DECIMAL(8,5)` | sim / `NULL` | Coeficientes em %/°C; negativos são válidos. |
| `ACTIVE` | `INTEGER` | `BOOLEAN` | não / `FALSE` | Disponibilidade no catálogo. |
| `ROW_VERSION` | — (novo) | `INT UNSIGNED` | não / `1` | Concorrência otimista. |

Índices: `(MANUFACTURER_ID, MODEL)`, `MODEL` e `ACTIVE`. A proposta pode usar `UNIQUE(MANUFACTURER_ID, MODEL)` após definir canonicalização; o snapshot não possui duplicatas desse par. Checks fechados de tecnologia são removidos. Checks locais impedem dimensões e grandezas elétricas negativas, sem confundir coeficientes físicos negativos com ausência.

## 5. `inverter_ac_output`

Perfil de saída CA de operação on-grid. Um inversor pode ter mais de um perfil coerente para redes/modos diferentes.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | — (novo) | `INT UNSIGNED` PK AI | não | Identidade do perfil. |
| `INVERTER_ID` | implícito no pai | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `OUTPUT_MODE_ID` | associação textual separada | `INT UNSIGNED` FK | não | Catálogo global; exclusão `RESTRICT`. |
| `RATED_ACTIVE_POWER` | `inverter.INTEGER` | `DECIMAL(12,2)` | sim / `NULL` | Potência ativa nominal contínua em W. |
| `MAX_ACTIVE_POWER` | `inverter.INTEGER` | `DECIMAL(12,2)` | sim / `NULL` | Potência ativa máxima em W. |
| `RATED_OUTPUT_VOLTAGE` | `inverter.REAL` | `DECIMAL(10,3)` | sim / `NULL` | Tensão nominal CA. |
| `RATED_OUTPUT_CURRENT` | `inverter.REAL` | `DECIMAL(10,3)` | sim / `NULL` | Corrente nominal CA. |
| `MAX_OUTPUT_CURRENT` | `inverter.REAL` | `DECIMAL(10,3)` | sim / `NULL` | Corrente máxima CA. |
| `ACTIVE` | — (novo) | `BOOLEAN` | não / `FALSE` | Perfil disponível para uso. |

Índices em `INVERTER_ID`, `OUTPUT_MODE_ID` e `(INVERTER_ID, ACTIVE)`. A busca deve aplicar todos os filtros elétricos à mesma linha, sem combinar valores de perfis distintos. No domínio, on-grid exige ao menos um perfil ativo de saída CA.

## 6. `inverter_ac_input`

Perfil de entrada CA, aplicável a equipamentos híbridos quando houver carregamento/entrada pela rede ou gerador.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | — (novo) | `INT UNSIGNED` PK AI | não | Identidade do perfil. |
| `INVERTER_ID` | — (novo) | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `RATED_ACTIVE_POWER` | — (novo) | `DECIMAL(12,2)` | sim / `NULL` | Potência nominal absorvida em W. |
| `MAX_ACTIVE_POWER` | — (novo) | `DECIMAL(12,2)` | sim / `NULL` | Potência máxima absorvida em W. |
| `RATED_INPUT_VOLTAGE` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Tensão nominal CA de entrada. |
| `RATED_INPUT_CURRENT` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Corrente nominal CA de entrada. |
| `MAX_INPUT_CURRENT` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Corrente máxima CA de entrada. |
| `ACTIVE` | — (novo) | `BOOLEAN` | não / `FALSE` | Perfil disponível para uso. |

Índices em `INVERTER_ID` e `(INVERTER_ID, ACTIVE)`. A presença do perfil declara suporte; não se cria flag equivalente no pai.

## 7. `inverter_eps_output`

Perfil de saída de emergência/off-grid. Potência nominal contínua e pico permanecem conceitos separados; tempo de comutação desconhecido é `NULL`, nunca zero.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | — (novo) | `INT UNSIGNED` PK AI | não | Identidade do perfil. |
| `INVERTER_ID` | — (novo) | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `OUTPUT_MODE_ID` | — (novo) | `INT UNSIGNED` FK | não | Catálogo global; exclusão `RESTRICT`. |
| `RATED_ACTIVE_POWER` | — (novo) | `DECIMAL(12,2)` | sim / `NULL` | Potência contínua em W. |
| `MAX_PEAK_ACTIVE_POWER` | — (novo) | `DECIMAL(12,2)` | sim / `NULL` | Pico em W, sem substituir potência contínua. |
| `RATED_OUTPUT_VOLTAGE` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Tensão nominal da saída EPS. |
| `RATED_OUTPUT_CURRENT` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Corrente nominal da saída EPS. |
| `MAX_OUTPUT_CURRENT` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Corrente máxima da saída EPS. |
| `SWITCHING_TIME` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Tempo de comutação em ms. |
| `ACTIVE` | — (novo) | `BOOLEAN` | não / `FALSE` | Perfil disponível para uso. |

Índices em `INVERTER_ID`, `OUTPUT_MODE_ID` e `(INVERTER_ID, ACTIVE)`. Off-grid exige perfil EPS e não deve receber perfil CA de saída fictício apenas para preencher campos legados.

## 8. `inverter_battery`

Perfis de interface/configuração de bateria. O nome conceitual fechado é `inverter_battery`.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | — (novo) | `INT UNSIGNED` PK AI | não | Identidade da configuração. |
| `INVERTER_ID` | — (novo) | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `BATTERY_INDEX` | — (novo) | `SMALLINT UNSIGNED` | não | Interface física: 0=primeira, 1=segunda etc. |
| `BATTERY_TYPE` | — (novo) | `VARCHAR(150)` | sim / `NULL` | Química/família suportada, extensível. |
| `BATTERY_VOLTAGE_MIN` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Tensão mínima em V. |
| `BATTERY_VOLTAGE_MAX` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Tensão máxima em V. |
| `MAX_CHARGE_CURRENT` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Corrente máxima de carga em A. |
| `MAX_DISCHARGE_CURRENT` | — (novo) | `DECIMAL(10,3)` | sim / `NULL` | Corrente máxima de descarga em A. |
| `BATTERY_COM` | — (novo) | `VARCHAR(150)` | sim / `NULL` | Protocolo/meio de comunicação com bateria. |
| `ACTIVE` | — (novo) | `BOOLEAN` | não / `FALSE` | Configuração disponível para uso. |

Índices em `INVERTER_ID`, `(INVERTER_ID, BATTERY_INDEX)` e `(INVERTER_ID, ACTIVE)`. Deliberadamente não há `UNIQUE(INVERTER_ID, BATTERY_INDEX)`: uma interface física pode possuir várias configurações suportadas. Checks locais garantem valores não negativos e tensão mínima não maior que máxima.

## 9. `inverter_system`

Capacidades de sistema declaradas pelo inversor.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade. |
| `INVERTER_ID` | `INTEGER` | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `SYSTEM_TYPE` | `TEXT` | `VARCHAR(100)` | não | Valor extensível, sem `CHECK` fechado. |

Índices em `INVERTER_ID` e `SYSTEM_TYPE`. Não se cria `ACTIVE`: adicionar/remover a relação representa a capacidade. Regras de domínio: on-grid implica saída CA; híbrido implica saída CA e pode ter entrada CA, EPS e bateria; off-grid implica EPS, pode ter bateria e não exige saída CA fictícia.

## 10. `inverter_communication`

Meios/protocolos de comunicação do inversor.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade. |
| `INVERTER_ID` | `INTEGER` | `INT UNSIGNED` FK | não | Pai; exclusão `CASCADE`. |
| `COMMUNICATION_TYPE` | `TEXT` | `VARCHAR(100)` | não | Valor extensível, sem `CHECK` fechado. |

Índices em `INVERTER_ID` e `COMMUNICATION_TYPE`. A nulabilidade e a política de exclusão divergentes do SQLite são normalizadas. Não se cria `ACTIVE`: a existência da linha declara suporte.

## 11. `inverter_output_mode`

Catálogo global editável de modos de saída, não mais associação direta entre inversor e texto.

| Campo | SQLite atual | MySQL proposto | Nulo/default | Regra e finalidade |
| --- | --- | --- | --- | --- |
| `ID` | `INTEGER` | `INT UNSIGNED` PK AI | não | Identidade global. |
| `OUTPUT_MODE` | `TEXT` | `VARCHAR(100)` | não | Nome do modo, extensível e editável. |
| `ACTIVE` | — (novo) | `BOOLEAN` | não / `TRUE` | Disponibilidade para novos perfis sem invalidar referências antigas. |

`INVERTER_ID` é removido. `inverter_ac_output.OUTPUT_MODE_ID` e `inverter_eps_output.OUTPUT_MODE_ID` referenciam o catálogo com exclusão `RESTRICT`. Índices em `OUTPUT_MODE` e `ACTIVE`. Não haverá enum/check fechado; a política de unicidade textual depende da canonicalização pendente.

## Integridade referencial proposta

| Relação | Ao excluir pai | Justificativa |
| --- | --- | --- |
| fabricante → inversor/módulo | `RESTRICT` | Impede equipamento órfão e perda silenciosa de catálogo. |
| inversor → MPPT, perfis, bateria, sistema e comunicação | `CASCADE` | São partes exclusivamente pertencentes ao equipamento. |
| modo de saída → perfis CA/EPS | `RESTRICT` | Um modo referenciado não pode desaparecer; desativação preserva histórico. |

IDs são imutáveis; `ON UPDATE RESTRICT`/`NO ACTION` é suficiente. Operações destrutivas continuam passando pelo serviço, com transação e auditoria da futura aplicação.

## Validação: banco versus aplicação

O banco deve garantir tipos, FKs, booleanos, categoria de fabricante, não negatividade de grandezas que fisicamente não podem ser negativas, faixas percentuais inequívocas e relações mínimo/máximo dentro da mesma linha. Vocabulários sujeitos a evolução não recebem `CHECK` fechado.

A aplicação deve garantir:

- campos mínimos antes de ativar equipamentos e perfis;
- compatibilidade entre `SYSTEM_TYPE` e perfis existentes;
- coerência dos totais agregados do inversor com grupos MPPT;
- validade e não sobreposição da codificação `MPPT_INDEX`;
- seleção de um único perfil elétrico coerente por cálculo/busca;
- prevenção de duplicatas conforme a futura canonicalização;
- concorrência otimista com `ROW_VERSION`;
- interpretação explícita de unidades e conversão de sentinelas na migração.

## Mapeamento da migração futura

| Origem SQLite | Destino proposto | Tratamento |
| --- | --- | --- |
| `inverter` exceto cinco campos CA | `inverter` | `-1` técnico vira `NULL`; preservar IDs se a estratégia permitir. |
| cinco campos CA de `inverter` | `inverter_ac_output` **ou** `inverter_eps_output` | Classificar pelo sistema e datasheet; não copiar cegamente para ambos. |
| `inverter_output_mode` por inversor | catálogo `inverter_output_mode` + FKs de perfis | Deduplicar/canonicalizar modos e associar cada perfil correto. |
| `mppt.MAX_*CURRENT` | colunas `*_PER_MPPT` | Preservar como corrente agregada; campos por string ficam `NULL` até fonte explícita. |
| `MPPT_INDEX=0` | `MPPT_INDEX=0` | Preservar significado de grupo homogêneo. |
| demais `-1` e ausência técnica | `NULL` | Zero não substitui desconhecido. |
| sistemas e comunicações | tabelas homônimas | Remover checks fechados sem inventar capacidades. |
| classificações de módulo | `VARCHAR` extensível | Preservar texto existente; normalização posterior controlada. |

O inversor off-grid não deve ganhar saída CA on-grid artificial. Para híbridos, os cinco campos legados só podem ser classificados após identificar se a ficha se refere à saída CA, EPS ou a ambas com valores coincidentes.

## Impacto esperado no código

- Repositórios deixam de montar SQL SQLite diretamente e passam a carregar agregados com perfis explícitos.
- O motor de compatibilidade continua recebendo grandezas, mas a potência nominal deve vir do perfil escolhido; a fórmula não decide qual perfil usar.
- Busca por saída/entrada/EPS precisa aplicar todos os critérios à mesma linha de perfil.
- Cadastro passa a editar listas de perfis e o catálogo global de modos de saída.
- DTOs precisam distinguir corrente por MPPT e por string e impedir conversões implícitas.
- Ferramentas da matriz precisam manter explícito qual perfil fornece a potência nominal usada.
- A futura camada MySQL deve substituir `?`, `PRAGMA`, `COLLATE NOCASE` e `sqlite3.Row` sem espalhar detalhes do driver pelo domínio.

## Decisões fechadas nesta etapa

- MySQL com InnoDB e `utf8mb4` como destino proposto.
- `battery` é `inverter_battery`; `BATTERY_INDEX` identifica a interface física, mas não é único por inversor.
- Saída CA, entrada CA e saída EPS são perfis separados; potência EPS contínua não se confunde com pico.
- A existência de perfis expressa suporte; não haverá flags ou ponte redundante.
- `inverter_output_mode` torna-se catálogo global editável, referenciado por perfis CA e EPS.
- Dados desconhecidos usam `NULL`; zero e `MPPT_INDEX=0` mantêm significados reais próprios.
- Correntes por MPPT e por string são independentes e jamais derivadas por divisão.
- Cada filtro/cálculo usa uma única linha de perfil coerente.

## Decisões ainda necessárias antes do DDL

1. Definir canonicalização, collation e regra de unicidade para fabricantes, modelos, modos de saída, sistemas e comunicações, inclusive tratamento de maiúsculas, acentos e espaços.
2. Classificar manualmente os cinco campos CA legados de inversores híbridos e off-grid durante a migração; o schema atual não informa a qual interface pertencem.
3. Confirmar, em amostra ampla de datasheets, as precisões `DECIMAL`, comprimentos de texto e limites máximos propostos.
4. Definir a identidade visual/descrição que diferencia várias configurações de bateria com o mesmo `BATTERY_INDEX`, além de como impedir duplicatas realmente idênticas.
5. Fechar os campos mínimos para ativação de cada perfil e o comportamento quando um tipo de sistema é removido, sem apagar dados técnicos inadvertidamente.
6. Validar se `(INVERTER_ID, MPPT_INDEX)` pode ser único após revisar todos os padrões heterogêneos e o fluxo de edição.
7. Definir como escolher o perfil CA nominal usado pelo motor quando um inversor tiver múltiplos perfis igualmente ativos; não é aceitável escolher pela primeira linha retornada.

Somente depois dessas decisões e da revisão humana deste dicionário deve ser escrita a primeira migração/DDL da Etapa 03.
