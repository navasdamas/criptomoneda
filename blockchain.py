import functools

# La recompensa que damos a los mineros (por crear un nuevo bloque)
MINING_REWARD = 10

# Nuestro bloque inicial para la blockchain
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
# Inicializar nuestra lista (vacía) de blockchain
blockchain = [genesis_block]
# Transacciones pendientes
open_transactions = []
# Somos los propietarios de este nodo de la blockchain, por lo que este es nuestro identificador (por ejemplo, para enviar monedas)
owner = 'Manuel'
# Participantes inscritos: Nosotros mismos + otras personas que envían/reciben monedas
participants = {'Manuel'}



def hash_block(block):
    """Realiza el hash de un bloque y devuelve una cadena que lo representa.
    
    Argumentos:
        :block: El bloque al que debe aplicarse el hash.
    """
    return '-'.join([str(block[key]) for key in block])


def get_balance(participant):
    """Calcular y devolver el saldo de un participante.

    Argumentos:
        :participant: El usuario para el que calcular el saldo.
    """
    # Obtiene una lista de todos los importes de monedas enviados por la persona dada (se devuelven listas vacías si la persona NO era el remitente)
    # Esto recupera las cantidades enviadas de transacciones que ya estaban incluidas en bloques de la blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    # Obtiene una lista de todos los importes de monedas enviados por la persona dada (se devuelven listas vacías si la persona NO era el remitente)
    # Esto recupera los importes enviados de las transacciones abiertas (para evitar el doble gasto)
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    print(tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    # Esto recupera las cantidades de monedas recibidas de transacciones que ya estaban incluidas en bloques de la blockchain
    # Ignoramos aquí las transacciones abiertas porque no deberías poder gastar monedas antes de que la transacción haya sido confirmada + incluida en un bloque
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    # Devuelve el saldo total
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Devuelve el último valor del blockchain actual. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    """Verificar una transacción comprobando si el remitente tiene monedas suficientes.

    Argumentos:
        :transaction: La transacción que debe verificarse.
    """
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Añade una nueva transacción, verificando previamente si es posible realizarla.

    Argumentos:
        :sender: El remitente de las monedas. (por defecto el propietario del nodo)
        :recipient: El destinatario de las monedas. 
        :amount: La cantidad de monedas enviadas con la transacción (por defecto = 1.0)
    """
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


def mine_block():
    """Crear un nuevo bloque y añadirle transacciones abiertas."""
    # Obtener el último bloque actual de la blockchain
    last_block = blockchain[-1]
    # Hash del último bloque (=> para poder compararlo con el valor hash almacenado)
    hashed_block = hash_block(last_block)
    # Los mineros deben ser recompensados, así que vamos a crear una transacción de recompensa
    reward_transaction = {
        'sender': 'RECOMPENSA_MINADO',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    # Copiar transacción en lugar de manipular la lista original open_transactions
    # Esto asegura que si por alguna razón la minería fallara,
    # no tenemos la transacción de recompensa almacenada en las transacciones abiertas
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions
    }
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Devuelve la entrada del usuario (un nuevo importe de transacción) como un float. """
    # Obtiene la entrada del usuario, la transforma de cadena a float y la almacena en user_input
    tx_recipient = input('Introduzca el destinatario de la transacción: ')
    tx_amount = float(input('Introduzca importe de la transacción: '))
    return tx_recipient, tx_amount


def get_user_choice():
    """Pregunta al usuario por su elección y la devuelve."""
    user_input = input('Su elección: ')
    return user_input


def print_blockchain_elements():
    """ Muestra todos los bloques de la blockchain. """
    # Envía la lista de blockchain a la consola
    for block in blockchain:
        print('Información del bloque:')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    """ Verifica la blockchain actual y devuelve True si es válida, False en caso contrario."""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
    return True


def verify_transactions():
    """Verifica todas las transacciones abiertas."""
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

# Un bucle while para la interfaz de entrada del usuario
# Es un bucle que sale cuando waiting_for_input se convierte en False o cuando se llama a break
while waiting_for_input:
    print('Por favor, elija una opción:')
    print('1: Añadir nueva transacción')
    print('2: Minar un nuevo bloque')
    print('3: Imprimir los bloques de la blockchain')
    print('4: Imprimir los participantes')
    print('5: Comprobar la validez de la transacción')
    print('h: Manipular la cadena') # simula un intento de manipulación de los datos de la blockchain
    print('q: Salir')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        # Añade el importe de la transacción a la blockchain
        if add_transaction(recipient, amount=amount):
            print('Transacción añadida!')
        else:
            print('Transacción fallida!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('Todas las transacciones son válidas')
        else:
            print('Hay transacciones no válidas')
    elif user_choice == 'h':
        # Asegura de que no se intenta " hackear " la blockchain si está vacía
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Alice', 'recipient': 'Bob', 'amount': 100.0}]
            }
    elif user_choice == 'q':
        # Esto hará que el bucle termine porque su condición de ejecución se convierte en False
        waiting_for_input = False
    else:
        print('La entrada no es válida, por favor elija un valor de la lista.')
    if not verify_chain():
        print_blockchain_elements()
        print('Blockchain no válida!')
        # Salir del bucle
        break
    print('Saldo de {}: {:6.2f}'.format('Manuel', get_balance('Manuel')))
else:
    print('El usuario abandona la sesión.')


print('Fin!')
