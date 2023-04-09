from time import time

from utility.printable import Printable

class Block(Printable):
    """Un único bloque de nuestra blockchain.
    
    Atributos:
        :index: El índice de este bloque.
        :previous_hash: El hash del bloque anterior en la blockchain.
        :timestamp: La marca de tiempo del bloque (generada automáticamente por defecto).
        :transactions: Una lista de transacciones que se incluyen en el bloque.
        :proof: El número de prueba de trabajo (nonce) que produjo este bloque.
    """
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof


