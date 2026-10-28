from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aacs-chave-secreta-lgpd-2026'

# Banco de dados temporario em memoria (Estoque PEPS)
ESTOQUE_PEPS = [
    {"id": 101, "item": "Feijao Carioca 1kg", "quantidade": 15, "validade": "2026-11-02"},
    {"id": 102, "item": "Feijao Carioca 1kg", "quantidade": 20, "validade": "2026-11-15"}
]

def mascarar_cpf(cpf):
    """Aplica mascara LGPD no CPF: ***.456.789-**"""
    digits = ''.join(filter(str.isdigit, str(cpf)))
    if len(digits) == 11:
        return f"***.{digits[3:6]}.{digits[6:9]}-**"
    return cpf

def validar_cpf(cpf):
    """Valida se o CPF possui 11 digitos numericos"""
    digits = ''.join(filter(str.isdigit, str(cpf)))
    return len(digits) == 11

@app.route('/')
@app.route('/atendimentos/busca', methods=['GET', 'POST'])
def busca():
    if request.method == 'POST':
        cpf = request.form.get('cpf', '')
        if validar_cpf(cpf):
            return jsonify({
                "status": "sucesso",
                "mensagem": "ASSISTIDO ELEGIVEL PARA BENEFICIO",
                "cpf_mascarado": mascarar_cpf(cpf)
            }), 200
        return jsonify({"status": "erro", "mensagem": "CPF Invalido"}), 400
    return render_template('busca.html')

@app.route('/estoque/painel-peps', methods=['GET', 'POST'])
def estoque():
    if request.method == 'POST':
        item = request.form.get('item')
        qtd = request.form.get('quantidade')
        validade = request.form.get('validade')
        
        if not item or not qtd or not validade:
            return jsonify({"status": "erro", "mensagem": "Campos obrigatorios ausentes"}), 400
            
        novo_lote = {
            "id": len(ESTOQUE_PEPS) + 101,
            "item": item,
            "quantidade": int(qtd),
            "validade": validade
        }
        ESTOQUE_PEPS.append(novo_lote)
        # Algoritmo PEPS: Ordena por data de validade mais proxima
        ESTOQUE_PEPS.sort(key=lambda x: datetime.strptime(x['validade'], '%Y-%m-%d'))
        return jsonify({"status": "sucesso", "estoque": ESTOQUE_PEPS}), 201
        
    return render_template('estoque.html', estoque=ESTOQUE_PEPS)

@app.route('/atendimentos/confirmar', methods=['POST'])
def confirmar_entrega():
    if not ESTOQUE_PEPS:
        return jsonify({"status": "erro", "mensagem": "Estoque vazio"}), 400
    
    # Baixa do primeiro lote da fila PEPS
    lote_retirado = ESTOQUE_PEPS[0]
    lote_retirado['quantidade'] -= 1
    if lote_retirado['quantidade'] <= 0:
        ESTOQUE_PEPS.pop(0)
        
    return jsonify({
        "status": "sucesso",
        "mensagem": "Entrega confirmada com sucesso",
        "item_baixado": lote_retirado['item']
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
