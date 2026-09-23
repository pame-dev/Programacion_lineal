# imprime las tablas de iteraciones


def imprimir_tabla(encabezados, filas, titulo=None):
    if titulo:
        print(f"\n--- {titulo} ---")
    filas_txt = [[str(c) for c in fila] for fila in filas]
    anchos = [max(len(encabezados[i]), *(len(f[i]) for f in filas_txt)) for i in range(len(encabezados))]
    linea = " | ".join(h.center(anchos[i]) for i, h in enumerate(encabezados))
    print(linea)
    print("-" * len(linea))
    for f in filas_txt:
        print(" | ".join(v.rjust(anchos[i]) for i, v in enumerate(f)))
