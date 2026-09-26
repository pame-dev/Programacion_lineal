# Método de la Gran M.
# Para RESOLVER el problema (las iteraciones) usamos M como un número muy
# grande y fijo (1,000,000): así el costo de cada variable es un solo
# número (el real, o -M si es artificial), sin necesidad de una clase
# especial para M.
#

try:
    from .numeros import fmt, EPS
    from .tablas import imprimir_tabla
except ImportError:
    from numeros import fmt, EPS
    from tablas import imprimir_tabla

M = 1_000_000  # "M" grande: penaliza fuertemente a las variables artificiales


def _texto_ecuacion(terminos):
    """Convierte una lista de (valor, nombre) en un texto tipo
    '3x1 + 2x2 - e2 + a2' (con los signos ya acomodados)."""
    texto = ""
    for idx, (valor, nombre) in enumerate(terminos):
        valor_abs = abs(valor)
        # Si el coeficiente es 1 no se escribe (queda solo el nombre).
        coef_txt = "" if abs(valor_abs - 1) < EPS else fmt(valor_abs)
        termino = f"{coef_txt}{nombre}"
        if idx == 0:
            texto = f"-{termino}" if valor < 0 else termino
        else:
            texto += f" - {termino}" if valor < 0 else f" + {termino}"
    return texto


def _texto_m(m_val, c_val, con_parentesis):
    """Da formato a la cantidad (m_val*M + c_val), por ejemplo:
    (3, 5) -> '3M + 5'   (-1, 0) -> '-M'   (0, 4) -> '4' """
    if abs(m_val) < EPS and abs(c_val) < EPS:
        return "0"
    if abs(m_val) < EPS:
        return fmt(c_val)

    if abs(m_val - 1) < EPS:
        parte_m = "M"
    elif abs(m_val + 1) < EPS:
        parte_m = "-M"
    else:
        parte_m = f"{fmt(m_val)}M"

    if abs(c_val) < EPS:
        return parte_m

    signo = "+" if c_val > 0 else "-"
    texto = f"{parte_m} {signo} {fmt(abs(c_val))}"
    return f"({texto})" if con_parentesis else texto


def _texto_objetivo_m(z_m, z_c, terminos_z):
    """Arma el texto completo de Z = <constante con M> + <términos con M
    por cada variable no básica>, tal como se muestra en clase."""
    partes = [_texto_m(z_m, z_c, con_parentesis=False)]
    for (m_j, c_j, nombre) in terminos_z:
        coef_txt = _texto_m(m_j, c_j, con_parentesis=True)
        if coef_txt == "1":
            termino = nombre
        elif coef_txt == "-1":
            termino = f"-{nombre}"
        else:
            termino = f"{coef_txt}{nombre}"
        if termino.startswith("-"):
            partes.append(f"- {termino[1:]}")
        else:
            partes.append(f"+ {termino}")
    return " ".join(partes)


def _mostrar_forma_aumentada(c_obj, restricciones, nombres, columnas_extra, tabla, base, b_col, n_vars, m):
    print("\n--- Forma aumentada ---")

    # 1) Restricciones con sus variables agregadas (holgura / exceso / artificial).
    extra_por_restriccion = {i: [] for i in range(m)}
    for (nom, tipo_col, fila) in columnas_extra:
        extra_por_restriccion[fila].append((nom, tipo_col))

    print("Restricciones:")
    for i, (*coefs, signo, b) in enumerate(restricciones):
        terminos = [(coefs[k], f"x{k+1}") for k in range(n_vars) if coefs[k] != 0]
        for (nom, tipo_col) in extra_por_restriccion[i]:
            terminos.append((-1 if tipo_col == 'e' else 1, nom))
        print("  " + _texto_ecuacion(terminos) + f" = {fmt(b)}")

    # 2) Función objetivo, sustituyendo la base inicial (variables básicas
    #    de holgura/artificial). Aquí sí se separa M de la parte constante,
    #    para poder escribir cosas como "(3M + 3)".
    #    costo de cada variable básica inicial: (-1, 0) si es artificial,
    #    (0, 0) si es de holgura o exceso.
    cb_m = [(-1, 0) if nombres[base[i]].startswith('a') else (0, 0) for i in range(m)]

    n_total = len(nombres)
    terminos_z = []
    for j in range(n_total):
        zj_m, zj_c = 0, 0
        for i in range(m):
            m_i, c_i = cb_m[i]
            zj_m += m_i * tabla[i][j]
            zj_c += c_i * tabla[i][j]
        costo_m, costo_c = (-1, 0) if nombres[j].startswith('a') else (0, c_obj[j] if j < n_vars else 0)
        m_j = costo_m - zj_m
        c_j = costo_c - zj_c
        if abs(m_j) > EPS or abs(c_j) > EPS:
            terminos_z.append((m_j, c_j, nombres[j]))

    z_m, z_c = 0, 0
    for i in range(m):
        m_i, c_i = cb_m[i]
        z_m += m_i * b_col[i]
        z_c += c_i * b_col[i]

    print("\nFunción objetivo Z, sustituyendo la base inicial (variables artificiales):")
    print("  Z = " + _texto_objetivo_m(z_m, z_c, terminos_z))


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

    # Antes de iterar, se muestra la forma aumentada (restricciones +
    # función objetivo con M simbólica), igual que en clase.
    _mostrar_forma_aumentada(c_obj, restricciones, nombres, columnas_extra, tabla, base, b_col, n_vars, m)

    print(f"\n(a partir de aquí, para las iteraciones se usa M = {M:,} como número)")

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