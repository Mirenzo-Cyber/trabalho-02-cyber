# Importa as ferramentas de teste padrão do Python e o Pytest
import unittest
import pytest

# Importa as classes que criamos no arquivo trabalho_02.py
from trabalho_02 import Computador, Servidor, SistemaInventario

# Importa a nossa API Flask do arquivo app.py
from app import app


# =====================================================================
# PARTE 1: TESTES DE ORIENTAÇÃO A OBJETOS (Usando Unittest)
# =====================================================================
class TestEquipamentos(unittest.TestCase):

    def test_fator_exposicao_computador(self):
        # 1. Cria um computador de teste
        pc = Computador(10, "PC Admin", "Matheus", "TI", "COMPUTADORES")

        # 2. Verifica se o fator de exposição dele é 1.0
        self.assertEqual(pc.fator_exposicao(), 1.0)

    def test_fator_exposicao_servidor_polimorfismo(self):
        # 1. Cria um servidor de teste
        servidor = Servidor(11, "Servidor Web", "Matheus", "TI", "SERVIDORES")

        # 2. Verifica se o polimorfismo funcionou e o fator mudou para 1.5
        self.assertEqual(servidor.fator_exposicao(), 1.5)


# =====================================================================
# PARTE 2: TESTES DA API E MATRIZES NUMPY (Usando Pytest)
# =====================================================================


# Cria um "cliente virtual" para testar a API sem precisar ligar o Docker
@pytest.fixture
def cliente_api():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_rota_listar_equipamentos(cliente_api):
    # 1. Simula um acesso à rota de listar equipamentos (GET)
    resposta = cliente_api.get("/equipamentos")

    # 2. Verifica se a API respondeu com sucesso (código 200)
    assert resposta.status_code == 200


def test_calculo_risco_numpy():
    # 1. Inicia o sistema de inventário
    sistema = SistemaInventario()

    # 2. Roda a função que faz o cálculo matricial
    resultado = sistema.calcular_analise_risco_api()

    # 3. Verifica se a matriz (I - A) é invertível matematicamente
    assert resultado["invertivel"] == True

    # 4. Verifica se o determinante é diferente de zero
    assert resultado["determinante"] != 0
