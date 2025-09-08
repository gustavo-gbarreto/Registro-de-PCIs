from flask import Blueprint, render_template

cliente_route = Blueprint('cliente', __name__)

"""
 -/cliente/lotes (GET) - Lista os lotes cadastrados
 -/cliente/lotes (POST) - Cadastrar um novo lote(precisa de permissão especial)
 -/cliente/lote_id (GET) - Detalhes do lote específico
 -/cliente/lote_id/serial_id (GET) - detalhe de uma PCI especiífica
 -/cliente/lote_id/serial_id/edit (PUT) - editar uma PCI específica(precisa de permissão especial)
 -/cliente/lote_id/serial_id/delete (DELETE) - deletar uma PCI específica(precisa de permissão especial)
"""
@cliente_route.route('/')
def listaPCI():
    pass
    return render_template('index.html')

@cliente_route.route('/<char:lote_id>')
def obter_PCI():
    pass
    