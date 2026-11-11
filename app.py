# Importa as ferramentas do Flask para criar a API
# jsonify: transforma dicionários Python em texto JSON para o Postman ler
# request: pega os dados que o usuário enviou pelo Postman
from flask import Flask, jsonify, request

# Importa a classe principal onde estão as regras e cálculos do inventário
from trabalho_02 import SistemaInventario

# Cria a aplicação Flask
app = Flask(__name__)

# Inicia o sistema e carrega os dados dos arquivos JSON para a memória
sistema = SistemaInventario()

# --- ROTA RAIZ: Evita o erro 404 se acessar apenas http://localhost:5000 ---
@app.route('/', methods=['GET'])
def rota_inicial():
    # Retorna a mesma lista de equipamentos caso chame sem o /equipamentos
    lista_equipamentos = [eq.to_dict() for eq in sistema.equipamentos.values()]
    return jsonify(lista_equipamentos), 200

# --- ROTA 1: Listar todos os Equipamentos (GET) ---
@app.route('/equipamentos', methods=['GET'])
def obter_equipamentos():
    # Transforma todos os objetos de equipamentos da memória em dicionários
    lista_equipamentos = [eq.to_dict() for eq in sistema.equipamentos.values()]
    
    # Retorna a lista em formato JSON com o código 200 (Sucesso)
    return jsonify(lista_equipamentos), 200

# --- ROTA EXTRA: Buscar um único Equipamento pelo ID (GET) ---
@app.route('/equipamentos/<int:id_ativo>', methods=['GET'])
def obter_equipamento_por_id(id_ativo):
    # Verifica se o ID procurado existe no dicionário de equipamentos
    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento não encontrado."}), 404
    
    # Retorna apenas os dados do equipamento encontrado com código 200
    return jsonify(sistema.equipamentos[id_ativo].to_dict()), 200

# --- ROTA 2: Cadastrar Novo Equipamento (POST) ---
@app.route('/equipamentos', methods=['POST'])
def criar_equipamento():
    # Pega os dados em JSON enviados no Body (corpo) do Postman
    dados = request.json
    
    # Verifica se algum dado foi enviado na requisição
    if not dados or 'id_ativo' not in dados:
        return jsonify({"erro": "Dados incompletos. Informe o id_ativo."}), 400

    # Separa cada informação recebida e garante que o ID seja um número inteiro
    id_ativo = int(dados.get('id_ativo'))
    nome = dados.get('nome')
    responsavel = dados.get('responsavel')
    setor = dados.get('setor')
    tipo = dados.get('tipo')

    # Verifica se o ID já está cadastrado para não duplicar
    if id_ativo in sistema.equipamentos:
        return jsonify({"erro": "ID do equipamento já existe."}), 400

    # Cria o objeto do equipamento usando a classe correta (Notebook, Servidor, etc.)
    novo_eq = sistema.criar_objeto_equipamento(id_ativo, nome, responsavel, setor, tipo)
    
    # Guarda na memória e salva no arquivo equipamentos.json
    sistema.equipamentos[id_ativo] = novo_eq
    sistema.salvar_dados()

    # Retorna os dados do ativo criado e o código 201 (Created / Criado)
    return jsonify({
        "mensagem": f"Equipamento '{nome}' cadastrado com sucesso!",
        "equipamento": novo_eq.to_dict()
    }), 201

# --- ROTA 3: Atualizar Equipamento Existente (PUT) ---
@app.route('/equipamentos/<int:id_ativo>', methods=['PUT'])
def atualizar_equipamento(id_ativo):
    # Verifica se o equipamento que queremos editar realmente existe
    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento não encontrado para atualização."}), 404

    # Pega os novos dados enviados no Body do Postman
    dados = request.json
    eq_atual = sistema.equipamentos[id_ativo]

    # Pega os valores novos ou mantém os antigos caso algum campo não tenha sido enviado
    novo_nome = dados.get('nome', eq_atual.nome)
    novo_resp = dados.get('responsavel', eq_atual.responsavel)
    novo_setor = dados.get('setor', eq_atual.setor)
    novo_tipo = dados.get('tipo', eq_atual.tipo)

    # Recria o objeto para atualizar também o fator de exposição se o tipo mudar
    eq_atualizado = sistema.criar_objeto_equipamento(id_ativo, novo_nome, novo_resp, novo_setor, novo_tipo)
    
    # Mantém as vulnerabilidades e dependências que o equipamento já tinha antes
    eq_atualizado.vulnerabilidades_ids = eq_atual.vulnerabilidades_ids
    eq_atualizado.dependencias = eq_atual.dependencias

    # Salva a atualização na memória e no arquivo JSON
    sistema.equipamentos[id_ativo] = eq_atualizado
    sistema.salvar_dados()

    # Retorna confirmação com código 200 (OK)
    return jsonify({
        "mensagem": f"Equipamento {id_ativo} atualizado com sucesso!",
        "equipamento": eq_atualizado.to_dict()
    }), 200

# --- ROTA 4: Apagar Equipamento (DELETE) ---
@app.route('/equipamentos/<int:id_ativo>', methods=['DELETE'])
def deletar_equipamento(id_ativo):
    # Verifica se o equipamento existe antes de tentar apagar
    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento não encontrado para exclusão."}), 404

    # Remove o equipamento do dicionário da memória
    removido = sistema.equipamentos.pop(id_ativo)

    # Remove também qualquer dependência que outros ativos tinham com este ID removido
    for eq in sistema.equipamentos.values():
        if str(id_ativo) in eq.dependencias:
            del eq.dependencias[str(id_ativo)]

    # Atualiza o arquivo equipamentos.json sem o ativo apagado
    sistema.salvar_dados()

    # Retorna confirmação de exclusão com código 200 (OK)
    return jsonify({"mensagem": f"Equipamento '{removido.nome}' (ID {id_ativo}) removido com sucesso!"}), 200

# --- ROTA 5: Calcular Risco Total com NumPy (GET) ---
@app.route('/risco', methods=['GET'])
def relatorio_risco():
    # Chama a função do trabalho_02 que monta as matrizes e resolve o sistema linear
    resultados = sistema.calcular_analise_risco_api()
    
    # Se faltar algum dado básico para o cálculo, retorna erro 400
    if isinstance(resultados, dict) and "erro" in resultados:
        return jsonify(resultados), 400
        
    # Retorna o relatório completo de risco com código 200 (OK)
    return jsonify(resultados), 200

# Inicia o servidor quando executamos o arquivo diretamente
if __name__ == '__main__':
    # host='0.0.0.0' libera o acesso para fora do container Docker
    app.run(host='0.0.0.0', port=5000, debug=False)