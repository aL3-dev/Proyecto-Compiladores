from analizadorLexico import ARCHIVO, tokenizar
from analizadorSintactico import actual, avanzar, verificar, programa

# ============================================================
# FASE 3: Analisis Semantico 
# ============================================================
def semantico():
    global sem_e, tabla_simbolos
    tabla_simbolos = []
    sem_e = False
    n_tok = len(all_tokens)
    k = 0
 
    pila_ambitos = [{}]
    contador_id  = [0]
 
    def buscar_var(nombre):
        for ambito in reversed(pila_ambitos):
            if nombre in ambito:
                return ambito[nombre]["tipo"]
        return None
 
    def declarar_var(nombre, tipo, linea):
        global sem_e
        ambito_actual = pila_ambitos[-1]
        if nombre in ambito_actual:
            print("ERROR SEMANTICO -> linea", linea,
                  ": variable '" + nombre + "' ya fue declarada en este ambito")
            sem_e = True
            return
        contador_id[0] += 1
        ambito_actual[nombre] = {"pos": contador_id[0], "tipo": tipo}
        tabla_simbolos.append((nombre, contador_id[0], tipo))
 
    def inferir_tipo(k_inicio, k_fin):
        tipo_result = "entero"
        j = k_inicio
        while j < k_fin:
            t  = all_tokens[j]
            lx = all_lexemas[j]
            if t == 1:
                return "cadena"
            if t == 2 and "." in lx:
                tipo_result = "real"
            if t in (25, 26, 27, 28, 29):
                tipo_result = "real"
            if t == 1000:
                tv = buscar_var(lx)
                if tv == "cadena":
                    return "cadena"
                if tv == "real":
                    tipo_result = "real"
            j += 1
        return tipo_result
 
    def tipos_compatibles(tipo_var, tipo_expr):
        if tipo_var == tipo_expr:
            return True
        if tipo_var == "real" and tipo_expr == "entero":
            return True
        return False
 
    while k < n_tok:
        tok = all_tokens[k]
        lx  = all_lexemas[k]
        lin = all_lin[k]
 
        if tok == 20:                    # inicio → nuevo ambito
            pila_ambitos.append({})
            k += 1
 
        elif tok == 21:                  # fin → cerrar ambito
            if len(pila_ambitos) > 1:
                pila_ambitos.pop()
            k += 1
 
        elif tok in (22, 23, 24):        # declaracion
            tipo_decl = {22: "entero", 23: "real", 24: "cadena"}[tok]
            k += 1
            while k < n_tok:
                if all_tokens[k] == 1000:
                    declarar_var(all_lexemas[k], tipo_decl, all_lin[k])
                    k += 1
                elif all_tokens[k] == 48:
                    k += 1
                else:
                    break
 
        elif tok == 1000 and k + 1 < n_tok and all_tokens[k + 1] == 47:
            nombre_var = lx
            tipo_var   = buscar_var(nombre_var)
            if tipo_var is None:
                sem_e = True
                print("ERROR SEMANTICO -> linea", lin,
                      ": variable '" + nombre_var + "' no declarada")
            k_expr = k + 2
            k_fin  = k_expr
            while k_fin < n_tok and all_tokens[k_fin] != 49:
                k_fin += 1
            tipo_expr = inferir_tipo(k_expr, k_fin)
            if tipo_var is not None and not tipos_compatibles(tipo_var, tipo_expr):
                sem_e = True
                print("ERROR SEMANTICO -> linea", lin,
                      ": incompatibilidad de tipos — variable '" + nombre_var +
                      "' es " + tipo_var + " pero se asigna " + tipo_expr)
            k += 1
        elif tok == 1000:
            if buscar_var(lx) is None:
                sem_e = True
                print("ERROR SEMANTICO -> linea", lin,
                      ": variable '" + lx + "' no declarada")
            k += 1
        else:
            k += 1
 
    print("\n{:<20} {:<15} {}".format("Identificador", "Tipo", "Representacion"))
    print("-" * 48)
    for nombre, pos, tipo in tabla_simbolos:
        print("{:<20} {:<15} {}".format(nombre, tipo, "[1000, " + str(pos) + "]"))

# ============================================================
# FASE 4: CÓDIGO INTERMEDIO (Cuartetos + Notación Polaca Inversa)
# ============================================================

ci_pos      = 0
ci_n        = 0
cuartetos   = []
temp_count  = 0
etiqueta = 0
sem_e         = False
tabla_simbolos = []


def ci_lex():  
    return all_lexemas[ci_pos] if ci_pos < ci_n else "_"

def ci_ver(t):
    global ci_pos
    ci_pos = verificar(ci_pos, t)


def nuevo_temp():
    global temp_count
    temp_count += 1
    return "T" + str(temp_count)


def nueva_etiqueta():
    global etiqueta
    etiqueta += 1
    return "L" + str(etiqueta)


def emitir(op, a1, a2, res):
    cuartetos.append((op, a1, a2, res))

def prio(op):
    if op in (39, 40): return 3
    if op in (37, 38): return 2
    if op in (41, 42, 43, 44, 45, 46): return 1
    return 0


def token_a_op(t):
    return {37:"+", 38:"-", 39:"*", 40:"/",
            41:"<",  42:">", 43:"<=", 44:">=",
            45:"==", 46:"!="}.get(t, "?")


# ------------------------------------------------------------
# PASO 1: Infija → Posfija (Shunting Yard)
# ------------------------------------------------------------
def infija_a_posfija():
    pila_ops  = []   # pila de operadores (strings de simbolo)
    pila_ids  = []   # pila paralela de IDs (para calcular prio)
    posfija   = []   # salida en orden postfijo
    infija    = []   # registro del orden de lectura (para mostrar)

    OPERADORES = {37:"+", 38:"-", 39:"*", 40:"/",
                  41:"<",  42:">", 43:"<=", 44:">=",
                  45:"==", 46:"!="}

    while True:
        t = actual(ci_pos)

        if t in (1000, 2):                              # variable o numero
            aux = ci_lex()
            infija.append(aux)
            posfija.append(aux)
            ci_ver(t)

        elif t in (25, 26, 27, 28, 29): 
            funciones = ((25, "sen"),
                        (26, "cos"),
                        (27, "tan"),
                        (28, "raiz"),
                        (29, "pi"),
                        )
            nombre = next((n for k, n in funciones if k == t), "?")
            #nombre = {25:"sen",26:"cos",27:"tan",
            #         28:"raiz",29:"pi"}.get(t,"?")
            ci_ver(t)
            if t == 29:                                 # pi: constante
                infija.append("pi")
                posfija.append("pi")
            else:
                ci_ver(50)                              # (
                sub_inf, sub_pos = infija_a_posfija()
                ci_ver(51)                              # )
                infija  += [nombre + "("] + sub_inf + [")"]
                posfija += sub_pos + [nombre]

        elif t == 50:                                   # ( subexpresion )
            ci_ver(50)
            sub_inf, sub_pos = infija_a_posfija()
            ci_ver(51)
            infija  += ["("] + sub_inf + [")"]
            posfija += sub_pos

        elif t in OPERADORES:                           # operador binario
            aux = OPERADORES[t]
            infija.append(aux)
            while (pila_ids and
                   prio(pila_ids[-1]) >= prio(t)):
                posfija.append(pila_ops.pop())
                pila_ids.pop()
            pila_ops.append(aux)
            pila_ids.append(t)
            ci_ver(t)
        else:
            break

    while pila_ops:
        posfija.append(pila_ops.pop())
        pila_ids.pop()

    return infija, posfija


# ------------------------------------------------------------
# PASO 2: Posfija → Cuartetos
# Recorre la lista postfija (strings legibles) y genera los
# cuartetos usando una pila de operandos.
# Muestra la tabla de trazado igual que el codigo de referencia.
# ------------------------------------------------------------
def posfija_a_cuartetos(posfija):
    pila       = []
    operadores = ["+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!="]
    funciones  = ["sen", "cos", "tan", "raiz", "pi"]

    for token in posfija:
        if token in operadores:                         # operador binario
            b = pila.pop(); a = pila.pop()
            tmp = nuevo_temp()
            emitir(token, a, b, tmp)
            pila.append(tmp)

        elif token in funciones:                        # funcion
            if token == "pi":
                tmp = nuevo_temp()
                emitir("=", "pi", "_", tmp)
                pila.append(tmp)
            else:
                arg = pila.pop()
                tmp = nuevo_temp()
                emitir(token, arg, "_", tmp)
                pila.append(tmp)

        else:                                           # operando directo
            pila.append(token)

    return pila[-1] if pila else "_"


# ------------------------------------------------------------
# gen_expresion: combina los dos pasos y muestra el trazado
# ------------------------------------------------------------
def gen_expresion():
    infija, posfija = infija_a_posfija()

    if len(posfija) > 1:                               # solo si hay operacion
        print("\n  Infija  :", " ".join(infija))
        print("  Posfija :", " ".join(posfija))

    return posfija_a_cuartetos(posfija)



def gen_exp_relacional():
    res = gen_comparacion()
    while actual(ci_pos) in (35, 36):
        op = "Y" if actual(ci_pos) == 35 else "O"
        ci_ver(actual(ci_pos))
        der = gen_comparacion()
        tmp = nuevo_temp(); emitir(op, res, der, tmp); res = tmp
    return res


def gen_comparacion():
    izq = gen_expresion()
    if actual(ci_pos) in (41, 42, 43, 44, 45, 46):
        op = token_a_op(actual(ci_pos)); ci_ver(actual(ci_pos))
        der = gen_expresion()
        tmp = nuevo_temp(); emitir(op, izq, der, tmp); return tmp
    return izq

def gen_declaracion():
    tipos = {22:"entero", 23:"real", 24:"cadena"}
    tipo = tipos.get(actual(ci_pos), "?"); ci_ver(actual(ci_pos))
    gen_lista_variables(tipo)


def gen_lista_variables(tipo):
    if actual(ci_pos) == 1000:
        var = ci_lex(); emitir("DECL", tipo, "_", var); ci_ver(1000)
    if actual(ci_pos) == 48:
        ci_ver(48); gen_lista_variables(tipo)


def gen_asignacion():
    var = ci_lex(); ci_ver(1000); ci_ver(47)
    res = gen_expresion(); emitir("=", res, "_", var)


def gen_io():
    t = actual(ci_pos)
    if t == 33:
        ci_ver(33); ci_ver(50)
        var = ci_lex(); ci_ver(1000); ci_ver(51)
        emitir("LEER", "_", "_", var)
    elif t == 34:
        ci_ver(34); ci_ver(50)
        res = gen_contenido(); ci_ver(51)
        emitir("MOSTRAR", res, "_", "_")


def gen_contenido():   return gen_exp_concat()


def gen_exp_concat():
    izq = gen_elemento_concat()
    if actual(ci_pos) == 52:
        ci_ver(52); der = gen_exp_concat()
        tmp = nuevo_temp(); emitir("++", izq, der, tmp); return tmp
    return izq


def gen_elemento_concat():
    if actual(ci_pos) == 1:
        lit = "'" + ci_lex() + "'"
        tmp = nuevo_temp(); emitir("=", lit, "_", tmp)
        ci_ver(1); return tmp
    return gen_expresion()


def gen_condicional():
    ci_ver(30); ci_ver(50)
    cond = gen_exp_relacional(); ci_ver(51)

    etiq_sino = nueva_etiqueta()
    emitir("JF", cond, "_", etiq_sino)

    ci_ver(20); gen_lista_sentencias(); ci_ver(21)

    if actual(ci_pos) == 31:             # hay al menos un sino
        etiq_fin = nueva_etiqueta()
        emitir("JMP", "_", "_", etiq_fin)
        emitir("LBL", "_", "_", etiq_sino)

        while actual(ci_pos) == 31:
            ci_ver(31)
            etiq_sino = nueva_etiqueta()
            if actual(ci_pos) == 50:
                ci_ver(50); cond = gen_exp_relacional(); ci_ver(51)
                emitir("JF", cond, "_", etiq_sino)
            ci_ver(20); gen_lista_sentencias(); ci_ver(21)
            if actual(ci_pos) == 31:
                emitir("JMP", "_", "_", etiq_fin)
                emitir("LBL", "_", "_", etiq_sino)

        emitir("LBL", "_", "_", etiq_fin)

    else:                                # sin sino: solo etiqueta de fin
        emitir("LBL", "_", "_", etiq_sino)


def gen_ciclo():
    ci_ver(32)
    etiq_ini = nueva_etiqueta(); etiq_fin = nueva_etiqueta()
    emitir("LBL", "_", "_", etiq_ini)
    ci_ver(50); cond = gen_exp_relacional(); ci_ver(51)
    emitir("JF", cond, "_", etiq_fin)
    ci_ver(20); gen_lista_sentencias(); ci_ver(21)
    emitir("JMP", "_", "_", etiq_ini)
    emitir("LBL", "_", "_", etiq_fin)


def gen_lista_sentencias():
    t = actual(ci_pos)
    if t in (22, 23, 24):
        gen_declaracion(); ci_ver(49); gen_lista_sentencias()
    elif t == 1000:
        gen_asignacion(); ci_ver(49); gen_lista_sentencias()
    elif t in (33, 34):
        gen_io(); ci_ver(49); gen_lista_sentencias()
    elif t == 30:
        gen_condicional(); gen_lista_sentencias()
    elif t == 32:
        gen_ciclo(); gen_lista_sentencias()
    elif t in (21, 31, -1):
        return


def gen_programa():
    ci_ver(20); gen_lista_sentencias(); ci_ver(21)


def mostrar_y_guardar(salida):
    print("\n" + "=" * 60)
    print("CODIGO INTERMEDIO - CUARTETOS")
    print("=" * 60)
    encabezado = f"{'#':<5} {'Operador':<12} {'Operando1':<16} {'Operando2':<16} {'Resultado'}"
    separador  = "-" * 60
    print(encabezado)
    print(separador)
    with open(salida, "w") as f:
        f.write("# Codigo Intermedio - Cuartetos\n")
        f.write(encabezado + "\n")
        f.write(separador + "\n")
        for idx in range(len(cuartetos)):
            op, a1, a2, res = cuartetos[idx]
            linea = f"{idx+1:<5} {op:<12} {a1:<16} {a2:<16} {res}"
            print(linea)
            f.write(linea + "\n")
    print("=" * 60)
    print("Cuartetos guardados en:", salida)


# ============================================================
# PROGRAMA PRINCIPAL - CLI
# ============================================================

import os 

ARCHIVO_FUENTE    = "prueba.txt"
ARCHIVO_TOKENS    = "tokens.txt"
ARCHIVO_CUARTETOS = "cuartetos.txt"


def resetear_estado():
    """Limpia todas las listas y variables compartidas entre fases."""
    global all_tokens, all_lexemas, all_lin
    global sint_pos, sint_n, sint_e
    global ci_pos, ci_n, cuartetos, temp_count, etiqueta
    all_tokens  = []
    all_lexemas = []
    all_lin     = []
    sint_pos = 0; sint_n = 0; sint_e = False
    ci_pos   = 0; ci_n   = 0
    cuartetos   = []
    temp_count  = 0
    etiqueta = 0
    sem_e          = False
    tabla_simbolos = []


def ejecutar_lexico():
    global sint_n, ci_n
    hubo_errores = False

    with open(ARCHIVO_FUENTE) as file, open(ARCHIVO_TOKENS, "w") as out:
        program = file.read().split("\n")
        num_linea = 0
        for line in program:
            num_linea += 1
            print("\nLinea", num_linea, ":", line)
            toks, lexs, errs = tokenizar(line, num_linea)

            if len(errs) > 0:
                hubo_errores = True
                for e in range(len(errs)):
                    print("  ERROR LEXICO ->", errs[e])

            if len(toks) > 0:
                print("  Tokens:", toks)
                print("  Lexemas:", lexs)

            for idx in range(len(toks)):
                if toks[idx] != 53:
                    all_tokens.append(toks[idx])
                    all_lexemas.append(lexs[idx])
                    all_lin.append(num_linea)

            for valor in toks:
                out.write(str(valor) + " ")
            out.write("\n")

    sint_n = len(all_tokens)
    ci_n   = len(all_tokens)

    print()
    if hubo_errores:
        print("Analisis lexico finalizado CON errores.")
    else:
        print("Analisis lexico finalizado SIN errores.")
    return not hubo_errores


def ejecutar_sintactico():
    global sint_pos, sint_e
    sint_pos = 0; sint_e = False

    print("\n" + "=" * 60)
    print("FASE 2: ANALISIS SINTACTICO")
    print("=" * 60)

    if sint_n == 0:
        print("No hay tokens para analizar.")
        return

    programa()

    if not sint_e and sint_pos == sint_n:
        print("Analisis sintactico SIN errores")
    else:
        print("Analisis sintactico CON errores")
    return not sint_e

def ejecutar_semantico():
    global sem_e
    sem_e = False

    print("\n" + "=" * 60)
    print("FASE 3: ANALISIS SEMANTICO")
    print("=" * 60)

    if len(all_tokens) == 0:
        print("No hay tokens para analizar.")
        return False

    semantico()
    if not sem_e:
        print("Analisis semantico SIN errores")
    else:
        print("Analisis semantico CON errores")

    return not sem_e


def ejecutar_ci():
    global ci_pos, cuartetos, temp_count, etiqueta
    ci_pos      = 0
    cuartetos   = []
    temp_count  = 0
    etiqueta = 0

    print("\n" + "=" * 60)
    print("FASE 4: GENERACION DE CODIGO INTERMEDIO")
    print("=" * 60)

    gen_programa()
    mostrar_y_guardar(ARCHIVO_CUARTETOS)


def opcion_ver_fuente():
    print("\n" + "=" * 60)
    print("CODIGO FUENTE:", ARCHIVO_FUENTE)
    print("=" * 60)
    with open(ARCHIVO_FUENTE) as f:
        lineas = f.read().split("\n")
        for idx in range(len(lineas)):
            print(str(idx + 1).rjust(3), "│", lineas[idx])
    print("=" * 60)


def opcion_analizar():
    print("\n" + "=" * 60)
    print("FASE 1: ANALISIS LEXICO")
    print("=" * 60)
    resetear_estado()
    lex_ok = ejecutar_lexico()
    sin_ok = ejecutar_sintactico()
    sem_ok = ejecutar_semantico()
    if lex_ok and sin_ok and sem_ok:
        ejecutar_ci()
    else:
            print("\nGeneracion de codigo intermedio OMITIDA: hay errores.")
            
def opcion_cargar():
    global ARCHIVO_FUENTE
    print("\nIngrese la ruta completa del archivo fuente (.txt):")
    ruta = input("Ruta: ").strip()
    if os.path.exists(ruta):
        ARCHIVO_FUENTE = ruta
        resetear_estado()
        print("Archivo cargado correctamente:", ARCHIVO_FUENTE)
    else:
        print("ERROR: No se encontro el archivo:", ruta)


def mostrar_menu():
    print( "="*30  )
    print("ELIGE UNA OPCION")
    print("="*30)
    print("OPCION (0): Ver codigo fuente ")
    print("OPCION (1): Analizar codigo")
    print("OPCION (2): Cargar nuevo archivo")
    print("OPCION (3): Salir")
    print("="*30)
    print("Archivo actual:", ARCHIVO_FUENTE)


while True:
    mostrar_menu()
    opcion = input("  Opcion: ").strip()

    if opcion == "0":
        opcion_ver_fuente()
    elif opcion == "1":
        opcion_analizar()
    elif opcion == "2":
        opcion_cargar()
    elif opcion == "3":
        print("\nSaliendo del compilador. Hasta luego.")
        break
    else:
        print("\nOpcion no valida. Ingrese 0, 1, 2 o 3.")