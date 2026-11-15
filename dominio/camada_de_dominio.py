# Camada de Domínio: Define apenas os objetos e regras básicas (sem banco de dados ou tela)


class Vulnerabilidade:
    def __init__(self, id_vul, descricao, categoria, severidade, status="Aberta"):
        self.id_vul = int(id_vul)
        self.descricao = descricao
        self.categoria = categoria
        self.severidade = float(severidade)  # Nota de risco para o cálculo (vetor v)
        self.status = status

    # Transforma o objeto em dicionário para facilitar o uso na API e no JSON
    def to_dict(self):
        return self.__dict__


class Equipamento:
    def __init__(self, id_ativo, nome, responsavel, setor, tipo):
        self.id_ativo = int(id_ativo)
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.tipo = tipo
        self.vulnerabilidades_ids = []  # Lista de IDs de vulnerabilidades (Matriz M)
        self.dependencias = {}  # Dicionário {"id_alvo": peso} (Matriz A)

    # Polimorfismo: cada tipo de equipamento terá seu próprio multiplicador de risco
    def fator_exposicao(self):
        return 1.0

    # Organiza os dados do equipamento em formato de dicionário
    def to_dict(self):
        return {
            "id_ativo": self.id_ativo,
            "nome": self.nome,
            "responsavel": self.responsavel,
            "setor": self.setor,
            "tipo": self.tipo,
            "fator_exposicao": self.fator_exposicao(),
            "vulnerabilidades_ids": self.vulnerabilidades_ids,
            "dependencias": self.dependencias,
        }


# Subclasses que herdam de Equipamento e mudam apenas o fator de exposição
class Computador(Equipamento):
    def fator_exposicao(self):
        return 1.0


class Notebook(Equipamento):
    def fator_exposicao(self):
        return 1.2


class Servidor(Equipamento):
    def fator_exposicao(self):
        return 1.5


class Switch(Equipamento):
    def fator_exposicao(self):
        return 1.3


# Função auxiliar que cria o objeto da classe certa conforme o tipo escolhido
def fabricar_equipamento(id_ativo, nome, responsavel, setor, tipo):
    mapa_classes = {
        "COMPUTADORES": Computador,
        "NOTEBOOKS": Notebook,
        "SERVIDORES": Servidor,
        "SWITCHES": Switch,
    }
    classe_escolhida = mapa_classes.get(str(tipo).upper(), Equipamento)
    return classe_escolhida(id_ativo, nome, responsavel, setor, str(tipo).upper())
