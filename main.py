from flask import Flask, render_template, request, redirect, url_for, flash
from routes.admin import admin_route
from routes.cliente import cliente_route
from routes.home import home_route
from routes.lotes import lotes_route
from database.user_database import users_db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-e-diferente-desta' 

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Por favor, faça login para aceder a esta página."

class User(UserMixin):
    def __init__(self, user_id, username, password_hash, role):
        self.id = user_id
        self.username = username
        self.password = password_hash
        self.role = role

users = {uid: User(user_id=uid, username=data['username'], password_hash=data['password'], role=data['role']) for uid, data in users_db.items()}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Registo de todos os blueprints da aplicação
app.register_blueprint(home_route)
app.register_blueprint(admin_route, url_prefix='/admin')
app.register_blueprint(cliente_route, url_prefix='/cliente')
app.register_blueprint(lotes_route, url_prefix='/lotes')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_to_login = None
        for u in users.values():
            if u.username == username:
                user_to_login = u
                break

        if user_to_login and bcrypt.check_password_hash(user_to_login.password, password):
            login_user(user_to_login)
            if user_to_login.role == 'admin':
                return redirect(url_for('admin.lista_lotes_admin'))
            else:
                return redirect(url_for('cliente.lista_lotes'))
        else:
            flash('Utilizador ou senha inválidos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)