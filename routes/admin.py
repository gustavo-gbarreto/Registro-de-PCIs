import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps

# Importações para o banco de dados
from extensions import db
from models import PCI

admin_route = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Você não tem permissão para aceder a esta página.', 'danger')
            return redirect(request.referrer or url_for('cliente.lista_lotes'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTA DE LEITURA (Read) ---
@admin_route.route('/')
@login_required
@admin_required
def lista_lotes_admin():
    # Busca todos os itens da tabela PCI, ordenados pelo ID
    todos_os_itens = PCI.query.order_by(PCI.id).all()
    return render_template('lotes.html', pci_list=todos_os_itens)

# --- ROTAS DE CRIAÇÃO (Create) ---
@admin_route.route('/new', methods=['POST'])
@login_required
@admin_required
def cadastro_lotes():
    data = request.get_json()
    
    # Validação de campos obrigatórios no backend
    required_fields = ['lote_id', 'serial_number', 'data_de_montagem', 'resultado_do_teste']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'O campo obrigatório "{field}" está em falta.'}), 400

    if data.get('resultado_do_teste') == 'Aprovada' and not data.get('tecnico_do_teste'):
        return jsonify({'success': False, 'message': 'Para itens aprovados, o campo "Técnico do Teste" é obrigatório.'}), 400


    serial_number = data.get('serial_number')
    if PCI.query.filter_by(serial_number=serial_number).first():
        return jsonify({'success': False, 'message': f'O Serial Number "{serial_number}" já existe.'}), 409

    try:
        data_montagem = datetime.strptime(data.get('data_de_montagem'), '%Y-%m-%d').date()
        novo_item = PCI(
            lote_id=data.get('lote_id'),
            serial_number=serial_number,
            data_de_montagem=data_montagem,
            resultado_do_teste=data.get('resultado_do_teste'),
            tecnico_do_teste=data.get('tecnico_do_teste'),
            retrabalho=data.get('retrabalho'),
            tecnico_do_retrabalho=data.get('tecnico_do_retrabalho'),
            observacoes=data.get('observacoes')
        )
        db.session.add(novo_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Novo item adicionado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao salvar no banco de dados: {e}'}), 500

@admin_route.route('/upload_csv', methods=['POST'])
@login_required
@admin_required
def upload_csv():
    if 'csv_file' not in request.files or not request.files['csv_file'].filename:
        flash('Nenhum ficheiro selecionado.', 'warning')
        return redirect(url_for('admin.lista_lotes_admin'))

    file = request.files['csv_file']
    if not file or not file.filename.endswith('.csv'):
        flash('Formato de ficheiro inválido. Por favor, envie um ficheiro .csv.', 'danger')
        return redirect(url_for('admin.lista_lotes_admin'))

    try:
        existing_serials = {p.serial_number for p in PCI.query.all()}
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        novos_itens = []
        for row in csv_reader:
            serial_number = row.get('serial_number') or row.get('Serial_Number')
            if not serial_number or serial_number in existing_serials:
                flash(f'Item com Serial Number "{serial_number}" foi ignorado (em branco ou duplicado).', 'warning')
                continue
            
            data_str = row.get('data_de_montagem') or row.get('Data_de_Montagem')
            data_montagem = None
            if data_str:
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                    try:
                        data_montagem = datetime.strptime(data_str, fmt).date()
                        break
                    except ValueError:
                        pass
            
            novo_item = PCI(
                lote_id=row.get('lote_id') or row.get('Lote_ID'),
                serial_number=serial_number,
                data_de_montagem=data_montagem,
                resultado_do_teste=row.get('resultado_do_teste') or row.get('Resultado_do_Teste'),
                tecnico_do_teste=row.get('tecnico_do_teste') or row.get('tecnico_do_teste'),
                retrabalho=row.get('retrabalho') or row.get('Retrabalho', 'Não'),
                tecnico_do_retrabalho=row.get('tecnico_do_retrabalho') or row.get('Tecnico_do_Retrabalho', 'N/A'),
                observacoes=row.get('observacoes') or row.get('Observacoes', '--')
            )
            novos_itens.append(novo_item)
            existing_serials.add(serial_number)

        if novos_itens:
            db.session.add_all(novos_itens)
            db.session.commit()
            flash(f'{len(novos_itens)} novos itens foram importados com sucesso!', 'success')
        else:
            flash('Nenhum item novo foi importado.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao processar o ficheiro: {e}', 'danger')
    
    return redirect(url_for('admin.lista_lotes_admin'))

# --- ROTAS DE ATUALIZAÇÃO (Update) ---
@admin_route.route('/<int:serial_id>/edit-form')
@login_required
@admin_required
def obter_pci_form(serial_id):
    item_para_editar = PCI.query.get_or_404(serial_id)
    return render_template('_edit_form.html', pci_dados=item_para_editar, pci_id=serial_id)

@admin_route.route('/<int:serial_id>/edit', methods=['PUT'])
@login_required
@admin_required
def editar_pci(serial_id):
    item_para_atualizar = PCI.query.get_or_404(serial_id)
    data = request.get_json()

    if data.get('resultado_do_teste') == 'Reprovada':
        if not data.get('retrabalho') or not data.get('tecnico_do_retrabalho'):
            return jsonify({'success': False, 'message': 'Para itens reprovados, "Retrabalho" e "Técnico" são obrigatórios.'}), 400

    for key, value in data.items():
        if hasattr(item_para_atualizar, key):
            setattr(item_para_atualizar, key, value)
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item atualizado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar: {e}'}), 500

# --- ROTA DE APAGAR (Delete) ---
@admin_route.route('/<int:serial_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def deletar_pci(serial_id):
    item_para_apagar = PCI.query.get_or_404(serial_id)
    try:
        db.session.delete(item_para_apagar)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500