"""Funções de cálculo e formatação independentes da interface gráfica."""

import math

def compensacao_termica(coef, t_min, t_max, grandeza):
    """Retorna os extremos térmicos de uma grandeza em torno de 25 °C."""
    if coef < 0:
        gr_min = grandeza * (1 + (t_max - 25) * coef)
        gr_max = grandeza * (1 + (t_min - 25) * coef)

    else:
        gr_min = grandeza * (1 + (t_min - 25) * coef)
        gr_max = grandeza * (1 + (t_max - 25) * coef)
    
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


def minimo_valido(valores, padrao=-1):
    """Seleciona o menor limite informado, ignorando sentinelas -1 e None."""
    validos = [valor for valor in valores if vv(valor)]
    return min(validos) if validos else padrao


def limite_strings_curto_circuito(corrente_maxima, isc_max):
    """Calcula o limite inteiro de strings pela corrente de curto-circuito."""
    if not vv(corrente_maxima, isc_max) or isc_max <= 0:
        return -1
    return math.trunc(corrente_maxima / isc_max)


def limite_strings_operacao(corrente_maxima, impp_max, tolerancia=0):
    """Calcula o limite inteiro de strings pela corrente de operação."""
    if not vv(corrente_maxima, impp_max, tolerancia) or impp_max <= 0:
        return -1
    return math.trunc(corrente_maxima * (1 + tolerancia) / impp_max)


def limites_modulos_serie(tensao_minima, tensao_maxima, tensao_modulo_minima, tensao_modulo_maxima):
    """Calcula limites mínimo e máximo de módulos em série para uma faixa."""
    valores = (tensao_minima, tensao_maxima, tensao_modulo_minima, tensao_modulo_maxima)
    if not vv(*valores) or tensao_modulo_minima <= 0 or tensao_modulo_maxima <= 0:
        return -1, -1
    return (
        math.ceil(tensao_minima / tensao_modulo_minima),
        math.trunc(tensao_maxima / tensao_modulo_maxima),
    )


def limite_modulos_sobrecarga(potencia_nominal, sobrecarga, tolerancia, potencia_modulo):
    """Calcula o total de módulos limitado pela potência admitida no inversor."""
    if not vv(potencia_nominal, sobrecarga, tolerancia, potencia_modulo) or potencia_modulo <= 0:
        return 0
    return math.trunc(potencia_nominal * (1 + sobrecarga) * (1 + tolerancia) / potencia_modulo)

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
