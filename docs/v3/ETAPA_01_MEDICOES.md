# Etapa 01 — medição e fluidez da matriz

Data: 18/09/2026. A versão de referência é a GUI da tag `v2.6.0`, carregada em processo isolado sem mudar o checkout. A versão posterior é o working tree de `feature/v3.0.0`. Ambas leram **somente** o snapshot da etapa 00, sem alterar `src/optimus_sun.db`. Células da medição visual usam valores sintéticos idênticos; as medições de cálculo usam a API real e equipamentos ativos repetidos do snapshot. Os números abaixo são execuções pontuais, não médias ou promessas para outro hardware.

Ambiente: Windows 11 Pro 10.0.22631, Python 3.13.3, Intel Core i5-1135G7 (8 processadores lógicos), cerca de 15,7 GiB de RAM. Janela de benchmark: 1200×800. `tools/benchmark_matrix.py` mede tempo de cálculo até o início de `_render_matrix`, tempo de preparação visual até status pronto, working set do processo e atraso de uma sonda Tk agendada a cada 20 ms. O p95 é calculado sobre as amostras de cada fase. Sem mouse humano durante o benchmark; responsividade interativa ainda pede validação manual.

## Comparação por fase

| Medida | 20×20 antes | 20×20 depois | 100×100 antes | 100×100 depois |
| --- | ---: | ---: | ---: | ---: |
| Tempo de cálculo | 0,206 s | 0,175 s | 48,070 s | 47,976 s |
| Tempo de preparação visual | 1,651 s | 0,027 s | 56,000 s | 0,025 s |
| Tempo total até matriz pronta | 1,856 s | 0,202 s | 104,070 s | 48,001 s |
| Atraso p95 durante cálculo | 10,5 ms | 7,6 ms | 90,7 ms | **110,2 ms** |
| Atraso máximo durante cálculo | 11,5 ms | 18,1 ms | 137 ms | 225 ms |
| Atraso p95 durante visualização | 362 ms | 9,1 ms | 12.209 ms | 1,8 ms |
| Atraso máximo durante visualização | 890 ms | 9,1 ms | 15.582 ms | 1,8 ms |
| Pico de working set do processo | 41,3 MB | 34,1 MB | 200,9 MB | 49,1 MB |

O algoritmo matemático não foi alterado; a diferença pequena nos tempos de cálculo é variação de execução e a cessão de CPU feita **na thread de trabalho** a cada 16 pares. O p95 do cálculo 100×100 ainda ultrapassou levemente o alvo inicial de 100 ms. A GUI ficou atendendo eventos e o maior atraso observado nessa fase foi 225 ms, contra uma pausa de mais de 15 s na visualização antiga. Não declarar esse resultado universal: CPU/VM/volume diferentes exigem nova medição. Processos separados foram considerados para CPU, mas não adotados nesta etapa pelo custo de spawn/empacotamento no Windows e porque o problema dominante medido era a criação de widgets. Se o p95 de cálculo ou o fechamento continuarem inadequados no hardware-alvo, reavaliar essa opção com snapshot serializável e `freeze_support`.

## Formatos extremos e semântica

| Formato | Visualização virtual | Working set | Cálculo real e atraso p95 |
| --- | ---: | ---: | --- |
| 5×400 (largo) | 0,011 s | 32,2 MB | 0,246 s; 5,1 ms |
| 400×5 (alto) | 0,020 s | 32,3 MB | 7,242 s; 80,8 ms |

As durações de cálculo diferem porque o benchmark repete equipamentos em disposições diferentes; não são comparação de cargas elétricas equivalentes. O viewport cria somente itens `Canvas` visíveis; os 10.000 resultados de 100×100 continuam em `MatrixCalculation.cells`. O teste exportou 101 linhas CSV com 301 colunas na matriz 100×100: 100 inversores × 100 módulos, três valores por módulo. Clique no viewport deslocado horizontal e verticalmente abriu o mesmo objeto de célula que a exportação usa. Os testes existentes de CSV e valores continuaram passando.

## Mudança implementada

- O worker informa pares concluídos de 16 em 16, com total real. A barra é determinada no cálculo e passa para a fase de preparação visual; só atinge 100% visual quando a primeira área visível está pronta. Durante preparação/erro/cancelamento, o status distingue as fases.
- A matriz usa canvas virtual: desenha cabeçalho e células visíveis sob rolagem, em vez de criar três widgets para cada par. Limpeza é proporcional ao viewport; não há lote fixo de oito linhas. Importação e reordenação reutilizam o dataset completo e repintam somente a área visível.
- Cancelar sinaliza a thread entre pares, descarta resultado parcial ou tardio e preserva a matriz anterior. Fechar sinaliza cancelamento, cancela timers de polling/desenho e não espera por destruição de milhares de widgets. A fila de progresso é limitada; mensagens de progresso velhas podem ser descartadas, mas o estado terminal sempre é entregue sem bloquear a thread.
- Callbacks de foco e inicialização da pesquisa avançada passaram a ser cancelados quando a janela dona é destruída. A baseline emitia `invalid command name ... <lambda>`/`after script` nos testes Tk; a suíte posterior terminou sem esses avisos.
- Conexões de leitura da matriz agora são fechadas ao sair do bloco, inclusive em erro/cancelamento. Fórmulas, política do banco, schema e formato CSV não foram alterados.

## Verificação e pendências

Os **100 testes isolados** da baseline continuaram aprovados. Após acrescentar três verificações para progresso/cancelamento, viewport/clique/exportação e fechamento, a suíte segura passou com **103 testes**. O teste de fechamento confirma que a thread interrompe e os IDs de `after` da matriz são cancelados; o teste de viewport confirma que 10.000 pares não criam 30.000 widgets. Nenhum teste de escrita usou o banco operacional.

Validação manual ainda pendente: abrir a GUI na resolução real, calcular 20×20 e 100×100, rolar rapidamente até o fim horizontal/vertical, clicar em quantidade/potência/sobrecarga de células distantes, importar/exportar CSV grande, cancelar durante cálculo e fechar durante cálculo ou visualização. Observar se a barra muda de fase e se a janela aceita foco, rolagem e fechamento; conferir terminal sem erros de callbacks. Não houve inspeção visual humana da janela neste ambiente de benchmark.

Para repetir com o snapshot de teste (não apontar testes de escrita ao banco original):

```powershell
py -3 -X utf8 -B tools/benchmark_matrix.py 20 20 CAMINHO_DO_SNAPSHOT calc baseline
py -3 -X utf8 -B tools/benchmark_matrix.py 20 20 CAMINHO_DO_SNAPSHOT calc
py -3 -X utf8 -B tools/benchmark_matrix.py 100 100 CAMINHO_DO_SNAPSHOT calc baseline
py -3 -X utf8 -B tools/benchmark_matrix.py 100 100 CAMINHO_DO_SNAPSHOT calc
```

O modo `baseline` carrega a GUI da tag `v2.6.0` sem modificar o checkout; requer Git e essa tag local. Após imprimir a medida, o processo de benchmark antigo termina diretamente para não aguardar a destruição de dezenas de milhares de widgets. O modo novo fecha normalmente.
