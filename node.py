from uuid import uuid4

from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet

class Node:
    """El nodo que ejecuta la instancia local de blockchain.
    
    Atributos:
        :id: El id del nodo.
        :blockchain: La blockchain que ejecuta este nodo.
    """
    def __init__(self):
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        """ Devuelve la entrada del usuario (un nuevo importe de transacción) como un float. """
        # Obtiene la entrada del usuario, la transforma de cadena a float y la almacena en user_input
        tx_recipient = input('Introduzca el destinatario de la transacción: ')
        tx_amount = float(input('Introduzca importe de la transacción: '))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        """Pregunta al usuario por su elección y la devuelve."""
        user_input = input('Su elección: ')
        return user_input

    def print_blockchain_elements(self):
        """ Muestra todos los bloques de la blockchain. """
        # Envía la lista de blockchain a la consola
        for block in blockchain:
            print('Información del bloque:')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        """Inicia el nodo y espera la entrada del usuario."""
        waiting_for_input = True

        # Un bucle while para la interfaz de entrada del usuario
        # Es un bucle que sale una vez que waiting_for_input se convierte en False o cuando se llama a break
        while waiting_for_input:
            print('Por favor, elija una opción')
            print('1: Añadir nueva transacción')
            print('2: Minar un nuevo bloque')
            print('3: Imprimir los bloques de la blockchain')
            print('4: Comprobar la validez de la transacción')
            print('5: Crear monedero')
            print('6: Cargar monedero')
            print('7: Guardar las llaves')
            print('q: Salir')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # Añade el importe de la transacción a la blockchain
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Transacción añadida!')
                else:
                    print('Transacción fallida!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('La minería ha fallado. ¿No hay monedero?')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('Todas las transacciones son válidas')
                else:
                    print('Hay transacciones no válidas')
            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == 'q':
                # Esto hará que el bucle termine porque su condición de ejecución se convierte en False
                waiting_for_input = False
            else:
                print('La entrada no es válida, por favor elija un valor de la lista!')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Blockchain no válida!')
                # Salir del bucle
                break
            print('Saldo de {}: {:6.2f}'.format(self.wallet.public_key, self.blockchain.get_balance()))
        else:
            print('El usuario abandona la sesión!')

        print('Fin!')

if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
