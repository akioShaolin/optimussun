import tkinter as tk

# Dados de exemplo
min_operacao = 6
max_operacao = 21
min_carga_max = 14
max_carga_max = 18
maximo_valor = 25  # por ex: 5 a mais que o valor máximo

# Configurações
largura_canvas = 600
altura_canvas = 100
altura_barras = 30
espaco_topo = 20

root = tk.Tk()
root.title("Teste de Barras - Optimus Sun")

canvas = tk.Canvas(root, width=largura_canvas + 50, height=altura_canvas + 100, bg='white')
canvas.pack()

# Centralizar: definir ponto inicial
x_offset = 25
barra_total = largura_canvas
valor_max = maximo_valor

# Função para converter valor -> posição X
def valor_para_x(valor):
    return x_offset + (valor / valor_max) * barra_total

# Desenhar barras
# Barra vermelha (fundo)
canvas.create_rectangle(
    valor_para_x(0), espaco_topo, 
    valor_para_x(valor_max), espaco_topo + altura_barras, 
    fill='red', outline='black'
)

# Barra amarela (faixa de operação)
canvas.create_rectangle(
    valor_para_x(min_operacao), espaco_topo, 
    valor_para_x(max_operacao), espaco_topo + altura_barras, 
    fill='yellow', outline='black'
)

# Barra verde (faixa de carga máxima)
canvas.create_rectangle(
    valor_para_x(min_carga_max), espaco_topo, 
    valor_para_x(max_carga_max), espaco_topo + altura_barras, 
    fill='green', outline='black'
)

# Função para desenhar marcador + label
def marcador(valor):
    x = valor_para_x(valor)
    canvas.create_line(x, espaco_topo + altura_barras, x, espaco_topo + altura_barras + 20, arrow=tk.LAST)
    canvas.create_text(x, espaco_topo + altura_barras + 35, text=str(valor), font=('Arial', 10, 'bold'))

# Desenhar marcadores
for v in [0, min_operacao, min_carga_max, max_carga_max, max_operacao, valor_max]:
    marcador(v)

# Legenda (na parte de baixo)
legenda_y = espaco_topo + altura_barras + 60
canvas.create_rectangle(50, legenda_y, 70, legenda_y + 15, fill='red', outline='black')
canvas.create_text(80, legenda_y + 7, text="Fora da faixa", anchor='w', font=('Arial', 9))

canvas.create_rectangle(200, legenda_y, 220, legenda_y + 15, fill='yellow', outline='black')
canvas.create_text(230, legenda_y + 7, text="Faixa de operação", anchor='w', font=('Arial', 9))

canvas.create_rectangle(400, legenda_y, 420, legenda_y + 15, fill='green', outline='black')
canvas.create_text(430, legenda_y + 7, text="Carga máxima", anchor='w', font=('Arial', 9))

root.mainloop()
