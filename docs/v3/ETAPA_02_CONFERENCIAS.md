# Etapa 02 — conferências do legado para migração

Leitura realizada em 02/10/2026 sobre `src/optimus_sun.db`, aberto por URI SQLite `mode=ro`. Hash SHA-256 inicial desta execução: `805f9c626a5474139dad270eecf39adc541419abb3a1db25cb9daa32e4864e36`. Nenhuma escrita ou extração de `INSERT` foi feita.

## Estado observado

- `PRAGMA integrity_check`: `ok`.
- `PRAGMA foreign_key_check`: nenhuma ocorrência.
- 28 fabricantes, 313 inversores, 317 grupos MPPT, 418 módulos, 465 relações de sistema, 1.202 comunicações e 366 associações legadas de modo.
- 65 inversores ativos e 248 inativos; 35 módulos ativos e 383 inativos.
- O inventário de 01/10 registrava 314 inversores. A diferença corresponde à correção feita pelo usuário antes desta execução; o banco não foi alterado por esta conferência.

## Duplicidades de fabricante e modelo

A comparação aplicou, ao modelo, remoção de espaços externos, redução de espaços duplicados e comparação sem diferenciar maiúsculas/minúsculas, dentro do mesmo `MANUFACTURER_ID`.

| Entidade | Duplicidades exatas/normalizadas |
| --- | ---: |
| Inversor | 0 |
| Módulo | 0 |

O duplicado histórico `SIW200H M037 W00` não existe mais no estado atual. A evidência permite preparar `UNIQUE(MANUFACTURER_ID, MODEL)`, desde que a mesma normalização seja aplicada antes da carga.

## MPPTs

- Duplicidades de `(INVERTER_ID, MPPT_INDEX)`: 0.
- Fatorações inválidas (`1`, fator repetido ou fator residual): 0.
- Grupo homogêneo `0` coexistindo com outro grupo do mesmo inversor: 0.
- Sobreposições entre posições decodificadas: 0.

A inspeção usou a sequência de primos por posição já estabelecida. Isso sustenta a unicidade proposta, mas a migração e a API ainda devem repetir as validações: igualdade de código não substitui verificação de cobertura e sobreposição.

## Modos de saída legados — conferência histórica de 02/10 antes dos ajustes

| Modos associados ao inversor | Inversores |
| ---: | ---: |
| 0 | 3 |
| 1 | 254 |
| 2 | 56 |

### Sem modo

| ID | Fabricante | Modelo |
| ---: | --- | --- |
| 277 | GROWATT | `MID22KTL3-X` |
| 278 | GROWATT | `MID25KTL3-X` |
| 236 | HUAWEI | `SUN2000-4KTL-L1` |

### Com dois modos

Todos os 56 casos possuem simultaneamente `THREE_PHASE_THREE_WIRE` e `THREE_PHASE_FOUR_WIRE`:

- **GOODWE (1):** `GW75K-MT` (ID 79).
- **GROWATT (10):** `MID6KTL3-XL` (267), `MID8KTL3-XL` (268), `MID10KTL3-XL` (269), `MID11KTL3-XL` (270), `MID12KTL3-XL` (271), `MID10KTL3-X` (272), `MID12KTL3-X` (273), `MID15KTL3-X` (274), `MID17KTL3-X` (275), `MID20KTL3-X` (276).
- **HUAWEI (22):** `SUN2000-29.9KTL` (15), `SUN2000-33KTL-A` (16), `SUN2000-36KTL` (17), `SUN2000-8KTL-M0` (19), `SUN2000-10KTL-M0` (20), `SUN2000-12KTL-M0` (21), `SUN2000-15KTL-M0` (22), `SUN2000-17KTL-M0` (23), `SUN2000-20KTL-M0` (24), `SUN2000-8KTL-M2` (25), `SUN2000-10KTL-M2` (26), `SUN2000-12KTL-M2` (27), `SUN2000-15KTL-M2` (28), `SUN2000-17KTL-M2` (29), `SUN2000-20KTL-M2` (30), `SUN2000-50KTL-M0` (36), `SUN2000-60KTL-M0` (37), `SUN2000-65KTL-M0` (38), `SUN2000-75KTL-M1` (39), `SUN2000-100KTL-M0` (40), `SUN2000-110KTL-M0` (41), `SUN2000-100KTL-M1` (43).
- **PHB (3):** `PHB35K-MT` (115), `PHB50K-MT` (116), `PHB60K-MT` (117).
- **SUNGROW (1):** `SG36KTL-M` (279).
- **WEG (19):** `SIW500G T075 W0` (201), `SIW500G T100 W0` (202), `SIW500H ST012` (204), `SIW500H ST015 ` (205), `SIW500H ST020` (206), `SIW500H ST030` (207), `SIW500H ST036` (208), `SIW500H ST040` (209), `SIW500H ST050` (210), `SIW500H ST060` (211), `SIW500H ST100` (212), `SIW500H ST012 M2` (213), `SIW500H ST015 M2` (214), `SIW500H ST020 M2` (215), `SIW400H T050 W30` (308), `SIW400H T075 W30` (309), `SIW400H T125 W30` (310), `SIW500G K075 W00` (313), `SIW500G K050 W00` (314).

### Encaminhamento histórico substituído pelo Prompt 02B

A orientação anterior era não duplicar os perfis. Ela foi substituída em 02/10/2026: os 56 pares de modos foram confirmados e agora geram dois perfis `AC_OUTPUT` por inversor. A tabela e a lista acima permanecem como evidência do estado observado antes dessa decisão.

## Reconferência após ajustes do usuário — 02/10/2026

Fonte: o mesmo arquivo `src/optimus_sun.db`, aberto novamente por URI `mode=ro`. Hash inicial desta execução complementar: `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188`. Integridade `ok` e nenhuma violação de FK.

| ID | Fabricante | Modelo | Modo atual |
| ---: | --- | --- | --- |
| 277 | GROWATT | `MID22KTL3-X` | `THREE_PHASE_FOUR_WIRE` |
| 278 | GROWATT | `MID25KTL3-X` | `THREE_PHASE_FOUR_WIRE` |
| 236 | HUAWEI | `SUN2000-4KTL-L1` | `SINGLE_PHASE` |

Distribuição atual:

| Modos associados | Inversores |
| ---: | ---: |
| 0 | 0 |
| 1 | 257 |
| 2 | 56 |

Os 56 casos continuam associados a `THREE_PHASE_THREE_WIRE` e `THREE_PHASE_FOUR_WIRE`. A migração futura cria 112 perfis `AC_OUTPUT`, um para cada par inversor+modo, copiando inicialmente potência/correntes legadas e registrando proveniência. A duplicação foi autorizada, mas não confirma o datasheet de cada configuração. Nenhum dos dois recebe padrão automaticamente: a revisão do usuário escolhe exatamente um e classifica a tensão legada. A relação `(ID legado, modo) → ID de perfil` torna a reexecução idempotente.

Hash final desta execução complementar: `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188`, idêntico ao inicial.

## Classificações que incluem off-grid

Há 21 relações `OFF-GRID`, mas todas pertencem a equipamentos também classificados como `HYBRID` e `ON-GRID`; não há equipamento exclusivamente off-grid. Isso é compatível com a decisão de que as cinco grandezas CA legadas são saída CA principal. Nenhum perfil EPS deve ser inventado a partir delas.

## Precisão efetiva

Nenhuma dimensão ou grandeza elétrica inspecionada perderia parte fracionária usando duas casas. Exceções:

| Campo | Linhas com mais de 2 casas | Exemplos observados |
| --- | ---: | --- |
| `module.COEF_PMAX` | 10 | `-0.408`, `-0.3528` |
| `module.COEF_VOC` | 41 | `-0.311`, `-0.2769`, `0.047` |
| `module.COEF_ISC` | 189 | `0.03528`, `0.043`, `0.057` |

Consequência: duas casas permanecem padrão para grandezas; coeficientes térmicos requerem cinco casas para preservar o legado sem arredondamento.

## Limite desta conferência

Não houve MySQL, DDL, migration, build, suíte completa ou teste de comportamento. As consultas foram diagnósticas e somente leitura. Antes da migração, o relatório de modos deve ser gerado novamente de forma automatizada a partir do snapshot definitivo, eliminando qualquer risco de transcrição manual.
