import re

import json 
# Definir los patrones para cada tipo de token
Tokens_permitidos = [
    ('NUMBER',    r'\d+'),            # Números
    ('STRING',    r'"[^"]*"'),        # Cadenas de texto entre comillas
    ('LBRACE',    r'{'),              # Llave de apertura {
    ('RBRACE',    r'}'),              # Llave de cierre }
    ('LBRACKET',  r'\['),             # Corchete de apertura [
    ('RBRACKET',  r'\]'),             # Corchete de cierre ]
    ('COLON',     r':'),              # Dos puntos :
    ('COMMA',     r','),              # Coma ,
    ('TRUE',      r'true'),           # Booleano true
    ('FALSE',     r'false'),          # Booleano false
    ('NULL',      r'null'),           # Null
    ('SKIP',      r'[ \t\n\r]+'),     # Espacios en blanco
    ('MISMATCH',  r'.'),              # Cualquier otro carácter inesperado
]

# Compilar los patrones en una expresión regular
tokens_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in Tokens_permitidos)
buscador = re.compile(tokens_regex).match

def lex(characters):
    posicion = 0
    tokens = []  # Lista para guardar los tokens

    while posicion < len(characters):
        match = buscador(characters[posicion:])
        if match:
            type_ = match.lastgroup
            value = match.group(type_)
            if type_ == 'SKIP':
                pass
            elif type_ == 'MISMATCH':
                raise RuntimeError(f'Unexpected character: {value}')
            else:
                tokens.append((type_, value))  
            posicion += len(value)
        else:
            raise RuntimeError(f'Unexpected character at position {position}')
    
    return tokens  # Retorna la lista de tokens o lista de simbolos
#----------------------------------------------------------------------------------------------------------------------
# Funciones para el analizador sintáctico según la gramática dada:

def parse_json(tokens):
    index = 0
    is_valid, index = parse_objeto(tokens, index)
    return is_valid and index == len(tokens)

def parse_objeto(tokens, index):
    # Un objeto comienza con '{' y termina con '}'
    if index < len(tokens) and tokens[index][0] == 'LBRACE':
        index += 1
        is_valid, index = parse_pares(tokens, index)
        if is_valid and index < len(tokens) and tokens[index][0] == 'RBRACE':
            index += 1
            return True, index
    return False, index

def parse_pares(tokens, index):
    # Los pares pueden ser uno o más, separados por comas
    if index < len(tokens):
        is_valid, index = parse_par(tokens, index)
        if not is_valid:
            return False, index
        while index < len(tokens) and tokens[index][0] == 'COMMA':
            index += 1
            is_valid, index = parse_par(tokens, index)
            if not is_valid:
                return False, index
        return True, index
    return False, index

def parse_par(tokens, index):
    # Un par consta de una clave seguida de un colon y un valor
    is_valid, index = parse_clave(tokens, index)
    if is_valid and index < len(tokens) and tokens[index][0] == 'COLON':
        index += 1
        return parse_valor(tokens, index)
    return False, index

def parse_clave(tokens, index):
    # Una clave debe ser una cadena
    if index < len(tokens) and tokens[index][0] == 'STRING':
        index += 1
        return True, index
    return False, index

def parse_valor(tokens, index):
    # Un valor puede ser: cadena, número, objeto, true, false o null
    if index < len(tokens):
        token = tokens[index]
        if token[0] == 'STRING':  # Es una cadena
            index += 1
        elif token[0] == 'NUMBER':  # Es un número
            index += 1
        elif token[0] == 'LBRACE':  # Es un objeto
            is_valid, index = parse_objeto(tokens, index)
        elif token[0] == 'TRUE':  # Es true
            index += 1
        elif token[0] == 'FALSE':  # Es false
            index += 1
        elif token[0] == 'NULL':  # Es null
            index += 1
        else:
            return False, index
        return True, index
    return False, index
#---------------------------------------------------------------------------------------------------------------------------

def generar_clase_csharp(nombre_clase, data):
    def to_csharp_type(valor):
        """Convierte tipos de Python a tipos de C#."""
        if isinstance(valor, str):
            return "string"
        elif isinstance(valor, int):
            return "int"
        elif isinstance(valor, float):
            return "double"
        elif isinstance(valor, bool):
            return "bool"
        elif isinstance(valor, list):
            # Supone que todos los elementos de la lista son del mismo tipo
            tipo_elemento = to_csharp_type(valor[0]) if valor else "object"
            return f"List<{tipo_elemento}>"
        elif isinstance(valor, dict):
            return "object"  # Las clases anidadas se manejan más adelante
        else:
            return "object"

    def procesar_dict(nombre_clase, contenido):
        """Procesa un diccionario JSON y genera una clase C#."""
        clases = []
        atributos = []

        for key, value in contenido.items():
            tipo = to_csharp_type(value)
            nombre_atributo = key.capitalize()
            
            if isinstance(value, dict):  # Crear una clase anidada
                clase_anidada, clase_nombre = procesar_dict(nombre_atributo, value)
                clases.append(clase_anidada)
                tipo = clase_nombre
            atributos.append(f"    public {tipo} {nombre_atributo} {{ get; set; }}")

        clase = f"public class {nombre_clase}\n{{\n" + "\n".join(atributos) + "\n}\n"
        return "\n".join(clases) + "\n" + clase, nombre_clase

    clases_generadas, _ = procesar_dict(nombre_clase, data)
    return clases_generadas
#--------------------------------------------------------------------------------------------------------------------------------
# Ejemplo de uso con el JSON dado
json_data = '''
{
  "id": "1",
  "nombre": "Juan",
  "direccion": {
    "calle": "Main St",
    "ciudad": "Madrid",
    "pais": "España"
  }
}
'''
#-----------------------------------------------------------------------------------------------------
# Ejecutar el analizador léxico
tokens = lex(json_data)

# Ejecutar el analizador sintáctico
is_valid_syntax = parse_json(tokens)

# Mostrar los resultados
for token in tokens:
    print(token)

if is_valid_syntax:
    data = json.loads(json_data)
    nombre_clase_principal = "Persona"
    clase_csharp = generar_clase_csharp(nombre_clase_principal, data)    
    print("La sintaxis del JSON es válida.","\n"+clase_csharp)
    
else:
    print("La sintaxis del JSON es inválida.")
