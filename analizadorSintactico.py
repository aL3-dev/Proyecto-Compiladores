# ============================================================
# Analizador Sintactico Descendente Recursivo LL(1) 
# ============================================================
tok = []
lin = []
pos = 0
n = 0
e = False   # bandera para saber si hubo errores

def leer_tokens(entrada):
    global tok, lin, n
    tok, lin = [], []
    with open(entrada, "r") as f:
        num = 0
        for linea in f:
            num += 1
            for p in linea.strip().split():
                tok.append(int(p))
                lin.append(num)
    n = len(tok)

def actual():
    return tok[pos] if pos < n else -1

def avanzar():
    global pos
    if pos < n:
        pos += 1

def error(msg):
    global e
    e = True
    if pos < n:
        print("ERROR SINTACTICO -> linea", lin[pos], ":", msg)
    elif n > 0:
        print("ERROR SINTACTICO -> final de linea", lin[-1], ":", msg)
    else:
        print("Error sintactico:", msg)

def verificar(t, desc=""):
    if actual() == t:
        avanzar()
    else:
        error("Se esperaba " + desc)

def programa():
    verificar(20, "'inicio'")
    lista_sentencias()
    verificar(21, "'fin'")

def lista_sentencias():
    t = actual()
    if t in (22, 23, 24, 1000, 33, 34):
        sentencia_simple()
        verificar(49, "';'")
        lista_sentencias()
    elif t == 30:
        condicional()
        lista_sentencias()
    elif t == 32:
        ciclo()
        lista_sentencias()
    elif t in (21, 31, -1):
        return
    else:
        error("Token inesperado")
        lista_sentencias()

def sentencia_simple():
    t = actual()
    if t in (22, 23, 24):
        declaracion()
    elif t == 1000:
        asignacion()
    elif t in (33, 34):
        io()
    else:
        error("Se esperaba declaracion, asignacion o entrada/salida")

def declaracion():
    tipo()
    lista_variables()

def tipo():
    if actual() not in (22, 23, 24):
        error("Se esperaba tipo (entero, real, cadena)")
    verificar(actual(), "tipo")

def lista_variables():
    verificar(1000, "variable")
    if actual() == 48:
        verificar(48, "','")
        lista_variables()

def asignacion():
    verificar(1000, "variable")
    verificar(47, "'='")
    expresion()

def io():
    t = actual()
    if t == 33:
        verificar(33, "'leer'")
        verificar(50, "'('")
        verificar(1000, "variable")
        verificar(51, "')'")
    elif t == 34:
        verificar(34, "'mostrar'")
        verificar(50, "'('")
        contenido()
        verificar(51, "')'")
    else:
        error("Se esperaba leer o mostrar")

def contenido():
    exp_concat()

def exp_concat():
    elemento_concat()
    if actual() == 52:
        verificar(52, "'++'")
        exp_concat()

def elemento_concat():
    if actual() == 1:
        verificar(1, "literal")
    else:
        expresion()

def condicional():
    verificar(30, "'si'")
    verificar(50, "'('")
    exp_relacional()
    verificar(51, "')'")
    verificar(20, "'inicio'")
    lista_sentencias()
    verificar(21, "'fin'")
    while actual() == 31:
        verificar(31, "'sino'")
        if actual() == 50:
            verificar(50, "'('")
            exp_relacional()
            verificar(51, "')'")
        verificar(20, "'inicio'")
        lista_sentencias()
        verificar(21, "'fin'")

def ciclo():
    verificar(32, "'mientras'")
    verificar(50, "'('")
    exp_relacional()
    verificar(51, "')'")
    verificar(20, "'inicio'")
    lista_sentencias()
    verificar(21, "'fin'")

def expresion():
    termino()
    while actual() in (37, 38):
        verificar(actual(), "'+' o '-'")
        termino()

def termino():
    factor()
    while actual() in (39, 40):
        verificar(actual(), "'*' o '/'")
        factor()

def factor():
    t = actual()
    if t == 50:
        verificar(50, "'('")
        expresion()
        verificar(51, "')'")
    elif t == 1000:
        verificar(1000, "variable")
    elif t == 2:
        verificar(2, "numero")
    elif t in (25, 26, 27, 28, 29):
        funcion()
    else:
        error("Se esperaba factor")

def funcion():
    t = actual()
    if t in (25, 26, 27, 28):
        verificar(t, "funcion trigonometrica")
        verificar(50, "'('")
        expresion()
        verificar(51, "')'")
    elif t == 29:
        verificar(29, "'pi'")
    else:
        error("Se esperaba funcion")

def exp_relacional():
    comparacion()
    while actual() in (35, 36):
        verificar(actual(), "'Y' o 'O'")
        comparacion()

def comparacion():
    expresion()
    if actual() in (41, 42, 43, 44, 45, 46):
        verificar(actual(), "operador relacional")
        expresion()
    else:
        error("Se esperaba operador relacional")

# Programa principal
leer_tokens("tokens2.txt")

if n == 0:
    print("Archivo de tokens vacio")
else:
    programa()
    if not e and pos == n:
        print("Analisis sintactico SIN errores")
    else:
        print("Analisis sintactico CON errores")