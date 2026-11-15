# Camada de Serviços: Concentra as regras de negócio, cadastros, associações e cálculos com NumPy
import numpy as np
from dominio import Vulnerabilidade, fabricar_equipamento
from persistencia import RepositorioJSON


class ServicoInventario:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioJSON()
        self.equipamentos = {}
        self.vulnerabilidades = {}
        self.carregar_dados()

    # Cria o objeto do equipamento de acordo com a sua categoria
    def criar_objeto_equipamento(self, id_ativo, nome, responsavel, setor, tipo):
        return fabricar_equipamento(id_ativo, nome, responsavel, setor, tipo)

    # Aciona a camada de persistência para gravar os dados em JSON
    def salvar_dados(self):
        self.repositorio.salvar(self.equipamentos, self.vulnerabilidades)

    # Aciona a camada de persistência para ler os dados do JSON
    def carregar_dados(self):
        self.equipamentos, self.vulnerabilidades = self.repositorio.carregar()

    # Regra de serviço para cadastrar um novo equipamento
    def registrar_equipamento(self, id_ativo, nome, responsavel, setor, tipo):
        id_ativo = int(id_ativo)
        if id_ativo in self.equipamentos:
            raise ValueError("ID do equipamento já existe.")
        novo_eq = self.criar_objeto_equipamento(
            id_ativo, nome, responsavel, setor, tipo
        )
        self.equipamentos[id_ativo] = novo_eq
        self.salvar_dados()
        return novo_eq

    # Regra de serviço para criar e associar uma vulnerabilidade a um equipamento
    def associar_vulnerabilidade(
        self,
        id_vul,
        id_ativo,
        descricao="Sem descrição",
        categoria="Geral",
        severidade=1.0,
    ):
        id_vul = int(id_vul)
        id_ativo = int(id_ativo)

        if id_ativo not in self.equipamentos:
            raise LookupError("Equipamento informado não existe.")

        if id_vul not in self.vulnerabilidades:
            self.vulnerabilidades[id_vul] = Vulnerabilidade(
                id_vul, descricao, categoria, float(severidade)
            )

        eq = self.equipamentos[id_ativo]
        if id_vul not in eq.vulnerabilidades_ids:
            eq.vulnerabilidades_ids.append(id_vul)

        self.salvar_dados()
        return self.vulnerabilidades[id_vul]

    # Regra de serviço para validar e registrar dependência entre equipamentos
    def registrar_dependencia(self, id_origem, id_destino, peso):
        id_origem = int(id_origem)
        id_destino = int(id_destino)
        peso = float(peso)

        if id_origem not in self.equipamentos or id_destino not in self.equipamentos:
            raise LookupError("Um ou ambos os equipamentos não existem.")

        if id_origem == id_destino:
            raise ValueError(
                "Um equipamento não pode depender de si mesmo (A_ii deve ser 0)."
            )

        if peso <= 0 or peso >= 1:
            raise ValueError("A fração de risco deve estar entre 0 e 1 (ex: 0.25).")

        eq = self.equipamentos[id_origem]
        soma_atual = sum(
            float(v) for k, v in eq.dependencias.items() if k != str(id_destino)
        )

        if soma_atual + peso >= 1.0:
            raise ValueError(
                f"Soma das dependências ({soma_atual + peso:.2f}) deve ser menor que 1.0."
            )

        eq.dependencias[str(id_destino)] = peso
        self.salvar_dados()

    # Monta as matrizes e resolve o sistema linear (I - A)x = b com NumPy
    def calcular_analise_risco_api(self):
        lista_eq = list(self.equipamentos.values())
        lista_vul = list(self.vulnerabilidades.values())

        n = len(lista_eq)
        m = len(lista_vul)

        if n == 0 or m == 0:
            return {
                "erro": "É necessário ter pelo menos um equipamento e uma vulnerabilidade cadastrados."
            }

        mapa_idx_eq = {eq.id_ativo: i for i, eq in enumerate(lista_eq)}
        mapa_idx_vul = {vul.id_vul: j for j, vul in enumerate(lista_vul)}

        M = np.zeros((n, m), dtype=np.float64)
        v = np.zeros((m, 1), dtype=np.float64)

        for j, vul in enumerate(lista_vul):
            v[j, 0] = vul.severidade

        for i, eq in enumerate(lista_eq):
            for id_vul in eq.vulnerabilidades_ids:
                if id_vul in mapa_idx_vul:
                    j = mapa_idx_vul[id_vul]
                    M[i, j] = 1.0

        fatores = np.array([eq.fator_exposicao() for eq in lista_eq]).reshape(-1, 1)
        b = (M @ v) * fatores

        A = np.zeros((n, n), dtype=np.float64)
        for i, eq in enumerate(lista_eq):
            for id_destino_str, peso in eq.dependencias.items():
                id_destino = int(id_destino_str)
                if id_destino in mapa_idx_eq:
                    k = mapa_idx_eq[id_destino]
                    A[i, k] = float(peso)

        I = np.eye(n, dtype=np.float64)
        matriz_sistema = I - A

        determinante = float(np.linalg.det(matriz_sistema))
        numero_condicao = float(np.linalg.cond(matriz_sistema))

        if abs(determinante) < 1e-9 or numero_condicao > 1e12:
            return {
                "erro": "O sistema linear (I - A) não é invertível ou é numericamente instável.",
                "determinante": determinante,
                "numero_condicao": numero_condicao,
            }

        x = np.linalg.solve(matriz_sistema, b)

        relatorio = []
        for i, eq in enumerate(lista_eq):
            risco_proprio = round(float(b[i, 0]), 2)
            risco_efetivo = round(float(x[i, 0]), 2)
            relatorio.append(
                {
                    "id_ativo": eq.id_ativo,
                    "nome": eq.nome,
                    "tipo": eq.tipo,
                    "fator_exposicao": eq.fator_exposicao(),
                    "risco_proprio": risco_proprio,
                    "risco_efetivo": risco_efetivo,
                    "risco_total": risco_efetivo,
                }
            )

        return {
            "invertivel": True,
            "determinante": round(determinante, 6),
            "numero_condicao": round(numero_condicao, 4),
            "equipamentos": relatorio,
        }
