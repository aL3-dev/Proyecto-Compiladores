# Compilador PseudoC — Proyecto Compiladores

Implementación de las fases de análisis léxico y sintáctico de PseudoC en Python. El analizador léxico usa un autómata finito determinista (AFD) para identificar tokens y lexemas; el analizador sintáctico es un descendente recursivo LL(1) que valida la secuencia de tokens según la gramática del lenguaje.

## Estructura del repositorio

```
.
├── analizadorLexico.py       # Analizador léxico (estados() + tokenizar())
├── analizadorSintactico.py   # Analizador sintáctico LL(1) (una función por no terminal)
├── main.py                   # Orquestador: corre el lexico y luego el sintactico
├── prueba.txt                # Código fuente PseudoC de entrada
├── tokens.txt                 # Salida generada por el lexico: tokens por linea
└── README.md
```

## Uso

Ejecuta ambas fases en secuencia con un solo comando:

```bash
python main.py
```

Esto corre primero `analizadorLexico.py`, que lee `prueba2.txt` y genera `tokens2.txt`; a continuación corre automáticamente `analizadorSintactico.py`, que lee ese mismo archivo de tokens y valida la estructura del programa.

También se puede ejecutar cada fase por separado:

```bash
python analizadorLexico.py        # genera tokens.txt a partir de prueba2.txt
python analizadorSintactico.py    # valida tokens.txt
```

## Palabras reservadas

| Lexema    | Token |
|-----------|-------|
| `inicio`  | 20    |
| `fin`     | 21    |
| `entero`  | 22    |
| `real`    | 23    |
| `cadena`  | 24    |
| `sen`     | 25    |
| `cos`     | 26    |
| `tan`     | 27    |
| `raiz`    | 28    |
| `pi`      | 29    |
| `si`      | 30    |
| `sino`    | 31    |
| `mientras`| 32    |
| `leer`    | 33    |
| `mostrar` | 34    |
| `Y`       | 35    |
| `O`       | 36    |

## Otros tokens

| Categoría       | Lexema(s)            | Token(s)       |
|-----------------|----------------------|----------------|
| Cadena de texto | `'...'`              | 1              |
| Número          | entero / real        | 2              |
| Identificador   | nombre de variable   | 1000           |
| `+` / `++`      | `+`, `++`            | 37, 52         |
| `-` `*` `/`     | `-`, `*`, `/`        | 38, 39, 40     |
| Relacionales    | `<` `<=` `>` `>=`   | 41, 42, 43, 44 |
| Igualdad        | `==` `!=` `=`        | 45, 46, 47     |
| `,` `;` `(` `)` |                      | 48, 49, 50, 51 |
| Error léxico    |                      | 53             |