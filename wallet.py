from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:
    """
    Crea, carga y conserva claves privadas y públicas. Gestiona la firma y
    verificación de transacciones.
    """

    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self):
        """Crear un nuevo par de claves privada y pública."""
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        """Guarda las claves en un archivo (wallet.txt)."""
        if self.public_key is not None and self.private_key is not None:
            try:
                with open('wallet-{}.txt'.format(self.node_id), mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Error al guardar el monedero...')
                return False

    def load_keys(self):
        """Carga en memoria las claves del archivo wallet.txt."""
        try:
            with open('wallet-{}.txt'.format(self.node_id), mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
            return True
        except (IOError, IndexError):
            print('Error al cargar el monedero...')
            return False

    def generate_keys(self):
        """Generar un nuevo par de claves privada y pública."""
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii
                .hexlify(private_key.exportKey(format='DER'))
                .decode('ascii'),
                binascii
                .hexlify(public_key.exportKey(format='DER'))
                .decode('ascii'))

    def sign_transaction(self, sender, recipient, amount):
        """Firmar una transacción y devolver la firma.

        Arguments:
            :sender: El remitente de la transacción.
            :recipient: El destinatario de la transacción.
            :amount: El importe de la transacción.
        """
        signer = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(self.private_key)))
        h = SHA256.new((str(sender) + str(recipient) +
                       str(amount)).encode('utf8'))
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        """Verificar la firma de una transacción.

        Arguments:
            :transaction: La transacción que debe verificarse.
        """
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) +
                       str(transaction.amount)).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
