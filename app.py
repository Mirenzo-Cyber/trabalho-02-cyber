# Importa as ferramentas do Flask para criar a API e carregar a página HTML
from flask import Flask, jsonify, request, render_template

# Importa as classes do nosso sistema principal
from trabalho_02 import SistemaInventario, Vulnerabilidade

# Cria a aplicação Flask
app = Flask(__name__)

# Inicia o sistema e carrega os dados dos arquivos JSON para a memória
sistema = SistemaInventario()


# --- ROTA RAIZ: Abre a Interface Web no navegador ---
@app.route("/", methods=["GET"])
def rota_inicial():
    # Carrega o arquivo index.html que está dentro da pasta templates
    return render_template("index.html")


# --- ROTA 1: Listar todos os Equipamentos (GET) ---
@app.route("/equipamentos", methods=["GET"])
def obter_equipamentos():
    # Transforma todos os objetos de equipamentos da memória em dicionários
    lista_equipamentos = [eq.to_dict() for eq in sistema.equipamentos.values()]
    return jsonify(lista_equipamentos), 200


# --- ROTA EXTRA: Buscar um único Equipamento pelo ID (GET) ---
@app.route("/equipamentos/<int:id_ativo>", methods=["GET"])
def obter_equipamento_por_id(id_ativo):
    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento não encontrado."}), 404
    return jsonify(sistema.equipamentos[id_ativo].to_dict()), 200


# --- ROTA 2: Cadastrar Novo Equipamento (POST) ---
@app.route("/equipamentos", methods=["POST"])
def criar_equipamento():
    dados = request.json

    if not dados or "id_ativo" not in dados:
        return jsonify({"erro": "Dados incompletos. Informe o id_ativo."}), 400

    id_ativo = int(dados.get("id_ativo"))
    nome = dados.get("nome")
    responsavel = dados.get("responsavel")
    setor = dados.get("setor")
    tipo = dados.get("tipo")

    if id_ativo in sistema.equipamentos:
        return jsonify({"erro": "ID do equipamento já existe."}), 400

    novo_eq = sistema.criar_objeto_equipamento(id_ativo, nome, responsavel, setor, tipo)
    sistema.equipamentos[id_ativo] = novo_eq
    sistema.salvar_dados()

    return (
        jsonify(
            {
                "mensagem": f"Equipamento '{nome}' cadastrado com sucesso!",
                "equipamento": novo_eq.to_dict(),
            }
        ),
        201,
    )


# --- ROTA 3: Atualizar Equipamento Existente (PUT) ---
@app.route("/equipamentos/<int:id_ativo>", methods=["PUT"])
def atualizar_equipamento(id_ativo):
    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento não encontrado para atualização."}), 404

    dados = request.json
    eq_atual = sistema.equipamentos[id_ativo]

    novo_nome = dados.get("nome", eq_atual.nome)
    novo_resp = dados.get("responsavel", eq_atual.responsavel)
    novo_setor = dados.get("setor", eq_atual.setor)
    novo_tipo = dados.get("tipo", eq_atual.tipo)

    eq_atualizado = sistema.criar_objeto_equipamento(
        id_ativo, novo_nome, novo_resp, novo_setor, novo_tipo
    )

    # Mantém as vulnerabilidades e dependências que o equipamento já tinha
    eq_atualizado.vulnerabilidades_ids = eq_atual.vulnerabilidades_ids
    eq_atualizado.dependencias = eq_atual.dependencias

    sistema.equipamentos[id_ativo] = eq_atualizado
    sistema.salvar_dados()

    return (
        jsonify(
            {
                "mensagem": f"Equipamento {id_ativo} atualizado com sucesso!",
                "equipamento": eq_atualizado.to_dict(),
            }
        ),
        200,
    )


# --- ROTA 4: Apagar Equipamento (DELETE) ---
@app.route("/equipamentos/<int:id_ativo>", methods=["DELETE"])
def deletar_equipamento(id_ativo):
    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento não encontrado para exclusão."}), 404

    removido = sistema.equipamentos.pop(id_ativo)

    # Remove também qualquer dependência que outros ativos tinham com este ID
    for eq in sistema.equipamentos.values():
        if str(id_ativo) in eq.dependencias:
            del eq.dependencias[str(id_ativo)]

    sistema.salvar_dados()

    return (
        jsonify(
            {
                "mensagem": f"Equipamento '{removido.nome}' (ID {id_ativo}) removido com sucesso!"
            }
        ),
        200,
    )


# --- ROTA 5: Listar Vulnerabilidades (GET) ---
@app.route("/vulnerabilidades", methods=["GET"])
def obter_vulnerabilidades():
    lista_vul = [vul.to_dict() for vul in sistema.vulnerabilidades.values()]
    return jsonify(lista_vul), 200


# --- ROTA 6: Cadastrar e Associar Vulnerabilidade (POST) ---
@app.route("/vulnerabilidades", methods=["POST"])
def criar_vulnerabilidade():
    dados = request.json
    if not dados or "id_vul" not in dados or "id_ativo" not in dados:
        return (
            jsonify({"erro": "Informe o ID da vulnerabilidade e o ID do equipamento."}),
            400,
        )

    id_vul = int(dados.get("id_vul"))
    id_ativo = int(dados.get("id_ativo"))

    if id_ativo not in sistema.equipamentos:
        return jsonify({"erro": "Equipamento informado não existe."}), 404

    # Se a vulnerabilidade ainda não existir, cria uma nova
    if id_vul not in sistema.vulnerabilidades:
        descricao = dados.get("descricao", "Sem descrição")
        categoria = dados.get("categoria", "Geral")
        severidade = float(dados.get("severidade", 1.0))
        sistema.vulnerabilidades[id_vul] = Vulnerabilidade(
            id_vul, descricao, categoria, severidade
        )

    # Associa a vulnerabilidade ao equipamento (Matriz M)
    eq = sistema.equipamentos[id_ativo]
    if id_vul not in eq.vulnerabilidades_ids:
        eq.vulnerabilidades_ids.append(id_vul)

    sistema.salvar_dados()
    return (
        jsonify({"mensagem": "Vulnerabilidade registrada e associada com sucesso!"}),
        201,
    )


# --- ROTA 7: Cadastrar Dependência entre Equipamentos (POST) ---
@app.route("/dependencias", methods=["POST"])
def criar_dependencia():
    dados = request.json
    if (
        not dados
        or "id_origem" not in dados
        or "id_destino" not in dados
        or "peso" not in dados
    ):
        return jsonify({"erro": "Dados de dependência incompletos."}), 400

    id_origem = int(dados.get("id_origem"))
    id_destino = int(dados.get("id_destino"))
    peso = float(dados.get("peso"))

    if id_origem not in sistema.equipamentos or id_destino not in sistema.equipamentos:
        return jsonify({"erro": "Um ou ambos os equipamentos não existem."}), 404

    # Regra da diagonal principal: um equipamento não pode depender de si mesmo (A_ii = 0)
    if id_origem == id_destino:
        return (
            jsonify(
                {
                    "erro": "Um equipamento não pode depender de si mesmo (A_ii deve ser 0)."
                }
            ),
            400,
        )

    if peso <= 0 or peso >= 1:
        return (
            jsonify({"erro": "A fração de risco deve estar entre 0 e 1 (ex: 0.25)."}),
            400,
        )

    eq = sistema.equipamentos[id_origem]
    soma_atual = sum(
        float(v) for k, v in eq.dependencias.items() if k != str(id_destino)
    )

    # Garante que a soma da linha seja < 1 para a matriz (I - A) ser invertível
    if soma_atual + peso >= 1.0:
        return (
            jsonify(
                {
                    "erro": f"Soma das dependências ({soma_atual + peso:.2f}) deve ser menor que 1.0."
                }
            ),
            400,
        )

    eq.dependencias[str(id_destino)] = peso
    sistema.salvar_dados()
    return jsonify({"mensagem": "Dependência registrada com sucesso!"}), 201


# --- ROTA 8: Calcular Risco Total com NumPy (GET) ---
@app.route("/risco", methods=["GET"])
def relatorio_risco():
    resultados = sistema.calcular_analise_risco_api()

    if isinstance(resultados, dict) and "erro" in resultados:
        return jsonify(resultados), 400

    return jsonify(resultados), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
