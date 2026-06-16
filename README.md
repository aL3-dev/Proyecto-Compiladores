# Analizador Léxico — Proyecto Compiladores

Analizador léxico implementado en Python mediante un autómata finito determinista (AFD). Lee un archivo fuente, identifica los tokens y lexemas por línea, y escribe los códigos de token en un archivo de salida.

## Uso

```bash
python analizadorLexico.py
```

El programa lee `prueba.txt` como entrada y escribe los tokens en `tokens.txt`.

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

## Errores detectados

- Números con ceros a la izquierda (`007`)
- Número real sin dígito tras el punto (`1.`)
- Cadena de texto sin cerrar
- Caracteres no reconocidos (`@`, `!` suelto, etc.)
