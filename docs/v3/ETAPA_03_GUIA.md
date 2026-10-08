# Etapa 03 — guia do esquema e importador

Guia para Windows PowerShell. O SQLite operacional continua sendo a origem; todos os artefatos locais ficam em `.test_tmp/`, que é ignorado pelo Git, e o único destino permitido termina em `_ensaio` ou `_test`.

## 1. Ambiente Python

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-v3-dev.txt
```

Dependências adicionadas: PyMySQL 1.x para MySQL e pytest 9.x apenas para testes. A simulação não importa nem conecta o driver MySQL.

## 2. Configuração local e segura

O arquivo `.env.example` lista `OPTIMUS_MYSQL_HOST`, `OPTIMUS_MYSQL_PORT`, `OPTIMUS_MYSQL_DATABASE`, `OPTIMUS_MYSQL_USER` e `OPTIMUS_MYSQL_PASSWORD`. Ele também oferece `OPTIMUS_MYSQL_SSL_CA`: em loopback esse campo pode permanecer vazio; para qualquer host não local ele é obrigatório e ativa validação do certificado e da identidade do servidor. Copie o exemplo somente se `.env` ainda não existir e preencha o `.env` local:

```powershell
if (-not (Test-Path -LiteralPath .env)) {
  Copy-Item -LiteralPath .env.example -Destination .env
}
```

Esse comando nunca sobrescreve uma configuração local existente. O loader não altera o ambiente do processo. Variáveis já definidas no ambiente prevalecem sobre `.env`, inclusive quando vazias. Senha não é aceita em argumento de comando, URL ou relatório. O schema deve ser explicitamente nomeado e terminar em `_ensaio` ou `_test`; o exemplo é `optimus_sun_v3_test`. Não use host remoto sem CA confiável.

Teste de conexão, sem exibir credenciais:

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py mysql inspect
```

Se faltar configuração, o comando informa apenas os nomes das variáveis a preencher. Não tenta usuário/senha alternativos.

## 3. Simulação padrão, sem MySQL

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py simulate `
  --output .test_tmp\migration_v3\ensaio-01 `
  --write-reconciliation-template
```

O comando abre a origem em `mode=ro`, cria snapshot por `sqlite3.backup`, compara o hash da origem antes/depois, executa integridade/FKs, transforma dados e grava:

- `optimus_sun.snapshot.db`: snapshot consistente;
- `import-plan.json`: plano completo e estruturado;
- `report.md`: relatório humano com ocorrências;
- `summary.json`: hashes, integridade e contagens;
- `reconciliation-template.json`: documento vazio para decisões;
- `reconciliation-used.json`: decisões efetivamente usadas.

Sem subcomando `mysql`, nenhuma conexão ou transação MySQL é aberta.
O plano inclui seu próprio `plan_sha256`, calculado sobre origem, decisões, tabelas,
mapeamentos, contagens e ocorrências. A validação rejeita remoção ou alteração de
pendências, erros ou dados sem a correspondente mudança dessa assinatura. Um plano
com erros continua gravado para auditoria, mas o subcomando de carga sempre o recusa.
Isso inclui faixas invertidas de temperatura quando a ocorrência
`INVALID_TEMPERATURE_RANGE` correspondente está registrada. Se a ocorrência exata
for removida ou não existir, o preflight rejeita o plano em vez de produzir um
diagnóstico falsamente completo.

## 4. Reconciliação manual

Copie o template para outro arquivo ignorado em `.test_tmp`. Cada entrada de `profiles` identifica `inverter_id` e `output_mode`, sem depender de ordem. Campos disponíveis:

| Campo | Uso |
| --- | --- |
| `active` | Promove explicitamente o perfil revisado. |
| `is_default` | Escolhe exatamente um padrão do inversor. |
| `voltage_reference` | `LINE_TO_LINE`, `LINE_TO_NEUTRAL` ou `UNRESOLVED`. |
| `source` | Fonte humana obrigatória da decisão. |
| `corrections` | Grandezas confirmadas daquela configuração. |

O contrato formal está em `migrations/mysql/reconciliation.schema.json`. Não invente valores para completar a lista. Execute novamente em um diretório novo:

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py simulate `
  --output .test_tmp\migration_v3\ensaio-reconciliado `
  --reconciliation .test_tmp\migration_v3\reconciliation.json
```

Mudança nas decisões altera seu hash e é tratada como revisão, não ignorada.

## 5. Aplicação explícita no schema de ensaio

Primeiro inspecione o servidor e confirme que o destino é o schema isolado correto. Depois aplique somente o DDL:

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py mysql inspect
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py mysql schema
```

O inicializador recusa nomes fora do padrão de teste e schemas existentes não reconhecidos. Não apaga tabelas/bancos. O DDL é separado da carga porque MySQL pode efetuar commit implícito; um rollback da carga não promete desfazer DDL.

Antes de qualquer escrita, a ferramenta exige, na própria conexão que executará a operação, o produto MySQL, versão 8.0.46, `sql_mode` estrito e página InnoDB de ao menos 8 KiB. O DDL fixa `ROW_FORMAT=DYNAMIC` para as 13 tabelas. Somente o arquivo versionado `migrations/mysql/0001_initial.sql` pode ser aplicado. Ao concluir, a assinatura SHA-256 normalizada do DDL e a assinatura da estrutura física observada são registradas em `schema_version`; aplicação, carga, verificação e troca de padrão recusam desvio de colunas, índices, constraints, FKs, checks, triggers, partições, engine, collation ou row format.

Se uma instrução DDL falhar no meio, tabelas anteriores podem permanecer por causa dos commits implícitos. A ferramenta detecta o schema parcial e não tenta completar, apagar ou reaplicar automaticamente. Preserve-o para diagnóstico e use outro schema isolado; a remoção do schema de ensaio falho exige inspeção e autorização explícita.

Carregue somente um plano sem erros estruturais:

```powershell
.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py mysql load `
  --plan .test_tmp\migration_v3\ensaio-reconciliado\import-plan.json

.\.venv\Scripts\python.exe -X utf8 tools\migrate_v3.py mysql verify `
  --plan .test_tmp\migration_v3\ensaio-reconciliado\import-plan.json
```

A carga de domínio, mapeamentos e pendências usa uma transação e um lock por schema. Falha faz rollback e libera o lock. Repetir exatamente snapshot+decisões só retorna `ALREADY_COMPLETED` depois de conferir novamente contagens, campos, mapeamentos, pendências e hash do plano; edição manual, decisões diferentes ou snapshot diferente são recusados.
A comparação dos mapeamentos é independente da ordem devolvida pela collation do MySQL: as tuplas completas são normalizadas e ordenadas em Python antes da comparação, de modo que diferença de ordenação não seja confundida com diferença de conteúdo.

O FK de `inverter_ac_profile.OUTPUT_MODE_ID` usa a ação padrão do MySQL
(`NO ACTION`/`RESTRICT`). Ela não foi escrita explicitamente porque a mesma coluna
participa de `CHECK`, combinação para a qual o MySQL restringe ações referenciais
explícitas; a exclusão do modo continua protegida pelo FK.

## 6. Testes

Testes locais e baseline segura:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m pytest -q --basetemp .test_tmp\pytest-v3 `
  --ignore tests\test_database_regression.py
```

Integração real é opt-in e somente depois de aplicar o DDL no schema configurado:

```powershell
$env:PYTHONPATH = "src"
$env:OPTIMUS_RUN_MYSQL_TESTS = "1"
.\.venv\Scripts\python.exe -m pytest -q --basetemp .test_tmp\pytest-mysql `
  tests\test_migration_v3_mysql_integration.py
Remove-Item Env:OPTIMUS_RUN_MYSQL_TESTS
```

Os testes de integração usam rollback quando a própria transação está sob teste e limpeza explícita, por ID, nos cenários que precisam de commit ou concorrência. Os ensaios de carga exigem um schema recém-inicializado e vazio; caso contrário são ignorados, sem limpar dados alheios. Não apontar `.env` para schema operacional.

## 7. Códigos de saída

| Código | Significado |
| ---: | --- |
| 0 | Comando concluído; simulação sem erro estrutural ou verificação equivalente. |
| 1 | Configuração, arquivo, conexão ou operação inválida. |
| 2 | Simulação concluída, mas plano contém erros estruturais e não pode ser carregado. |
| 3 | Verificação pós-carga não corresponde ao plano. |

Pendências permitidas não descartam registros; permanecem no JSON, relatório e tabela técnica `migration_pending` quando a carga for possível.

## 8. Referências da decisão física

- [MySQL 8.0 — CHECK Constraints](https://dev.mysql.com/doc/refman/8.0/en/create-table-check-constraints.html)
- [MySQL 8.0 — Generated Columns](https://dev.mysql.com/doc/refman/8.0/en/create-table-generated-columns.html)
- [MySQL 8.0 — CREATE INDEX](https://dev.mysql.com/doc/refman/8.0/en/create-index.html)
- [MySQL 8.0 — Atomic DDL](https://dev.mysql.com/doc/refman/8.0/en/atomic-ddl.html)

O DDL usa checks apenas para colunas da própria linha. Elegibilidade híbrida, cobertura/sobreposição de grupos, exatamente um padrão para conjunto pronto e troca transacional permanecem no domínio.

