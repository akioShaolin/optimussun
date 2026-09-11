# CSV da matriz de compatibilidade

O intercâmbio CSV da matriz provisória registra a representação que o usuário
vê na tela. Ele não substitui o banco de equipamentos e não armazena os detalhes
técnicos completos de cada cálculo.

## Exportação

O arquivo é criado com:

- codificação UTF-8 com BOM, para facilitar a abertura no Excel;
- ponto e vírgula (`;`) como separador;
- vírgula como separador decimal;
- uma única linha de cabeçalho;
- três colunas por módulo: `Qtd. <MODELO>`, `Potência (kW) <MODELO>` e
  `Sobrecarga <MODELO>`.

Exemplo:

```text
Inversor;Qtd. WPV 550 HMM3;Potência (kW) WPV 550 HMM3;Sobrecarga WPV 550 HMM3
GW3300-XS-30;10;5,5;0,67
```

A potência nominal do módulo não possui linha própria. Quando o modelo é
associado durante a importação, essa potência é recuperada diretamente do banco.
Para módulo não associado, o nome e os valores das células são preservados sem
inventar uma potência nominal.

A primeira coluna contém o texto exibido de cada ocorrência de inversor. Por
isso, o mesmo equipamento pode aparecer várias vezes com rótulos diferentes. A
ordem manual dos módulos é mantida. Cada célula exporta o `display_result`: se o
modo que ignora corrente de operação tiver quantidade válida maior, seus três
valores coerentes são exportados; caso contrário, usa-se o modo normal. Resultado
sem dados suficientes é escrito como `N/D` nas três células.

Quando o cálculo foi realizado, mas nenhuma configuração válida foi encontrada,
o grupo é exportado como `Não suporta;0;-`. Isso é diferente de `N/D;N/D;N/D`,
que indica dados insuficientes para avaliar a combinação. A importação reconhece
as duas representações e as preserva sem recalcular.

## Importação

O leitor aceita UTF-8 com ou sem BOM e, para arquivos legados, Windows-1252. O
separador é detectado entre `;`, vírgula e tabulação. Números podem usar ponto ou
vírgula decimal. A exportação nova grava sobrecarga como razão com duas casas
(`0,50` corresponde a 50%); o símbolo `%` continua aceito na importação antiga.

A partir da segunda coluna, o cabeçalho é interpretado rigorosamente em grupos
de três. Os prefixos devem identificar quantidade, potência e sobrecarga, e o
modelo extraído dos três títulos precisa ser idêntico. Além do cabeçalho atual
`Sobrecarga <MODELO>`, o importador reconhece o legado com `%` e o intermediário
com `(razão)`. No cabeçalho comum sem discriminador, a escala deve ser escolhida
explicitamente; cancelar ou fechar preserva a matriz anterior. O formato anterior
com três linhas de cabeçalho não é aceito.

Importar não chama o motor de compatibilidade. Quantidades, potências,
sobrecargas, repetições, rótulos personalizados e ordem são exibidos como vieram
do arquivo. O painel de detalhes identifica esses dados como importados e não
apresenta fator limitante, strings ou MPPTs inexistentes no CSV.

O vínculo automático com o banco ocorre somente quando o texto coincide
exatamente com um único modelo ativo. Um rótulo personalizado de inversor, um
modelo ausente ou um nome ambíguo permanece não associado. Selecione a linha ou
coluna, escolha o equipamento ativo na caixa correspondente e pressione
**Associar**. O texto importado continua preservado e a associação mantém o ID
real do banco.

## Recalcular e exportar novamente

Depois de associar todos os equipamentos, pressione **Recalcular matriz** para
substituir explicitamente os valores importados pelos resultados atuais do
motor. Enquanto houver associação pendente, o recálculo é bloqueado e as
pendências são informadas. É possível exportar novamente uma matriz importada
sem recalculá-la.

## Validação e limitações

Arquivos com grupos incompletos de três colunas, cabeçalhos inconsistentes,
linhas com largura diferente, números inválidos ou `N/D` parcial são rejeitados
com mensagem de erro. CSV não preserva os dois modos técnicos, fatores
limitantes, distribuição por MPPT, configuração de strings nem a sobrecarga
personalizada original de uma linha. Esses dados são reconstruídos apenas pelo
recálculo com os equipamentos associados.
