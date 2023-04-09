from time import time

from utility.printable import Printable


class Block(Printable):
    """
    Bloque de la blockchain.

    Atributos:
        :index: El índice de este bloque.
        :previous_hash: El hash del bloque anterior en la blockchain.
        :timestamp: La marca de tiempo del bloque (generada automáticamente por defecto).
        :transactions: Lista de transacciones incluidas en el bloque.
        :proof: El número de Proof of Work que dio lugar a este bloque.
    """

    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof
