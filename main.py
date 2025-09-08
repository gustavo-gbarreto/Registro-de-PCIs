from flask import Flask
from routes.home import home_route

#inicializando o flask
app = Flask(__name__)

#definiçâo das rotas
app.register_blueprint(home_route)

app.run(debug=True)


