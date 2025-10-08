from flask import Flask, render_template, request, redirect, url_for, flash
from routes.admin import admin_route
from routes.cliente import cliente_route
from routes.home import home_route
from database.user_database import users_db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-aqui' 

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Por favor, faça login para acessar esta página."

class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password = password_hash
        self.role = role

users = {uid: User(uid, data['username'], data['password'], data['role']) for uid, data in users_db.items()}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

app.register_blueprint(home_route)
app.register_blueprint(admin_route, url_prefix='/admin')
app.register_blueprint(cliente_route, url_prefix='/cliente')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # --- INÍCIO DA DEPURAÇÃO ---
        print("\n--- Nova Tentativa de Login ---")
        print(f"Usuário digitado no formulário: '{username}'")
        print(f"Senha digitada no formulário: '{password}'")
        
        user_to_login = None
        for u in users.values():
            if u.username == username:
                user_to_login = u
                break
        
        print(f"Usuário encontrado no banco de dados: {user_to_login.username if user_to_login else 'Nenhum'}")

        if user_to_login:
            is_password_correct = bcrypt.check_password_hash(user_to_login.password, password)
            print(f"A senha está correta? {is_password_correct}")

            if is_password_correct:
                login_user(user_to_login)
                flash('Login realizado com sucesso!', 'success')
                print("--- Login BEM-SUCEDIDO ---\n")
                if user_to_login.role == 'admin':
                    return redirect(url_for('admin.lista_lotes_admin'))
                else:
                    return redirect(url_for('cliente.lista_lotes'))

        flash('Usuário ou senha inválidos.', 'danger')
        print("--- Login FALHOU ---\n")
        # --- FIM DA DEPURAÇÃO ---

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)