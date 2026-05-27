# GET  /                    → abre o dashboard visual
# POST /requisicao          → executa uma requisição protegida
# POST /configurar          → ajusta a taxa de falha do serviço
# GET  /status              → retorna estado atual do Circuit Breaker
# GET  /resetar             → reseta tudo para testar de novo

from flask import Flask, render_template, request, jsonify
from circuit_breaker import CircuitBreaker
from servico_externo import ServicoExterno

app = Flask(__name__)

# Circuit Breaker com 3 erros para abrir e 10s de recuperação
cb      = CircuitBreaker(limite_erros=3, tempo_recuperacao=10.0, limite_sucesso=2)
servico = ServicoExterno()

# ─── DASHBOARD ───────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ─── EXECUTAR REQUISIÇÃO ─────────────────────────────────
@app.route("/requisicao", methods=["POST"])
def requisicao():
    """
    Executa uma requisição protegida pelo Circuit Breaker.
    O CB decide automaticamente se deixa passar ou bloqueia.
    """
    resultado = cb.executar(servico.chamar)
    status_code = 200 if resultado["sucesso"] else (
        503 if resultado["bloqueado"] else 500
    )
    return jsonify(resultado), status_code

# ─── CONFIGURAR SERVIÇO ──────────────────────────────────
@app.route("/configurar", methods=["POST"])
def configurar():
    """
    Permite ajustar a taxa de falha e tempo de resposta
    do serviço externo em tempo real.
    """
    data           = request.get_json()
    taxa_falha     = float(data.get("taxa_falha", 0.7))
    tempo_resposta = float(data.get("tempo_resposta", 0.5))
    servico.configurar(taxa_falha, tempo_resposta)
    return jsonify({
        "message":      f"⚙️ Serviço configurado — Taxa de falha: {int(taxa_falha * 100)}%",
        "taxa_falha":   taxa_falha,
        "tempo_resposta": tempo_resposta
    })

# ─── STATUS ──────────────────────────────────────────────
@app.route("/status")
def status():
    dados = cb.status()
    dados["taxa_falha"]      = servico.taxa_falha
    dados["tempo_resposta"]  = servico.tempo_resposta
    dados["nome_servico"]    = servico.nome
    return jsonify(dados)

# ─── RESETAR ─────────────────────────────────────────────
@app.route("/resetar")
def resetar():
    cb.resetar()
    return jsonify({"message": "✅ Circuit Breaker resetado!"})

if __name__ == "__main__":
    app.run(debug=True)