# Optimus Sun v2.6.0 — notas da candidata

> Documento local de preparação. A v2.6.0 ainda não foi publicada.

## Principais mudanças

- Novo cadastro unificado de fabricantes, inversores, módulos e grupos de MPPT, com edição em rascunho, confirmação e persistência transacional.
- Pesquisa da aplicação principal por Id, modelo e fabricante, com fabricante opcional, filtros independentes por equipamento e filtros avançados em janela própria.
- Seleção explícita na pesquisa: filtros e digitação apenas atualizam a lista; o equipamento é confirmado por clique na linha ou Enter com foco na lista.
- Navegação por Tab e Shift+Tab revisada nas janelas auxiliares, com foco inicial útil, campos desabilitados ignorados, rolagem até o controle focado e retorno ao acionador ao fechar.
- Separação dos filtros elétricos do inversor entre saída CA e entrada CC, incluindo critérios por ao menos um grupo ou por todos os grupos de MPPT.
- Cartões persistentes para os equipamentos selecionados e recolhimento total da pesquisa após um cálculo válido.
- Sobrecarga cadastrada ou personalizada para a sessão, sem alteração do banco.
- Resultados inferiores roláveis e acesso explícito a **Gráfico e cálculos**.
- Matriz de Compatibilidade mantida como aplicativo independente, com cálculo em segundo plano, renderização em lotes, seletores de equipamentos ativos e detalhes por combinação.
- CSV com cabeçalho único; sobrecarga exportada como razão decimal com duas casas e importação compatível com os formatos anteriores suportados.
- Versão 2.6.0 compartilhada entre os três aplicativos e novo arquivo de build `optimus_sun_v2_6_0.spec`.

## Distribuição prevista

O pacote Windows continua em modo `onedir` e contém:

- `Optimus Sun.exe`;
- `Optimus Sun Cadastros.exe`;
- `Matriz de Compatibilidade.exe`;
- uma única cópia externa de `optimus_sun.db`, ao lado dos executáveis.

Comando de reprodução a partir da raiz do projeto:

```powershell
py -3 -m PyInstaller --noconfirm --clean optimus_sun_v2_6_0.spec
```

## Compatibilidade e limitações

- O banco e o schema não são migrados por esta versão.
- Registros legados inconsistentes continuam disponíveis para inspeção e correção manual.
- RS232, CAN, Ethernet, GPRS e Split Phase permanecem indisponíveis enquanto os `CHECK` do schema não aceitarem esses valores.
- A matriz continua separada da interface principal.
- Os resultados são apoio técnico e devem ser conferidos com datasheets, normas e condições reais do projeto.
