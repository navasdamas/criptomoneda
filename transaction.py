from collections import OrderedDict
from utility.printable import Printable


class Transaction(Printable):
    """Transacción que puede añadirse a un bloque de la blockchain.

    Atributos:
        :sender: El remitente de las monedas.
        :recipient: El receptor de las monedas.
        :signature: La firma de la transacción.
        :amount: La cantidad de monedas enviadas.
    """

    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        """Convierte esta operación en un OrderedDict para poder calcular el hash."""
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
