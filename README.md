
# Criptomoneda con Python

Desarrollo de una criptomoneda con Python con fines didácticos, asociado al TFM "Tendencias actuales en la implementación de criptodivisas" para conocer cómo se pueden implementar los conceptos básicos que subyacen sobre la tecnología Blockchain y las criptomonedas, su principal aplicación hoy en día.

## Versiones

### v 0.1
- Implementación básica de una lista de datos (cadena)
- Implementación básica del proceso de minado de nuevos bloques
- Implementación básica de obtención de un hash a partir de un bloque

### v 0.2
- Implementación básica de la lógica para analizar y verificar la cadena de datos, así como detectar cadenas inválidas.
- Mejora del proceso de minado, añadiendo una interfaz de usuario mediante la cual el usuario puede de forma dinámica añadir nuevos elementos, imprimir la blockchain completa, etc.

### v 0.3
- Manejo de transacciones con remitente/destinatario.
- Mejora de la cadena de datos, donde ahora se trabaja con bloques que son capaces de: 
	- reconocer al bloque predecesor a través de su hash calculado mediante la implementación básica.
	- mantener una lista de transacciones pendientes.
- Mejora del proceso de minado ofreciendo una recompensa en monedas a los mineros.
- Mejora del proceso del cálculo del hash, obteniéndose ahora una representación en forma de cadena de caracteres de un bloque.
- Mejora del proceso de análisis y verificación de la cadena, añadiendo el cálculo de saldos que se incluye como medida de verificación, comparando la cantidad de monedas a transferir con el saldo del remitente, para determinar si una transacción puede o no llevarse a cabo.


## Autores

- [@navasdamas](https://github.com/navasdamas)

