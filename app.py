from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aacs-chave-secreta-lgpd-2026'

# 1. BASE DE DADOS SIMULADA DE ASSISTIDOS
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

# 2. ESTOQUE PEPS EXPANDIDO
ESTOQUE_PEPS = [
    {"id": 101, "item": "Feijão Carioca 1kg", "quantidade": 15, "validade": "2026-11-02"},
    {"id": 102, "item": "Leite Integral 1L", "quantidade": 1, "validade": "2026-11-05"},
    {"id": 103, "item": "Óleo de Soja 900ml", "quantidade": 8, "validade": "2026-11-10"},
    {"id": 104, "item": "Arroz Agulhinha 5kg", "quantidade": 20, "validade": "2026-11-15"},
    {"id": 105, "item": "Panetone 500g (Item Especial)", "quantidade": 5, "validade": "2026-12-25"}
]

def extrair_apenas_digitos(cpf):
    return ''.join(filter(str.isdigit, str(cpf)))

def processar_status_estoque(estoque_lista):
    hoje = date.today()
    estoque_processado = []
    
    for lote in estoque_lista:
        data_val = datetime.strptime(lote['validade'], '%Y-%m-%d').date()
        status = "REGULAR"
        
        if data_val < hoje:
            status = "VENCIDO"
        elif data_val == hoje or (data_val - hoje).days <= 3:
            status = "CRITICO"
            
        lote_copy = lote.copy()
        lote_copy['status_validade'] = status
        lote_copy['dias_para_vencer'] = (data_val - hoje).days
        estoque_processado.append(lote_copy)
        
    return estoque_processado

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/atendimentos/busca', methods=['POST'])
def busca():
    cpf_bruto = request.form.get('cpf', '')
    cpf_limpo = extrair_apenas_digitos(cpf_bruto)
    
    if len(cpf_limpo) != 11:
        return render_template('index.html', erro="CPF inválido. Digite os 11 números.")
    
    # Filtra apenas itens válidos para doação
    hoje = date.today()
    estoque_validos = [item for item in ESTOQUE_PEPS if datetime.strptime(item['validade'], '%Y-%m-%d').date() >= hoje]
    
    if cpf_limpo in ASSISTIDOS_DB:
        assistido = ASSISTIDOS_DB[cpf_limpo]
        return render_template('confirmar.html', assistido=assistido, cpf_limpo=cpf_limpo, estoque=estoque_validos)
    
    return render_template('index.html', erro=f"CPF {cpf_bruto} não encontrado no cadastro da AACS.")

@app.route('/atendimentos/confirmar', methods=['POST'])
def confirmar_entrega():
    cpf_limpo = request.form.get('cpf_limpo', '')
    item_extra_id = request.form.get('item_extra')
    
    if cpf_limpo in ASSISTIDOS_DB:
        assistido = ASSISTIDOS_DB[cpf_limpo]
        assistido['recebeu_este_mes'] = True
        assistido['data_ultimo_recebimento'] = datetime.now().strftime("%d/%m/%Y às %H:%M")
    else:
        assistido = {
            "nome": "Maria Oliveira da Silva",
            "cpf_formatado": "***.456.789-**",
            "data_ultimo_recebimento": datetime.now().strftime("%d/%m/%Y às %H:%M")
        }

    # 1. Baixa no primeiro lote PEPS prioritário (da Cesta)
    hoje = date.today()
    item_baixado = "Cesta Básica Completa"
    for i, lote in enumerate(ESTOQUE_PEPS):
        data_val = datetime.strptime(lote['validade'], '%Y-%m-%d').date()
        if data_val >= hoje:
            item_baixado = lote['item']
            ESTOQUE_PEPS[i]['quantidade'] -= 1
            if ESTOQUE_PEPS[i]['quantidade'] <= 0:
                ESTOQUE_PEPS.pop(i)
            break

    # 2. Baixa no item extra selecionado (se houver)
    nome_item_extra = None
    if item_extra_id:
        for i, lote in enumerate(ESTOQUE_PEPS):
            if str(lote['id']) == str(item_extra_id):
                nome_item_extra = lote['item']
                ESTOQUE_PEPS[i]['quantidade'] -= 1
                if ESTOQUE_PEPS[i]['quantidade'] <= 0:
                    ESTOQUE_PEPS.pop(i)
                break

    return render_template('sucesso.html', assistido=assistido, item_baixado=item_baixado, item_extra=nome_item_extra)

@app.route('/estoque', methods=['GET', 'POST'])
def estoque():
    if request.method == 'POST':
        categoria = request.form.get('categoria')
        outro_item = request.form.get('outro_item')
        qtd = request.form.get('quantidade')
        validade = request.form.get('data_validade')
        
        item_final = outro_item.strip().title() if categoria == "outro" and outro_item else categoria
        
        if item_final and qtd and validade:
            novo_lote = {
                "id": len(ESTOQUE_PEPS) + 101,
                "item": item_final,
                "quantidade": int(qtd),
                "validade": validade
            }
            ESTOQUE_PEPS.append(novo_lote)
            ESTOQUE_PEPS.sort(key=lambda x: datetime.strptime(x['validade'], '%Y-%m-%d'))
            
    estoque_processado = processar_status_estoque(ESTOQUE_PEPS)
    return render_template('estoque.html', estoque=estoque_processado)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
