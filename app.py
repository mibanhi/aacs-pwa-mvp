from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aacs-chave-secreta-lgpd-2026'

# Banco de dados temporário em memória (Estoque PEPS)
ESTOQUE_PEPS = [
    {"id": 101, "item": "Feijão Carioca 1kg", "quantidade": 15, "validade": "2026-11-02"},
    {"id": 102, "item": "Arroz Agulhinha 5kg", "quantidade": 20, "validade": "2026-11-15"}
]

def mascarar_cpf(cpf):
    """Aplica máscara LGPD no CPF: ***.456.789-**"""
    digits = ''.join(filter(str.isdigit, str(cpf)))
    if len(digits) == 11:
        return f"***.{digits[3:6]}.{digits[6:9]}-**"
    return cpf

def validar_cpf(cpf):
    """Valida se o CPF possui 11 dígitos numéricos"""
    digits = ''.join(filter(str.isdigit, str(cpf)))
    return len(digits) == 11

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/atendimentos/busca', methods=['POST'])
def busca():
    cpf = request.form.get('cpf', '')
    if validar_cpf(cpf):
        cpf_formatado = mascarar_cpf(cpf)
        # Renderiza a página de confirmação com os dados do assistido
        return render_template('confirmar.html', cpf=cpf_formatado, estoque=ESTOQUE_PEPS)
    
    # Se CPF for inválido, recarrega a busca com mensagem de erro
    return render_template('index.html', erro="CPF inválido. Digite 11 números.")

@app.route('/estoque', methods=['GET', 'POST'])
@app.route('/estoque/painel-peps', methods=['GET', 'POST'])
def estoque():
    if request.method == 'POST':
        item = request.form.get('categoria') or request.form.get('item')
        qtd = request.form.get('quantidade')
        validade = request.form.get('data_validade') or request.form.get('validade')
        
        if item and qtd and validade:
            novo_lote = {
                "id": len(ESTOQUE_PEPS) + 101,
                "item": item.title(),
                "quantidade": int(qtd),
                "validade": validade
            }
            ESTOQUE_PEPS.append(novo_lote)
            # Ordenação PEPS: Validade mais próxima primeiro
            ESTOQUE_PEPS.sort(key=lambda x: datetime.strptime(x['validade'], '%Y-%m-%d'))
            
    return render_template('estoque.html', estoque=ESTOQUE_PEPS)

@app.route('/atendimentos/confirmar', methods=['POST'])
def confirmar_entrega():
    if ESTOQUE_PEPS:
        # Baixa do primeiro lote da fila PEPS
        ESTOQUE_PEPS[0]['quantidade'] -= 1
        if ESTOQUE_PEPS[0]['quantidade'] <= 0:
            ESTOQUE_PEPS.pop(0)
            
    return redirect(url_for('estoque'))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
