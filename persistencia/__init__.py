# Camada de Persistência: Cuida apenas de salvar e carregar dados nos arquivos JSON
import json
from dominio import Vulnerabilidade, fabricar_equipamento


class RepositorioJSON:
    def __init__(self, arq_eq="equipamentos.json", arq_vul="vulnerabilidades.json"):
        self.arq_eq = arq_eq
        self.arq_vul = arq_vul

    # Salva os dicionários de equipamentos e vulnerabilidades nos arquivos JSON
    def salvar(self, equipamentos, vulnerabilidades):
        with open(self.arq_eq, "w", encoding="utf-8") as f:
            lista_eq = [eq.to_dict() for eq in equipamentos.values()]
            json.dump(lista_eq, f, indent=4, ensure_ascii=False)

        with open(self.arq_vul, "w", encoding="utf-8") as f:
            lista_vul = [vul.to_dict() for vul in vulnerabilidades.values()]
            json.dump(lista_vul, f, indent=4, ensure_ascii=False)

    # Lê os arquivos JSON e reconstrói os objetos na memória
    def carregar(self):
        equipamentos = {}
        vulnerabilidades = {}

        try:
            with open(self.arq_eq, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    eq = fabricar_equipamento(
                        d["id_ativo"],
                        d["nome"],
                        d["responsavel"],
                        d["setor"],
                        d["tipo"],
                    )
                    eq.vulnerabilidades_ids = d.get("vulnerabilidades_ids", [])
                    eq.dependencias = d.get("dependencias", {})
                    equipamentos[eq.id_ativo] = eq
        except FileNotFoundError:
            pass

        try:
            with open(self.arq_vul, "r", encoding="utf-8") as f:
                for d in json.load(f):
                    vul = Vulnerabilidade(
                        d["id_vul"],
                        d["descricao"],
                        d["categoria"],
                        d["severidade"],
                        d.get("status", "Aberta"),
                    )
                    vulnerabilidades[vul.id_vul] = vul
        except FileNotFoundError:
            pass

        return equipamentos, vulnerabilidades
