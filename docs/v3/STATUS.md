# Status — Optimus Sun v3

Última atualização: 03/10/2026. Branch de trabalho: `feature/v3.0.0`. Última versão publicada: **v2.6.0**. A v3 ainda não é uma release e não houve corte operacional.

| Etapa | Estado | Evidência / próxima condição |
| --- | --- | --- |
| 00 — diagnóstico e base | Concluída | [Diagnóstico local](DIAGNOSTICO.md), snapshot SQLite íntegro, baseline de 100 testes seguros. |
| 01 — fluidez da matriz | Concluída e validada manualmente | [Medições antes/depois](ETAPA_01_MEDICOES.md), canvas virtual, barra por pares reais, cancelamento/fechamento testados e matriz 65×35 aprovada pelo usuário. |
| 02 — inventário e proposta de schema | Consolidada e revisada pelo 02B; duas decisões fechadas na Etapa 03 | [Dicionário consolidado](ETAPA_02_DICIONARIO_DADOS.md), [conferências](ETAPA_02_CONFERENCIAS.md), [handoff](ETAPA_02_CONSOLIDACAO_2026-10-02.md) e [complemento 02B](ETAPA_02B_PERFIS_TENSOES_ROTULOS_2026-10-02.md). Revisões de dados continuam rastreadas. |
| 03 — esquema e importador | DDL e integração MySQL validados; migração de dados bloqueada | [Guia](ETAPA_03_GUIA.md) e [relatório](ETAPA_03_RELATORIO.md). O schema isolado foi validado; faltam correção/decisão sobre dez ocorrências estruturais antes da carga. |
| 04–09 | Não iniciadas | Não avançar antes de concluir e revisar o ensaio da Etapa 03. |

## Escopo da etapa 00

- Confirmado `main` em `a9ef57a`/tag v2.6.0 como base e criada a branch `feature/v3.0.0` sem descartar a alteração pendente do banco.
- Lidos código, testes, specs e plano recebido; criado snapshot consistente por `sqlite3.backup` e inventariados schema, dados, sentinelas, flags, índices e FKs.
- Mapeados acoplamentos de SQLite/Tk/recursos e pontos de medição da matriz. Nenhuma causa de lentidão foi declarada sem benchmark.
- Criados [PLANO.md](PLANO.md), [DIAGNOSTICO.md](DIAGNOSTICO.md) e este registro. Não houve alteração de código do produto, fórmulas, schema, banco de origem, executáveis ou interfaces.

## Verificações

- Snapshot: `integrity_check=ok`; `foreign_key_check` vazio; SHA-256 `317889cd875a5d2e8754206d57250930a0c0e05f147f12989c9ca85f3116dee8`.
- Baseline segura, sem testes que consultam diretamente o banco real: 100 testes aprovados. Mensagens de callbacks Tk após destruição apareceram no terminal sem falha; investigar isoladamente quando relevante.
- Durante a Etapa 02, o MySQL não foi acessado e não era necessário para o inventário/proposta documental. Versão/configuração, DDL e testes reais ficaram para a etapa seguinte, depois da revisão humana.

## Pendências e decisões

As duas decisões restantes foram aprovadas na Etapa 03: `AC_INPUT` ativo exige híbrido e ao menos uma grandeza nominal positiva; fabricante tem nome normalizado globalmente único. O DDL materializa normalização e padrão condicional. A validação física no MySQL real foi concluída. Permanecem as revisões de dados — padrão/tensões dos pares, inconsistências MPPT e classificação de sistema ausente.

Continuam acompanhadas, sem alteração nesta etapa, duas pendências da Etapa 01: a diferença percebida entre **Calcular** e **Recalcular** e o comportamento da rolagem vertical sobre tabela/barra vertical e horizontal sobre barra horizontal.

## Etapa 01 — fluidez e progresso

- A comparação local 100×100 separou cálculo (~48 s nos dois estados) de preparação visual (**56,000 s → 0,025 s**). A memória do processo ao fim caiu de **200,9 MB para 49,1 MB**. Formatos 5×400 e 400×5 também foram medidos.
- Células calculadas/importadas permanecem completas; o canvas desenha só o viewport. Progresso de cálculo reflete pares concluídos e a fase visual só é concluída depois do primeiro desenho. Cancelamento preserva a matriz anterior e fechamento cancela timers/worker sem callbacks pendentes nos testes.
- Baseline de 100 testes preservada; 103 testes seguros passaram após três verificações novas. Mensagens Tk de callbacks órfãos da baseline não reapareceram.
- Limitação medida: atraso p95 no **cálculo** 100×100 foi 110 ms, ligeiramente acima da meta inicial de 100 ms; atraso máximo observado 225 ms. A visualização deixou de bloquear por mais de 15 s. Ver [metodologia, tabela e roteiro manual](ETAPA_01_MEDICOES.md).
- Nenhuma fórmula, schema, banco operacional ou regra de CSV foi alterada.

> **Validação manual aprovada.**  
> Teste realizado com matriz de 65 inversores × 35 módulos, totalizando 2.275 combinações. O comando **Recalcular matriz** apresenta pequena espera perceptível, porém permanece aceitável em uso real. O comando **Calcular matriz** responde rapidamente. A responsividade geral foi considerada adequada para encerramento da Etapa 01.

## Etapa 02 — inventário e dicionário proposto

- O banco `src/optimus_sun.db` foi lido em modo somente leitura: 7 tabelas, 7 índices explícitos, nenhuma view/trigger, integridade `ok` e nenhuma violação de FK.
- O inventário registra DDL, tipos, defaults, checks, FKs, índices, contagens, sentinelas e uso real no código, sem misturar estado atual com proposta futura.
- O dicionário consolidado propõe nove tabelas e unifica saída CA, entrada CA e EPS em `inverter_ac_profile`, com tipo controlado e perfil padrão explícito.
- A proposta preserva perfis elétricos coerentes, mantém `MPPT_INDEX=0`, adota agrupamento equivalente para bateria, distingue correntes por MPPT/string e converte ausência técnica para `NULL`.
- A primeira releitura de 02/10 encontrou 3 inversores sem modo e 56 com dois; após ajustes do usuário, nova leitura confirmou 257 com um modo, 56 com dois e nenhum sem modo.
- Os 56 multimodo terão dois perfis `AC_OUTPUT` cada, com revisão manual e escolha de um único padrão. A tensão legada será classificada como fase–fase ou fase–neutro somente com evidência.
- Somente coeficientes térmicos exigem mais de duas casas entre os campos inspecionados; foram propostos cinco decimais para preservá-los.
- Não houve acesso a MySQL, criação de DDL, migração, alteração do SQLite ou mudança funcional nesta etapa.

## Etapa 03 — esquema, importador e ensaio

- Criados DDL 0001, importador por snapshot, simulação padrão, reconciliação estruturada, carga transacional, verificação e configuração `.env` segura.
- Simulação leu 28 fabricantes, 313 inversores, 418 módulos, 317 MPPTs e produziu 369 perfis; hash operacional permaneceu `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188`.
- Três grupos dos inversores 203/227 codificam posições além do total de MPPTs; 267/268 têm total ponderado divergente; 280/282 contêm três valores `-4` não reconhecidos como sentinela; 260 possui faixa Full Load invertida; e o perfil 275 do inversor 235 está ativo sem classificação de sistema. As dez ocorrências bloqueiam a carga. Pendências de tensão/multimodo continuam rastreadas sem descarte.
- Dos 257 perfis inicialmente ativos/padrão, 256 atendem às regras completas de prontidão. Foram aprovados 50 testes de migração/configuração e 11 de 11 testes de integração MySQL. A regressão segura final com integração habilitada resultou em 141 aprovados, 23 ignorados por indisponibilidade de Tk/Tcl e 25 subtestes; nenhum teste MySQL ficou ignorado.
- A validação autenticada confirmou MySQL 8.0.46 Community, `utf8mb4_0900_ai_ci`, modo estrito, página InnoDB de 16.384 bytes e row format `dynamic`. O schema isolado `optimus_sun_v3_test` foi criado com DDL SHA-256 `1afdfc9a2ac1aed3fbe9fe07ac99bbf443bcf2bf1dcef36f62eb47a2f60a3654` e estrutura física SHA-256 `91fd7725007ead0c410d3ec0cbfd4f770734954aa3922dacdf5fb987bd00e89e`.
- A reaplicação do DDL foi reconhecida de forma idempotente, com as mesmas assinaturas. A tentativa de carregar o plano com dez erros foi recusada antes de qualquer `INSERT`. As nove tabelas de domínio e as três tabelas de metadados da migração permaneceram vazias; `schema_version` registra somente `0001`. Portanto, o DDL e as proteções foram validados, mas a migração de dados continua bloqueada pelas dez ocorrências.
- SQLite operacional preservado; nenhuma interface, fórmula, motor, API ou executável foi adaptado.

## Próximo marco

Resolver as dez ocorrências informadas no relatório, repetir a simulação sem erros e então carregar/verificar o novo plano no schema MySQL isolado já validado. Não iniciar a Etapa 04 automaticamente.
