# Aquí usamos simplemente números float, que son mucho más
# fáciles de leer y de reproducir a mano. Para que las comparaciones como
# <=, >= y = no fallen por errores mínimos de redondeo, usamos un margen
# de tolerancia muy pequeño (EPS).

EPS = 1e-9


def texto_a_numero(texto):
    """Convierte texto ingresado por el usuario a float.
    Acepta enteros (5), decimales (2.5) y fracciones (3/4)."""
    texto = texto.strip().replace(" ", "")
    if texto == "":
        raise ValueError("Entrada vacía.")
    if "/" in texto:
        num_txt, den_txt = texto.split("/")
        return float(num_txt) / float(den_txt)
    return float(texto)


def fmt(x):
    """Da formato legible a un número: lo redondea a 3 decimales y le
    quita los ceros que sobran (por ejemplo 4.000 -> '4')."""
    x = round(x, 3)
    if x == int(x):
        return str(int(x))
    return str(x)


def es_menor_o_igual(a, b):
    return a <= b + EPS


def es_mayor_o_igual(a, b):
    return a >= b - EPS


def es_igual(a, b):
    return abs(a - b) <= EPS