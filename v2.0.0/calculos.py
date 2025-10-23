#calculos.py

def compensacao_termica (coef, t_min, t_max, gr):
    # gr = grandeza
    if coef < 0:
        gr_min = gr * (1 + (t_max - 25) * coef / 100)
        gr_max = gr * (1 + (t_min - 25) * coef / 100)

    else:
        gr_min = gr * (1 + (t_min - 25) * coef / 100)
        gr_max = gr * (1 + (t_max - 25) * coef / 100)
    
    return gr_min, gr_max