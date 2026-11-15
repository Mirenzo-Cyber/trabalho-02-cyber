# Camada de Persistência (S4_04): Escrita atômica, tratamento de JSON corrompido/vazio e reconstrução polimórfica
import json
import os
from abc import ABC, abstractmethod
from dominio import Vulnerabilidade, FabricaEquipamento


class InterfaceRepositorio(ABC):
    @abstractmethod
    def salvar(self, equipamentos, vulnerabilidades):
        pass

    @abstractmethod
    def carregar(self):
        pass


class RepositorioJSON(InterfaceRepositorio):
    def __init__(self, arq_eq="equipamentos.json", arq_vul="vulnerabilidades.json"):
        self.arq_eq = arq_eq
        self.arq_vul = arq_vul

    # Escrita atômica: grava primeiro em um arquivo temporário (.tmp) e depois substitui o original com os.replace
    def _gravar_atomico(self, caminho, dados):
        caminho_tmp = f"{caminho}.tmp"
        with open(caminho_tmp, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(caminho_tmp, caminho)

    # Salva os ativos e vulnerabilidades como array de objetos JSON com acentuação correta (ensure_ascii=False)
    def salvar(self, equipamentos, vulnerabilidades):
        lista_eq = [eq.to_dict() for eq in equipamentos.values()]
        lista_vul = [v.to_dict() for v in vulnerabilidades.values()]
        self._gravar_atomico(self.arq_eq, lista_eq)
        self._gravar_atomico(self.arq_vul, lista_vul)

    # Lê um arquivo JSON tratando arquivos ausentes, vazios ou corrompidos sem travar o sistema
    def _ler_lista_json(self, caminho):
        if not os.path.exists(caminho):
            return []
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if not conteudo:
                    return []
                dados = json.loads(conteudo)
                return dados if isinstance(dados, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    # Reconstrói os objetos das subclasses corretas preservando IDs, tipos, vulnerabilidades e dependências
    def carregar(self):
        equipamentos = {}
        vulnerabilidades = {}

        for d in self._ler_lista_json(self.arq_eq):
            if isinstance(d, dict) and "id_ativo" in d and "nome" in d and "tipo" in d:
                try:
                    eq = FabricaEquipamento.de_dicionario(d)
                    equipamentos[eq.id_ativo] = eq
                except (ValueError, TypeError, KeyError):
                    continue

        for d in self._ler_lista_json(self.arq_vul):
            if isinstance(d, dict) and "id_vul" in d and "descricao" in d and "severidade" in d:
                try:
                    vul = Vulnerabilidade(
                        d["id_vul"],
                        d["descricao"],
                        d.get("categoria", "Geral"),
                        d["severidade"],
                        d.get("status", "Aberta"),
                    )
                    vulnerabilidades[vul.id_vul] = vul
                except (ValueError, TypeError, KeyError):
                    continue

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
