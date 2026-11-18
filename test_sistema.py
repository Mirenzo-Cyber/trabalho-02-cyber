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

def test_solid():
    from dominio import Firewall, Equipamento
    from persistencia import RepositorioMemoria
    from servicos import ServicoInventario
    s = ServicoInventario(repositorio=RepositorioMemoria())
    fw = s.registrar_equipamento(99, "FW", "TI", "Rede", "FIREWALLS")
    assert isinstance(fw, Equipamento) and isinstance(fw, Firewall) and fw.fator_exposicao() == 1.4
    s.associar_vulnerabilidade(1, 99, "CVE", "Rede", 5.0)
    assert s.calcular_analise_risco_api()["equipamentos"][0]["risco_proprio"] == 7.0

def test_design_patterns_s4_03():
    from dominio import FabricaEquipamento, Servidor
    from persistencia import RepositorioMemoria
    from servicos import ServicoInventario, OrdenacaoPorRiscoEfetivo, estrategia_ordenar_por_nome
    eq = FabricaEquipamento.de_dicionario({"id_ativo": 10, "nome": "Z-Server", "responsavel": "TI", "setor": "Core", "tipo": "SERVIDORES"})
    assert isinstance(eq, Servidor) and eq.fator_exposicao() == 1.5
    s = ServicoInventario(repositorio=RepositorioMemoria())
    s.registrar_equipamento(1, "B-Ativo", "TI", "Rede", "COMPUTADORES")
    s.registrar_equipamento(2, "A-Ativo", "TI", "Rede", "SERVIDORES")
    s.associar_vulnerabilidade(1, 1, "V1", "Geral", 2.0)
    s.associar_vulnerabilidade(2, 2, "V2", "Geral", 8.0)
    rel_risco = s.calcular_analise_risco_api(estrategia_ordenacao=OrdenacaoPorRiscoEfetivo())
    assert rel_risco["equipamentos"][0]["id_ativo"] == 2
    rel_nome = s.calcular_analise_risco_api(estrategia_ordenacao=estrategia_ordenar_por_nome)
    assert rel_nome["equipamentos"][0]["nome"] == "A-Ativo"

def test_persistencia_json_s4_04(tmp_path):
    from dominio import Servidor, Firewall
    from persistencia import RepositorioJSON
    from servicos import ServicoInventario

    arq_eq = str(tmp_path / "eq_teste.json")
    arq_vul = str(tmp_path / "vul_teste.json")
    repo = RepositorioJSON(arq_eq=arq_eq, arq_vul=arq_vul)

    # 1. Testa gravação atômica e recarga preservando subclasses, acentuação e vínculos
    s1 = ServicoInventario(repositorio=repo)
    s1.registrar_equipamento(10, "Servidor de Aplicação", "João", "TI", "SERVIDORES")
    s1.registrar_equipamento(20, "Firewall de Perímetro", "Maria", "Segurança", "FIREWALLS")
    s1.associar_vulnerabilidade(500, 10, "Injeção de Comando", "Validação", 9.0)
    s1.registrar_dependencia(10, 20, 0.4)

    s2 = ServicoInventario(repositorio=repo)
    assert isinstance(s2.equipamentos[10], Servidor)
    assert isinstance(s2.equipamentos[20], Firewall)
    assert s2.equipamentos[10].vulnerabilidades_ids == [500]
    assert s2.equipamentos[10].dependencias == {"20": 0.4}
    assert s2.vulnerabilidades[500].descricao == "Injeção de Comando"

    # 2. Testa tratamento de arquivo corrompido ou vazio sem quebrar o sistema
    open(arq_eq, "w", encoding="utf-8").write("{json_corrompido_invalido")
    open(arq_vul, "w", encoding="utf-8").write("")
    eq_lidos, vul_lidos = repo.carregar()
    assert eq_lidos == {} and vul_lidos == {}


def test_health_s4_05():
    from app import app
    assert app.test_client().get("/health").status_code == 200

def test_sql_joins_parametrizados_s4_06(tmp_path):
    from dominio import Vulnerabilidade
    from consultas_sql import RepositorioSQLite
    from servicos import ServicoInventario

    banco_teste = str(tmp_path / "teste_s4_06.db")
    repo_sql = RepositorioSQLite(caminho_banco=banco_teste)
    servico = ServicoInventario(repositorio=repo_sql)

    servico.registrar_equipamento(1, "Servidor SQL", "DBA", "TI", "SERVIDORES")
    servico.registrar_equipamento(2, "Switch Core", "Redes", "Infra", "SWITCHES")
    servico.associar_vulnerabilidade(10, 1, "SQL Injection", "Web", 9.8)
    servico.vulnerabilidades[20] = Vulnerabilidade(20, "Porta Telnet Aberta", "Rede", 5.0)
    servico.registrar_dependencia(1, 2, 0.35)

    afetados = repo_sql.listar_vulnerabilidades_com_equipamentos(severidade_minima=8.0)
    assert len(afetados) == 1 and afetados[0]["id_vul"] == 10

    orfas = repo_sql.listar_vulnerabilidades_sem_equipamento(status_filtro="Aberta")
    assert len(orfas) == 1 and orfas[0]["id_vul"] == 20

    deps = repo_sql.listar_dependencias_autojuncao(peso_minimo=0.1)
    assert len(deps) == 1 and deps[0]["nome_origem"] == "Servidor SQL" and deps[0]["nome_destino"] == "Switch Core"

def test_hash_e_indices_s4_08(tmp_path):
    from dominio import Servidor, Computador
    from consultas_sql import RepositorioSQLite

    # 1. Testa uso de Equipamento como chave de dicionário (Item 4)
    srv1 = Servidor(1, "Srv-A", "TI", "Data Center", "SERVIDORES")
    srv1_copia = Computador(1, "Srv-A-Renomeado", "Outro", "Outro", "COMPUTADORES")
    mapa_alocacao = {srv1: "Rack Principal 01"}
    assert mapa_alocacao[srv1_copia] == "Rack Principal 01"

    # 2. Testa criação de índice e comparação com EXPLAIN QUERY PLAN (Item 5)
    banco = str(tmp_path / "teste_indices.db")
    repo = RepositorioSQLite(caminho_banco=banco)
    repo.salvar({1: srv1}, {})
    planos = repo.comparar_plano_execucao_indice("Data Center")
    assert "SCAN" in planos["antes_sem_indice"].upper()
    assert "SEARCH" in planos["depois_com_indice"].upper()
    assert "IDX_EQUIPAMENTOS_SETOR" in planos["depois_com_indice"].upper()
