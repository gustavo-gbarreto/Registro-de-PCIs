import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import json

# Importações para o banco de dados
from extensions import db
from models import PCI

admin_route = Blueprint('admin', __name__)

# O decorador e a função de salvar (que agora é obsoleta)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Você não tem permissão para aceder a esta página.', 'danger')
            return redirect(request.referrer or url_for('cliente.lista_lotes'))
        return f(*args, **kwargs)
    return decorated_function

# Esta função já não é necessária, pois o db.session.commit() faz o trabalho de salvar.
# def salvar_dados_no_arquivo():
#     ...

@admin_route.route('/')
@login_required
@admin_required
def lista_lotes_admin():
    todos_os_itens = PCI.query.all()
    return render_template('lotes.html', pci_list=todos_os_itens)

# --- INÍCIO DA REATORAÇÃO: Rota de Cadastro Manual ---
@admin_route.route('/new', methods=['POST'])
@login_required
@admin_required
def cadastro_lotes():
    data = request.get_json()
    serial_number = data.get('serial_number')

    # Validação: Verifica se o Serial Number já existe no banco de dados
    if PCI.query.filter_by(serial_number=serial_number).first():
        return jsonify({'success': False, 'message': f'O Serial Number "{serial_number}" já existe.'}), 409

    try:
        # Converte a data de string para objeto date, se ela existir
        data_montagem = None
        if data.get('data_de_montagem'):
            data_montagem = datetime.strptime(data.get('data_de_montagem'), '%Y-%m-%d').date()

        # Cria um novo objeto PCI com os dados do formulário
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

        # Adiciona o novo item à sessão e salva no banco de dados
        db.session.add(novo_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Novo item adicionado com sucesso'}), 200
    except Exception as e:
        db.session.rollback() # Desfaz a transação em caso de erro
        return jsonify({'success': False, 'message': f'Erro ao salvar no banco de dados: {e}'}), 500
# --- FIM DA REATORAÇÃO ---


# --- INÍCIO DA REATORAÇÃO: Rota de Upload de CSV ---
@admin_route.route('/upload_csv', methods=['POST'])
@login_required
@admin_required
def upload_csv():
    if 'csv_file' not in request.files or not request.files['csv_file'].filename:
        flash('Nenhum ficheiro selecionado.', 'warning')
        return redirect(url_for('admin.lista_lotes_admin'))

    file = request.files['csv_file']

    if file and file.filename.endswith('.csv'):
        try:
            # Busca todos os serial numbers existentes no DB de uma só vez para otimização
            existing_serials = {p.serial_number for p in PCI.query.all()}
            
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            novos_itens_count = 0
            for row in csv_reader:
                serial_number = row.get('serial_number') or row.get('Serial_Number')
                
                # Validação: ignora se não tiver serial number ou se for duplicado
                if not serial_number or serial_number in existing_serials:
                    flash(f'Item com Serial Number "{serial_number}" foi ignorado (em branco ou duplicado).', 'warning')
                    continue
                
                data_montagem = None
                if row.get('data_de_montagem') or row.get('Data_de_Montagem'):
                    data_str = row.get('data_de_montagem') or row.get('Data_de_Montagem')
                    # Tenta múltiplos formatos de data comuns
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
                db.session.add(novo_item)
                existing_serials.add(serial_number) # Adiciona à verificação para duplicados dentro do mesmo ficheiro
                novos_itens_count += 1

            if novos_itens_count > 0:
                db.session.commit() # Salva todos os novos itens no DB de uma só vez
                flash(f'{novos_itens_count} novos itens foram importados com sucesso!', 'success')
            else:
                flash('Nenhum item novo foi importado. Verifique os Serial Numbers no seu ficheiro.', 'info')

        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao processar o ficheiro: {e}', 'danger')
        
        return redirect(url_for('admin.lista_lotes_admin'))

    else:
        flash('Formato de ficheiro inválido. Por favor, envie um ficheiro .csv.', 'danger')
        return redirect(url_for('admin.lista_lotes_admin'))
# --- FIM DA REATORAÇÃO ---


# As rotas de Editar e Apagar ainda usam a lógica antiga e serão as próximas a serem refatoradas
@admin_route.route('/<int:serial_id>/edit-form')
@login_required
@admin_required
def obter_pci_form(serial_id):
    # (Esta função será refatorada no próximo passo)
    pass 

@admin_route.route('/<int:serial_id>/edit', methods=['PUT'])
@login_required
@admin_required
def editar_pci(serial_id):
    # (Esta função será refatorada no próximo passo)
    pass

@admin_route.route('/<int:serial_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def deletar_pci(serial_id):
    # (Esta função já está correta da nossa última modificação)
    item_para_apagar = PCI.query.get(serial_id)
    if item_para_apagar:
        db.session.delete(item_para_apagar)
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'message': 'Item não encontrado.'}), 404