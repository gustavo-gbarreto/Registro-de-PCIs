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
    return render_template('index.html')

@cliente_route.route('/<char:lote_id>')
def obter_lote():
    pass

@cliente_route.route('/<char:lote_id>/<char:serial_id>')
def obter_pci():
    pass

    return render_template('index.html')