# main.py (agora com o conteúdo correto)

from flask import Flask
# Certifique-se de que os caminhos de importação estão corretos
# Se você criou a pasta 'routes', o caminho será 'routes.admin', etc.
from routes.admin import admin_route
from routes.cliente import cliente_route
from routes.home import home_route

# 1. Cria a instância principal da aplicação
app = Flask(__name__)

# 2. Registra os blueprints na aplicação principal
#    Cada blueprint é um conjunto de rotas de um arquivo diferente.
app.register_blueprint(home_route)
app.register_blueprint(admin_route, url_prefix='/admin')
app.register_blueprint(cliente_route, url_prefix='/cliente')

# 3. Roda a aplicação (APENAS se este arquivo for executado diretamente)
if __name__ == '__main__':
    # O debug=True é ótimo para desenvolvimento, pois reinicia o servidor a cada alteração.
    app.run(debug=True)