from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, bcrypt, login_manager
from models import User
from flask_login import login_user, logout_user, login_required, current_user

# 1. Criar e configurar a App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-e-diferente-desta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:NMEL1234@localhost/registro_pci'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Inicializar as extensões com a App
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# 3. Configurar o LoginManager
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para aceder a esta página."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 4. Registar os Blueprints (rotas)
from routes.admin import admin_route
from routes.cliente import cliente_route
from routes.home import home_route
from routes.lotes import lotes_route

app.register_blueprint(home_route)
app.register_blueprint(admin_route, url_prefix='/admin')
app.register_blueprint(cliente_route, url_prefix='/cliente')
app.register_blueprint(lotes_route, url_prefix='/lotes')

# Rotas de Login/Logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_to_login = User.query.filter_by(username=username).first()

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