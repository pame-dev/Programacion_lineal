# Aquí usamos simplemente números float, que son mucho más
# fáciles de leer y de reproducir a mano. Para que las comparaciones como
# <=, >= y = no fallen por errores mínimos de redondeo, usamos un margen
# de tolerancia muy pequeño (EPS).

EPS = 1e-9 #numero muy pequeño para comparar flotantes


def texto_a_numero(texto):
    """Convierte texto ingresado por el usuario a float.
    Acepta enteros (5), decimales (2.5) y fracciones (3/4)."""
    texto = texto.strip().replace(" ", "") #te da lo que el usuario ingreso como texto y quita espacios
    if texto == "":
        raise ValueError("Entrada vacía.") #error si el usuario no ingreso nada
    if "/" in texto: #si el usuario ingresa / significa que es una fraccion 
        num_txt, den_txt = texto.split("/") # divide el texto en numerador y denominador y divide
        return float(num_txt) / float(den_txt) #si ingreso un numero entero solo se convierte a decimal
    return float(texto)


def fmt(x): #esta funcion redondea a 3 decimales y quita 0 sobrantes
    x = round(x, 3)
    if x == int(x):
        return str(int(x))
    return str(x)
