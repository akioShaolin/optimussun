# Guia de operação do Optimus Sun

Este guia apresenta o fluxo básico de dimensionamento e explica as informações exibidas pelo Optimus Sun. Os valores mostrados nas imagens são apenas um exemplo; o resultado depende dos equipamentos selecionados e dos dados armazenados no banco `optimus_sun.db`.

## 1. Selecionar os equipamentos

Na parte superior da tela principal:

1. Selecione o **fabricante do inversor**.
2. Selecione o modelo em **Selecione o inversor**.
3. Selecione o **fabricante do módulo**.
4. Selecione o modelo em **Selecione o módulo**.

Ao trocar um fabricante, a lista de modelos correspondente é recarregada. Quando os dois modelos estão definidos, o programa consulta o banco de dados e atualiza os resultados automaticamente.

![Seleção dos equipamentos e resultado principal](../screenshots/scrsht_1.png)

Os botões **Detalhes** abrem as fichas técnicas completas dos equipamentos. Essa consulta é útil para confirmar se o cadastro representa corretamente o datasheet que será usado no projeto.

## 2. Conferir os dados técnicos

A janela **Detalhes do Inversor** apresenta identificação, sistema, propriedades elétricas e informações organizadas por MPPT. A janela **Detalhes do Módulo** apresenta identificação, tecnologia, grandezas elétricas, coeficientes de temperatura e dados mecânicos.

![Detalhes técnicos do inversor e do módulo](../screenshots/scrsht_2.png)

Use as barras de rolagem para consultar todos os campos. Antes de aceitar o dimensionamento, confira principalmente:

- tensão e corrente máximas de entrada do inversor;
- faixa de tensão de operação e de carga máxima dos MPPTs;
- número de entradas por MPPT;
- potência, `Voc`, `Isc`, `Vmpp` e `Impp` do módulo;
- coeficientes de temperatura do módulo.

Dados ausentes ou divergentes no cadastro podem alterar os limites calculados. A referência final deve ser sempre o datasheet vigente do fabricante.

## 3. Ler o resultado principal

O bloco **Potência máxima no inversor** informa:

- **Qtd. máx. de módulos:** limite adotado pelo programa para o inversor completo;
- **Sobrecarga admitida:** potência CC correspondente e seu percentual em relação à potência de referência do inversor;
- **Cálculos:** abre o resumo geral e mostra qual condição limitou a quantidade total.

Cada aba representa um MPPT ou um grupo de MPPTs com os mesmos parâmetros. A indicação, por exemplo, **MPPT 1 a 6**, significa que o resultado apresentado se aplica a todos os MPPTs desse intervalo.

### Faixa de módulos por string

A barra **Quantidade de módulos por String** reúne os limites calculados:

- **Vermelho — Fora da faixa:** quantidade abaixo ou acima das condições admitidas;
- **Amarelo — Faixa de operação:** intervalo compatível com a faixa operacional do MPPT;
- **Verde — Carga máxima:** intervalo que também satisfaz a faixa de carga máxima;
- **Marcadores numéricos:** pontos de transição entre os limites.

O texto **Quantidade máxima de Strings por MPPT: X/Y** deve ser lido como:

- `X`: quantidade máxima de strings admitida pelos cálculos elétricos;
- `Y`: quantidade física de entradas disponível no MPPT.

O arranjo não deve ultrapassar nenhum dos dois valores.

## 4. Analisar os limites por MPPT

Clique em **Cálculos** dentro da aba do MPPT para abrir **Detalhes dos Limites**.

![Gráficos dos limites por MPPT](../screenshots/scrsht_3.png)

O gráfico **Máximo de strings por MPPT** compara os limites impostos por:

- corrente de curto-circuito;
- número de entradas físicas;
- corrente de operação.

O gráfico **Quantidade máxima de módulos por string** compara os limites de:

- tensão de circuito aberto;
- faixa de operação;
- faixa de carga máxima.

Nos gráficos, **vermelho** identifica o valor limitante e **verde** identifica as demais condições válidas. O menor limite aplicável é o que restringe o dimensionamento; portanto, não se deve escolher uma quantidade apenas por ela caber em uma das barras verdes.

## 5. Consultar o resumo geral do inversor

Clique em **Cálculos** no bloco **Potência máxima no inversor** para abrir o resumo de todo o equipamento.

![Resumo geral do inversor](../screenshots/scrsht_4.png)

O gráfico **Quantidade máxima de módulos por inversor** compara as restrições de circuito aberto, operação, potência em sobrecarga e carga máxima. A barra vermelha indica a condição que limita o total de módulos.

O painel lateral repete a quantidade máxima e a sobrecarga admitida e detalha, por grupo de MPPTs:

- a quantidade de módulos e a potência na faixa de operação;
- a quantidade de módulos e a potência na faixa de carga máxima.

Esse resumo facilita a comparação entre o limite global do inversor e a distribuição calculada para os MPPTs, mas não define sozinho como as strings serão distribuídas no projeto executivo.

## 6. Opções para ignorar critérios

Depois da seleção do inversor, ficam disponíveis duas opções avançadas:

- **Ignorar corrente de operação:** desconsidera o limite de corrente operacional ao determinar o máximo de strings por MPPT;
- **Ignorar faixa de carga máxima:** desconsidera essa faixa ao determinar os limites de módulos por string e por inversor.

Ao marcar ou desmarcar uma opção, os resultados são recalculados. Critérios ignorados podem aparecer em cinza nos gráficos. Essas opções não corrigem um cadastro incompleto e não devem ser usadas apenas para aumentar a quantidade calculada de módulos.

## 7. Verificação antes de utilizar o resultado

Antes de aplicar o dimensionamento em um projeto:

1. confirme os modelos exatos dos equipamentos;
2. compare os dados cadastrados com os datasheets vigentes;
3. verifique as condições de temperatura consideradas no projeto;
4. confirme os limites de tensão, corrente, potência e quantidade de entradas;
5. valide a distribuição das strings entre os MPPTs;
6. considere normas, requisitos da concessionária e orientações dos fabricantes.

O Optimus Sun é uma ferramenta de apoio. O resultado não substitui a análise de um profissional tecnicamente habilitado.
