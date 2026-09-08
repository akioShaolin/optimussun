# CSV da matriz de compatibilidade

O intercâmbio CSV da matriz provisória registra a representação que o usuário
vê na tela. Ele não substitui o banco de equipamentos e não armazena os detalhes
técnicos completos de cada cálculo.

## Exportação

O arquivo é criado com:

- codificação UTF-8 com BOM, para facilitar a abertura no Excel;
- ponto e vírgula (`;`) como separador;
- vírgula como separador decimal;
- três linhas de cabeçalho;
- três colunas por módulo: `Quantidade de módulos`, `Potência (kW)` e
  `Sobrecarga (%)`.

A primeira coluna contém o texto exibido de cada ocorrência de inversor. Por
isso, o mesmo equipamento pode aparecer várias vezes com rótulos diferentes. A
ordem manual dos módulos é mantida. Cada célula exporta o `display_result`: se o
modo que ignora corrente de operação tiver quantidade válida maior, seus três
valores coerentes são exportados; caso contrário, usa-se o modo normal. Resultado
sem dados suficientes é escrito como `N/D` nas três células.

## Importação

O leitor aceita UTF-8 com ou sem BOM e, para arquivos legados, Windows-1252. O
separador é detectado entre `;`, vírgula e tabulação. Números podem usar ponto ou
vírgula decimal e o símbolo `%` é aceito na sobrecarga.

Importar não chama o motor de compatibilidade. Quantidades, potências,
sobrecargas, repetições, rótulos personalizados e ordem são exibidos como vieram
do arquivo. O painel de detalhes identifica esses dados como importados e não
apresenta fator limitante, strings ou MPPTs inexistentes no CSV.

O vínculo automático com o banco ocorre somente quando o texto coincide
exatamente com um único modelo ativo. Um rótulo personalizado de inversor, um
modelo ausente ou um nome ambíguo permanece não associado. Selecione a linha ou
coluna, escolha o equipamento ativo na caixa correspondente e pressione
**Associar**. O texto importado continua preservado.

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
