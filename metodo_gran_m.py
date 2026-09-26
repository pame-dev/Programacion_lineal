# Método de la Gran M.
# Versión simplificada: en vez de manejar M de forma simbólica (m*M + c),
# usamos M como un número muy grande y fijo (1,000,000). El costo de cada
# variable se guarda como un solo número: el costo real, menos M si es una
# variable artificial. Como M es enorme, cualquier columna con -M siempre
# pierde frente a una columna sin M, así que el efecto es el mismo que usar
# M de forma simbólica.

try:
    from .numeros import fmt, EPS
    from .tablas import imprimir_tabla
except ImportError:
    from numeros import fmt, EPS
    from tablas import imprimir_tabla

M = 1_000_000  # "M" grande: penaliza fuertemente a las variables artificiales


def metodo_gran_m(c, restricciones, tipo):
    n_vars = len(c)
    m = len(restricciones)
    es_min = (tipo == 'min')

    # Gran M también trabaja internamente como maximización.
    c_obj = [(-v if es_min else v) for v in c]

    nombres = [f"x{i+1}" for i in range(n_vars)]
    costos = list(c_obj)  # costo de cada variable: real, o -M si es artificial
    columnas_extra = []

    for i, (*coefs, signo, b) in enumerate(restricciones):
        # <=  -> se agrega una holgura (costo 0)
        # >=  -> se agrega una variable de exceso (costo 0) y una artificial (-M)
        # =   -> se agrega solo una variable artificial (-M)
        if signo == '<=':
            columnas_extra.append((f"s{i+1}", 's', i))
        elif signo == '>=':
            columnas_extra.append((f"e{i+1}", 'e', i))
            columnas_extra.append((f"a{i+1}", 'a', i))
        elif signo == '=':
            columnas_extra.append((f"a{i+1}", 'a', i))
        else:
            raise ValueError(f"Signo no reconocido: {signo}")

    for (nom, tipo_col, fila) in columnas_extra:
        nombres.append(nom)
        costos.append(-M if tipo_col == 'a' else 0)

    n_total = len(nombres)

    # Se arma la tabla de coeficientes y la columna b.
    tabla = [[0.0] * n_total for _ in range(m)]
    b_col = [0.0] * m
    for i, (*coefs, signo, b) in enumerate(restricciones):
        for k in range(n_vars):
            tabla[i][k] = coefs[k]
        b_col[i] = b

    base = [None] * m
    for idx, (nom, tipo_col, fila) in enumerate(columnas_extra):
        j = n_vars + idx
        if tipo_col == 's':
            tabla[fila][j] = 1
            base[fila] = j
        elif tipo_col == 'e':
            tabla[fila][j] = -1
        elif tipo_col == 'a':
            tabla[fila][j] = 1
            base[fila] = j

    # Si b quedó negativo, se cambia el signo de toda la fila.
    for i in range(m):
        if b_col[i] < 0:
            b_col[i] = -b_col[i]
            tabla[i] = [-v for v in tabla[i]]

    print("\n===== MÉTODO DE LA GRAN M =====")
    print("Z = " + " + ".join(f"{fmt(c[i])}·x{i+1}" for i in range(n_vars)) + f"   ({tipo})")
    print(f"(se usa M = {M:,})")

    iteracion = 0
    MAX_ITER = 200
    while True:
        if iteracion > MAX_ITER:
            print("\n>>> El método no convergió tras muchas iteraciones (posible ciclado).")
            return None

        cb = [costos[base[i]] for i in range(m)]

        # Zj para cada columna, usando los costos de la base actual.
        z_j = []
        for j in range(n_total):
            suma = 0.0
            for i in range(m):
                suma += cb[i] * tabla[i][j]
            z_j.append(suma)

        cj_zj = [costos[j] - z_j[j] for j in range(n_total)]

        # Valor actual de Z, usando la columna b.
        z_actual = sum(cb[i] * b_col[i] for i in range(m))

        encabezados = ["Base"] + nombres + ["b"]
        filas_tabla = [[nombres[base[i]]] + [fmt(v) for v in tabla[i]] + [fmt(b_col[i])] for i in range(m)]
        filas_tabla.append(["Cj-Zj"] + [fmt(v) for v in cj_zj] + [fmt(z_actual)])
        imprimir_tabla(encabezados, filas_tabla, titulo=f"Iteración {iteracion}")

        # Entra la columna con el Cj-Zj más positivo.
        col_entra = None
        mejor_val = EPS
        for j in range(n_total):
            if cj_zj[j] > mejor_val:
                mejor_val = cj_zj[j]
                col_entra = j

        if col_entra is None:
            break

        # Prueba de la razón mínima para decidir qué fila sale.
        fila_sale = None
        mejor_razon = None
        for i in range(m):
            if tabla[i][col_entra] > EPS:
                razon = b_col[i] / tabla[i][col_entra]
                if mejor_razon is None or razon < mejor_razon:
                    mejor_razon = razon
                    fila_sale = i

        if fila_sale is None:
            print(f"\nLa columna de '{nombres[col_entra]}' no tiene elementos positivos.")
            print(">>> El problema es NO ACOTADO. No tiene solución óptima finita.")
            return None

        print(f"Entra: {nombres[col_entra]}   |   Sale: {nombres[base[fila_sale]]}   |   "
              f"Pivote: {fmt(tabla[fila_sale][col_entra])}")

        piv = tabla[fila_sale][col_entra]
        tabla[fila_sale] = [v / piv for v in tabla[fila_sale]]
        b_col[fila_sale] = b_col[fila_sale] / piv

        for i in range(m):
            if i != fila_sale and abs(tabla[i][col_entra]) > EPS:
                factor = tabla[i][col_entra]
                tabla[i] = [tabla[i][j] - factor * tabla[fila_sale][j] for j in range(n_total)]
                b_col[i] = b_col[i] - factor * b_col[fila_sale]

        base[fila_sale] = col_entra
        iteracion += 1

    # Si alguna artificial sigue en la base con valor positivo, no hay solución factible.
    for i in range(m):
        if nombres[base[i]].startswith('a') and b_col[i] > EPS:
            print("\n>>> El problema NO TIENE SOLUCIÓN FACTIBLE.")
            print("    (una variable artificial quedó positiva en la base óptima)")
            return None

    solucion = {nombres[j]: 0 for j in range(n_total)}
    for i in range(m):
        solucion[nombres[base[i]]] = b_col[i]

    # Como las artificiales ya valen 0, Z (con M incluido) coincide con el
    # verdadero valor de Z. Solo hay que deshacer el cambio de signo si era min.
    z_final = sum(costos[base[i]] * b_col[i] for i in range(m))
    if es_min:
        z_final = -z_final

    print("\n>>> SOLUCIÓN ÓPTIMA ENCONTRADA:")
    for k in range(n_vars):
        print(f"    x{k+1} = {fmt(solucion[f'x{k+1}'])}")
    print(f"    Z = {fmt(z_final)}")
    return {"variables": solucion, "Z": z_final}