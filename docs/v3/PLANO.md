# Optimus Sun 3.0.0 — plano de trabalho

Este documento consolida o plano técnico recebido em 18/09/2026. É uma proposta de implementação, não um registro de código v3 pronto. Executar uma etapa por vez e manter [STATUS.md](STATUS.md) atualizado. A v2.6.0 continua sendo a última versão publicada até o lançamento da v3.

## Resultado pretendido

Quatro programas Windows: Optimus Sun (principal), OS-Cadastros, OS-Matriz de Compatibilidade e OS-Web-Server. O MySQL é infraestrutura da VM, não um executável do projeto. Preservar as interações aprovadas na v2.6.0, inclusive seleção explícita, filtros independentes, pesquisa recolhível, sobrecarga personalizada, gráficos, rascunhos, navegação por teclado e CSV.

Arquitetura proposta: os três clientes desktop e a interface web falam com uma API central na VM; **somente o servidor acessa o MySQL**. O núcleo de cálculos e as regras de cadastro são Python compartilhado, separado de Tkinter, HTTP e SQL. Os clientes v3 dependem do servidor ligado; não se presume modo offline. A paridade web obrigatória é com a aplicação principal, não com cadastros e matriz completos.

Stack proposta, sujeita à verificação de ambiente: Tkinter/ttk e Matplotlib no desktop; FastAPI/Uvicorn no servidor; SQLAlchemy 2 para a aplicação futura, driver MySQL e migrações versionadas; web com recursos locais, sem dependência operacional de CDN. O importador administrativo da Etapa 03 usa PyMySQL diretamente e concentra todo SQL em um DDL versionado e num único adaptador; isso não antecipa a camada ORM/API das etapas seguintes.

## Ordem e marcos

| Etapa | Entrega e condição para avançar |
| --- | --- |
| 00 | Diagnóstico local, snapshot SQLite, baseline e decisões pendentes. Sem refatoração ou DDL. |
| 01 | Medir e corrigir fluidez/progresso da matriz ainda no adaptador atual; preservar resultados e CSV. |
| 02 | Fechar decisões, dicionário, contratos e conferências somente leitura do legado. Sem DDL ou migração nesta consolidação. |
| 03 | Importador SQLite → MySQL, simulação padrão, ensaio e reconciliação sem corte operacional. |
| 04 | Núcleo único de cálculos, contexto de saída explícito e regressão de resultados. |
| 05 | API, filas limitadas, controle de acesso de escrita e OS-Web-Server. |
| 06 | OS-Cadastros com perfis, flags, rascunhos e concorrência. |
| 07 | Principal e matriz desktop adaptados à API e aos perfis. |
| 08 | Web com paridade funcional com o principal e isolamento por usuário. |
| 09 | Quatro executáveis, homologação separada e preparação da release; publicação não automática. |

As etapas 00–01 não requerem MySQL. A consolidação documental da etapa 02 também não acessa MySQL nem produz DDL. O próximo marco pode preparar o DDL, mas sua validação exige um MySQL descartável ou de homologação; a etapa 03 exige tal destino para o ensaio. Conferir a versão real do MySQL e não presumir equivalência com MariaDB.

## Contratos e regras a decidir antes do esquema

- Saída/entrada elétrica usa a tabela unificada `inverter_ac_profile`, identificada por **tipo e ID**. Os tipos controlados são `AC_OUTPUT`, `AC_INPUT` e `EPS_OUTPUT`. O cálculo explicita inversor, perfil, módulo, opções e revisão de dados. Perfis alternativos não são somados nem escolhidos pelo maior valor; `IS_DEFAULT` seleciona explicitamente o perfil inicial de saída.
- Cada perfil distingue tensão nominal fase–fase e fase–neutro. Filtros, detalhes e resultados identificam a referência usada; não se deriva uma da outra nem se mistura potência/tensão de perfis diferentes.
- Inversores on-grid usam saída CA aplicável; exclusivamente off-grid usam EPS, sem saída de rede fictícia; híbridos podem ter CA, entrada CA, EPS e bateria conforme flags. Mudanças de flags inativam dependentes que perderam elegibilidade na mesma transação, preservando registros. Reativação de flag não reativa automaticamente filhos.
- Preservar inicialmente a semântica de `MPPT_INDEX`, inclusive `0` homogêneo; auditar limites do produto de primos. `MAX_OPERATING_CURRENT` legado passa a significar corrente por MPPT. Corrente por string nova permanece desconhecida sem fonte, nunca deduzida por divisão.
- Proposta para dados técnicos desconhecidos: `NULL` na v3, com exigências diferentes para rascunho e ativação/cálculo. Definir conversão por campo; não substituir genericamente `-1`, pois temperatura e coeficiente podem ser negativos válidos. Sobrecarga fica em percentual adicional (`50` = 50%); eficiências também em percentual, mas não são fator novo de cálculo FV.
- `BATTERY_INDEX` usa produto dos primos das posições físicas, como `MPPT_INDEX`; `0` representa grupo homogêneo e `1` é inválido. `inverter.NUMBER_OF_BATTERY_INPUTS` registra o total físico. A tabela descreve grupos de entradas e especificações compartilhadas, não estoque, autonomia ou quantidade gerenciada externamente pelo BMS.
- Perfil ativo e equipamento ativo são conceitos distintos. O principal pode consultar/simular equipamento de catálogo inativo com perfil habilitado e dados suficientes; a matriz oferece apenas equipamentos/perfis ativos.
- Definir versão/revisão otimista do agregado do inversor, transações para pais/filhos e autorização de escrita na API. Credenciais MySQL ficam somente no servidor, fora do código, clientes e logs. Estado de filtros, seleções e jobs deve ser isolado por requisição/usuário.

O dicionário consolidado cobre nove tabelas de domínio: `manufacturer`, `inverter`, `mppt`, `module`, `inverter_ac_profile`, `inverter_battery`, `inverter_system`, `inverter_communication` e `inverter_output_mode`. O DDL 0001 usa InnoDB, `utf8mb4`, tipos/precisão documentados, FKs/índices, unicidade textual normalizada e padrão condicional. Preservar IDs legados e mapear IDs novos dos perfis.

## Migração e homologação

Importar de snapshot consistente, com inventário e simulação antes de escrita. Não inventar eficiência, bateria, EPS, entrada CA, corrente por string ou opções de tensão. As cinco grandezas CA legadas representam saída CA principal. Os 257 inversores com um modo geram um perfil `AC_OUTPUT`; os 56 com dois modos confirmados geram dois perfis cada, copiando inicialmente potência/correntes e registrando proveniência para revisão. Somente um perfil poderá ser padrão, escolhido explicitamente. `RATED_OUTPUT_VOLTAGE` só entra em fase–fase ou fase–neutro com evidência; se ambíguo, permanece pendente no relatório. Registrar `(ID legado, modo) → perfil` para reexecução idempotente. Relatar registros lidos, importados, pendentes e motivos; não usar `REPLACE`, `INSERT IGNORE`, FKs desligadas ou substituição textual para esconder conflitos. Separar DDL de importação; DDL MySQL pode causar commit implícito.

Homologar em ambiente separado com MySQL real, servidor e dois clientes simultâneos, navegador em outro computador, perfis de saída alternativos, falha/reconexão, conflitos de edição, cálculos equivalentes e matrizes grandes. A migração operacional final exige interrupção de escrita no legado, novo snapshot, backup do destino, reconciliação e decisão do usuário. O backup de ensaio não substitui o snapshot final. Não prometer rollback sem perdas após novas escritas na v3.

## Regras de execução

Preservar `src/optimus_sun.db` e trabalho pendente. Não alterar firewall, serviços da VM ou banco operacional por iniciativa própria. Não fazer commit, push, merge, tag ou release sem pedido explícito. Documentar evidência executada separadamente de implementação e de validação manual pendente. Atualizar `STATUS.md` a cada etapa e parar após a entrega solicitada.

## Estado da Etapa 03

DDL, importador, simulação, reconciliação e configuração segura foram implementados. O schema isolado foi criado e validado no MySQL 8.0.46; os 11 testes reais de integração e a reaplicação idempotente do DDL passaram. A simulação encontrou dez ocorrências: três índices MPPT fora do total declarado, dois totais de entradas divergentes, três valores `-4` não reconhecidos como sentinela, uma faixa Full Load invertida e um perfil de saída ativo sem classificação de sistema. O preflight recusou a carga antes de qualquer inserção e a migração dos dados permanece bloqueada até correção explícita. Ver [guia](ETAPA_03_GUIA.md) e [relatório](ETAPA_03_RELATORIO.md).
