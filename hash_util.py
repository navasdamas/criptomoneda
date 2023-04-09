import hashlib as hl
import json

def hash_string_256(string):
    """Crear un hash SHA256 para una cadena de entrada dada.

    Argumentos:
        :string: La cadena a la que se aplicará el hash.
    """
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """Realiza el hash de un bloque y devuelve una cadena que lo representa.

    Argumentos:
        :block: El bloque que se empleará como entrada para la función hash.
    """
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())