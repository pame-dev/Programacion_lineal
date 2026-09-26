# Método Simplex estándar (solo para restricciones <= con b >= 0).
# Versión simplificada: usa números float normales en vez de fracciones
# exactas, así que las operaciones se ven igual que en una calculadora.

try:
    from .numeros import fmt, EPS
    from .tablas import imprimir_tabla
except ImportError:
    from numeros import fmt, EPS
    from tablas import imprimir_tabla


def metodo_simplex(c, restricciones, tipo):
    # Primero se valida que el problema cumpla lo que el simplex estándar
    # necesita: todas las restricciones deben ser <= y b debe ser >= 0.
    for (*coefs, signo, b) in restricciones:
        if signo != '<=' or b < -EPS:
            raise ValueError("El simplex estándar requiere restricciones '<=' con b >= 0.")

    n_vars = len(c)
    m = len(restricciones)
    es_min = (tipo == 'min')

    # El algoritmo siempre maximiza. Si el problema es de minimización,
    # se le cambia el signo a la función objetivo y al final se revierte.
    c_obj = [(-v if es_min else v) for v in c]

    # Se agrega una variable de holgura (s1, s2, ...) por cada restricción.
    nombres = [f"x{i+1}" for i in range(n_vars)] + [f"s{i+1}" for i in range(m)]
    n_total = n_vars + m
    c_ext = c_obj + [0] * m

    # Se arma la tabla inicial: coeficientes de x, luego la identidad de
    # las holguras, y al final la columna b.
    tabla = []
    for i, (*coefs, signo, b) in enumerate(restricciones):
        fila = [coefs[k] for k in range(n_vars)]
        fila += [1 if k == i else 0 for k in range(m)]
        fila.append(b)
        tabla.append(fila)

    # Al inicio, cada holgura es la variable básica de su propia fila.
    base = [n_vars + i for i in range(m)]

    print("\n===== MÉTODO SIMPLEX ESTÁNDAR =====")
    print("Z = " + " + ".join(f"{fmt(c[i])}·x{i+1}" for i in range(n_vars)) + f"   ({tipo})")

    iteracion = 0
    MAX_ITER = 200
    while True:
        if iteracion > MAX_ITER:
            print("\n>>> El método no convergió tras muchas iteraciones (posible ciclado).")
            return None

        # cb: costos de las variables que están en la base ahora mismo.
        cb = [c_ext[base[i]] for i in range(m)]

        # Zj: combina cada columna con los costos de la base.
        z_j = []
        for j in range(n_total):
            suma = 0
            for i in range(m):
                suma += cb[i] * tabla[i][j]
            z_j.append(suma)

        # Cj-Zj: indica cuánto mejora Z si esa variable entra a la base.
        cj_zj = [c_ext[j] - z_j[j] for j in range(n_total)]

        # Valor actual de Z, usando la columna b.
        z_actual = 0
        for i in range(m):
            z_actual += cb[i] * tabla[i][n_total]

        encabezados = ["Base"] + nombres + ["b"]
        filas_tabla = [[nombres[base[i]]] + [fmt(v) for v in tabla[i]] for i in range(m)]
        filas_tabla.append(["Cj-Zj"] + [fmt(v) for v in cj_zj] + [fmt(z_actual)])
        imprimir_tabla(encabezados, filas_tabla, titulo=f"Iteración {iteracion}")

        # Se busca la columna que entra: la de Cj-Zj más positivo.
        col_entra = None
        mejor_val = EPS  # se exige que sea claramente positivo, no solo redondeo
        for j in range(n_total):
            if cj_zj[j] > mejor_val:
                mejor_val = cj_zj[j]
                col_entra = j

        if col_entra is None:
            # Ningún Cj-Zj es positivo: la tabla ya es óptima.
            break

        # Prueba de la razón mínima: decide qué fila (variable) sale.
        fila_sale = None
        mejor_razon = None
        for i in range(m):
            if tabla[i][col_entra] > EPS:
                razon = tabla[i][n_total] / tabla[i][col_entra]
                if mejor_razon is None or razon < mejor_razon:
                    mejor_razon = razon
                    fila_sale = i

        if fila_sale is None:
            print(f"\nLa columna de '{nombres[col_entra]}' no tiene elementos positivos.")
            print(">>> El problema es NO ACOTADO. No tiene solución óptima finita.")
            return None

        print(f"Entra: {nombres[col_entra]}   |   Sale: {nombres[base[fila_sale]]}   |   "
              f"Pivote: {fmt(tabla[fila_sale][col_entra])}")

        # Se hace el pivoteo: la fila pivote se divide entre el pivote,
        # y el resto de filas se ajustan para dejar ceros en esa columna.
        piv = tabla[fila_sale][col_entra]
        tabla[fila_sale] = [v / piv for v in tabla[fila_sale]]

        for i in range(m):
            if i != fila_sale and abs(tabla[i][col_entra]) > EPS:
                factor = tabla[i][col_entra]
                tabla[i] = [tabla[i][j] - factor * tabla[fila_sale][j] for j in range(n_total + 1)]

        base[fila_sale] = col_entra
        iteracion += 1

    # Se arma el diccionario de solución: básicas toman su valor, el resto 0.
    solucion = {nombres[j]: 0 for j in range(n_total)}
    for i in range(m):
        solucion[nombres[base[i]]] = tabla[i][n_total]

    z_final = 0
    for i in range(m):
        z_final += c_ext[base[i]] * tabla[i][n_total]
    if es_min:
        z_final = -z_final

    print("\n>>> SOLUCIÓN ÓPTIMA ENCONTRADA:")
    for k in range(n_vars):
        print(f"    x{k+1} = {fmt(solucion[f'x{k+1}'])}")
    print(f"    Z = {fmt(z_final)}")
    return {"variables": solucion, "Z": z_final}