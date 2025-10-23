#calculos.py

def compensacao_termica (coef, t_min, t_max, gr):
    # gr = grandeza
    if coef < 0:
        gr_min = gr * (1 + (t_max - 25) * coef)
        gr_max = gr * (1 + (t_min - 25) * coef)

    else:
        gr_min = gr * (1 + (t_min - 25) * coef)
        gr_max = gr * (1 + (t_max - 25) * coef)
    
    return gr_min, gr_max

def validar(valor):

    eq = {
        "THREE_PHASE_THREE_WIRE": "TRÊS FIOS TRIF.",
        "THREE_PHASE_FOUR_WIRE": "QUATRO FIOS TRIF.",
        "SINGLE_PHASE": "MONOFÁSICO",
        "HYBRID": "HÍBRIDO"
    }

    if isinstance(valor, list):
        return "\n".join(str(validar(v)) for v in valor)
    if valor == -1:
        return "Não Informado"
    
    return eq.get(valor, str(valor))

# Valores Validos
def vv(*args):
    return all(v != -1 and v is not None for v in args)
