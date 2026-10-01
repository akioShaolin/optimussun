# Optimus Sun 3.0.0 — plano de trabalho

Este documento consolida o plano técnico recebido em 18/09/2026. É uma proposta de implementação, não um registro de código v3 pronto. Executar uma etapa por vez e manter [STATUS.md](STATUS.md) atualizado. A v2.6.0 continua sendo a última versão publicada até o lançamento da v3.

## Resultado pretendido

Quatro programas Windows: Optimus Sun (principal), OS-Cadastros, OS-Matriz de Compatibilidade e OS-Web-Server. O MySQL é infraestrutura da VM, não um executável do projeto. Preservar as interações aprovadas na v2.6.0, inclusive seleção explícita, filtros independentes, pesquisa recolhível, sobrecarga personalizada, gráficos, rascunhos, navegação por teclado e CSV.

Arquitetura proposta: os três clientes desktop e a interface web falam com uma API central na VM; **somente o servidor acessa o MySQL**. O núcleo de cálculos e as regras de cadastro são Python compartilhado, separado de Tkinter, HTTP e SQL. Os clientes v3 dependem do servidor ligado; não se presume modo offline. A paridade web obrigatória é com a aplicação principal, não com cadastros e matriz completos.

Stack proposta, sujeita à verificação de ambiente: Tkinter/ttk e Matplotlib no desktop; FastAPI/Uvicorn no servidor; SQLAlchemy 2, driver MySQL e migrações versionadas; web com recursos locais, sem dependência operacional de CDN. Não introduzir Node, Redis, Docker ou outros componentes sem necessidade demonstrada.

## Ordem e marcos

| Etapa | Entrega e condição para avançar |
| --- | --- |
| 00 | Diagnóstico local, snapshot SQLite, baseline e decisões pendentes. Sem refatoração ou DDL. |
| 01 | Medir e corrigir fluidez/progresso da matriz ainda no adaptador atual; preservar resultados e CSV. |
| 02 | Fechar decisões, dicionário e contratos; esquema/migrações MySQL validados em banco de teste. |
| 03 | Importador SQLite → MySQL, simulação padrão, ensaio e reconciliação sem corte operacional. |
| 04 | Núcleo único de cálculos, contexto de saída explícito e regressão de resultados. |
| 05 | API, filas limitadas, controle de acesso de escrita e OS-Web-Server. |
| 06 | OS-Cadastros com perfis, flags, rascunhos e concorrência. |
| 07 | Principal e matriz desktop adaptados à API e aos perfis. |
| 08 | Web com paridade funcional com o principal e isolamento por usuário. |
| 09 | Quatro executáveis, homologação separada e preparação da release; publicação não automática. |

As etapas 00–01 não requerem MySQL. A etapa 02 pode produzir contratos e DDL sem conexão, mas sua validação exige um MySQL descartável ou de homologação. A etapa 03 exige tal destino para o ensaio. Conferir versão real do MySQL; não presumir equivalência com MariaDB.

## Contratos e regras a decidir antes do esquema

- Saída elétrica é um perfil identificado por **tipo e ID**, não apenas por ID. O cálculo deve explicitar inversor, perfil, módulo, opções e revisão de dados. Perfis alternativos não são somados nem escolhidos pelo maior valor. Entrada CA e pico EPS não substituem potência nominal de saída.
- Inversores on-grid usam saída CA aplicável; exclusivamente off-grid usam EPS, sem saída de rede fictícia; híbridos podem ter CA, entrada CA, EPS e bateria conforme flags. Mudanças de flags inativam dependentes que perderam elegibilidade na mesma transação, preservando registros. Reativação de flag não reativa automaticamente filhos.
- Preservar inicialmente a semântica de `MPPT_INDEX`, inclusive `0` homogêneo; auditar limites do produto de primos. `MAX_OPERATING_CURRENT` legado passa a significar corrente por MPPT. Corrente por string nova permanece desconhecida sem fonte, nunca deduzida por divisão.
- Proposta para dados técnicos desconhecidos: `NULL` na v3, com exigências diferentes para rascunho e ativação/cálculo. Definir conversão por campo; não substituir genericamente `-1`, pois temperatura e coeficiente podem ser negativos válidos. Sobrecarga fica em percentual adicional (`50` = 50%); eficiências também em percentual, mas não são fator novo de cálculo FV.
- `BATTERY_INDEX` proposto como índice de porta física começando em `0`, sem produto de primos. Decidir alternativas por porta e unicidade antes do DDL. A tabela descreve especificações/portas aceitas, não estoque, autonomia ou comunicação BMS implementada.
- Perfil ativo e equipamento ativo são conceitos distintos. O principal pode consultar/simular equipamento de catálogo inativo com perfil habilitado e dados suficientes; a matriz oferece apenas equipamentos/perfis ativos.
- Definir versão/revisão otimista do agregado do inversor, transações para pais/filhos e autorização de escrita na API. Credenciais MySQL ficam somente no servidor, fora do código, clientes e logs. Estado de filtros, seleções e jobs deve ser isolado por requisição/usuário.

O dicionário final da etapa 02 deve cobrir `manufacturer`, `inverter`, `mppt`, `module`, `inverter_system`, `inverter_communication`, `inverter_output_mode`, `inverter_ac_output`, `inverter_ac_input`, `inverter_eps_output` e `battery`. Usar InnoDB, `utf8mb4`, tipos/precisão documentados, FKs/índices conferidos e migrações versionadas; apresentar alternativas de negócio antes de aplicar DDL real. Preservar IDs legados e mapear IDs novos das saídas.

## Migração e homologação

Importar de snapshot consistente, com inventário e simulação antes de escrita. Não inventar eficiência, bateria, EPS, entrada CA ou corrente por string. Transferir as cinco grandezas CA legadas para perfil de saída somente quando a classificação for inequívoca; máximo contínuo não vira pico EPS por renomeação. Relatar por registro lidos, importados, pendentes e motivos; reconhecer repetição do mesmo snapshot sem duplicar dados. Não usar `REPLACE`, `INSERT IGNORE`, FKs desligadas ou substituição textual de SQL para esconder conflitos. Separar DDL de importação; DDL MySQL pode causar commit implícito.

Homologar em ambiente separado com MySQL real, servidor e dois clientes simultâneos, navegador em outro computador, perfis de saída alternativos, falha/reconexão, conflitos de edição, cálculos equivalentes e matrizes grandes. A migração operacional final exige interrupção de escrita no legado, novo snapshot, backup do destino, reconciliação e decisão do usuário. O backup de ensaio não substitui o snapshot final. Não prometer rollback sem perdas após novas escritas na v3.

## Regras de execução

Preservar `src/optimus_sun.db` e trabalho pendente. Não alterar firewall, serviços da VM ou banco operacional por iniciativa própria. Não fazer commit, push, merge, tag ou release sem pedido explícito. Documentar evidência executada separadamente de implementação e de validação manual pendente. Atualizar `STATUS.md` a cada etapa e parar após a entrega solicitada.
