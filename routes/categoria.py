from flask import Blueprint, request, jsonify
from models import db, Categoria

categoria_bp = Blueprint('categoria', __name__)

@categoria_bp.route("/", methods=["GET"])
def listar():
    categorias = Categoria.query.all()
    return jsonify([{"id": c.id, "nome": c.nome, "tipo": c.tipo} for c in categorias])

@categoria_bp.route("/", methods=["POST"])
def criar():
    data = request.get_json()
    c = Categoria(nome=data["nome"], tipo=data["tipo"])
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id}), 201

@categoria_bp.route("/<int:id>", methods=["GET"])
def obter(id):
    c = Categoria.query.get_or_404(id)
    return jsonify({"id": c.id, "nome": c.nome, "tipo": c.tipo})

@categoria_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    c = Categoria.query.get_or_404(id)
    data = request.get_json()
    c.nome = data.get("nome", c.nome)
    c.tipo = data.get("tipo", c.tipo)
    db.session.commit()
    return jsonify({"message": "Categoria atualizada com sucesso."})

@categoria_bp.route("/<int:id>", methods=["DELETE"])
def deletar(id):
    c = Categoria.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Categoria deletada com sucesso."})
