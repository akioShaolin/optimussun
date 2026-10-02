# Status — Optimus Sun v3

Última atualização: 02/10/2026. Branch de trabalho: `feature/v3.0.0`. Última versão publicada: **v2.6.0**. A v3 ainda não é uma release e nenhum banco foi migrado.

| Etapa | Estado | Evidência / próxima condição |
| --- | --- | --- |
| 00 — diagnóstico e base | Concluída | [Diagnóstico local](DIAGNOSTICO.md), snapshot SQLite íntegro, baseline de 100 testes seguros. |
| 01 — fluidez da matriz | Concluída e validada manualmente | [Medições antes/depois](ETAPA_01_MEDICOES.md), canvas virtual, barra por pares reais, cancelamento/fechamento testados e matriz 65×35 aprovada pelo usuário. |
| 02 — inventário e proposta de schema | Consolidada e revisada pelo 02B; revisão de dados/duas decisões pendentes | [Dicionário consolidado](ETAPA_02_DICIONARIO_DADOS.md), [conferências](ETAPA_02_CONFERENCIAS.md), [handoff](ETAPA_02_CONSOLIDACAO_2026-10-02.md) e [complemento 02B](ETAPA_02B_PERFIS_TENSOES_ROTULOS_2026-10-02.md). Nenhum DDL foi aplicado. |
| 03–09 | Não iniciadas | Dependem da aprovação das decisões remanescentes da Etapa 02. |

## Escopo da etapa 00

- Confirmado `main` em `a9ef57a`/tag v2.6.0 como base e criada a branch `feature/v3.0.0` sem descartar a alteração pendente do banco.
- Lidos código, testes, specs e plano recebido; criado snapshot consistente por `sqlite3.backup` e inventariados schema, dados, sentinelas, flags, índices e FKs.
- Mapeados acoplamentos de SQLite/Tk/recursos e pontos de medição da matriz. Nenhuma causa de lentidão foi declarada sem benchmark.
- Criados [PLANO.md](PLANO.md), [DIAGNOSTICO.md](DIAGNOSTICO.md) e este registro. Não houve alteração de código do produto, fórmulas, schema, banco de origem, executáveis ou interfaces.

## Verificações

- Snapshot: `integrity_check=ok`; `foreign_key_check` vazio; SHA-256 `317889cd875a5d2e8754206d57250930a0c0e05f147f12989c9ca85f3116dee8`.
- Baseline segura, sem testes que consultam diretamente o banco real: 100 testes aprovados. Mensagens de callbacks Tk após destruição apareceram no terminal sem falha; investigar isoladamente quando relevante.
- MySQL/VM indisponível nesta máquina e **não necessário** para o inventário/proposta documental da etapa 02. Versão/configuração, DDL e testes reais de MySQL pertencem à etapa seguinte, depois da revisão humana.

## Pendências e decisões

As decisões estruturais de perfil CA unificado, padrão explícito, atividade, `NULL`/sentinelas, catálogo global de modos, corrente por MPPT/string, grupos de bateria e destino dos campos CA legados foram incorporadas ao [dicionário](ETAPA_02_DICIONARIO_DADOS.md). O 02B resolveu os modos: não há mais inversor sem modo, e os 56 multimodo gerarão 112 perfis `AC_OUTPUT`. Também separou tensões fase–fase/fase–neutro e fechou os rótulos. Restam duas decisões de negócio: mínimo de disponibilidade de `AC_INPUT` e política para fabricantes homônimos. Corrente total compartilhada de bateria continua hipótese sem caso concreto, não campo aprovado. A versão do MySQL e a unicidade condicional do padrão são validações técnicas posteriores.

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

## Próximo marco

Revisar os dados duplicados/tensões e decidir o mínimo de `AC_INPUT` e a política de fabricantes homônimos. Depois, confirmar a versão do MySQL e preparar/validar DDL e migração em ambiente de teste; não executar a etapa seguinte automaticamente.
