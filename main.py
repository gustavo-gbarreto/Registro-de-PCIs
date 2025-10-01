from flask import Flask
from database.PCI_list import PCI
from routes.home import home_route
from routes.cliente import cliente_route
from routes.admin import admin_route

#inicializando o flask
app = Flask(__name__)

#definiçâo das rotas
app.register_blueprint(home_route)
app.register_blueprint(cliente_route,url_prefix='/cliente')
app.register_blueprint(admin_route,url_prefix='/admin')


app.run(debug=True)
