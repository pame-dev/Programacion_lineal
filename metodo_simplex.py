# Metodo simplex

try:
    from .aritmetica import Frac, fmt
    from .tablas import imprimir_tabla
except ImportError:
    from aritmetica import Frac, fmt
    from tablas import imprimir_tabla


def metodo_simplex(c, restricciones, tipo):
    # Simplex estándar solo aplica a problemas con restricciones <= y lado derecho no negativo.
    # La idea es convertir el problema a una forma matricial y pivoteando en la tabla.
    for (*coefs, signo, b) in restricciones:
        # El simplex estándar necesita una base inicial formada por holguras.
        # Esto solo es directo cuando todas las restricciones son <= y b >= 0.
        if signo != '<=' or b < Frac(0):
            raise ValueError("El simplex estándar requiere restricciones '<=' con b >= 0.")

    n_vars = len(c)
    m = len(restricciones)
    es_min = (tipo == 'min')
    # El algoritmo busca maximizar; una minimización se transforma cambiando
    # el signo de la función objetivo y se corrige al final.
    c_obj = [(-v if es_min else v) for v in c]

    # Se agregan variables de holgura, una por cada restricción.
    nombres = [f"x{i+1}" for i in range(n_vars)] + [f"s{i+1}" for i in range(m)]
    n_total = n_vars + m
    c_ext = c_obj + [Frac(0)] * m

    tabla = []
    for i, (*coefs, signo, b) in enumerate(restricciones):
        # Cada fila contiene: coeficientes de x, una holgura, y el lado derecho b.
        fila = [coefs[k] for k in range(n_vars)]
        fila += [Frac(1) if k == i else Frac(0) for k in range(m)]
        fila.append(b)
        tabla.append(fila)

    # Al inicio, cada variable de holgura es básica en su propia fila.
    base = [n_vars + i for i in range(m)]

    print("\n===== MÉTODO SIMPLEX ESTÁNDAR =====")
    print(f"Z = " + " + ".join(f"{fmt(c[i])}·x{i+1}" for i in range(n_vars)) + f"   ({tipo})")

    iteracion = 0
    MAX_ITER = 200
    while True:
        # Cada repetición mejora la solución mediante un pivote.
        if iteracion > MAX_ITER:
            print("\n>>> El método no convergió tras muchas iteraciones (posible ciclado).")
            return None

        cb = [c_ext[base[i]] for i in range(m)]
        # Zj es el resultado de combinar cada columna con los costos básicos.
        z_j = [sum((cb[i] * tabla[i][j] for i in range(m)), Frac(0)) for j in range(n_total)]
        # Los valores Cj-Zj muestran qué variable puede mejorar el objetivo.
        cj_zj = [c_ext[j] - z_j[j] for j in range(n_total)]
        # Valor actual de la función objetivo usando la columna b.
        z_actual = sum((cb[i] * tabla[i][n_total] for i in range(m)), Frac(0))

        encabezados = ["Base"] + nombres + ["b"]
        filas_tabla = [[nombres[base[i]]] + [fmt(v) for v in tabla[i]] for i in range(m)]
        filas_tabla.append(["Cj-Zj"] + [fmt(v) for v in cj_zj] + [fmt(z_actual)])
        imprimir_tabla(encabezados, filas_tabla, titulo=f"Iteración {iteracion}")

        col_entra = None
        mejor_val = Frac(0)
        for j in range(n_total):
            # Entra la columna con el Cj-Zj positivo más grande.
            if cj_zj[j] > mejor_val:
                mejor_val = cj_zj[j]
                col_entra = j
        if col_entra is None:
            # Todos los Cj-Zj son <= 0: ya no se puede mejorar Z.
            break

        fila_sale = None
        mejor_razon = None
        for i in range(m):
            # Se aplica la razón b/a para conservar la factibilidad.
            if tabla[i][col_entra] > Frac(0):
                razon = tabla[i][n_total] / tabla[i][col_entra]
                if mejor_razon is None or razon < mejor_razon:
                    mejor_razon = razon
                    fila_sale = i

        if fila_sale is None:
            print(f"\nLa columna de '{nombres[col_entra]}' no tiene elementos positivos.")
            print(">>> El problema es NO ACOTADO (Z puede crecer/decrecer sin límite). No tiene solución óptima finita.")
            return None

        print(f"Entra: {nombres[col_entra]}   |   Sale: {nombres[base[fila_sale]]}   |   "
              f"Pivote: {fmt(tabla[fila_sale][col_entra])}")

        piv = tabla[fila_sale][col_entra]
        # Primero se normaliza la fila pivote para que el pivote sea 1.
        tabla[fila_sale] = [v / piv for v in tabla[fila_sale]]
        for i in range(m):
            if i != fila_sale and tabla[i][col_entra] != Frac(0):
            # Después se eliminan los demás valores de la columna pivote.
                factor = tabla[i][col_entra]
                tabla[i] = [tabla[i][j] - factor * tabla[fila_sale][j] for j in range(n_total + 1)]

        base[fila_sale] = col_entra
        # Se actualiza la base: entra la nueva variable y sale la anterior.
        iteracion += 1

    solucion = {nombres[j]: Frac(0) for j in range(n_total)}
    # Las variables básicas toman el valor de la última columna; las demás son 0.
    for i in range(m):
        solucion[nombres[base[i]]] = tabla[i][n_total]

    z_final = sum((c_ext[base[i]] * tabla[i][n_total] for i in range(m)), Frac(0))
    # Se deshace el cambio de signo si el problema original era de minimización.
    if es_min:
        z_final = -z_final

    print("\n>>> SOLUCIÓN ÓPTIMA ENCONTRADA:")
    for k in range(n_vars):
        print(f"    x{k+1} = {fmt(solucion[f'x{k+1}'])}")
    print(f"    Z = {fmt(z_final)}")
    return {"variables": solucion, "Z": z_final}
