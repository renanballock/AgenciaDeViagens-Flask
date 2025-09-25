from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="cliente")  # cliente ou admin

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    vagas = db.Column(db.Integer, default=10)
    preco = db.Column(db.Float, nullable=False)

    reservas = db.relationship('Reservation', backref='pacote', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    pacote_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
