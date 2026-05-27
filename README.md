# ⚡ Circuit Breaker

Sistema de Circuit Breaker desenvolvido em Python com Flask,
implementando os 3 estados do padrão (Fechado, Aberto e Semi-Aberto)
com dashboard visual em tempo real e simulação de serviço instável.

## 💼 Valor para empresas
Sistemas distribuídos falham. Sem Circuit Breaker, uma falha em
um serviço derruba toda a aplicação. Com Circuit Breaker, o sistema
detecta a falha automaticamente, para de tentar chamadas que vão
falhar e se recupera sozinho quando o serviço volta — sem
intervenção humana e sem derrubar os outros serviços.

## 🚀 Como usar

1. Clone o repositório
2. Instale as dependências:
pip install flask
3. Execute:
python app.py
4. Acesse: http://127.0.0.1:5000

## ✨ Funcionalidades
- 3 estados automáticos: Fechado, Aberto e Semi-Aberto
- Abre após 3 erros consecutivos
- Recuperação automática após 10 segundos
- Fecha após 2 sucessos no modo Semi-Aberto
- Taxa de falha configurável em tempo real (0% a 100%)
- Dashboard tema escuro com animações
- Histórico completo de eventos com timestamp

## 🧠 Os 3 estados
- 🟢 FECHADO → requisições passando normalmente
- 🔴 ABERTO → bloqueando tudo, aguardando recuperação
- 🟡 SEMI-ABERTO → testando se o serviço voltou

