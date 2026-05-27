# 🟢 FECHADO  → passou do limite de erros → abre
# 🔴 ABERTO   → aguarda tempo de recuperação → vai para semi-aberto
# 🟡 SEMI-ABERTO → testa uma requisição → fecha ou abre novamente

import time
import threading

class CircuitBreaker:
    def __init__(self,
                 limite_erros: int   = 3,
                 tempo_recuperacao: float = 10.0,
                 limite_sucesso: int = 2):
        """
        limite_erros       → quantos erros seguidos para abrir o disjuntor
        tempo_recuperacao  → segundos aguardando antes de testar novamente
        limite_sucesso     → quantos sucessos no semi-aberto para fechar
        """
        self.limite_erros      = limite_erros
        self.tempo_recuperacao = tempo_recuperacao
        self.limite_sucesso    = limite_sucesso

        self.estado            = "FECHADO"
        self.erros             = 0
        self.sucessos          = 0
        self.total_requisicoes = 0
        self.total_bloqueadas  = 0
        self.total_erros       = 0
        self.total_sucessos    = 0
        self.ultimo_erro       = None
        self.aberto_em         = None
        self.historico         = []
        self.lock              = threading.Lock()

    def _registrar(self, tipo: str, mensagem: str):
        """Registra um evento no histórico."""
        self.historico.insert(0, {
            "tipo":      tipo,
            "mensagem":  mensagem,
            "timestamp": time.strftime("%H:%M:%S")
        })
        self.historico = self.historico[:20]

    def _abrir(self):
        """Abre o disjuntor."""
        self.estado    = "ABERTO"
        self.aberto_em = time.time()
        self._registrar("ABERTO", f"⚡ Disjuntor ABERTO após {self.limite_erros} erros seguidos")

    def _fechar(self):
        """Fecha o disjuntor."""
        self.estado   = "FECHADO"
        self.erros    = 0
        self.sucessos = 0
        self._registrar("FECHADO", "✅ Disjuntor FECHADO — serviço recuperado!")

    def _semi_abrir(self):
        """Coloca o disjuntor em modo de teste."""
        self.estado   = "SEMI_ABERTO"
        self.sucessos = 0
        self._registrar("SEMI_ABERTO", "🟡 Disjuntor SEMI-ABERTO — testando serviço...")

    def executar(self, funcao, *args, **kwargs) -> dict:
        """
        Tenta executar uma função protegida pelo Circuit Breaker.
        Gerencia automaticamente os estados do disjuntor.
        """
        with self.lock:
            self.total_requisicoes += 1

            # ─── ESTADO ABERTO ───────────────────────────────
            if self.estado == "ABERTO":
                tempo_passado = time.time() - self.aberto_em
                if tempo_passado >= self.tempo_recuperacao:
                    self._semi_abrir()
                else:
                    self.total_bloqueadas += 1
                    restante = round(self.tempo_recuperacao - tempo_passado, 1)
                    return {
                        "sucesso":  False,
                        "bloqueado": True,
                        "estado":   self.estado,
                        "message":  f"🔴 Disjuntor ABERTO. Recuperando em {restante}s..."
                    }

            # ─── ESTADO SEMI-ABERTO ──────────────────────────
            if self.estado == "SEMI_ABERTO":
                try:
                    resultado = funcao(*args, **kwargs)
                    self.sucessos      += 1
                    self.total_sucessos += 1
                    if self.sucessos >= self.limite_sucesso:
                        self._fechar()
                    return {
                        "sucesso":  True,
                        "bloqueado": False,
                        "estado":   self.estado,
                        "resultado": resultado,
                        "message":  f"🟡 Teste bem-sucedido ({self.sucessos}/{self.limite_sucesso})"
                    }
                except Exception as e:
                    self.erros         += 1
                    self.total_erros   += 1
                    self.ultimo_erro    = str(e)
                    self._abrir()
                    return {
                        "sucesso":  False,
                        "bloqueado": False,
                        "estado":   self.estado,
                        "message":  f"🔴 Teste falhou — disjuntor reaberto: {e}"
                    }

            # ─── ESTADO FECHADO ──────────────────────────────
            try:
                resultado = funcao(*args, **kwargs)
                self.erros          = 0
                self.total_sucessos += 1
                self._registrar("SUCESSO", "✅ Requisição bem-sucedida")
                return {
                    "sucesso":  True,
                    "bloqueado": False,
                    "estado":   self.estado,
                    "resultado": resultado,
                    "message":  "✅ Requisição processada com sucesso"
                }
            except Exception as e:
                self.erros       += 1
                self.total_erros += 1
                self.ultimo_erro  = str(e)
                self._registrar("ERRO", f"❌ Erro: {e}")
                if self.erros >= self.limite_erros:
                    self._abrir()
                return {
                    "sucesso":  False,
                    "bloqueado": False,
                    "estado":   self.estado,
                    "message":  f"❌ Erro ({self.erros}/{self.limite_erros}): {e}"
                }

    def status(self) -> dict:
        """Retorna o estado atual do Circuit Breaker."""
        with self.lock:
            tempo_restante = 0
            if self.estado == "ABERTO" and self.aberto_em:
                tempo_restante = max(0, round(
                    self.tempo_recuperacao - (time.time() - self.aberto_em), 1
                ))
            return {
                "estado":            self.estado,
                "erros":             self.erros,
                "limite_erros":      self.limite_erros,
                "tempo_restante":    tempo_restante,
                "tempo_recuperacao": self.tempo_recuperacao,
                "total_requisicoes": self.total_requisicoes,
                "total_bloqueadas":  self.total_bloqueadas,
                "total_erros":       self.total_erros,
                "total_sucessos":    self.total_sucessos,
                "historico":         self.historico
            }

    def resetar(self):
        """Reseta o Circuit Breaker."""
        with self.lock:
            self.estado            = "FECHADO"
            self.erros             = 0
            self.sucessos          = 0
            self.total_requisicoes = 0
            self.total_bloqueadas  = 0
            self.total_erros       = 0
            self.total_sucessos    = 0
            self.ultimo_erro       = None
            self.aberto_em         = None
            self.historico         = []