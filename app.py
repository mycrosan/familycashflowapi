from flask import Flask
from models import db
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

from routes.responsavel import responsavel_bp
from routes.categoria import categoria_bp
from routes.lancamento import lancamento_bp
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
CORS(app)

db.init_app(app)

app.register_blueprint(responsavel_bp, url_prefix='/responsavel')
app.register_blueprint(categoria_bp, url_prefix='/categoria')
app.register_blueprint(lancamento_bp, url_prefix='/lancamento')

@app.route('/')
def index():
    return {"message": "API de fluxo de caixa ativa."}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



