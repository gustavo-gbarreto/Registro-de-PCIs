from extensions import db  # <-- Importa do novo ficheiro central
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(80), nullable=False)

class PCI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    data_de_montagem = db.Column(db.Date, nullable=True)
    resultado_do_teste = db.Column(db.String(50), nullable=True)
    tecnico_do_teste = db.Column(db.String(100), nullable=True)
    retrabalho = db.Column(db.String(50), nullable=True)
    tecnico_do_retrabalho = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

class Lote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    import_date = db.Column(db.DateTime, server_default=db.func.now())