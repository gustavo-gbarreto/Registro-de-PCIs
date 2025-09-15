from flask import Blueprint, render_template

cliente_route = Blueprint('cliente', __name__)

"""
 -/cliente/ (GET) - Lista os lotes cadastrados
 -/cliente/lote_id (GET) - Detalhes do lote específico
 -/cliente/lote_id/serial_id (GET) - detalhe de uma PCI especiífica
"""

@cliente_route.route('/')
def lista_lotes():
    pass
    return render_template('lotes.html')

@cliente_route.route('/<string:lote_id>')
def obter_lote(lote_id):
    return { 'lote especifico x'}
    pass


@cliente_route.route('/<string:lote_id>/<string:serial_id>')
def obter_pci():
    pass

    return render_template('index.html')