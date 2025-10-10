import csv
import io
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from database.PCI_list import PCI
from flask_login import login_required, current_user
from functools import wraps
import json

admin_route = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Você não tem permissão para aceder a esta página.', 'danger')
            return redirect(request.referrer or url_for('cliente.lista_lotes'))
        return f(*args, **kwargs)
    return decorated_function

def salvar_dados_no_arquivo():
    with open('database/PCI_list.py', 'w', encoding='utf-8') as f:
        f.write("PCI = ")
        f.write(json.dumps(PCI, indent=4, ensure_ascii=False))

@admin_route.route('/')
@login_required
@admin_required
def lista_lotes_admin():
    return render_template('lotes.html', pci_list=PCI)

@admin_route.route('/new', methods=['POST'])
@login_required
@admin_required
def cadastro_lotes():
    novo_item_dados = request.get_json()
    novo_serial_number = novo_item_dados.get('Serial_Number')
    for item in PCI.values():
        if item.get('Serial_Number') == novo_serial_number:
            return jsonify({'success': False, 'message': f'O Serial Number "{novo_serial_number}" já existe.'}), 409
    if PCI:
        ultimo_id = max(int(k) for k in PCI.keys())
        novo_id = str(ultimo_id + 1)
    else: novo_id = '1'
    PCI[novo_id] = novo_item_dados
    salvar_dados_no_arquivo()
    return jsonify({'success': True, 'message': 'Novo item adicionado com sucesso'}), 200

@admin_route.route('/upload_csv', methods=['POST'])
@login_required
@admin_required
def upload_csv():
    if 'csv_file' not in request.files or request.files['csv_file'].filename == '':
        flash('Nenhum ficheiro selecionado.', 'warning')
        return redirect(url_for('admin.lista_lotes_admin'))
    file = request.files['csv_file']
    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            csv_reader = csv.DictReader(stream)
            existing_serials = {item['Serial_Number'] for item in PCI.values()}
            ultimo_id = max((int(k) for k in PCI.keys()), default=0)
            novos_itens_count = 0
            for row in csv_reader:
                serial_number = row.get('Serial_Number')
                if not serial_number or serial_number in existing_serials:
                    flash(f'Item com Serial Number "{serial_number}" foi ignorado (em branco ou duplicado).', 'warning')
                    continue
                ultimo_id += 1; novo_id = str(ultimo_id)
                PCI[novo_id] = {
                    "Lote_ID": row.get("Lote_ID", ""),"Serial_Number": serial_number,
                    "Data_de_Montagem": row.get("Data_de_Montagem", ""),"Resultado_do_Teste": row.get("Resultado_do_Teste", "Não Testado"),
                    "tecnico_do_teste": row.get("tecnico_do_teste", "N/A"),"Retrabalho": row.get("Retrabalho", "Não"),
                    "Tecnico_do_Retrabalho": row.get("Tecnico_do_Retrabalho", "N/A"),"Observacoes": row.get("Observacoes", "--")
                }
                existing_serials.add(serial_number)
                novos_itens_count += 1
            if novos_itens_count > 0:
                salvar_dados_no_arquivo()
                flash(f'{novos_itens_count} novos itens foram importados com sucesso!', 'success')
            else: flash('Nenhum item novo foi importado. Verifique o seu ficheiro.', 'info')
        except Exception as e: flash(f'Ocorreu um erro ao processar o ficheiro: {e}', 'danger')
        return redirect(url_for('admin.lista_lotes_admin'))
    else:
        flash('Formato de ficheiro inválido. Por favor, envie um ficheiro .csv.', 'danger')
        return redirect(url_for('admin.lista_lotes_admin'))

@admin_route.route('/<string:serial_id>/edit-form')
@login_required
@admin_required
def obter_pci_form(serial_id):
    if serial_id in PCI:
        pci_data = PCI[serial_id]
        return render_template('_edit_form.html', pci_dados=pci_data, pci_id=serial_id)
    return "PCI não encontrada", 404

@admin_route.route('/<string:serial_id>/edit', methods=['PUT'])
@login_required
@admin_required
def editar_pci(serial_id):
    if serial_id in PCI:
        dados_atualizados = request.get_json()
        PCI[serial_id].update(dados_atualizados)
        salvar_dados_no_arquivo()
        return jsonify({'success': True, 'message': 'PCI atualizada com sucesso'}), 200
    return jsonify({'success': False, 'message': 'PCI não encontrada'}), 404

@admin_route.route('/<string:lote_id>/<string:serial_id>/delete', methods=['DELETE'])
@login_required
@admin_required
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