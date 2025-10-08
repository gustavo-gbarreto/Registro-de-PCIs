from flask import Blueprint, render_template
from database.PCI_list import PCI
from flask_login import login_required # Importe o decorador

cliente_route = Blueprint('cliente', __name__)

@cliente_route.route('/')
@login_required # Adicione esta linha para proteger a rota
def lista_lotes():
    return render_template("lotes.html", pci_list=PCI)