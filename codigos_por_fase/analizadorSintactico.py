from analizadorLexico import ARCHIVO
# ============================================================
# Analizador Sintactico Descendente Recursivo LL(1) 
#L (Left-to-right): La cadena de entrada se lee de izquierda a derecha.
# L (Leftmost derivation): Construye una derivación más a la izquierda.
# 1 (One symbol lookahead): Utiliza exactamente un símbolo de anticipación 
# para decidir qué regla aplicar, sin necesidad de retroceder
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
                valor = int(p)
                if valor == 53:
                    print("ERROR LEXICO -> linea:", num)
                    continue
                tok.append(int(p))
                lin.append(num)
    n = len(tok)

def actual():
    return tok[pos] if pos < n else -1

def avanzar():
    global pos
    if pos < n: pos += 1

def error(msg):
    global e
    e = True
    if pos < n:
        print("ERROR SINTACTICO -> linea", lin[pos-1], ":", msg)
    else:
        print("Error sintactico:", msg)

def verificar(t, desc=""):
    if actual() == t:
        avanzar()
    else:
        error("Se esperaba " + desc)

#programa = "inicio" listaSentencias "fin" 
def programa():
    verificar(20, "'inicio'")
    lista_sentencias()
    verificar(21, "'fin'")

#sentencia = ( declaracion | asignacion | IO ) ";" | condicional | ciclo 
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
    elif t == 53:
        print("ERROR LEXICO -> linea", lin[pos])
        avanzar()
        lista_sentencias()
    elif t in (21, 31, -1):
        return
    else:
        error("Token inesperado")
        avanzar()
        lista_sentencias()
        
#( declaracion | asignacion | IO ) ";"
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

#declaracion = tipo listaVariables
def declaracion(): 
    tipo()
    lista_variables()

#tipo = "entero" | "real" | "cadena" 
def tipo():
    if actual() not in (22, 23, 24):
        error("Se esperaba tipo (entero, real, cadena)")
    verificar(actual(), "tipo")

#listaVariables = variable { "," variable } 
def lista_variables():  
    verificar(1000, "variable") 
    if actual() == 48:  
        verificar(48, "','") 
        lista_variables()

#asignacion = variable "=" expresion   
def asignacion():
    verificar(1000, "variable")
    verificar(47, "'='")
    expresion()
    
#IO = "leer" "(" variable ")" | "mostrar" "(" contenido ")" 
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

#expConcat = elementoConcat { "++" elementoConcat } 
def exp_concat():
    elemento_concat()
    if actual() == 52:
        verificar(52, "'++'")
        exp_concat()
        
#elementoConcat = literal | variable | expresion 
def elemento_concat():
    if actual() == 1:
        verificar(1, "literal")
    else:
        expresion()
        
#condicional = "si" "(" expRelacional ")" "inicio" listaSentencias "fin"  
# { "sino" ["(" expRelacional ")"] "inicio" listaSentencias "fin" }
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

#ciclo = "mientras" "(" expRelacional ")" "inicio" listaSentencias "fin"
def ciclo():
    verificar(32, "'mientras'")
    verificar(50, "'('")
    exp_relacional()
    verificar(51, "')'")
    verificar(20, "'inicio'")
    lista_sentencias()
    verificar(21, "'fin'")

#expresion = termino { ( "+" | "-" ) termino } 
def expresion():
    termino()
    while actual() in (37, 38):
        verificar(actual(), "'+' o '-'")
        termino()

#termino = factor { ( "*" | "/" ) factor } 
def termino():
    factor()
    while actual() in (39, 40):
        verificar(actual(), "'*' o '/'")
        factor()

#factor = "(" expresion ")" | variable | numeros | funcion 
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

#funcion = ( "sen" | "cos" | "tan" | "raiz" ) "(" expresion ")" | "pi" 
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
        
#expRelacional= expresion opRelacional expresion { opLogico expresion opRelacional expresion } 
def exp_relacional():
    comparacion()
    while actual() in (35, 36):
        verificar(actual(), "'Y' o 'O'")
        comparacion()

#opRelacional = "<" | ">" | "<=" | ">=" | "==" | "!=" 
def comparacion():
    expresion()
    if actual() in (41, 42, 43, 44, 45, 46):
        verificar(actual(), "operador relacional")
        expresion() 
    else:
        error("Se esperaba operador relacional")

# Programa principal
leer_tokens(ARCHIVO)

if n == 0:
    print("Archivo de tokens vacio")
else:
    programa()
    if not e and pos == n:
        print("Analisis sintactico SIN errores")
    else:
        print("Analisis sintactico CON errores")