# Camada de Domínio: Entidades, Objetos Hashable (S4_08) e Padrão Factory (S4_03)

class Vulnerabilidade:
    def __init__(self, id_vul, descricao, categoria, severidade, status="Aberta"):
        self.id_vul = int(id_vul)
        self.descricao = descricao
        self.categoria = categoria
        self.severidade = float(severidade)
        self.status = status

    # Permite usar Vulnerabilidade como chave de dicionário ou em conjuntos (set) (S4_08)
    def __hash__(self):
        return hash(self.id_vul)

    def __eq__(self, outro):
        return isinstance(outro, Vulnerabilidade) and self.id_vul == outro.id_vul

    def to_dict(self):
        return self.__dict__


class Equipamento:
    def __init__(self, id_ativo, nome, responsavel, setor, tipo):
        self.id_ativo = int(id_ativo)
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.tipo = tipo
        self.vulnerabilidades_ids = []
        self.dependencias = {}

    # Torna Equipamento utilizável como chave de dicionário (S4_08 - Item 4)
    # Cuidado necessário: usa apenas id_ativo (identificador imutável) para não quebrar o hash
    def __hash__(self):
        return hash(self.id_ativo)

    def __eq__(self, outro):
        return isinstance(outro, Equipamento) and self.id_ativo == outro.id_ativo

    def fator_exposicao(self):
        return 1.0

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


# Padrão Factory (S4_03): Centraliza a criação e reconstrução das subclasses corretas a partir do tipo ou JSON
class FabricaEquipamento:
    @staticmethod
    def criar(id_ativo, nome, responsavel, setor, tipo):
        cls = MAPA_TIPOS_EQUIPAMENTO.get(str(tipo).upper(), Equipamento)
        return cls(id_ativo, nome, responsavel, setor, str(tipo).upper())

    @staticmethod
    def de_dicionario(dados):
        eq = FabricaEquipamento.criar(
            dados["id_ativo"], dados["nome"], dados["responsavel"], dados["setor"], dados["tipo"]
        )
        eq.vulnerabilidades_ids = dados.get("vulnerabilidades_ids", [])
        eq.dependencias = dados.get("dependencias", {})
        return eq


def fabricar_equipamento(id_ativo, nome, responsavel, setor, tipo):
    return FabricaEquipamento.criar(id_ativo, nome, responsavel, setor, tipo)
