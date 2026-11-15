import numpy as np
from dominio import Vulnerabilidade, fabricar_equipamento
from persistencia import InterfaceRepositorio, RepositorioJSON

class CalculadoraRisco:
    def calcular(self, equipamentos, vulnerabilidades):
        lista_eq = list(equipamentos.values())
        lista_vul = list(vulnerabilidades.values())
        n, m = len(lista_eq), len(lista_vul)
        if n == 0 or m == 0:
            return {"erro": "É necessário ter pelo menos um equipamento e uma vulnerabilidade cadastrados."}
        mapa_eq = {eq.id_ativo: i for i, eq in enumerate(lista_eq)}
        mapa_vul = {v.id_vul: j for j, v in enumerate(lista_vul)}
        M = np.zeros((n, m), dtype=np.float64)
        v = np.zeros((m, 1), dtype=np.float64)
        for j, vul in enumerate(lista_vul): v[j, 0] = vul.severidade
        for i, eq in enumerate(lista_eq):
            for id_v in eq.vulnerabilidades_ids:
                if id_v in mapa_vul: M[i, mapa_vul[id_v]] = 1.0
        fatores = np.array([eq.fator_exposicao() for eq in lista_eq]).reshape(-1, 1)
        b = (M @ v) * fatores
        A = np.zeros((n, n), dtype=np.float64)
        for i, eq in enumerate(lista_eq):
            for dst, peso in eq.dependencias.items():
                if int(dst) in mapa_eq: A[i, mapa_eq[int(dst)]] = float(peso)
        matriz = np.eye(n, dtype=np.float64) - A
        det = float(np.linalg.det(matriz))
        cond = float(np.linalg.cond(matriz))
        if abs(det) < 1e-9 or cond > 1e12:
            return {"erro": "O sistema linear (I - A) não é invertível.", "determinante": det, "numero_condicao": cond}
        x = np.linalg.solve(matriz, b)
        rel = []
        for i, eq in enumerate(lista_eq):
            rp, re = round(float(b[i, 0]), 2), round(float(x[i, 0]), 2)
            rel.append({"id_ativo": eq.id_ativo, "nome": eq.nome, "tipo": eq.tipo, "fator_exposicao": eq.fator_exposicao(), "risco_proprio": rp, "risco_efetivo": re, "risco_total": re})
        return {"invertivel": True, "determinante": round(det, 6), "numero_condicao": round(cond, 4), "equipamentos": rel}

class ServicoInventario:
    def __init__(self, repositorio: InterfaceRepositorio = None, calculadora: CalculadoraRisco = None):
        self.repositorio = repositorio if repositorio is not None else RepositorioJSON()
        self.calculadora = calculadora if calculadora is not None else CalculadoraRisco()
        self.equipamentos, self.vulnerabilidades = {}, {}
        self.carregar_dados()
    def definir_repositorio(self, novo_repo: InterfaceRepositorio):
        self.repositorio = novo_repo
        self.carregar_dados()
    def criar_objeto_equipamento(self, id_ativo, nome, responsavel, setor, tipo):
        return fabricar_equipamento(id_ativo, nome, responsavel, setor, tipo)
    def salvar_dados(self):
        self.repositorio.salvar(self.equipamentos, self.vulnerabilidades)
    def carregar_dados(self):
        self.equipamentos, self.vulnerabilidades = self.repositorio.carregar()
    def registrar_equipamento(self, id_ativo, nome, responsavel, setor, tipo):
        id_ativo = int(id_ativo)
        if id_ativo in self.equipamentos: raise ValueError("ID já existe.")
        eq = self.criar_objeto_equipamento(id_ativo, nome, responsavel, setor, tipo)
        self.equipamentos[id_ativo] = eq
        self.salvar_dados()
        return eq
    def associar_vulnerabilidade(self, id_vul, id_ativo, descricao="Sem descrição", categoria="Geral", severidade=1.0):
        id_vul, id_ativo = int(id_vul), int(id_ativo)
        if id_ativo not in self.equipamentos: raise LookupError("Equipamento não existe.")
        if id_vul not in self.vulnerabilidades:
            self.vulnerabilidades[id_vul] = Vulnerabilidade(id_vul, descricao, categoria, float(severidade))
        eq = self.equipamentos[id_ativo]
        if id_vul not in eq.vulnerabilidades_ids: eq.vulnerabilidades_ids.append(id_vul)
        self.salvar_dados()
        return self.vulnerabilidades[id_vul]
    def registrar_dependencia(self, id_origem, id_destino, peso):
        id_origem, id_destino, peso = int(id_origem), int(id_destino), float(peso)
        if id_origem not in self.equipamentos or id_destino not in self.equipamentos: raise LookupError("Equipamento não existe.")
        if id_origem == id_destino: raise ValueError("A_ii deve ser 0.")
        if peso <= 0 or peso >= 1: raise ValueError("Fração deve estar entre 0 e 1.")
        eq = self.equipamentos[id_origem]
        soma = sum(float(v) for k, v in eq.dependencias.items() if k != str(id_destino))
        if soma + peso >= 1.0: raise ValueError("Soma das dependências deve ser < 1.0.")
        eq.dependencias[str(id_destino)] = peso
        self.salvar_dados()
    def calcular_analise_risco_api(self):
        return self.calculadora.calcular(self.equipamentos, self.vulnerabilidades)
