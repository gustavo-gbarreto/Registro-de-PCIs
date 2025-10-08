from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

home_route = Blueprint('home', __name__)

@home_route.route('/')
def home():
    # Se o utilizador já estiver autenticado
    if current_user.is_authenticated:
        # Encaminha para a página de admin se a função for 'admin'
        if current_user.role == 'admin':
            return redirect(url_for('admin.lista_lotes_admin'))
        # Senão, encaminha para a página do cliente
        else:
            return redirect(url_for('cliente.lista_lotes'))
    
    # Se não estiver autenticado, encaminha para a página de login
    return redirect(url_for('login'))