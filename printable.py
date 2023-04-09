class Printable:
    """Una clase base que implementa la funcionalidad de impresión (devuelve una representación en cadena de caracteres)."""
    def __repr__(self):
        return str(self.__dict__)
