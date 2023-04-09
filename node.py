from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_node_ui():
    """
    Este método sirve la interfaz de usuario HTML para el nodo actual.
    Devuelve el archivo node.html ubicado en el directorio "ui", que permite al usuario
    interactuar con el nodo a través de una interfaz web.
    """
    return send_from_directory('ui', 'node.html')


@app.route('/network', methods=['GET'])
def get_network_ui():
    """
    Devuelve la página HTML Network desde el directorio 'ui'. La cual implementa una
    interfaz web para gestionar la red de nodos conectados a la blockchain.
    """
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    """
    Crea un nuevo par de claves pública y privada para el monedero, lo guarda e inicializa
    una nueva blockchain con la clave pública. 
    """
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    """
    Carga las claves pública y privada del monedero e inicializa una nueva instancia de
    la blockchain con la clave pública cargada y el identificador del nodo especificado.
    Si las claves se han cargado correctamente, devuelve una respuesta JSON con la clave pública,
    la clave privada y el saldo actual del monedero. En caso contrario, devuelve una respuesta
    JSON indicando que la carga de claves falló.
    """
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Error al cargar las llaves.'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    """
    Este endpoint devuelve el saldo actual del monedero asociado a la blockchain.
    Devuelve un objeto JSON que contiene un mensaje y el saldo calculado.
    """
    balance = blockchain.get_balance()
    if balance is not None:
        response = {
            'message': 'Saldo obtenido con éxito.',
            'funds': balance
        }
        return jsonify(response), 200

    response = {
        'messsage': 'Error al obtener el saldo.',
        'wallet_set_up': wallet.public_key is not None
    }
    return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    """
    Difunde una transacción a otros nodos de la red. Devuelve una respuesta
    con un mensaje que indica si la transacción se ha añadido correctamente o no.

    Datos de la solicitud POST:
    - sender (str): clave pública del remitente
    - recipient (cadena): clave pública del destinatario
    - amount (float): cantidad de criptomoneda que se transfiere
    - signature (str): firma digital de la transacción

    Devuelve:
    - message (str): mensaje que indica si la transacción se ha añadido correctamente o no
    - transaction (dict): diccionario que contiene la información de la transacción
      - sender (str): clave pública del remitente
      - recipient (cadena): clave pública del destinatario
      - amount (float): cantidad de criptomoneda que se transfiere
      - signature (str): firma digital de la transacción
    """
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    """
    Este endpoint recibe un nuevo bloque añadido por algún otro nodo de la red
    y lo añade a la copia local de la blockchain si es válido.

    El método recibe un objeto JSON que contiene el nuevo bloque en el campo
    'block'. El bloque se añade a la blockchain si tiene el índice correcto,
    y se valida su contenido. Si el índice del nuevo bloque es mayor que el
    de la cadena local, el método establece una bandera para resolver conflictos
    con los demás nodos de la red. Si el índice del bloque es menor o igual que
    la cadena local, se rechaza.

    El método devuelve una respuesta JSON que indica si el bloque se ha añadido
    a la blockchain local o no, y el motivo.
    """
    values = request.get_json()
    if not values:
        response = {'message': 'No se han encontrado datos.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Faltan algunos datos.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Bloque añadido'}
            return jsonify(response), 201
        else:
            response = {'message': 'El bloque no parece válido.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'La blockchain parece diferir de la blockchain local.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            'message': 'La blockchain parece más corta, no se añaden bloques.'}
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():
    """
    Añade una transacción a la cadena de bloques.

    El remitente de la transacción es la clave pública del monedero configurado en este nodo.
    El destinatario y el importe de la transacción se toman de los datos de la solicitud.
    La transacción se firma utilizando la clave privada del monedero. La transacción se añade
    a la lista de transacciones abiertas.

    Devuelve una respuesta con los detalles de la transacción añadida, junto con el saldo
    actual del monedero.

    Si el monedero no ha sido configurado en este nodo, se devuelve una respuesta de error 400.
    Si faltan los campos requeridos (destinatario e importe) en los datos de la solicitud,
    se devuelve una respuesta de error 400. Si hay un error al añadir la transacción al blockchain,
    se devuelve una respuesta de error 500.
    """
    if wallet.public_key is None:
        response = {
            'message': 'Sin monedero configurado.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No se han encontrado datos.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Faltan datos obligatorios.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Transacción añadida correctamente.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Error al crear una transacción.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    """
    Este endpoint permite a un usuario minar un nuevo bloque en la blockchain.

    Si hay conflictos sin resolver en la blockchain, la función devuelve un código
    de estado 409 Conflict con un mensaje que indica que hay conflictos que deben
    resolverse.

    Si la operación de minado del bloque se realiza correctamente, la función devuelve
    un código de estado 201 Created con un mensaje que indica que el bloque se ha añadido
    correctamente, junto con la información del nuevo bloque y el saldo actual del usuario.

    Si la extracción del bloque falla por cualquier motivo, la función devuelve un código
    de estado 500 Internal Server Error con un mensaje que indica que el bloque no se ha
    podido añadir y si el monedero del usuario está configurado.
    """
    if blockchain.resolve_conflicts:
        response = {
            'message': 'Resolver conflictos pendientes, bloque no añadido!'}
        return jsonify(response), 409
    block = blockchain.mine_block()
    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Bloque añadido correctamente.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Fallo al añadir un bloque.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    """
    Este endpoint permite al usuario resolver conflictos en la blockchain.

    Si hay conflictos que resolver, la función llama al método resolve() de la blockchain,
    que compara el blockchain local con el blockchain de la red y reemplaza el blockchain
    local si es necesario. es necesario. A continuación, la función devuelve un código de
    estado 200 OK con un mensaje que indica si el blockchain local local fue reemplazada o no.

    Si no hay conflictos que resolver, la función devuelve un código de estado 200 OK con un
    mensaje indicando que la copia local del blockchain se mantuvo.
    """
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Se sustituyó la blockchain!'}
    else:
        response = {
            'message': 'Se ha mantenido la copia local de la blockchain!'}
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    """
    Este endpoint permite a un usuario recuperar una lista de transacciones pendientes 
    en la blockchain.

    La función llama al método get_open_transactions() del blockchain para recuperar una lista de
    todas las transacciones que aún no están incluidas en ningún bloque. A continuación,
    la función crea un diccionario de cada transacción y la devuelve como una respuesta JSON
    con un código de estado 200 OK.
    """
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Este endpoint permite al usuario recuperar una instantánea de la copia local de la blockchain.

    La función llama a la propiedad chain del blockchain para recuperar una lista de todos los
    bloques del blockchain. A continuación, crea una representación de diccionario de cada bloque,
    incluyendo las transacciones del bloque.

    Por último, la función devuelve una respuesta JSON con un código de estado 200 OK que contiene
    la lista de bloques de la cadena junto con sus respectivas transacciones.
    """
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    """
    Este endpoint permite a un usuario añadir un nuevo nodo a la red.

    La función comprueba primero si la solicitud contiene los campos necesarios. Si no es así,
    devuelve un código de estado 400 Bad Request con un mensaje de error.

    Si la solicitud es válida, la función recupera el nuevo nodo de los datos JSON de la solicitud
    y lo añade a la lista de nodos de la blockchain mediante el método add_peer_node().
    A continuación, la función devuelve una respuesta JSON con un código de estado 201 Created que
    contiene un mensaje de éxito y una lista de todos los nodos de la red.
    """
    values = request.get_json()
    if not values:
        response = {
            'message': 'No se adjuntan datos.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No se han encontrado datos del nodo.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Nodo añadido correctamente.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    """
    Este endpoint permite a un usuario eliminar un nodo par de la red.

    La función comprueba primero si el parámetro URL del nodo es válido. Si no lo es, devuelve un
    código de estado 400 Bad Request con un mensaje de error.

    Si la URL del nodo es válida, la función elimina el nodo de la lista de nodos pares de la
    blockchain utilizando el método remove_peer_node(). A continuación, la función devuelve una
    respuesta JSON con un código de estado 200 OK que contiene un mensaje de éxito y una lista de
    todos los nodos de la red.
    """
    if node_url == '' or node_url is None:
        response = {
            'message': 'No se ha encontrado ningún nodo.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Nodo eliminado',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    """
    Este endpoint permite al usuario recuperar una lista de todos los nodos de la red.

    La función llama al método get_peer_nodes() de la blockchain para recuperar una lista de
    todos los nodos pares de la red y, a continuación, devuelve una respuesta JSON con un código
    de estado 200 OK que contiene la lista de todos los nodos de la red.
    """
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5001)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)
