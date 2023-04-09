from hash_util import hash_string_256, hash_block

class Verification:
    """Una clase auxiliar que ofrece varios métodos de verificación y validación estáticos y basados en clases."""
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """Valida un número de prueba de trabajo (nonce) y comprueba si resuelve el requisito del PoW (dos 0 a la izquierda)

        Argumentos:
            :transactions: Las transacciones del bloque para el que se crea el nonce.
            :last_hash: El hash del bloque anterior que se almacenará en el bloque actual.
            :proof: El número de PoW (nonce) que estamos probando.
        """
        # Crear una cadena con todas las entradas hash
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        # Calcula el Hash de la cadena
        # IMPORTANTE: Este NO es el mismo hash que se almacenará en el previous_hash. No es el hash de un bloque. 
        # Sólo se utiliza para el algoritmo proof-of-work. 
        guess_hash = hash_string_256(guess)
        # Sólo se considera válido un hash (basado en las entradas anteriores) que empiece por dos 0.
        # Esta condición es modificable. También podría requerir 10 ceros a la izquierda, lo que llevaría mucho más tiempo
        # (nos permite controlar la velocidad a la que se pueden añadir nuevos bloques). 
        return guess_hash[0:2] == '00'
        
    @classmethod
    def verify_chain(cls, blockchain):
        """ Verifica la blockchain actual y devuelve True si es válida, False en caso contrario.."""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('PoW no válido')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance):
        """Verifica una transacción comprobando si el remitente tiene monedas suficientes.

        Argumentos:
            :transaction: La transacción que debe ser verificada.
        """
        sender_balance = get_balance()
        return sender_balance >= transaction.amount

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Verifica todas las transacciones abiertas."""
        return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions])