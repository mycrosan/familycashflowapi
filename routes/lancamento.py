from flask import Blueprint, request, jsonify
from models import db, Lancamento, Recorrencia
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange

lancamento_bp = Blueprint('lancamento', __name__)

# Função utilitária para gerar as datas da recorrência
def gerar_datas_recorrencia(tipo, inicio, fim=None, qtd=None, intervalo=1):
    datas = []
    atual = inicio
    while True:
        datas.append(atual)

        if qtd and len(datas) >= qtd:
            break
        if fim and atual > fim:
            break

        if tipo == 'diario':
            atual += relativedelta(days=intervalo)
        elif tipo == 'semanal':
            atual += relativedelta(weeks=intervalo)
        elif tipo == 'mensal':
            atual += relativedelta(months=intervalo)
        elif tipo == 'anual':
            atual += relativedelta(years=intervalo)
        else:
            break

        if fim and atual > fim:
            break

    return datas

# GET: listar lançamentos de um mês (reais + simulados)
@lancamento_bp.route("/mes/<string:ano_mes>", methods=["GET"])
def listar_lancamentos_do_mes(ano_mes):
    try:
        ano, mes = map(int, ano_mes.split("-"))
        inicio_mes = date(ano, mes, 1)
        fim_mes = date(ano, mes, monthrange(ano, mes)[1])

        lancamentos_unicos = Lancamento.query.filter(
            db.and_(
                Lancamento.recorrente == False,
                Lancamento.data >= inicio_mes,
                Lancamento.data <= fim_mes
            )
        ).all()

        recorrentes = Lancamento.query.filter(Lancamento.recorrente == True).all()
        simulados = []

        for lanc in recorrentes:
            rec = lanc.recorrencia
            if not rec:
                continue

            datas = gerar_datas_recorrencia(
                rec.tipo,
                rec.data_inicio,
                rec.data_fim,
                rec.quantidade_ocorrencias,
                rec.intervalo or 1
            )

            for d in datas:
                if d.year == ano and d.month == mes:
                    simulados.append({
                        "id": None,
                        "descricao": lanc.descricao,
                        "valor": float(lanc.valor),
                        "data": d.strftime("%Y-%m-%d"),
                        "tipo": lanc.tipo,
                        "categoria_id": lanc.categoria_id,
                        "responsavel_id": lanc.responsavel_id,
                        "observacoes": lanc.observacoes,
                        "recorrente": True,
                        "recorrencia_id": lanc.recorrencia_id,
                        "simulado": True
                    })

        reais = [{
            "id": l.id,
            "descricao": l.descricao,
            "valor": float(l.valor),
            "data": l.data.strftime("%Y-%m-%d"),
            "tipo": l.tipo,
            "categoria_id": l.categoria_id,
            "responsavel_id": l.responsavel_id,
            "observacoes": l.observacoes,
            "recorrente": l.recorrente,
            "recorrencia_id": l.recorrencia_id,
            "simulado": False
        } for l in lancamentos_unicos]

        return jsonify(reais + simulados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST: criar novo lançamento (com ou sem recorrência)
@lancamento_bp.route("/", methods=["POST"])
def criar_lancamento():
    try:
        data = request.get_json()

        lanc = Lancamento(
            descricao=data["descricao"],
            valor=float(data["valor"]),
            data=datetime.strptime(data["data"], "%Y-%m-%d"),
            tipo=data["tipo"],
            categoria_id=data["categoria_id"],
            responsavel_id=data["responsavel_id"],
            observacoes=data.get("observacoes"),
            recorrente=data.get("recorrente", False)
        )

        if lanc.recorrente and data.get("recorrencia"):
            r = data["recorrencia"]
            nova_rec = Recorrencia(
                tipo=r["tipo"],
                data_inicio=datetime.strptime(r["data_inicio"], "%Y-%m-%d"),
                data_fim=datetime.strptime(r["data_fim"], "%Y-%m-%d") if r.get("data_fim") else None,
                quantidade_ocorrencias=r.get("quantidade_ocorrencias"),
                intervalo=r.get("intervalo", 1),
                observacoes=r.get("observacoes")
            )
            db.session.add(nova_rec)
            db.session.flush()
            lanc.recorrencia_id = nova_rec.id

        db.session.add(lanc)
        db.session.commit()
        return jsonify({"id": lanc.id, "message": "Lançamento criado com sucesso."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# GET: obter um lançamento por ID
@lancamento_bp.route("/<int:id>", methods=["GET"])
def obter_lancamento(id):
    lanc = Lancamento.query.get_or_404(id)
    return jsonify({
        "id": lanc.id,
        "descricao": lanc.descricao,
        "valor": lanc.valor,
        "data": lanc.data.strftime("%Y-%m-%d"),
        "tipo": lanc.tipo,
        "categoria_id": lanc.categoria_id,
        "responsavel_id": lanc.responsavel_id,
        "observacoes": lanc.observacoes,
        "recorrente": lanc.recorrente,
        "recorrencia_id": lanc.recorrencia_id
    })

# PUT: atualizar um lançamento
@lancamento_bp.route("/<int:id>", methods=["PUT"])
def atualizar_lancamento(id):
    lanc = Lancamento.query.get_or_404(id)
    data = request.get_json()

    try:
        lanc.descricao = data.get("descricao", lanc.descricao)
        lanc.valor = float(data.get("valor", lanc.valor))
        if "data" in data:
            lanc.data = datetime.strptime(data["data"], "%Y-%m-%d")
        lanc.tipo = data.get("tipo", lanc.tipo)
        lanc.categoria_id = data.get("categoria_id", lanc.categoria_id)
        lanc.responsavel_id = data.get("responsavel_id", lanc.responsavel_id)
        lanc.observacoes = data.get("observacoes", lanc.observacoes)

        db.session.commit()
        return jsonify({"message": "Lançamento atualizado com sucesso."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# DELETE: remover um lançamento
@lancamento_bp.route("/<int:id>", methods=["DELETE"])
def deletar_lancamento(id):
    lanc = Lancamento.query.get_or_404(id)
    try:
        db.session.delete(lanc)
        db.session.commit()
        return jsonify({"message": "Lançamento excluído com sucesso."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
