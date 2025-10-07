from flask import Blueprint, render_template, jsonify, request
from database.PCI_list import PCI
import json

admin_route = Blueprint('admin', __name__)

def salvar_dados_no_arquivo():
    """
    Salva o estado atual do dicionário PCI de volta no arquivo.
    """
    with open('database/PCI_list.py', 'w', encoding='utf-8') as f:
        f.write("PCI = ")
        f.write(json.dumps(PCI, indent=4, ensure_ascii=False))

@admin_route.route('/')
def lista_lotes_admin():
    return render_template('lotes.html', pci_list=PCI)

@admin_route.route('/new', methods=['POST'])
def cadastro_lotes():
    novo_item_dados = request.get_json()
    novo_serial_number = novo_item_dados.get('Serial_Number')

    for item in PCI.values():
        if item.get('Serial_Number') == novo_serial_number:
            mensagem_erro = f'O Serial Number "{novo_serial_number}" já existe. A criação foi cancelada.'
            return jsonify({'success': False, 'message': mensagem_erro}), 409

    if PCI:
        ultimo_id = max(int(k) for k in PCI.keys())
        novo_id = str(ultimo_id + 1)
    else:
        novo_id = '1'
    
    PCI[novo_id] = novo_item_dados
    salvar_dados_no_arquivo()

    return jsonify({'success': True, 'message': 'Novo item adicionado com sucesso'}), 200

# --- ROTA CORRIGIDA AQUI ---
# A rota agora espera receber APENAS o 'serial_id', exatamente como o template envia.
@admin_route.route('/<string:serial_id>/edit-form')
def obter_pci_form(serial_id):
    if serial_id in PCI:
        pci_data = PCI[serial_id]
        return render_template('_edit_form.html', pci_dados=pci_data, pci_id=serial_id)
    return "PCI não encontrada", 404

# A rota para salvar a edição também foi ajustada para receber apenas 'serial_id'.
@admin_route.route('/<string:serial_id>/edit', methods=['PUT'])
def editar_pci(serial_id):
    if serial_id in PCI:
        dados_atualizados = request.get_json()
        PCI[serial_id].update(dados_atualizados)
        salvar_dados_no_arquivo()
        return jsonify({'success': True, 'message': 'PCI atualizada com sucesso'}), 200
    return jsonify({'success': False, 'message': 'PCI não encontrada'}), 404

@admin_route.route('/<string:lote_id>/<string:serial_id>/delete', methods=['DELETE'])
def deletar_pci(lote_id, serial_id):
    if serial_id in PCI:
        del PCI[serial_id]
        itens_restantes = sorted(PCI.items(), key=lambda item: int(item[0]))
        pci_reindexado = {}
        novo_id = 1
        for chave_antiga, valor in itens_restantes:
            pci_reindexado[str(novo_id)] = valor
            novo_id += 1
        PCI.clear()
        PCI.update(pci_reindexado)
        salvar_dados_no_arquivo()
        return jsonify({'success': True, 'message': 'PCI deletada e re-indexada com sucesso'}), 200
    else:
        return jsonify({'success': False, 'message': 'PCI não encontrada'}), 404