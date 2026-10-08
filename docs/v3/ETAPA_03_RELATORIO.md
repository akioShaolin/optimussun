# Etapa 03 — relatório de implementação e ensaio

Última atualização: 08/10/2026. Branch: `feature/v3.0.0`.

## Implementação concluída

- DDL versionado `0001` para nove tabelas de domínio e quatro tabelas técnicas: versão, execução, mapeamento de IDs e pendências.
- Importador separado em configuração, snapshot SQLite, normalização, reconciliação, transformação, domínio, persistência MySQL e CLI.
- Simulação é o padrão e não depende de MySQL.
- Carga exige ação explícita e schema cujo nome termine em `_ensaio` ou `_test`.
- Arquivo `.env` local é ignorado; variáveis de processo prevalecem; segredos não entram em argumentos/relatórios.
- Conexão remota exige CA explícita e validação de certificado/identidade; loopback não exige TLS.
- Plano JSON, relatório Markdown, resumo, snapshot e decisões usadas permitem reprodução e auditoria.
- O plano possui checksum canônico próprio; o preflight aceita inconsistências produzidas somente quando há ocorrência estruturada exata, preservando o relatório, enquanto a carga recusa qualquer plano com erros.
- Corrigido o preflight de faixa de temperatura: `INVALID_TEMPERATURE_RANGE` devidamente registrado permite gerar os artefatos de diagnóstico; a ausência ou remoção dessa ocorrência continua sendo rejeitada.

## Decisões físicas

- MySQL alvo informado: 8.0.46; engine InnoDB com `ROW_FORMAT=DYNAMIC`; charset/collation `utf8mb4`/`utf8mb4_0900_ai_ci`; página InnoDB mínima de 8 KiB.
- Normalização de fabricante/modelo/modo: trim e compactação por coluna gerada; índice único com comparação sem caixa/acento. A aplicação usa a mesma semântica para detectar colisões antes da carga.
- Perfil padrão: `DEFAULT_SLOT` gerado retorna `1` apenas para `IS_DEFAULT`, `NULL` nos demais; índice único composto permite vários não padrões e rejeita segundo padrão.
- `CHECK` impede padrão inativo/entrada, modo em `AC_INPUT`, saída ativa sem modo e `AC_INPUT` ativo sem grandeza nominal positiva.
- Elegibilidade híbrida de `AC_INPUT`, cobertura de grupos e exatamente um padrão para catálogo pronto são validações transacionais de domínio.
- DDL e carga são operações separadas. Nenhuma FK é desativada e não há `REPLACE`/`INSERT IGNORE`.
- A ferramenta exige MySQL 8.0.46 com modo estrito na mesma conexão usada pela operação, aceita apenas o DDL oficial e registra as assinaturas do DDL e da estrutura física; a carga usa lock por schema e verifica conteúdo na repetição idempotente.

## Correção cadastral autorizada em 05/10/2026

Antes da escrita, IDs, modelos, vínculos e valores foram conferidos. Foi criado por `sqlite3.backup` o arquivo `.test_tmp/migration_v3/backups/optimus_sun-before-catalog-corrections-20261008.db`, com `integrity_check=ok`, nenhuma violação de FK e SHA-256 físico `2efb2112ccb6fc206fcea4508c0ad43ba3389aae728adc38244bdaade6dd75ac`. A assinatura lógica canônica do backup e da origem era a mesma: `a28b857e16ec3d42ba08877da19240b0999518d82004e8563d61128a92f55d1a`.

A transação modificou oito linhas, somente nos campos autorizados:

| ID / grupo | Antes | Depois |
| --- | --- | --- |
| Inversor 203 — `SIW500G H250 W0` | 2 MPPTs, 28 entradas | 6 MPPTs, 28 entradas |
| Inversor 227 — `SIW500H ST200 H3` | 1 MPPT, 14 entradas | 3 MPPTs, 14 entradas |
| MPPT 261 — `H3-PRO-15.0` | plena carga mínima 850 V; máxima 170 V | mínima e máxima `-1` — não informado |
| MPPT 271 — `MID6KTL3-XL` | 2 entradas por MPPT homogêneo | 1 entrada por MPPT homogêneo |
| MPPT 272 — `MID8KTL3-XL` | 2 entradas por MPPT homogêneo | 1 entrada por MPPT homogêneo |
| MPPT 281 — `INGECON SUN 100TL PRO` | tensão nominal `-4 V` | `-1` — não informado |
| MPPT 290 — `MAX50KTL3 LV` | plena carga mínima/máxima `-4 V` | ambas `-1` — não informado |
| Inversor 235 — `SUN2000-3KTL-L1` | sem classificação | uma relação `ON-GRID` |

Os índices e quantidades já corretos dos grupos 228, 229, 256 e 257 foram verificados e preservados. Após a transação, as distribuições calculadas foram 4/5/5 para o inversor 227 e 4/5/5/4/5/5 para o 203; todos os oito inversores ficaram com cobertura completa e total ponderado igual ao total declarado. Integridade e FKs permaneceram válidas. O hash do SQLite mudou de `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188` para `d12c15cb337bfeac7b5afe405656ae538ade62ed2a6e5871a804724d2d04fc1a`. Uma segunda execução alterou zero linhas e preservou o hash final.

Nos grupos 256/257 do inversor 203, os demais campos elétricos coincidem. Nos grupos 228/229 do inversor 227, `MAX_SHORT_CIRCUIT_CURRENT` permanece respectivamente `130,0 A` e `162,5 A`; a divergência foi registrada, não corrigida nem atribuída a fonte técnica. As sentinelas `-1` foram tratadas apenas nos campos previstos pelo contrato. A decisão sobre o `H3-PRO-15.0` é confirmação do usuário; a conferência futura em datasheet permanece pendente.

## Simulação executada

Comando:

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py simulate `
  --source src\optimus_sun.db `
  --output .test_tmp\migration_v3\simulation-20261008-stage03-corrected
```

Evidência:

- SHA-256 do SQLite antes/depois da captura: `d12c15cb337bfeac7b5afe405656ae538ade62ed2a6e5871a804724d2d04fc1a` — idêntico.
- SHA-256 do snapshot: `c990777fb9d35dd62f5f7d013e54e976b6209f64c9a1235ad4f8dc10965b91f7`.
- SHA-256 canônico do plano: `1e2481aeb309b246dfd96236756711857accda2433b423ec23f31153aa9d28ad`.
- `integrity_check=ok`; nenhuma violação de FK.
- 28 fabricantes, 313 inversores, 418 módulos, 317 MPPTs, 466 sistemas, 1.205 comunicações e 3 modos globais.
- 369 perfis `AC_OUTPUT`: 257 casos unívocos e 112 perfis dos 56 pares.
- 257 perfis ativos/padrão; os 257 atendem também às regras de classificação e modo e são contabilizados como prontos. Os 112 multimodo ficam inativos/não padrão.
- 484 pendências: 369 classificações de tensão, 112 revisões multimodo e 3 inversores sem grupos MPPT (`PHB15K-MT`, `PHB20K-MT`, `PHB36K-MT`). Esses três são preservados como rascunhos, não descartados.
- Zero erros estruturais; a simulação terminou com código de saída 0.

## Resolução dos erros estruturais

As dez ocorrências registradas em 05/10/2026 foram resolvidas exclusivamente pelas confirmações do usuário. A simulação de 08/10 não encontrou erro estrutural:

| ID | Modelo | Ocorrência anterior | Resolução aplicada |
| ---: | --- | --- | --- |
| 227 | `SIW500H ST200 H3` | índice 15 excedia 1 MPPT declarado | total confirmado como 3 MPPTs; grupos 228/229 preservados |
| 203 | `SIW500G H250 W0` | índices 14/2145 excediam 2 MPPTs declarados | total confirmado como 6 MPPTs; grupos 256/257 preservados |
| 267 | `MID6KTL3-XL` | grupo homogêneo calculava 4 entradas | 1 entrada por cada um dos 2 MPPTs |
| 268 | `MID8KTL3-XL` | grupo homogêneo calculava 4 entradas | 1 entrada por cada um dos 2 MPPTs |
| 280 | `INGECON SUN 100TL PRO` | tensão nominal `-4 V` | sentinela autorizada `-1`, convertida para `NULL` no plano |
| 282 | `MAX50KTL3 LV` | plena carga máxima `-4 V` | sentinela autorizada `-1`, convertida para `NULL` no plano |
| 282 | `MAX50KTL3 LV` | plena carga mínima `-4 V` | sentinela autorizada `-1`, convertida para `NULL` no plano |
| 260 | `H3-PRO-15.0` | plena carga 850/170 V invertida | ambos os campos marcados `-1` e convertidos para `NULL`; datasheet ainda pendente |
| 235 | `SUN2000-3KTL-L1` | perfil ativo sem sistema | relação única `ON-GRID` cadastrada |

Não foi criada conversão genérica de números negativos: somente as sentinelas e os campos já previstos pelo contrato foram convertidos. As 484 pendências restantes não são erros bloqueadores e permanecem integralmente rastreadas.

## Testes realmente executados

- Testes de migração/configuração: 55 aprovados. Além das quatro regressões de temperatura, foi acrescentada regressão para a comparação de mapeamentos independente da ordenação do banco, ainda sensível a conteúdo alterado.
- Testes MySQL após a carga real: 8 aprovados e 3 ignorados. Os três cenários de carga sintética exigem schema vazio e foram ignorados deliberadamente porque o catálogo real já estava carregado; não houve limpeza para forçá-los.
- Regressão segura final com integração MySQL habilitada: 143 aprovados, 26 ignorados e 25 subtestes aprovados. Dos 26 skips, 23 dependem de Tk/Tcl e 3 exigem destino MySQL vazio.
- Regressão somente leitura do SQLite operacional: 5 aprovados, incluindo expansão dos seis MPPTs do inversor 203.
- A carga, verificação e repetição idempotente do plano real complementam os cenários sintéticos que ficaram indisponíveis após o preenchimento legítimo do schema.

## Ensaio MySQL real

- Conexão autenticada com MySQL 8.0.46 Community, `utf8mb4_0900_ai_ci`, modo estrito, `innodb_page_size=16384` e row format padrão `dynamic`.
- Schema isolado `optimus_sun_v3_test` compatível com DDL SHA-256 `1afdfc9a2ac1aed3fbe9fe07ac99bbf443bcf2bf1dcef36f62eb47a2f60a3654` e estrutura física SHA-256 `91fd7725007ead0c410d3ec0cbfd4f770734954aa3922dacdf5fb987bd00e89e`.
- O destino foi conferido vazio antes da carga, sem exclusão ou recriação de dados.
- O plano SHA-256 `1e2481aeb309b246dfd96236756711857accda2433b423ec23f31153aa9d28ad` foi carregado como `migration_run` 19, status `COMPLETED`.
- Contagens verificadas: 28 fabricantes, 313 inversores, 418 módulos, 317 MPPTs, 3 modos, 369 perfis CA, 0 baterias, 466 sistemas, 1.205 comunicações e 257 perfis prontos. Há 369 mapeamentos e 484 pendências técnicas.
- Os campos `-1` autorizados chegaram ao MySQL como `NULL` somente onde o contrato prevê: tensão nominal do MPPT 281 e faixas de plena carga dos MPPTs 261/290.
- A primeira verificação expôs uma falha no verificador, não nos dados: MySQL e Python ordenavam `SOURCE_KEY` de forma diferente. Os 369 mapeamentos eram conjuntos idênticos. A comparação foi corrigida para ordenar ambos em Python, preservando a validação integral das tuplas.
- Após a correção, a verificação integral retornou `matches=true`; a repetição exata retornou `ALREADY_COMPLETED` para a execução 19, sem duplicação; uma segunda verificação também retornou `matches=true`.

## Pendências permitidas após o ensaio

1. Classificar gradualmente as 369 referências de tensão ainda não resolvidas.
2. Revisar os 112 perfis dos 56 inversores multimodo e escolher padrões somente com evidência.
3. Revisar os três inversores sem grupos MPPT preservados como rascunhos.
4. Conferir futuramente em datasheet as tensões de plena carga do `H3-PRO-15.0`; até lá, permanecem como não informadas por confirmação do usuário.
5. Conferir a diferença de `MAX_SHORT_CIRCUIT_CURRENT` entre os grupos 228/229 do inversor 227.

Essas pendências não são erros estruturais e não bloquearam a carga. Não houve corte operacional, adaptação de GUI/motor/API, mudança de schema, commit ou publicação. A Etapa 04 não foi iniciada.
