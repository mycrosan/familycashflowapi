from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Responsavel(db.Model):
    __tablename__ = 'responsavel'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum('entrada', 'saida'), nullable=False)

class Recorrencia(db.Model):
    __tablename__ = 'recorrencia'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.Enum('diario', 'semanal', 'mensal', 'anual'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=True)
    quantidade_ocorrencias = db.Column(db.Integer, nullable=True)
    intervalo = db.Column(db.Integer, default=1)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Lancamento(db.Model):
    __tablename__ = 'lancamento'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.Enum('entrada', 'saida'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('responsavel.id'), nullable=False)
    observacoes = db.Column(db.Text)
    recorrente = db.Column(db.Boolean, default=False)
    recorrencia_id = db.Column(db.Integer, db.ForeignKey('recorrencia.id'))

    categoria = db.relationship('Categoria')
    responsavel = db.relationship('Responsavel')
    recorrencia = db.relationship('Recorrencia')
