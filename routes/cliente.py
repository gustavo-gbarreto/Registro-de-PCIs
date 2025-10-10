from flask import Blueprint, render_template
from models import PCI
from flask_login import login_required

# Cria o Blueprint para as rotas do cliente
cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
@login_required
def lista_lotes():
    # A indentação aqui é feita com 4 espaços
    todos_os_itens = PCI.query.all()
    # Esta linha também, alinhada com a anterior
    return render_template("lotes.html", pci_list=todos_os_itens)