# Módulo Python de Persistência Relacional e Consultas SQL Parametrizadas (S4_06)
import sqlite3
from dominio import Vulnerabilidade, FabricaEquipamento
from persistencia import InterfaceRepositorio


class RepositorioSQLite(InterfaceRepositorio):
    def __init__(self, caminho_banco="inventario.db"):
        self.caminho_banco = caminho_banco
        self.criar_tabelas()

    # Abre conexão com o banco SQLite e ativa chaves estrangeiras
    def _conectar(self):
        conn = sqlite3.connect(self.caminho_banco)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # Cria as 4 tabelas relacionais do banco de dados
    def criar_tabelas(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS equipamentos ("
                "id_ativo INTEGER PRIMARY KEY, nome TEXT NOT NULL, responsavel TEXT NOT NULL, "
                "setor TEXT NOT NULL, tipo TEXT NOT NULL, fator_exposicao REAL NOT NULL)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS vulnerabilidades ("
                "id_vul INTEGER PRIMARY KEY, descricao TEXT NOT NULL, categoria TEXT NOT NULL, "
                "severidade REAL NOT NULL, status TEXT NOT NULL DEFAULT 'Aberta')"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS equipamento_vulnerabilidade ("
                "id_ativo INTEGER NOT NULL, id_vul INTEGER NOT NULL, PRIMARY KEY (id_ativo, id_vul), "
                "FOREIGN KEY (id_ativo) REFERENCES equipamentos(id_ativo) ON DELETE CASCADE, "
                "FOREIGN KEY (id_vul) REFERENCES vulnerabilidades(id_vul) ON DELETE CASCADE)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS dependencias_equipamentos ("
                "id_origem INTEGER NOT NULL, id_destino INTEGER NOT NULL, peso REAL NOT NULL, "
                "PRIMARY KEY (id_origem, id_destino), "
                "FOREIGN KEY (id_origem) REFERENCES equipamentos(id_ativo) ON DELETE CASCADE, "
                "FOREIGN KEY (id_destino) REFERENCES equipamentos(id_ativo) ON DELETE CASCADE)"
            )
            conn.commit()

    # Salva os dados usando apenas parâmetros '?' e respeitando a ordem das chaves estrangeiras
    def salvar(self, equipamentos, vulnerabilidades):
        with self._conectar() as conn:
            cursor = conn.cursor()
            # 1. Limpa primeiro as tabelas associativas (filhas) e depois as tabelas principais (pais)
            cursor.execute("DELETE FROM equipamento_vulnerabilidade")
            cursor.execute("DELETE FROM dependencias_equipamentos")
            cursor.execute("DELETE FROM equipamentos")
            cursor.execute("DELETE FROM vulnerabilidades")

            # 2. Insere TODAS as vulnerabilidades primeiro
            for vul in vulnerabilidades.values():
                cursor.execute(
                    "INSERT INTO vulnerabilidades (id_vul, descricao, categoria, severidade, status) VALUES (?, ?, ?, ?, ?)",
                    (vul.id_vul, vul.descricao, vul.categoria, vul.severidade, vul.status),
                )

            # 3. Insere TODOS os equipamentos antes de gravar qualquer vínculo ou dependência
            for eq in equipamentos.values():
                cursor.execute(
                    "INSERT INTO equipamentos (id_ativo, nome, responsavel, setor, tipo, fator_exposicao) VALUES (?, ?, ?, ?, ?, ?)",
                    (eq.id_ativo, eq.nome, eq.responsavel, eq.setor, eq.tipo, eq.fator_exposicao()),
                )

            # 4. Agora que todos os equipamentos e vulnerabilidades já existem no banco, insere os vínculos e dependências
            for eq in equipamentos.values():
                for id_vul in eq.vulnerabilidades_ids:
                    cursor.execute(
                        "INSERT OR IGNORE INTO equipamento_vulnerabilidade (id_ativo, id_vul) VALUES (?, ?)",
                        (eq.id_ativo, int(id_vul)),
                    )
                for id_dest, peso in eq.dependencias.items():
                    cursor.execute(
                        "INSERT INTO dependencias_equipamentos (id_origem, id_destino, peso) VALUES (?, ?, ?)",
                        (eq.id_ativo, int(id_dest), float(peso)),
                    )
            conn.commit()

    # Carrega os dados das tabelas SQL e reconstrói os objetos na memória
    def carregar(self):
        equipamentos = {}
        vulnerabilidades = {}
        with self._conectar() as conn:
            cursor = conn.cursor()
            for row in cursor.execute("SELECT id_vul, descricao, categoria, severidade, status FROM vulnerabilidades"):
                vul = Vulnerabilidade(row[0], row[1], row[2], row[3], row[4])
                vulnerabilidades[vul.id_vul] = vul

            for row in cursor.execute("SELECT id_ativo, nome, responsavel, setor, tipo FROM equipamentos"):
                eq = FabricaEquipamento.criar(row[0], row[1], row[2], row[3], row[4])
                equipamentos[eq.id_ativo] = eq

            for row in cursor.execute("SELECT id_ativo, id_vul FROM equipamento_vulnerabilidade"):
                if row[0] in equipamentos:
                    equipamentos[row[0]].vulnerabilidades_ids.append(row[1])

            for row in cursor.execute("SELECT id_origem, id_destino, peso FROM dependencias_equipamentos"):
                if row[0] in equipamentos:
                    equipamentos[row[0]].dependencias[str(row[1])] = float(row[2])

        return equipamentos, vulnerabilidades

    # Consulta 1 (INNER JOIN parametrizado): Lista cada vulnerabilidade com os equipamentos afetados
    def listar_vulnerabilidades_com_equipamentos(self, severidade_minima=0.0):
        sql = (
            "SELECT v.id_vul, v.descricao, v.severidade, e.id_ativo, e.nome, e.tipo "
            "FROM vulnerabilidades v "
            "INNER JOIN equipamento_vulnerabilidade ev ON v.id_vul = ev.id_vul "
            "INNER JOIN equipamentos e ON ev.id_ativo = e.id_ativo "
            "WHERE v.severidade >= ? "
            "ORDER BY v.severidade DESC, e.id_ativo ASC"
        )
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (float(severidade_minima),))
            return [
                {
                    "id_vul": r[0],
                    "descricao": r[1],
                    "severidade": r[2],
                    "id_ativo": r[3],
                    "nome_equipamento": r[4],
                    "tipo": r[5],
                }
                for r in cursor.fetchall()
            ]

    # Consulta 2 (LEFT JOIN parametrizado): Lista vulnerabilidades ainda não associadas a nenhum equipamento
    def listar_vulnerabilidades_sem_equipamento(self, status_filtro="Aberta"):
        sql = (
            "SELECT v.id_vul, v.descricao, v.categoria, v.severidade "
            "FROM vulnerabilidades v "
            "LEFT JOIN equipamento_vulnerabilidade ev ON v.id_vul = ev.id_vul "
            "WHERE ev.id_ativo IS NULL AND v.status = ? "
            "ORDER BY v.id_vul ASC"
        )
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (str(status_filtro),))
            return [
                {"id_vul": r[0], "descricao": r[1], "categoria": r[2], "severidade": r[3]}
                for r in cursor.fetchall()
            ]

    # Consulta 3 (SELF JOIN / Autojunção parametrizada): Lista dependências entre equipamentos
    def listar_dependencias_autojuncao(self, peso_minimo=0.0):
        sql = (
            "SELECT e_orig.id_ativo, e_orig.nome, e_dest.id_ativo, e_dest.nome, d.peso "
            "FROM dependencias_equipamentos d "
            "INNER JOIN equipamentos e_orig ON d.id_origem = e_orig.id_ativo "
            "INNER JOIN equipamentos e_dest ON d.id_destino = e_dest.id_ativo "
            "WHERE d.peso >= ? "
            "ORDER BY d.peso DESC"
        )
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (float(peso_minimo),))
            return [
                {
                    "id_origem": r[0],
                    "nome_origem": r[1],
                    "id_destino": r[2],
                    "nome_destino": r[3],
                    "peso": r[4],
                }
                for r in cursor.fetchall()
            ]
