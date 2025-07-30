from flask import Blueprint, request, jsonify
from models import db, Responsavel

responsavel_bp = Blueprint('responsavel', __name__)

@responsavel_bp.route("/", methods=["GET"])
def listar():
    dados = Responsavel.query.all()
    return jsonify([{"id": r.id, "nome": r.nome, "email": r.email, "telefone": r.telefone} for r in dados])

@responsavel_bp.route("/", methods=["POST"])
def criar():
    data = request.get_json()
    r = Responsavel(
        nome=data["nome"],
        email=data.get("email"),
        telefone=data.get("telefone")
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"id": r.id}), 201

@responsavel_bp.route("/<int:id>", methods=["GET"])
def obter(id):
    r = Responsavel.query.get_or_404(id)
    return jsonify({
        "id": r.id,
        "nome": r.nome,
        "email": r.email,
        "telefone": r.telefone
    })

@responsavel_bp.route("/<int:id>", methods=["PUT"])
def atualizar(id):
    r = Responsavel.query.get_or_404(id)
    data = request.get_json()
    r.nome = data.get("nome", r.nome)
    r.email = data.get("email", r.email)
    r.telefone = data.get("telefone", r.telefone)
    db.session.commit()
    return jsonify({"message": "Responsável atualizado com sucesso."})

@responsavel_bp.route("/<int:id>", methods=["DELETE"])
def deletar(id):
    r = Responsavel.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    return jsonify({"message": "Responsável excluído com sucesso."})
