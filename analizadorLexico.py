# ============================================================
# Analizador Léxico
# ============================================================

#variables globales
cadena = ""
i = 0
estado = 0
lex = ""
tokens = []
lexemas = []
errores = []
col_inicio = 0


def es_reservada(lexema):
    v = ["inicio", "fin", "entero", "real", "cadena", "sen", "cos",
         "tan", "raiz", "pi", "si", "sino", "mientras", "leer",
         "mostrar", "Y", "O"]
    for k in range(len(v)):
        if v[k] == lexema:
            return 20 + k
    return -1


# ------------------------------------------------------------
# Funcion de transicion de estdos del automata 
# ------------------------------------------------------------
def estados():
    global cadena, i, estado, lex
    c = cadena[i]

    if estado == 0:
        if c.isspace():
            return 0
        if c.isalpha():
            return 1
        if c.isdigit():
            return 4
        if c == "'":
            return 7
        if c == "+":
            return 9
        if c == "-":
            return 12
        if c == "*":
            return 13
        if c == "/":
            return 14
        if c == "<":
            return 15
        if c == ">":
            return 18
        if c == "=":
            return 21
        if c == "!":
            if i + 1 < len(cadena) and cadena[i + 1] == "=":
                return 24
            return 33
        if c == "(":
            return 25
        if c == ")":
            return 26
        if c == ";":
            return 27
        if c == ",":
            return 28
        return 33

    if estado == 1:                       # identificador / reservada
        if c.isalpha() or c.isdigit():
            return 1
        if es_reservada(lex) != -1:
            return 2
        return 3

    if estado == 2:                       # confirmo que es reservada
        return 3

    if estado == 4:                       # numero, antes del punto
        if c.isdigit():
            if lex == "0":
                return 33                 # error: cero seguido de digito
            return 4
        if c == ".":
            return 5
        return 6

    if estado == 5:                       # numero, despues del punto
        if c.isdigit():
            return 5
        if lex.endswith("."):
            return 33                     # error: falta digito tras el punto
        return 6

    if estado == 7:                       # cadena de texto
        if c == "'":
            return 8
        if c.isalpha() or c.isdigit() or c == " ":
            return 7
        return 33                         # caracter no permitido o sin cerrar

    if estado == 9:                       # se leyo '+'
        if c == "+":
            return 10
        return 11

    if estado == 10:                      # se leyo '++'
        return 11

    if estado == 15:                      # se leyo '<'
        if c == "=":
            return 16
        return 17

    if estado == 16:                      # se leyo '<='
        return 17

    if estado == 18:                      # se leyo '>'
        if c == "=":
            return 19
        return 20

    if estado == 19:                      # se leyo '>='
        return 20

    if estado == 21:                      # se leyo '='
        if c == "=":
            return 22
        return 23

    if estado == 22:                      # se leyo '=='
        return 23

    return estado


# ===============================================================
# Usa estados() para recorrer el automata, acumular los lexemas
# y emitir los tokens al llegar a un estado de aceptacion.
# ===============================================================
def tokenizar(cadena_linea, num_linea):
    global cadena, i, estado, lex, tokens, lexemas, errores, col_inicio
    cadena = cadena_linea + "$"
    i = 0
    estado = 0
    tokens = []
    lexemas = []
    errores = []
    lex = ""
    col_inicio = 0

    while i < len(cadena) - 1 or estado != 0:
        c = cadena[i]

        # ---------------- 0: estado inicial ----------------
        if estado == 0:
            if c.isspace():
                i += 1
                continue

            col_inicio = i
            lex = ""
            estado = estados()

            if estado == 33:
                if c == "!":
                    msg = "'!' no es valido sin '=' a continuacion"
                else:
                    msg = "caracter no reconocido '" + c + "'"
                errores.append("Linea " + str(num_linea) + ", columna " +
                                str(col_inicio + 1) + ": " + msg)
                tokens.append(53)
                lexemas.append(c)
                i += 1
                estado = 0
                continue

            if estado == 7:
                i += 1     # la comilla de apertura no forma parte del lexema
            continue

        # ---------------- 1: identificador / reservada (bucle) ----------------
        if estado == 1:
            while estados() == 1:
                lex += cadena[i]
                i += 1
            estado = estados()
            continue
        

        # ---------------- 2: confirmo que es reservada ----------------
        if estado == 2:
            estado = 3
            continue

        # ---------------- 3: ACEPTACION identificador / reservada ----------------
        if estado == 3:
            r = es_reservada(lex)
            tokens.append(r if r != -1 else 1000)
            lexemas.append(lex)
            estado = 0
            continue

        # ---------------- 4: numero, antes del punto (bucle) ----------------
        if estado == 4:
            lex += cadena[i]  # --> .09
            i += 1
            while estados() == 4:
                lex += cadena[i]
                i += 1
            siguiente = estados()

            if siguiente == 33:
                errores.append("Linea " + str(num_linea) + ", columna " +
                                str(col_inicio + 1) +
                                ": el numero no puede tener ceros a la izquierda")
                tokens.append(53)
                lexemas.append(lex)
                while cadena[i].isdigit():       # recuperacion: descarta el resto
                    i += 1
                estado = 0
                continue

            if siguiente == 5:
                lex += cadena[i]      # consume el punto decimal
                i += 1
                estado = 5
                continue

            estado = 6
            continue

        # ---------------- 5: numero, despues del punto (bucle) ----------------
        if estado == 5:
            siguiente = estados()

            if siguiente == 33:
                errores.append("Linea " + str(num_linea) + ", columna " +
                                str(col_inicio + 1) +
                                ": se esperaba un digito despues del punto decimal")
                tokens.append(53)
                lexemas.append(lex)
                estado = 0
                continue

            while estados() == 5:
                lex += cadena[i]
                i += 1

            estado = 6
            continue

        # ---------------- 6: ACEPTACION numero ----------------
        if estado == 6:
            tokens.append(2)
            lexemas.append(lex)
            estado = 0
            continue

        # ---------------- 7: cadena de texto (bucle) ----------------
        if estado == 7:
            siguiente = estados()

            if siguiente == 7:
                lex += cadena[i]
                i += 1
                continue

            if siguiente == 8:
                estado = 8
                continue

            # siguiente == 33: caracter no permitido o cadena sin cerrar
            if cadena[i] == "$":
                errores.append("Linea " + str(num_linea) + ", columna " +
                                str(col_inicio + 1) + ": cadena de texto sin cerrar")
            else:
                errores.append("Linea " + str(num_linea) + ", columna " +
                                str(i + 1) + ": caracter '" + cadena[i] +
                                "' no permitido dentro de comillas")
            tokens.append(53)
            lexemas.append(lex)
            estado = 0
            continue

        # ---------------- 8: ACEPTACION cadena de texto ----------------
        if estado == 8:
            i += 1     # consume la comilla de cierre
            tokens.append(1)
            lexemas.append(lex)
            estado = 0
            continue

        # ---------------- 9: se leyo '+' ----------------
        if estado == 9:
            lex += cadena[i]
            i += 1
            estado = estados()
            continue

        # ---------------- 10: se leyo '++' ----------------
        if estado == 10:
            lex += cadena[i]
            i += 1
            estado = 11
            continue

        # ---------------- 11: ACEPTACION '+' o '++' ----------------
        if estado == 11:
            if lex == "++":
                tokens.append(52); lexemas.append("++")
            else:
                tokens.append(37); lexemas.append("+")
            estado = 0
            continue

        # ---------------- 12: ACEPTACION directa '-' ----------------
        if estado == 12:
            tokens.append(38); lexemas.append("-")
            i += 1; estado = 0; continue

        # ---------------- 13: ACEPTACION directa '*' ----------------
        if estado == 13:
            tokens.append(39); lexemas.append("*")
            i += 1; estado = 0; continue

        # ---------------- 14: ACEPTACION directa '/' ----------------
        if estado == 14:
            tokens.append(40); lexemas.append("/")
            i += 1; estado = 0; continue

        # ---------------- 15: se leyo '<' ----------------
        if estado == 15:
            lex += cadena[i]
            i += 1
            estado = estados()
            continue

        # ---------------- 16: se leyo '<=' ----------------
        if estado == 16:
            lex += cadena[i]
            i += 1
            estado = 17
            continue

        # ---------------- 17: ACEPTACION '<' o '<=' ----------------
        if estado == 17:
            if lex == "<=":
                tokens.append(43); lexemas.append("<=")
            else:
                tokens.append(41); lexemas.append("<")
            estado = 0
            continue

        # ---------------- 18: se leyo '>' ----------------
        if estado == 18:
            lex += cadena[i]
            i += 1
            estado = estados()
            continue

        # ---------------- 19: se leyo '>=' ----------------
        if estado == 19:
            lex += cadena[i]
            i += 1
            estado = 20
            continue

        # ---------------- 20: ACEPTACION '>' o '>=' ----------------
        if estado == 20:
            if lex == ">=":
                tokens.append(44); lexemas.append(">=")
            else:
                tokens.append(42); lexemas.append(">")
            estado = 0
            continue

        # ---------------- 21: se leyo '=' ----------------
        if estado == 21:
            lex += cadena[i]
            i += 1
            estado = estados()
            continue

        # ---------------- 22: se leyo '==' ----------------
        if estado == 22:
            lex += cadena[i]
            i += 1
            estado = 23
            continue

        # ---------------- 23: ACEPTACION '=' o '==' ----------------
        if estado == 23:
            if lex == "==":
                tokens.append(45); lexemas.append("==")
            else:
                tokens.append(47); lexemas.append("=")
            estado = 0
            continue

        # ---------------- 24: ACEPTACION directa '!=' ----------------
        if estado == 24:
            tokens.append(46); lexemas.append("!=")
            i += 2     # consume '!' y '='
            estado = 0
            continue

        # ---------------- 25: ACEPTACION directa '(' ----------------
        if estado == 25:
            tokens.append(50); lexemas.append("(")
            i += 1; estado = 0; continue

        # ---------------- 26: ACEPTACION directa ')' ----------------
        if estado == 26:
            tokens.append(51); lexemas.append(")")
            i += 1; estado = 0; continue

        # ---------------- 27: ACEPTACION directa ';' ----------------
        if estado == 27:
            tokens.append(49); lexemas.append(";")
            i += 1; estado = 0; continue

        # ---------------- 28: ACEPTACION directa ',' ----------------
        if estado == 28:
            tokens.append(48); lexemas.append(",")
            i += 1; estado = 0; continue

    return tokens, lexemas, errores


# ============================================================
# Lectura del codigo fuente y escritura de la lista de tokens
# ============================================================
with open(r"prueba.txt") as file, open(r"tokens.txt", "w") as out:

    program = file.read().split("\n")
    linea = 0
    hubo_errores = False

    for line in program:
        linea += 1
        print("\nLinea", linea, ":", line)

        toks, lexs, errs = tokenizar(line, linea)

        if len(errs) > 0:
            hubo_errores = True
            for e in range(len(errs)):
                print("  ERROR LEXICO ->", errs[e])

        if len(toks) > 0:
            print("  Tokens:", toks)
            print("  Lexemas:", lexs)

        for valor in toks:
            out.write(str(valor) + " ")
        out.write("\n")

    print()
    if hubo_errores:
        print("Analisis lexico finalizado CON errores.")
    else:
        print("Analisis lexico finalizado SIN errores.")