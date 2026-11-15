class Vulnerabilidade:
    def __init__(self, id_vul, descricao, categoria, severidade, status="Aberta"):
        self.id_vul = int(id_vul)
        self.descricao = descricao
        self.categoria = categoria
        self.severidade = float(severidade)
        self.status = status
    def to_dict(self): return self.__dict__

class Equipamento:
    def __init__(self, id_ativo, nome, responsavel, setor, tipo):
        self.id_ativo = int(id_ativo)
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.tipo = tipo
        self.vulnerabilidades_ids = []
        self.dependencias = {}
    def fator_exposicao(self): return 1.0
    def to_dict(self):
        return {
            "id_ativo": self.id_ativo, "nome": self.nome, "responsavel": self.responsavel,
            "setor": self.setor, "tipo": self.tipo, "fator_exposicao": self.fator_exposicao(),
            "vulnerabilidades_ids": self.vulnerabilidades_ids, "dependencias": self.dependencias,
        }

class Computador(Equipamento):
    def fator_exposicao(self): return 1.0
class Notebook(Equipamento):
    def fator_exposicao(self): return 1.2
class Servidor(Equipamento):
    def fator_exposicao(self): return 1.5
class Switch(Equipamento):
    def fator_exposicao(self): return 1.3
class Firewall(Equipamento):
    def fator_exposicao(self): return 1.4

MAPA_TIPOS_EQUIPAMENTO = {
    "COMPUTADORES": Computador, "NOTEBOOKS": Notebook,
    "SERVIDORES": Servidor, "SWITCHES": Switch, "FIREWALLS": Firewall,
}

def fabricar_equipamento(id_ativo, nome, responsavel, setor, tipo):
    cls = MAPA_TIPOS_EQUIPAMENTO.get(str(tipo).upper(), Equipamento)
    return cls(id_ativo, nome, responsavel, setor, str(tipo).upper())
