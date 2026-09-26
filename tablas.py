# imprime las tablas de iteraciones

def imprimir_tabla(encabezados, filas, titulo=None):
    if titulo:
        print(f"\n--- {titulo} ---")

    # Se calcula el ancho de cada columna según el texto más largo que
    # tenga que caber en ella (encabezado o algún valor de las filas).
    anchos = []
    for i in range(len(encabezados)):
        ancho_col = len(encabezados[i])
        for fila in filas:
            ancho_col = max(ancho_col, len(fila[i]))
        anchos.append(ancho_col)

    # Se imprime el encabezado centrado y luego una línea separadora.
    linea = " | ".join(encabezados[i].center(anchos[i]) for i in range(len(encabezados)))
    print(linea)
    print("-" * len(linea))

    # Se imprime cada fila con los valores alineados a la derecha.
    for fila in filas:
        print(" | ".join(fila[i].rjust(anchos[i]) for i in range(len(fila))))