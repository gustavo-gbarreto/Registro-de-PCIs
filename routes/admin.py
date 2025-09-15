from flask import Blueprint, render_template

admin_route = Blueprint('admin', __name__)

"""
 -/admin/ (GET) - Lista os lotes cadastrados
 -/admin/new (POST) - Cadastrar um novo lote(precisa de permissão especial)
 -/admin/lote_id (GET) - Detalhes do lote específico
 -/admin/lote_id (DELETE) - Deletar um lote específico(precisa de permissão especial)
 -/admin/lote_id/serial_id (GET) - detalhe de uma PCI especiífica
 -/admin/lote_id/serial_id/edit (PUT) - editar uma PCI específica(precisa de permissão especial)
 -/admin/lote_id/serial_id/delete (DELETE) - deletar uma PCI específica(precisa de permissão especial)
"""

@admin_route.route('/')
def lista_lotes():
    pass
    return render_template('lotes.html')

@admin_route.route('/new', methods=['POST'])
def cadastro_lotes():
    render_template('lote_form.html')
    pass

@admin_route.route('/<string:lote_id>')
def obter_lote():
    pass

@admin_route.route('/<string:lote_id>', methods=['DELETE'])
def deletar_lote():
    pass

@admin_route.route('/<string:lote_id>/<string:serial_id>')
def obter_pci():
    return render_template('detalhe_lote.html')
    pass

@admin_route.route('/<string:lote_id>/<string:serial_id>/edit', methods=['PUT'])
def editar_pci():
    pass

@admin_route.route('/<string:lote_id>/<string:serial_id>/delete', methods=['DELETE'])
def deletar_pci():
    pass


    return render_template('index.html')