# Inicializar nuestra lista (vacía) de blockchains
blockchain = []


def get_last_blockchain_value():
    """ Devuelve el último valor de la blockchain actual. """
    return blockchain[-1]

# Esta función acepta dos argumentos.
# Uno obligatorio (transaction_amount) y otro opcional (last_transaction)
def add_value(transaction_amount, last_transaction=[1]):
    """ Añade un nuevo valor, así como el último valor de la blockchain a la blockchain.
    
    Argumentos:
        :transaction_amount: La cantidad que debe añadirse.
        :last_transaction: La última transacción del blockchain (por defecto [1]).
    """
    blockchain.append([last_transaction, transaction_amount])


def get_user_input():
    """ Devuelve la entrada del usuario (un nuevo importe de transacción) como un float. """
    # Obtiene la entrada del usuario, la transforma de cadena a float y la almacena en user_input
    user_input = float(input('Introduzca importe de la transacción: '))
    return user_input

# Obtiene la entrada de la primera transacción y añade el valor a la blockchain
tx_amount = get_user_input()
add_value(tx_amount)

# Obtiene la entrada de la segunda transacción y añade el valor a la blockchain
tx_amount = get_user_input()
add_value(last_transaction=get_last_blockchain_value(), transaction_amount=tx_amount)

# Obtiene la entrada de la tercera transacción y añade el valor a la blockchain
tx_amount = get_user_input()
add_value(tx_amount, get_last_blockchain_value())

# Muestra la lista de la blockchain por consola
print(blockchain)
