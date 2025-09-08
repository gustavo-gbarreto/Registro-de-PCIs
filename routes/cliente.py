from flask import Blueprint, render_template

cliente_route = Blueprint('cliente', __name__)

"""
 -/cliente/ (GET) - Lista os lotes cadastrados
 -/cliente/new (POST) - Cadastrar um novo lote(precisa de permissão especial)
 -/cliente/lote_id (GET) - Detalhes do lote específico
 -/cliente/lote_id/serial_id (GET) - detalhe de uma PCI especiífica
 -/cliente/lote_id/serial_id/edit (PUT) - editar uma PCI específica(precisa de permissão especial)
 -/cliente/lote_id/serial_id/delete (DELETE) - deletar uma PCI específica(precisa de permissão especial)
"""
@cliente_route.route('/')
def lista_lotes():
    pass
    return render_template('index.html')

@cliente_route.route('/new', methods=['POST'])
def cadastro_lotes():
    pass

@cliente_route.route('/<char:lote_id>')
def obter_lote():
    pass

@cliente_route.route('/<char:lote_id>/<char:serial_id>')
def obter_pci():
    pass

@cliente_route.route('/<char:lote_id>/<char:serial_id>/edit', methods=['PUT'])
def editar_pci():
    pass

@cliente_route.route('/<char:lote_id>/<char:serial_id>/delete', methods=['DELETE'])
def deletar_pci():
    pass


    return render_template('index.html')