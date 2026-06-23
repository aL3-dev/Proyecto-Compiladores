# Compilador PseudoC

Implementación de un compilador en Python para **PseudoC**, un lenguaje de programación estructurado desarrollado con fines académicos en la asignatura **INF 3631A Diseño de Compiladores** — Universidad Técnica de Oruro.

El compilador integra las fases de **Análisis Léxico**, **Análisis Sintáctico**, **Análisis Semántico** y **Generación de Código Intermedio**, demostrando el correcto funcionamiento e integración de cada fase como un sistema compilador funcional.

---

## Estado del proyecto

- [x] Diseño de la gramática formal (BNF / EBNF) y Diagramas de Conway
- [x] Analizador Léxico (autómata finito determinista)
- [x] Analizador Sintáctico descendente recursivo LL(1)
- [x] Analizador Semántico (verificación de variables declaradas)
- [x] Generación de Código Intermedio en cuádruplos (Notación Polaca Inversa)
- [x] Interfaz CLI con menú interactivo

---

## Estructura del repositorio

```
Proyecto-Compiladores/
│
├── compilador.py              # Compilador unificado (todas las fases + CLI)
├── prueba.txt                 # Código fuente PseudoC de entrada (por defecto)
├── tokens.txt                 # Generado por el léxico: lista de tokens por línea
├── cuartetos.txt              # Generado por el código intermedio: cuádruplos
├── README.md
│
├── codigos_por_fase/          # Implementaciones individuales de cada fase
│   ├── analizadorLexico.py    # Analizador Léxico independiente
│   ├── analizadorSemantico.py # Analizador Semántico independiente
│   └── analizadorSintactico.py# Analizador Sintáctico independiente
│
└── codigo_de_prueba/          # Programas PseudoC de ejemplo
    ├── ejem1.txt              # Suma de dos números
    ├── ejem2.txt              # Mayor entre dos números (si/sino)
    ├── ejem3.txt              # Factorial con ciclo mientras
    ├── ejem4.txt              # Área de un triángulo
    └── ejem5.txt              # Funciones trigonométricas
```

---

## Requisitos

- Python 3.8 o superior
- No requiere dependencias externas (solo librería estándar)

---

## Instalación y uso

**1.** Clonar el repositorio:
```bash
git clone https://github.com/aL3-dev/Proyecto-Compiladores.git
cd Proyecto-Compiladores
```

**2.** Escribir el código fuente PseudoC en `prueba.txt` o usar alguno de los ejemplos de `codigo_de_prueba/`.

**3.** Ejecutar el compilador:
```bash
python compilador.py
```

---

## Menú del compilador

```
==============================
ELIGE UNA OPCION
==============================
OPCION (0): Ver codigo fuente
OPCION (1): Analizar codigo
OPCION (2): Cargar nuevo archivo
OPCION (3): Salir
==============================
Archivo actual: prueba.txt
```

| Opción | Descripción |
|---|---|
| 0 | Muestra el código fuente actual con números de línea |
| 1 | Ejecuta las 4 fases en secuencia (léxico → sintáctico → semántico → código intermedio) |
| 2 | Carga un nuevo archivo ingresando su ruta completa |
| 3 | Cierra el compilador |

> El código intermedio solo se genera si las fases léxica, sintáctica y semántica finalizan sin errores.

---

## Gramática del lenguaje (EBNF)

```
programa        = "inicio" listaSentencias "fin"
listaSentencias = { sentencia }
sentencia       = ( declaracion | asignacion | IO ) ";" | condicional | ciclo
declaracion     = tipo listaVariables
listaVariables  = variable { "," variable }
tipo            = "entero" | "real" | "cadena"
asignacion      = variable "=" expresion
IO              = "leer" "(" variable ")" | "mostrar" "(" contenido ")"
contenido       = expConcat
expConcat       = elementoConcat { "++" elementoConcat }
elementoConcat  = literal | variable | expresion
literal         = "'" cadenas "'"
condicional     = "si" "(" expRelacional ")" "inicio" listaSentencias "fin"
                  { "sino" [ "(" expRelacional ")" ] "inicio" listaSentencias "fin" }
ciclo           = "mientras" "(" expRelacional ")" "inicio" listaSentencias "fin"
expresion       = termino { ( "+" | "-" ) termino }
termino         = factor { ( "*" | "/" ) factor }
factor          = "(" expresion ")" | variable | numeros | funcion
funcion         = ( "sen" | "cos" | "tan" | "raiz" ) "(" expresion ")" | "pi"
expRelacional   = expresion opRelacional expresion { opLogico expresion opRelacional expresion }
opRelacional    = "<" | ">" | "<=" | ">=" | "==" | "!="
opLogico        = "Y" | "O"
variable        = letra { letra | digito }
numeros         = ( digitoNocero [ numero ] | "0" ) [ "." numero ]
```

---

## Tabla de tokens

| Categoría | Token(s) | ID |
|---|---|---|
| Literal de texto | cadena entre comillas | 1 |
| Número | entero o real | 2 |
| Identificador | variable | 1000 |
| Reservada | inicio, fin | 20, 21 |
| Reservada | entero, real, cadena | 22, 23, 24 |
| Reservada | sen, cos, tan, raiz, pi | 25, 26, 27, 28, 29 |
| Reservada | si, sino, mientras | 30, 31, 32 |
| Reservada | leer, mostrar | 33, 34 |
| Reservada | Y, O | 35, 36 |
| Símbolo | +, -, *, / | 37, 38, 39, 40 |
| Símbolo | <, >, <=, >= | 41, 42, 43, 44 |
| Símbolo | ==, !=, = | 45, 46, 47 |
| Símbolo | , ; ( ) | 48, 49, 50, 51 |
| Símbolo | ++ | 52 |
| Error léxico | — | 53 |

---

## Ejemplo de programa PseudoC

```
inicio
entero n, resultado;
n = 5;
resultado = 1;
mientras (n > 0)
inicio
    resultado = resultado * n;
    n = n - 1;
fin
mostrar('el factorial es');
mostrar(resultado);
fin
```

---

## Autor

**Alejandro Soliz Mamani**
Carrera de Ingeniería Informática — Universidad Técnica de Oruro
Asignatura: INF 3631A Diseño de Compiladores
Docente: M. Sc. Ing. Gregorio Fernando Ureña Merida