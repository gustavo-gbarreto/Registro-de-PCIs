from flask import Blueprint, render_template

cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
def listaPCI():
    pass
    return render_template('index.html')

@cliente_route.route('/<char:lote_id>')
def obter_PCI():
    pass
