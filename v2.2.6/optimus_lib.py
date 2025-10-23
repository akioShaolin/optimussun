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

# Decomposição em valores primos
def mppt_index_dec(n):
    if n == 0 or abs(n) == 1 or n < 0:
        return []

    fatores = []
    divisor = 2
    while n > 1:
        while n % divisor == 0:
            fatores.append(divisor)
            n //= divisor
        divisor += 1
        if divisor * divisor > n and n > 1:
            fatores.append(n)
            break
    
    fatores_unicos = sorted(set(fatores))

    # Gerar lista de primos até o maior fator encontrado
    primos = []
    limite = max(fatores_unicos)  # o suficiente é ir até o maior fator encontrado
    c = 2

    while c <= limite:
        pr = True
        for p in primos:
            if p * p > c:
                break
            if c % p == 0:
                pr = False
                break

        if pr:
            primos.append(c)
        c += 1

    return tuple(primos.index(p) + 1 for p in fatores_unicos)

def formatar_tupla(tupla):
    tupla = list(tupla)  # garante que seja mutável
    if not tupla:
        return ""
    elif len(tupla) == 1:
        return f"{tupla[0]}"
    else:
        return f"{', '.join(map(str, tupla[:-1]))} e {tupla[-1]}"