# Etapa 03 — relatório de implementação e ensaio

Data: 03/10/2026. Branch: `feature/v3.0.0`.

## Implementação concluída

- DDL versionado `0001` para nove tabelas de domínio e quatro tabelas técnicas: versão, execução, mapeamento de IDs e pendências.
- Importador separado em configuração, snapshot SQLite, normalização, reconciliação, transformação, domínio, persistência MySQL e CLI.
- Simulação é o padrão e não depende de MySQL.
- Carga exige ação explícita e schema cujo nome termine em `_ensaio` ou `_test`.
- Arquivo `.env` local é ignorado; variáveis de processo prevalecem; segredos não entram em argumentos/relatórios.
- Conexão remota exige CA explícita e validação de certificado/identidade; loopback não exige TLS.
- Plano JSON, relatório Markdown, resumo, snapshot e decisões usadas permitem reprodução e auditoria.
- O plano possui checksum canônico próprio; o preflight aceita inconsistências produzidas somente quando há ocorrência estruturada exata, preservando o relatório, enquanto a carga recusa qualquer plano com erros.

## Decisões físicas

- MySQL alvo informado: 8.0.46; engine InnoDB com `ROW_FORMAT=DYNAMIC`; charset/collation `utf8mb4`/`utf8mb4_0900_ai_ci`; página InnoDB mínima de 8 KiB.
- Normalização de fabricante/modelo/modo: trim e compactação por coluna gerada; índice único com comparação sem caixa/acento. A aplicação usa a mesma semântica para detectar colisões antes da carga.
- Perfil padrão: `DEFAULT_SLOT` gerado retorna `1` apenas para `IS_DEFAULT`, `NULL` nos demais; índice único composto permite vários não padrões e rejeita segundo padrão.
- `CHECK` impede padrão inativo/entrada, modo em `AC_INPUT`, saída ativa sem modo e `AC_INPUT` ativo sem grandeza nominal positiva.
- Elegibilidade híbrida de `AC_INPUT`, cobertura de grupos e exatamente um padrão para catálogo pronto são validações transacionais de domínio.
- DDL e carga são operações separadas. Nenhuma FK é desativada e não há `REPLACE`/`INSERT IGNORE`.
- A ferramenta exige MySQL 8.0.46 com modo estrito na mesma conexão usada pela operação, aceita apenas o DDL oficial e registra as assinaturas do DDL e da estrutura física; a carga usa lock por schema e verifica conteúdo na repetição idempotente.

## Simulação executada

Comando:

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py simulate `
  --source src\optimus_sun.db `
  --output .test_tmp\migration_v3\simulation-final-20261003-v3
```

Evidência:

- SHA-256 do SQLite antes/depois: `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188` — idêntico.
- SHA-256 do snapshot: `2efb2112ccb6fc206fcea4508c0ad43ba3389aae728adc38244bdaade6dd75ac`.
- SHA-256 canônico do plano: `6b3d6983316b9448ffe358c6bab0097a81a43815aa82aa26bd00ea74b8964c2b`.
- `integrity_check=ok`; nenhuma violação de FK.
- 28 fabricantes, 313 inversores, 418 módulos, 317 MPPTs, 465 sistemas, 1.205 comunicações e 3 modos globais.
- 369 perfis `AC_OUTPUT`: 257 casos unívocos e 112 perfis dos 56 pares.
- 257 perfis inicialmente ativos/padrão; 256 atendem também às regras de classificação e modo e são contabilizados como prontos. Os 112 multimodo ficam inativos/não padrão.
- 484 pendências: 369 classificações de tensão, 112 revisões multimodo e 3 inversores sem grupos MPPT (`PHB15K-MT`, `PHB20K-MT`, `PHB36K-MT`). Esses três são preservados como rascunhos, não descartados.

## Erros estruturais encontrados

A simulação recusou carga por dez ocorrências estruturais. Três grupos têm produto de primos referenciando posições além de `NUMBER_OF_TRACKERS`:

| Inversor | Modelo | MPPT | Índice | Total declarado | Posições codificadas |
| ---: | --- | ---: | ---: | ---: | --- |
| 227 | `SIW500H ST200 H3` | 229 | 15 | 1 | 2 e 3 |
| 203 | `SIW500G H250 W0` | 256 | 14 | 2 | 1 e 4 |
| 203 | `SIW500G H250 W0` | 257 | 2145 | 2 | 2, 3, 5 e 6 |

Além disso, `MID6KTL3-XL` (ID 267) e `MID8KTL3-XL` (ID 268) declaram 2 MPPTs, 2 entradas totais e um grupo homogêneo com 2 entradas por MPPT, o que pondera 4 entradas. O importador não escolhe qual campo está incorreto.

O preflight físico encontrou mais quatro incompatibilidades que impediriam a carga:

| Inversor | Modelo | MPPT | Campo | Valor / problema |
| ---: | --- | ---: | --- | --- |
| 280 | `INGECON SUN 100TL PRO` | 281 | `RATED_INPUT_VOLTAGE` | `-4` |
| 282 | `MAX50KTL3 LV` | 290 | `MAX_FULL_LOAD_VOLTAGE` | `-4` |
| 282 | `MAX50KTL3 LV` | 290 | `MIN_FULL_LOAD_VOLTAGE` | `-4` |
| 260 | `H3-PRO-15.0` | 261 | faixa Full Load | mínimo 850 V maior que máximo 170 V |

`-4` não é uma sentinela aprovada. Somente os `-1` conhecidos por campo são convertidos para `NULL`; portanto esses valores permanecem relatados, sem inferência silenciosa.

Há ainda uma décima ocorrência: o perfil `AC_OUTPUT` 275, pertencente ao inversor 235 (`SUN2000-3KTL-L1`), está ativo, mas o inversor não possui classificação em `inverter_system`. Ele não é contado entre os perfis prontos. O importador não inventa a classificação ausente.

Os primeiros valores sugerem revisar `NUMBER_OF_TRACKERS`, mas o importador não assume 3/6 nem altera a origem. As dez ocorrências precisam de uma correção de catálogo separadamente autorizada ou de uma futura extensão explícita do contrato. A reconciliação implementada nesta etapa trata somente perfis CA e não corrige MPPT nem classificação de sistema; por isso a carga permanece bloqueada.

## Testes realmente executados

- Testes de migração/configuração: 50 aprovados.
- Testes MySQL reais: 11 de 11 aprovados no schema isolado `optimus_sun_v3_test`. Eles cobriram inspeção física, reaplicação do DDL, constraints, destino não vazio, rollback e nova tentativa, concorrência, carga, verificação, adulteração e repetição idempotente.
- Regressão segura final com integração MySQL habilitada: 141 aprovados, 23 ignorados e 25 subtestes aprovados. Os 23 skips dependem de Tk/Tcl indisponível nesta instalação Python; nenhum teste MySQL ficou ignorado. `test_database_regression.py` foi excluído para não consultar o SQLite operacional.

## Ensaio MySQL real

- Conexão autenticada com MySQL 8.0.46 Community, `utf8mb4_0900_ai_ci`, modo estrito, `innodb_page_size=16384` e row format padrão `dynamic`.
- Schema isolado `optimus_sun_v3_test` criado e DDL `0001` aplicado.
- SHA-256 normalizado do DDL: `1afdfc9a2ac1aed3fbe9fe07ac99bbf443bcf2bf1dcef36f62eb47a2f60a3654`.
- SHA-256 da estrutura física: `91fd7725007ead0c410d3ec0cbfd4f770734954aa3922dacdf5fb987bd00e89e`.
- Uma segunda aplicação reconheceu o schema como já inicializado e devolveu as mesmas assinaturas, sem executar novamente o DDL.
- A tentativa controlada de carregar o plano com dez erros foi recusada pelo preflight antes de qualquer `INSERT`.
- Após a recusa e a regressão final, as nove tabelas de domínio e as três tabelas de metadados da migração permaneceram vazias; `schema_version` contém somente o registro `0001` do DDL aplicado.

Esse resultado valida conexão, configuração física, DDL e proteções de carga. Ele não representa uma migração de dados concluída: as dez ocorrências estruturais continuam bloqueando a importação do catálogo.

## O que ainda falta para concluir o ensaio

1. Resolver, em mudança separadamente autorizada, as dez ocorrências dos inversores 203, 227, 235, 260, 267, 268, 280 e 282 e gerar nova simulação sem erros.
2. Carregar esse novo plano no schema isolado e executar a verificação e a repetição idempotente com os dados reais transformados.
3. Preencher gradualmente a reconciliação dos 56 pares e das tensões; essas pendências não impediram criar e validar o schema, mas impedem homologar todos os perfis.

Não houve corte operacional, adaptação de GUI/motor/API, alteração do SQLite, commit ou publicação.
