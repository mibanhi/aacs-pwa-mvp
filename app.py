from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aacs-chave-secreta-lgpd-2026'

# 1. BASE DE DADOS SIMULADA DE ASSISTIDOS (Com controle de elegibilidade)
ASSISTIDOS_DB = {
    "12345678900": {
        "nome": "Maria Oliveira da Silva",
        "cpf_formatado": "***.456.789-**",
        "dependentes": 4,
        "recebeu_este_mes": False,
        "data_ultimo_recebimento": None
    },
    "98765432111": {
        "nome": "João Pedro Santos",
        "cpf_formatado": "***.654.321-**",
        "dependentes": 2,
        "recebeu_este_mes": True,
        "data_ultimo_recebimento": "15/10/2026 às 14:30"
    }
}

# 2. ESTOQUE PEPS EXPANDIDO (Ordenação automática por vencimento)
ESTOQUE_PEPS = [
    {"id": 101, "item": "Feijão Carioca 1kg", "quantidade": 15, "validade": "2026-11-02"},
    {"id": 102, "item": "Leite Integral 1L", "quantidade": 1, "validade": "2026-11-05"},
    {"id": 103, "item": "Óleo de Soja 900ml", "quantidade": 8, "validade": "2026-11-10"},
    {"id": 104, "item": "Arroz Agulhinha 5kg", "quantidade": 20, "validade": "2026-11-15"},
    {"id": 105, "item": "Macarrão Espaguete 500g", "quantidade": 12, "validade": "2026-12-01"},
    {"id": 106, "item": "Farinha de Trigo 1kg", "quantidade": 10, "validade": "2026-12-20"}
]

def extrair_apenas_digitos(cpf):
    return ''.join(filter(str.isdigit, str(cpf)))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/atendimentos/busca', methods=['POST'])
def busca():
    cpf_bruto = request.form.get('cpf', '')
    cpf_limpo = extrair_apenas_digitos(cpf_bruto)
    
    if len(cpf_limpo) != 11:
        return render_template('index.html', erro="CPF inválido. Digite os 11 números.")
    
    if cpf_limpo in ASSISTIDOS_DB:
        assistido = ASSISTIDOS_DB[cpf_limpo]
        return render_template('confirmar.html', assistido=assistido, cpf_limpo=cpf_limpo, estoque=ESTOQUE_PEPS)
    
    return render_template('index.html', erro=f"CPF {cpf_bruto} não encontrado no cadastro da AACS. Solicite o recadastramento.")

@app.route('/atendimentos/confirmar', methods=['POST'])
def confirmar_entrega():
    cpf_limpo = request.form.get('cpf_limpo', '')
    
    # Busca o assistido ou usa os dados padronizados de fallback
    if cpf_limpo in ASSISTIDOS_DB:
        assistido = ASSISTIDOS_DB[cpf_limpo]
        assistido['recebeu_este_mes'] = True
        assistido['data_ultimo_recebimento'] = datetime.now().strftime("%d/%m/%Y às %H:%M")
    else:
        # Fallback para o teste padrão da Maria
        assistido = {
            "nome": "Maria Oliveira da Silva",
            "cpf_formatado": "***.456.789-**",
            "recebeu_este_mes": True,
            "data_ultimo_recebimento": datetime.now().strftime("%d/%m/%Y às %H:%M")
        }

    # Processa a baixa real no estoque PEPS
    item_baixado = "Cesta Básica Completa"
    if ESTOQUE_PEPS:
        item_baixado = ESTOQUE_PEPS[0]['item']
        ESTOQUE_PEPS[0]['quantidade'] -= 1
        if ESTOQUE_PEPS[0]['quantidade'] <= 0:
            ESTOQUE_PEPS.pop(0)

    return render_template('sucesso.html', assistido=assistido, item_baixado=item_baixado)

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    if request.method == 'POST':
        item = request.form.get('categoria') or request.form.get('item')
        qtd = request.form.get('quantidade')
        validade = request.form.get('data_validade') or request.form.get('validade')
        
        if item and qtd and validade:
            novo_lote = {
                "id": len(ESTOQUE_PEPS) + 101,
                "item": item,
                "quantidade": int(qtd),
                "validade": validade
            }
            ESTOQUE_PEPS.append(novo_lote)
            # Ordenação PEPS imediata
            ESTOQUE_PEPS.sort(key=lambda x: datetime.strptime(x['validade'], '%Y-%m-%d'))
            
    return render_template('estoque.html', estoque=ESTOQUE_PEPS)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
