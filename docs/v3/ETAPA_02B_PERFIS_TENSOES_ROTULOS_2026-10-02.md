# Complemento 02B — perfis, tensões e rótulos

Registro das decisões de 02/10/2026 que complementam e, onde indicado, substituem a [consolidação anterior](ETAPA_02_CONSOLIDACAO_2026-10-02.md). Não houve alteração de código, interface, SQLite ou MySQL.

## Decisões resolvidas

- Os 56 inversores com dois modos confirmados geram dois perfis `AC_OUTPUT` cada: 112 perfis, um para `THREE_PHASE_THREE_WIRE` e outro para `THREE_PHASE_FOUR_WIRE`.
- Potências e correntes legadas são copiadas inicialmente para ambos com origem rastreável. Isso não confirma que os dois datasheets tenham valores iguais.
- A migração registra `(inverter_id legado, output_mode) → ac_profile_id`; reexecução reconhece a correspondência e não duplica novamente.
- Somente o perfil é duplicado. Inversor, MPPTs, sistemas e comunicações preservam identidade.
- Cada perfil mantém um único `OUTPUT_MODE_ID`; não há tabela associativa nova e o modelo continua com nove tabelas de domínio.
- Um único perfil de saída poderá ser padrão. Nos 56 casos, os dois começam em reconciliação e o usuário escolhe explicitamente o padrão.
- `RATED_VOLTAGE` foi substituído por `RATED_LINE_TO_LINE_VOLTAGE` e `RATED_LINE_TO_NEUTRAL_VOLTAGE`.
- Não se deriva uma tensão da outra e não se gera automaticamente 480 V, tensão fase–neutro ou combinações por fabricante/modelo.
- Os rótulos aprovados foram consolidados sem alterar identidades persistidas.

## Conferência dos três cadastros

Leitura SQLite `mode=ro`, hash inicial `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188`:

- GROWATT `MID22KTL3-X` (ID 277): `THREE_PHASE_FOUR_WIRE`.
- GROWATT `MID25KTL3-X` (ID 278): `THREE_PHASE_FOUR_WIRE`.
- HUAWEI `SUN2000-4KTL-L1` (ID 236): `SINGLE_PHASE`.

Distribuição atual: 257 inversores com um modo, 56 com dois e nenhum sem modo.

Hash final após a revisão documental: `f467e8a234bca437ef7de807a4ca64d487ef842cfdcb9cac9185804df3b29188`, idêntico ao inicial.

## Reconciliação das tensões

O valor físico legado `inverter.RATED_OUTPUT_VOLTAGE` permanece intacto. Na migração, uma evidência de datasheet/cadastro define se ele é fase–fase ou fase–neutro. Se ambíguo, o relatório preserva valor, coluna e ID de origem e deixa a classificação pendente; não descarta o número e não preenche silenciosamente ambos os campos.

Filtros, seleção, detalhes e resultados distinguem as duas referências. Um intervalo consulta somente o campo escolhido, com limites inclusivos. Potência e tensão combinadas precisam pertencer ao mesmo perfil.

## Contrato de rótulos

| Identidade | Exibição |
| --- | --- |
| `ON-GRID` | On grid |
| `OFF-GRID` | Off grid |
| `GRIDZERO` | Grid zero |
| `HYBRID` | Híbrido |
| `SPLIT PHASE` | Splitphase |
| `THREE_PHASE_FOUR_WIRE` | Trifásico a quatro fios |
| `THREE_PHASE_THREE_WIRE` | Trifásico a três fios |
| `SINGLE_PHASE` | Monofásico |

`SPLIT PHASE` é a identidade já prevista no código atual. A implementação futura centraliza esse mapa para cadastros, filtros, detalhes e desktop/web, sem renomear códigos e sem habilitar capacidades apenas por mudar o texto.

## Revisão de dados pendente

- Escolher exatamente um padrão entre cada par dos 56 inversores.
- Conferir potência/correntes das cópias contra fonte por configuração.
- Classificar cada tensão legada como fase–fase ou fase–neutro; cadastrar opções adicionais somente com fonte confirmada.

## Decisões de negócio abertas e recomendações

1. **Mínimo para disponibilizar `AC_INPUT`.** Proposta: exigir inversor, tipo, atividade, `IS_DEFAULT=FALSE` e pelo menos uma grandeza nominal significativa — potência, corrente ou uma das tensões —, deixando o perfil disponível somente para os filtros suportados pelos campos presentes. A decisão precisa ser aprovada antes do DDL.
2. **Fabricantes homônimos após normalização.** Proposta: nome normalizado globalmente único, preservando grafia de exibição, com mesclagem/renomeação explícita para exceções. Evita fabricantes visualmente duplicados e FKs ambíguas.

## Questão de bateria e validações técnicas

Corrente total compartilhada de bateria continua hipotética: nenhum caso concreto foi demonstrado nesta etapa. Não se cria campo e não se divide nem copia limite total para entradas sem fonte.

A próxima etapa deve confirmar a versão real do MySQL e validar a implementação física da unicidade condicional de um perfil padrão por inversor. Essas são validações técnicas; não reabrem a decisão de padrão único.

## Fora do escopo preservado

Continuam pendentes da Etapa 01 a diferença percebida entre Calcular/Recalcular e a direção da rolagem conforme a posição do ponteiro. Não foram alteradas nesta revisão.
