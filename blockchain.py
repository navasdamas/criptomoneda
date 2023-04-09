from functools import reduce
import hashlib as hl

import json
import pickle

from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

# La recompensa que damos a los mineros (por crear un nuevo bloque)
MINING_REWARD = 10

print(__name__)

class Blockchain:
    """La clase Blockchain gestiona la cadena de bloques, así como las transacciones abiertas y el nodo en el que se está ejecutando.
    
    Atributos:
        :chain: La lista de bloques
        :open_transactions (privado): La lista de transacciones abiertas
        :hosting_node: El nodo conectado (que ejecuta la blockchain).
    """
    def __init__(self, hosting_node_id):
        """El constructor de la clase Blockchain."""
        # Nuestro bloque inicial para la blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Inicializar nuestra lista de blockchain (solo con el bloque génesis)
        self.chain = [genesis_block]
        # Transacciones pendientes
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    # Esto convierte el atributo chain en una propiedad con un getter (el método siguiente) y un setter (@chain.setter)
    @property
    def chain(self):
        return self.__chain[:]

    # El setter de la propiedad chain
    @chain.setter 
    def chain(self, val):
        self.__chain = val


    def get_open_transactions(self):
        """Devuelve una copia de la lista de transacciones abiertas."""
        return self.__open_transactions[:]

    def load_data(self):
        """Inicializar blockchain + abrir datos de transacciones desde un archivo."""
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                # Necesitamos convertir los datos cargados porque las transacciones de los bloques deben utilizar OrderedDict
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                # Necesitamos convertir los datos cargados porque las transacciones de los bloques deben utilizar OrderedDict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass
        finally:
            print('Datos cargados!')

    def save_data(self):
        """Guardar blockchain + instantánea de transacciones abiertas en un archivo."""
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                    tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Fallo al guardar!')

    def proof_of_work(self):
        """
        Generar una prueba de trabajo (nonce) para las transacciones abiertas, 
        el hash del bloque anterior y un número aleatorio (que se adivina hasta que se ajuste al requisito del protocolo PoW).
        """         
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Prueba con diferentes números PoW (nonces) y devuelve el primero que sea válido
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        """Calcular y devolver el saldo de un participante."""
        if self.hosting_node == None:
            return None
        participant = self.hosting_node
        # Obtiene una lista de todos los importes de monedas enviados por la persona dada (se devuelven listas vacías si la persona NO era el remitente)
        # Esto recupera las cantidades enviadas de transacciones que ya estaban incluidas en bloques de la blockchain
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        # Obtiene una lista de todos los importes de monedas enviados por la persona dada (se devuelven listas vacías si la persona NO era el remitente)
        # Esto recupera los importes enviados de las transacciones abiertas (para evitar el doble gasto)
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # Esto recupera las cantidades de monedas recibidas de transacciones que ya estaban incluidas en bloques de la blockchain
        # Ignoramos aquí las transacciones abiertas porque no deberías poder gastar monedas antes de que la transacción haya sido confirmada + incluida en un bloque
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                 if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        # Devuelve el saldo total
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Devuelve el último bloque del blockchain actual. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Añade una nueva transacción, verificando previamente si es posible realizarla.

        Argumentos:
            :sender: El remitente de las monedas. (por defecto el propietario del nodo)
            :recipient: El destinatario de las monedas. 
            :amount: La cantidad de monedas enviadas con la transacción (por defecto = 1.0)
        """
        if self.hosting_node == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """Crear un nuevo bloque y añadirle transacciones abiertas."""
        # Obtener el último bloque actual de la blockchain
        if self.hosting_node == None:
            return None
        last_block = self.__chain[-1]
        # Hash del último bloque (=> para poder compararlo con el valor hash almacenado)
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # Los mineros deben ser recompensados, así que vamos a crear una transacción de recompensa
        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD)
        # Copiar transacción en lugar de manipular la lista original open_transactions
        # Esto asegura que si por alguna razón la minería fallara,
        # no tenemos la transacción de recompensa almacenada en las transacciones abiertas
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block
