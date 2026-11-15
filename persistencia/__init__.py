import json
from abc import ABC, abstractmethod
from dominio import Vulnerabilidade, fabricar_equipamento

class InterfaceRepositorio(ABC):
    @abstractmethod
    def salvar(self, equipamentos, vulnerabilidades): pass
    @abstractmethod
    def carregar(self): pass

class RepositorioJSON(InterfaceRepositorio):
    def __init__(self, arq_eq="equipamentos.json", arq_vul="vulnerabilidades.json"):
        self.arq_eq = arq_eq
        self.arq_vul = arq_vul
    def salvar(self, equipamentos, vulnerabilidades):
        with open(self.arq_eq, "w", encoding="utf-8") as f:
            json.dump([eq.to_dict() for eq in equipamentos.values()], f, indent=4, ensure_ascii=False)
        with open(self.arq_vul, "w", encoding="utf-8") as f:
            json.dump([v.to_dict() for v in vulnerabilidades.values()], f, indent=4, ensure_ascii=False)
    def carregar(self):
        equipamentos, vulnerabilidades = {}, {}
        try:
            with open(self.arq_eq, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    eq = fabricar_equipamento(d["id_ativo"], d["nome"], d["responsavel"], d["setor"], d["tipo"])
                    eq.vulnerabilidades_ids = d.get("vulnerabilidades_ids", [])
                    eq.dependencias = d.get("dependencias", {})
                    equipamentos[eq.id_ativo] = eq
        except FileNotFoundError: pass
        try:
            with open(self.arq_vul, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    vul = Vulnerabilidade(d["id_vul"], d["descricao"], d["categoria"], d["severidade"], d.get("status", "Aberta"))
                    vulnerabilidades[vul.id_vul] = vul
        except FileNotFoundError: pass
        return equipamentos, vulnerabilidades

class RepositorioMemoria(InterfaceRepositorio):
    def __init__(self):
        self._eq = {}
        self._vul = {}
    def salvar(self, equipamentos, vulnerabilidades):
        self._eq = dict(equipamentos)
        self._vul = dict(vulnerabilidades)
    def carregar(self):
        return dict(self._eq), dict(self._vul)
