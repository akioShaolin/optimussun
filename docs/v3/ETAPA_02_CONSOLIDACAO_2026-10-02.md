# Handoff — consolidação da Etapa 02 em 02/10/2026

> Complementado por [ETAPA_02B_PERFIS_TENSOES_ROTULOS_2026-10-02.md](ETAPA_02B_PERFIS_TENSOES_ROTULOS_2026-10-02.md). O complemento substitui a proibição anterior de duplicar perfis multimodo, resolve os três cadastros sem modo e separa tensão fase–fase de fase–neutro. Este documento permanece como registro histórico da primeira consolidação.

## Resultado

A proposta foi reduzida de onze para **nove tabelas de domínio** pela unificação de saída CA, entrada CA e EPS em `inverter_ac_profile`. O modelo, os contratos de seleção, a atividade, os mínimos de cálculo, os grupos de bateria e o mapeamento do legado estão consolidados em [ETAPA_02_DICIONARIO_DADOS.md](ETAPA_02_DICIONARIO_DADOS.md).

Nenhum código funcional, tela, fórmula, schema SQLite ou dado foi alterado. Não houve acesso a MySQL, DDL ou migration.

## Decisões incorporadas

1. `PROFILE_TYPE` usa `AC_OUTPUT`, `AC_INPUT` e `EPS_OUTPUT`; não é cadastro livre.
2. Há no máximo um perfil padrão de saída por inversor; seleção alternativa de sessão não altera o padrão.
3. On-grid/híbrido usam inicialmente `AC_OUTPUT`; exclusivamente off-grid usa `EPS_OUTPUT`; `AC_INPUT` nunca alimenta potência de saída.
4. Sobrecarga usa a potência nominal do perfil selecionado; potência máxima e pico permanecem separadas.
5. `ACTIVE` significa disponibilidade. Equipamento inativo ainda pode ser usado no principal, mas não na matriz; perfil inativo nunca é opção de cálculo.
6. Baterias usam grupos codificados por produtos de primos; `BATTERY_INDEX=0` é homogêneo e `NUMBER_OF_BATTERY_INPUTS` registra o total físico.
7. As cinco grandezas CA legadas migram para `AC_OUTPUT` padrão, inclusive nos híbridos; não geram EPS, entrada ou bateria.
8. Duas casas são padrão; coeficientes térmicos preservam cinco. Ausência técnica é `NULL`.
9. Fabricante+modelo e inversor+índice MPPT podem receber unicidade após as conferências sem conflitos.

## Evidências de leitura

- Banco íntegro e sem violações de FK.
- 313 inversores; duplicado histórico removido.
- Nenhuma duplicidade normalizada de inversor/módulo.
- Nenhuma duplicidade ou sobreposição MPPT detectada.
- Modos: 254 inversores unívocos, 3 sem modo e 56 com dois modos.
- 21 relações `OFF-GRID`, todas também híbridas/on-grid; nenhum equipamento exclusivamente off-grid.
- Precisão acima de duas casas somente nos coeficientes térmicos inspecionados.

Detalhes e IDs: [ETAPA_02_CONFERENCIAS.md](ETAPA_02_CONFERENCIAS.md).

## Fronteira transacional

- Atualizações do agregado verificam `ROW_VERSION`.
- Troca do perfil padrão e inativação/exclusão do antigo formam uma transação única.
- Mudança de capacidade inativa dependentes elegíveis, mas preserva dados; reativação não reativa filhos automaticamente.
- Validação de grupos MPPT/bateria e persistência ocorrem na mesma transação, com proteção contra conflito concorrente.
- Exclusão integral do inversor pode remover filhos em cascata; isso não se confunde com inativação do catálogo.

## Pendências registradas nesta consolidação histórica

- Resolver os 59 inversores sem associação unívoca de modo de saída. **Resolvido no 02B:** os três sem modo foram corrigidos e os 56 multimodo gerarão dois perfis cada.
- Definir o mínimo de disponibilidade de `AC_INPUT`.
- Decidir representação de eventual corrente total compartilhada de bateria.
- Fechar a política de homônimos de fabricante após normalização.
- Escolher a implementação MySQL para unicidade condicional de um padrão de saída por inversor e validá-la no servidor real.

## Pendências preservadas da Etapa 01

- Diferença perceptível entre **Calcular** e **Recalcular**.
- Rolagem vertical sobre tabela/barra vertical e horizontal sobre barra horizontal.

Esses itens permanecem fora desta execução.

## Próximo marco

Revisar as ambiguidades acima e, somente após aprovação, preparar DDL e plano de migração em banco MySQL de teste. Não iniciar automaticamente.
