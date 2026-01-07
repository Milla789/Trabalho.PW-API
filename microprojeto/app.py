import os
import random
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from google import genai  # Biblioteca moderna de 2026
from dotenv import load_dotenv

# --- CARREGAR VARIÁVEIS DO .env ---
load_dotenv()

app = Flask(__name__)

# --- BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jolly.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Jogo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    data = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# --- CONFIGURAÇÃO DA IA ---
CHAVE_API = os.getenv("GEMINI_API_KEY")  # pega do .env
client = genai.Client(api_key=CHAVE_API)

def gerar_resposta_ia(materiais, estilo):
    try:
        # PROMPT DE ELITE PARA CRIATIVIDADE EXTREMA
        prompt = f"""
        Aja como um renomado Game Designer e Diretor Criativo. 
        Sua missão é criar um jogo de mesa de LUXO, COMPLEXO e MEMORÁVEL.
        
        MATERIAIS: {materiais}
        ESTILO EXIGIDO: {estilo}
        
        DIRETRIZES PARA RESPOSTA (SEJA EXTREMAMENTE DETALHISTA):
        1. LORE: Crie uma história de fundo sombria ou heróica (mínimo 2 parágrafos).
        2. COMPONENTES: Transforme {materiais} em artefatos lendários com nomes próprios.
        3. MECÂNICA DE RISCO: O jogo deve ter um sistema de "Tudo ou Nada".
        4. REGRAS PASSO A PASSO: Divida em: Setup, Fase de Ação e Fase de Consequência.
        
        Use Markdown rico (## e **) e responda em Português do Brasil.
        """

        # Use um modelo suportado (ex: gemini-1.0-pro ou gemini-3-pro)
        response = client.models.generate_content(
             model="models/gemini-flash-latest",  
            contents=prompt,
            config={
                "temperature": 1.0,
                "max_output_tokens": 2000
            }
        )
        return response.text
    except Exception as e:
        print(f"ERRO NO GEMINI: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    resposta_ia = None
    if request.method == 'POST':
        materiais = request.form.get('materiais')
        estilos_complexos = [
            "RPG de Horror Cósmico",
            "Thriller de Espionagem High-Tech",
            "Estratégia de Guerra de Recursos"
        ]
        estilo_sorteado = random.choice(estilos_complexos)
        resposta_ia = gerar_resposta_ia(materiais, estilo_sorteado)
        
        if not resposta_ia:
            resposta_ia = "## 🏮 O Mestre Jolly está em silêncio profundo...\nOcorreu um erro técnico. Verifique o terminal."
        else:
            try:
                novo_jogo = Jogo(
                    titulo=f"{estilo_sorteado}: {materiais[:15]}",
                    descricao=resposta_ia,
                    data=datetime.now().strftime("%d/%m/%Y %H:%M")
                )
                db.session.add(novo_jogo)
                db.session.commit()
            except Exception as e:
                print(f"Erro no Banco: {e}")
                db.session.rollback()
        
    return render_template('index.html', resposta=resposta_ia)

@app.route('/historico')
def historico():
    jogos = Jogo.query.order_by(Jogo.id.desc()).all()
    return render_template('historico.html', lista_jogos=jogos)

if __name__ == '__main__':
    app.run(debug=True)