"""Proporciona métodos de ayuda a la verificación."""

from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet


class Verification:
    """
    Una clase auxiliar que ofrece varios métodos de verificación y validación
    estáticos y basados en clases y validación basados en clases.
    """
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """
        Validar un número de prueba de trabajo y ver si resuelve el algoritmo de
        prueba (dos ceros a la izquierda)

        Arguments:
            :transactions: Las transacciones del bloque para el que se crea la prueba.
            :last_hash: El hash del bloque anterior que se almacenará en el bloque actual.
            :proof: El número de prueba que estamos probando.
        """
        # Crear una cadena con todas las entradas hash
        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                str(last_hash) + str(proof)).encode()
        # Calcular el hash de la cadena
        # IMPORTANTE: Este NO es el mismo hash que se almacenará en previous_hash.
        # No es el hash de un bloque. Sólo se utiliza para el algoritmo de Proof of Work
        guess_hash = hash_string_256(guess)
        # Sólo un hash (que se basa en las entradas anteriores)
        # que empiece por dos 0 se considera válido
        # Por supuesto, se puede redefinir esta condición. También se podrían exigir 10
        # ceros a la izquierda, lo que llevaría bastante más tiempo (esto además permitiría
        # controlar la velocidad a la que se pueden añadir nuevos bloques).
        return guess_hash[0:2] == '00'

    @classmethod
    def verify_chain(cls, blockchain):
        """
        Verifica la blockchain actual y devuelve True si es válida, False en caso contrario.
        """
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work no válido')
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """
        Verificar una transacción comprobando si el remitente tiene monedas suficientes.

        Argumentos:
            :transaction: La transacción que debe verificarse.
        """
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return (sender_balance >= transaction.amount and 
                    Wallet.verify_transaction(transaction))
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """
        Verifica todas las transacciones pendientes.
        """
        return all([cls.verify_transaction(tx, get_balance, False) 
                    for tx in open_transactions])
        