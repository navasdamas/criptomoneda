# Inicializar nuestra lista (vacía) de blockchains
blockchain = []


def get_last_blockchain_value():
    """ Devuelve el último valor de la blockchain actual. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

# Esta función acepta dos argumentos.
# Uno obligatorio (transaction_amount) y otro opcional (last_transaction)
def add_transaction(transaction_amount, last_transaction=[1]):
    """ Añade un nuevo valor, así como el último valor de la blockchain a la blockchain.
    
    Argumentos:
        :transaction_amount: La cantidad que debe añadirse.
        :last_transaction: La última transacción del blockchain (por defecto [1]).
    """
    if last_transaction == None:
        last_transaction = [1]
    blockchain.append([last_transaction, transaction_amount])


def get_transaction_value():
    """ Devuelve la entrada del usuario (un nuevo importe de transacción) como un float. """
    # Obtiene la entrada del usuario, la transforma de cadena a float y la almacena en user_input
    user_input = float(input('Introduzca importe de la transacción: '))
    return user_input


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
    """ Comprueba la blockchain actual y devuelve True si es válida, False en caso contrario."""
    is_valid = True
    for block_index in range(len(blockchain)):
        if block_index == 0:
            # Si estamos comprobando el primer bloque (bloque génesis), 
            # deberíamos saltarnos la iteración (ya que no hay bloque anterior)
            continue
        # Comprueba el bloque anterior (el completo) frente 
        # al primer elemento del bloque actual
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
            is_valid = True
        else:
            is_valid = False
    return is_valid


waiting_for_input = True

# Un bucle while para la interfaz de entrada del usuario
# Termina cuando waiting_for_input se convierte en False o cuando se llama a break
while waiting_for_input:
    print('Por favor, elija una opción:')
    print('1: Añadir nueva transacción')
    print('2: Imprimir los bloques de la blockchain')
    print('h: Manipular la cadena') # simula un intento de manipulación de los datos de la blockchain
    print('q: Salir')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_amount = get_transaction_value()
        # Añade el importe de la transacción a la blockchain
        add_transaction(tx_amount, get_last_blockchain_value())
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == 'h':
        # Asegúrese de no intentar " hackear " la blockchain si está vacía
        if len(blockchain) >= 1:
            blockchain[0] = [2]
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
else:
    print('El usuario abandona la sesión.')


print('Fin!')
