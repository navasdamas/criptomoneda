from collections import OrderedDict

from printable import Printable

class Transaction(Printable):
    """Transacción que puede añadirse a un bloque de la blockchain.

    Atributos:
        :sender: El remitente de las monedas.
        :recipient: El receptor de las monedas.
        :amount: La cantidad de monedas enviadas.
    """
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_ordered_dict(self):
        """Convierte esta operación en un OrderedDict (hasheable)."""
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
