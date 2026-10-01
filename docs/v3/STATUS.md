# Status — Optimus Sun v3

Última atualização: 01/10/2026. Branch de trabalho: `feature/v3.0.0`. Última versão publicada: **v2.6.0**. A v3 ainda não é uma release e nenhum banco foi migrado.

| Etapa | Estado | Evidência / próxima condição |
| --- | --- | --- |
| 00 — diagnóstico e base | Concluída | [Diagnóstico local](DIAGNOSTICO.md), snapshot SQLite íntegro, baseline de 100 testes seguros. |
| 01 — fluidez da matriz | Concluída e validada manualmente | [Medições antes/depois](ETAPA_01_MEDICOES.md), canvas virtual, barra por pares reais, cancelamento/fechamento testados e matriz 65×35 aprovada pelo usuário. |
| 02 — inventário e proposta de schema | Documentação concluída; revisão humana pendente | [Schema SQLite atual](ETAPA_02_SCHEMA_ATUAL.md) e [dicionário v3 proposto](ETAPA_02_DICIONARIO_DADOS.md). Nenhum DDL foi aplicado. |
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

As decisões estruturais de perfis, `NULL`/sentinelas, catálogo global de modos, corrente por MPPT/string e significado de `BATTERY_INDEX` foram incorporadas ao [dicionário da Etapa 02](ETAPA_02_DICIONARIO_DADOS.md). Permanecem sete decisões objetivas antes do DDL: canonicalização/unicidade textual, classificação dos campos CA legados, precisão final, distinção de configurações de bateria, regras de ativação de perfis, unicidade de grupos MPPT e escolha do perfil nominal para o motor. Não congelar nem aplicar o DDL enquanto elas estiverem abertas.

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
- O dicionário propõe 11 tabelas: fabricante, inversor, MPPT, módulo, três perfis CA/EPS, bateria, sistema, comunicação e catálogo global de modos de saída.
- A proposta separa perfis elétricos coerentes, mantém `MPPT_INDEX=0`, distingue correntes por MPPT/string e converte ausência técnica para `NULL`.
- Não houve acesso a MySQL, criação de DDL, migração, alteração do SQLite ou mudança funcional nesta etapa.

## Próximo marco

Revisar o dicionário e fechar suas sete decisões remanescentes. Somente com aprovação explícita iniciar a etapa seguinte para DDL/migração e validação em MySQL; não executá-la automaticamente.
