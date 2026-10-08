# Status — Optimus Sun v3

Última atualização: 08/10/2026. Branch de trabalho: `feature/v3.0.0`. Última versão publicada: **v2.6.0**. A v3 ainda não é uma release e não houve corte operacional.

| Etapa | Estado | Evidência / próxima condição |
| --- | --- | --- |
| 00 — diagnóstico e base | Concluída | [Diagnóstico local](DIAGNOSTICO.md), snapshot SQLite íntegro, baseline de 100 testes seguros. |
| 01 — fluidez da matriz | Concluída e validada manualmente | [Medições antes/depois](ETAPA_01_MEDICOES.md), canvas virtual, barra por pares reais, cancelamento/fechamento testados e matriz 65×35 aprovada pelo usuário. |
| 02 — inventário e proposta de schema | Consolidada e revisada pelo 02B; duas decisões fechadas na Etapa 03 | [Dicionário consolidado](ETAPA_02_DICIONARIO_DADOS.md), [conferências](ETAPA_02_CONFERENCIAS.md), [handoff](ETAPA_02_CONSOLIDACAO_2026-10-02.md) e [complemento 02B](ETAPA_02B_PERFIS_TENSOES_ROTULOS_2026-10-02.md). Revisões de dados continuam rastreadas. |
| 03 — esquema e importador | Ensaio concluído no schema MySQL isolado | [Guia](ETAPA_03_GUIA.md) e [relatório](ETAPA_03_RELATORIO.md). Correções autorizadas aplicadas, simulação sem erros, carga verificada e repetição idempotente confirmada. |
| 04 — núcleo de cálculos | Concluída | [Baseline](ETAPA_04_BASELINE.md) e [relatório](ETAPA_04_RELATORIO.md). Principal e matriz consomem o núcleo puro por adaptadores compatíveis. |
| 05–09 | Não iniciadas | Aguardar revisão desta entrega e autorização explícita antes de iniciar a Etapa 05. |

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

As duas decisões restantes foram aprovadas na Etapa 03: `AC_INPUT` ativo exige híbrido e ao menos uma grandeza nominal positiva; fabricante tem nome normalizado globalmente único. O DDL materializa normalização e padrão condicional. A validação física no MySQL real foi concluída. As inconsistências MPPT e a classificação ausente que bloqueavam a carga foram corrigidas com confirmação do usuário. Permanecem como pendências permitidas as classificações de tensão, a revisão dos perfis multimodo, três inversores sem grupos MPPT e a conferência futura das tensões de plena carga do `H3-PRO-15.0` em datasheet.

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
- Corrigido o preflight para que `INVALID_TEMPERATURE_RANGE` registrado gere plano e relatório auditáveis; adulteração/ausência da ocorrência e toda carga com erros continuam recusadas.
- Em 08/10/2026, as dez correções cadastrais confirmadas pelo usuário foram aplicadas em transação sobre oito linhas do SQLite. O backup anterior está em `.test_tmp/migration_v3/backups/optimus_sun-before-catalog-corrections-20261008.db`, íntegro, com SHA-256 `2efb2112ccb6fc206fcea4508c0ad43ba3389aae728adc38244bdaade6dd75ac`. O hash operacional mudou, como esperado, de `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188` para `d12c15cb337bfeac7b5afe405656ae538ade62ed2a6e5871a804724d2d04fc1a`.
- Cobertura de MPPT e totais de entradas ficaram coerentes nos oito inversores; integridade e FKs permaneceram válidas. A repetição da correção alterou zero linhas. A diferença já existente de `MAX_SHORT_CIRCUIT_CURRENT` entre os grupos 228/229 foi preservada para conferência, sem inferência técnica.
- A nova simulação leu 28 fabricantes, 313 inversores, 418 módulos e 317 MPPTs, gerou 369 perfis e terminou com zero erros. Os 257 perfis ativos/padrão agora atendem às regras de prontidão. Permanecem 484 pendências permitidas: 369 referências de tensão, 112 revisões multimodo e 3 inversores sem grupos MPPT.
- Corrigida também a verificação de `migration_id_map`: o conteúdo agora é comparado independentemente da ordenação de collation do MySQL, sem deixar de detectar qualquer tupla alterada.
- A validação autenticada confirmou MySQL 8.0.46 Community, `utf8mb4_0900_ai_ci`, modo estrito, página InnoDB de 16.384 bytes e row format `dynamic`. O schema isolado `optimus_sun_v3_test` foi criado com DDL SHA-256 `1afdfc9a2ac1aed3fbe9fe07ac99bbf443bcf2bf1dcef36f62eb47a2f60a3654` e estrutura física SHA-256 `91fd7725007ead0c410d3ec0cbfd4f770734954aa3922dacdf5fb987bd00e89e`.
- O plano SHA-256 `1e2481aeb309b246dfd96236756711857accda2433b423ec23f31153aa9d28ad` foi carregado como execução 19. Verificação integral de contagens e conteúdo retornou correspondência; a repetição do mesmo plano retornou `ALREADY_COMPLETED` sem duplicação e uma segunda verificação também passou.
- Validação final: 55 testes de migração/configuração aprovados; 8 testes MySQL aprovados e 3 ignorados porque o catálogo de ensaio agora está legitimamente preenchido; regressão segura com 143 aprovados, 26 ignorados e 25 subtestes; mais 5 testes somente leitura sobre o SQLite operacional aprovados.
- Nenhuma interface, fórmula, motor, schema ou executável foi alterado. O SQLite foi modificado somente nas correções expressamente autorizadas.

## Etapa 04 — núcleo compartilhado de cálculos

- Criado `calculation_core`, independente de interface, banco e transporte, com contratos imutáveis para inversor, módulo, MPPT, perfil de saída, opções, resultados, limites e ocorrências estruturadas.
- A seleção de perfil aceita escolha explícita ou um único padrão válido; `AC_INPUT`, perfil inativo, perfil de outro inversor e ausência de modo/potência são recusados sem heurística. Potências nominal/máxima/pico e tensões fase–fase/fase–neutro permanecem separadas.
- A matriz passou a consumir o núcleo pela API pública v2 preservada. A aplicação principal usa um adaptador puro que conserva os campos, arredondamentos e limites exigidos por seus cartões e gráficos. `optimus_lib` mantém compatibilidade nominal sem duplicar fórmulas.
- A baseline anterior à extração registrou 163 aprovados, 11 ignorados e 25 subtestes. A regressão final registrou 186 aprovados, 12 ignorados e 28 subtestes, além de compilação e cinco testes somente leitura do catálogo. Dos ignorados, 11 exigem ativação explícita da integração MySQL e um depende do Tk/Tcl ausente neste interpretador.
- O modo que ignora corrente operacional não exige um limite operacional desconhecido; os demais limites continuam obrigatórios. Dados estruturais ausentes retornam `None` e ocorrências, sem aparentar compatibilidade zero.
- O SQLite permaneceu inalterado nesta etapa, SHA-256 `d12c15cb337bfeac7b5afe405656ae538ade62ed2a6e5871a804724d2d04fc1a`. MySQL e migração não foram executados.
- Permanecem documentadas as diferenças legadas entre o fechamento da matriz e a agregação do principal, inclusive a semântica antiga de ignorar plena carga. Nenhuma foi corrigida silenciosamente.

## Próximo marco

Revisar o encerramento da Etapa 04. A Etapa 05 poderá usar os contratos puros no servidor, mas API, filas, autenticação e acesso MySQL da aplicação não foram iniciados. Continuar acompanhando as 484 pendências permitidas e a conferência futura do `H3-PRO-15.0`. Não iniciar a Etapa 05 automaticamente; aguardar autorização explícita.
