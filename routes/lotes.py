import os
import csv
import io
import datetime
import json
import importlib.util
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from routes.admin import admin_required

lotes_route = Blueprint('lotes', __name__)

DATABASE_DIR = 'database'
EXCLUDED_FILES = ['PCI_list.py', 'user_database.py', '__init__.py']

@lotes_route.route('/')
@login_required # Clientes e Admins podem ver a lista
def listar_lotes():
    lote_files_info = []
    try:
        all_files = os.listdir(DATABASE_DIR)
        for filename in sorted(all_files):
            if filename.endswith('.py') and filename not in EXCLUDED_FILES:
                filepath = os.path.join(DATABASE_DIR, filename)
                mod_time = os.path.getmtime(filepath)
                mod_date = datetime.datetime.fromtimestamp(mod_time).strftime('%d-%m-%Y %H:%M:%S')
                lote_files_info.append({'name': filename, 'date': mod_date})
    except FileNotFoundError:
        flash("O diretório 'database' não foi encontrado.", 'danger')
    return render_template('lista_lotes.html', lotes=lote_files_info)

@lotes_route.route('/upload_lote', methods=['POST'])
@login_required
@admin_required # Apenas admins podem criar lotes
def upload_lote():
    if 'csv_file' not in request.files or request.files['csv_file'].filename == '':
        flash('Nenhum ficheiro selecionado.', 'warning')
        return redirect(url_for('lotes.listar_lotes'))

    file = request.files['csv_file']

    if file and file.filename.endswith('.csv'):
        try:
            base_filename = os.path.splitext(file.filename)[0].replace(' ', '_').lower()
            new_py_filename = f"{base_filename}.py"
            new_filepath = os.path.join(DATABASE_DIR, new_py_filename)

            if os.path.exists(new_filepath):
                flash(f'Um lote com o nome "{new_py_filename}" já existe. Por favor, renomeie o ficheiro CSV e tente novamente.', 'danger')
                return redirect(url_for('lotes.listar_lotes'))

            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            lote_data = {}
            item_id = 1
            for row in csv_reader:
                lote_data[str(item_id)] = row
                item_id += 1

            if not lote_data:
                flash('O ficheiro CSV está vazio ou em formato incorreto.', 'warning')
                return redirect(url_for('lotes.listar_lotes'))

            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write("LOTE_DATA = ")
                f.write(json.dumps(lote_data, indent=4, ensure_ascii=False))

            flash(f'O lote "{new_py_filename}" foi criado com sucesso com {len(lote_data)} itens!', 'success')

        except (OSError, csv.Error, UnicodeDecodeError) as e:
            flash(f'Ocorreu um erro ao processar o ficheiro: {e}', 'danger')
        
        return redirect(url_for('lotes.listar_lotes'))

    else:
        flash('Formato de ficheiro inválido. Por favor, envie um ficheiro .csv.', 'danger')
        return redirect(url_for('lotes.listar_lotes'))

@lotes_route.route('/<string:lote_filename>')
@login_required # Clientes e Admins podem ver os detalhes
def detalhe_lote(lote_filename):
    if not lote_filename.endswith('.py') or lote_filename in EXCLUDED_FILES or '..' in lote_filename:
        flash("Nome de lote inválido ou acesso não permitido.", "danger")
        return redirect(url_for('lotes.listar_lotes'))

    filepath = os.path.join(DATABASE_DIR, lote_filename)

    if not os.path.exists(filepath):
        flash(f"O lote '{lote_filename}' não foi encontrado.", "danger")
        return redirect(url_for('lotes.listar_lotes'))

    try:
        spec = importlib.util.spec_from_file_location(lote_filename, filepath)
        lote_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lote_module)
        lote_data = lote_module.LOTE_DATA
    
    except (AttributeError, ImportError) as e:
        flash(f"Não foi possível ler os dados do lote '{lote_filename}'. Verifique o formato do ficheiro. Erro: {e}", "danger")
        return redirect(url_for('lotes.listar_lotes'))
    
    return render_template('detalhe_lote.html', lote_data=lote_data, filename=lote_filename)

@lotes_route.route('/<string:lote_filename>/delete', methods=['DELETE'])
@login_required
@admin_required # Apenas admins podem apagar
def apagar_lote(lote_filename):
    if not lote_filename.endswith('.py') or lote_filename in EXCLUDED_FILES or '..' in lote_filename:
        return jsonify({'success': False, 'message': 'Nome de ficheiro inválido.'}), 400

    filepath = os.path.join(DATABASE_DIR, lote_filename)

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            flash(f'O lote "{lote_filename}" foi apagado com sucesso.', 'success')
            return jsonify({'success': True}), 200
        except OSError as e:
            flash(f'Não foi possível apagar o lote. Erro: {e}', 'danger')
            return jsonify({'success': False, 'message': str(e)}), 500
    else:
        return jsonify({'success': False, 'message': 'Lote não encontrado.'}), 404