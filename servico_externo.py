# 🎲 Simula um serviço instável que falha aleatoriamente
# ⚙️ Você controla a taxa de falha (0% a 100%)
# ⏳ Cada chamada demora um tempo simulado
# 📊 Representa qualquer serviço externo real — pagamento, API, banco

import time
import random

class ServicoExterno:
    def __init__(self):
        self.taxa_falha     = 0.7   # 70% de chance de falhar
        self.tempo_resposta = 0.5  # segundos por chamada
        self.total_chamadas = 0
        self.nome           = "Serviço de Pagamento"

    def chamar(self) -> dict:
        """
        Simula uma chamada a um serviço externo instável.
        Lança uma exceção quando falha, igual a serviços reais.
        """
        self.total_chamadas += 1
        time.sleep(self.tempo_resposta)

        if random.random() < self.taxa_falha:
            raise Exception(f"Timeout — {self.nome} não respondeu")

        return {
            "status":      "ok",
            "servico":     self.nome,
            "chamada":     self.total_chamadas,
            "message":     f"✅ {self.nome} respondeu com sucesso"
        }

    def configurar(self, taxa_falha: float, tempo_resposta: float):
        """Permite ajustar o comportamento do serviço em tempo real."""
        self.taxa_falha     = max(0.0, min(1.0, taxa_falha))
        self.tempo_resposta = max(0.1, tempo_resposta)