from functools import reduce
import hashlib as hl

import json
import pickle
import requests

# Importa dos funciones desde el archivo hash_util.py
from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

# La recompensa que se le da a los mineros (por crear un nuevo bloque)
MINING_REWARD = 10

print(__name__)


class Blockchain:
    """
    La clase Blockchain gestiona la blockchain, así como las transacciones abiertas
    y el nodo en el que se está ejecutando.

    Atributos:
        :chain: La lista de bloques
        :open_transactions (private): La lista de transacciones abiertas
        :hosting_node: El nodo conectado (que ejecuta la copia local de la blockchain).
    """

    def __init__(self, public_key, node_id):
        """El constructor de la clase Blockchain."""
        # Bloque inicial para la blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Inicializar nuestra lista (vacía) de blockchain
        self.chain = [genesis_block]
        # Transacciones no tramitadas
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    # Convertir el atributo chain en una propiedad con un getter (el método de abajo)
    # y un setter (@chain.setter)
    @property
    def chain(self):
        return self.__chain[:]

    # El setter de la propiedad chain
    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        """
        Devuelve una copia de la lista de transacciones abiertas.
        """
        return self.__open_transactions[:]

    def load_data(self):
        """Inicializar blockchain y abrir datos de transacciones desde un archivo."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                file_content = f.readlines()
                ## Cargamos la blockchain ##
                blockchain = json.loads(file_content[0][:-1])
                # Necesitamos convertir los datos cargados porque Transactions debe utilizar OrderedDict
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                ## Cargamos las transacciones abiertas ##
                open_transactions = json.loads(file_content[1][:-1])
                # De nuevo necesitamos convertir los datos cargados porque Transactions debe utilizar OrderedDict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass
        finally:
            print('Datos de la blockchain y transacciones abiertas cargados!')

    def save_data(self):
        """Guardar estado actual de la blockchain y transacciones abiertas en un archivo."""
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                saveable_chain = [
                    block.__dict__ for block in
                    [
                        Block(block_el.index,
                              block_el.previous_hash,
                              [tx.__dict__ for tx in block_el.transactions],
                              block_el.proof,
                              block_el.timestamp) for block_el in self.__chain
                    ]
                ]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                # Almacena las transacciones abiertas
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                f.write('\n')
                # Almacena la lista de nodos homólogos
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Fallo al guardar!')

    def proof_of_work(self):
        """
        Generar una Proof of Work para las transacciones abiertas, el hash del bloque anterior
        y un número aleatorio (que se obtiene de forma aleatoria hasta que se ajuste).
        """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Prueba con diferentes números PoW y devuelve el primero válido
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        """Calcular y devolver el saldo de un participante.
        """
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender
        # Obtiene una lista de todos los importes enviados por la persona dada (se devuelven
        # listas vacías si la persona NO era el remitente)
        # Esto recupera las cantidades enviadas de transacciones que ya estaban incluidas
        # en bloques de la blockchain
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        # Obtiene una lista de todos los importes enviados por la persona dada
        # (se devuelven listas vacías si la persona NO era el remitente)
        # Esto recupera los importes enviados de las transacciones abiertas (para evitar
        # el doble gasto)
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # Se recupera las cantidades de monedas recibidas de transacciones que ya estaban
        # incluidas en bloques de la blockchain
        # Se ignoran aquí las transacciones abiertas porque no deberías poder gastar
        # monedas antes de que la transacción haya sido confirmada + incluida en un bloque
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                 if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        # Devuelve el saldo total
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Devuelve el último valor del blockchain actual. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    # Esta función acepta dos argumentos.
    # Uno obligatorio (transaction_amount) y otro opcional (last_transaction)
    # El opcional es opcional porque tiene un valor por defecto => [1]

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """ Añade a la blockchain un nuevo valor, así como el último valor de la blockchain.

        Argumentos:
            :sender: El remitente de las monedas.
            :recipient: El destinatario de las monedas.
            :amount: La cantidad de monedas enviadas con la transacción (por defecto = 1.0).
        """
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={
                                                 'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        """Crea un nuevo bloque y se le añade transacciones abiertas."""
        # Obtener el último bloque actual de la blockchain
        if self.public_key is None:
            return None
        last_block = self.__chain[-1]
        # Hash del último bloque (=> para poder compararlo con el valor hash almacenado)
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # Los mineros deben ser recompensados, así que se genera una transacción de recompensa
        reward_transaction = Transaction(
            'RECOMPENSA_MINADO', self.public_key, '', MINING_REWARD)
        # Copiar transacción en lugar de manipular la lista original open_transactions
        # Esto asegura que si por alguna razón la minería fallara, no tenemos la transacción de recompensa almacenada en las transacciones abiertas
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
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [
                tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        """Add a block which was received via broadcasting to the local blockchain."""
        # Create a list of transaction objects
        transactions = [Transaction(
            tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        # Validate the proof of work of the block and store the result (True or False) in a variable
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block['previous_hash'], block['proof'])
        # Check if previous_hash stored in the block is equal to the local blockchain's last block's hash and store the result in a block
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        # Create a Block object
        converted_block = Block(
            block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        # Check which open transactions were included in the received block and remove them
        # This could be improved by giving each transaction an ID that would uniquely identify it
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True

    def resolve(self):
        """Checks all peer nodes' blockchains and replaces the local one with longer valid ones."""
        # Initialize the winner chain with the local chain
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                # Send a request and store the response
                response = requests.get(url)
                # Retrieve the JSON data as a dictionary
                node_chain = response.json()
                # Convert the dictionary list to a list of block AND transaction objects
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(
                    tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']],
                    block['proof'], block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                # Store the received chain as the current winner chain if it's longer AND valid
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        # Replace the local chain with the winner chain
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """Adds a new node to the peer node set.

        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Removes a node from the peer node set.

        Arguments:
            :node: The node URL which should be removed.
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """Return a list of all connected peer nodes."""
        return list(self.__peer_nodes)
