from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Apenas criamos as instâncias aqui, sem inicializar.
# Este ficheiro serve como uma fonte central e neutra.
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()