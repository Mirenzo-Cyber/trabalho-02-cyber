-- =========================================================================
-- S4_06: Script SQL de Criação das Tabelas e Consultas com Junções (JOINs)
-- =========================================================================

-- 1. Tabela de Equipamentos (Ativos)
CREATE TABLE IF NOT EXISTS equipamentos (
    id_ativo INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    responsavel TEXT NOT NULL,
    setor TEXT NOT NULL,
    tipo TEXT NOT NULL,
    fator_exposicao REAL NOT NULL
);

-- 2. Tabela de Vulnerabilidades
CREATE TABLE IF NOT EXISTS vulnerabilidades (
    id_vul INTEGER PRIMARY KEY,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    severidade REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Aberta'
);

-- 3. Tabela Associativa (N:N) entre Equipamentos e Vulnerabilidades
-- Comparação com o modelo de risco (Item 6): Cada par (id_ativo, id_vul) nesta tabela equivale a M[i, j] = 1.0 na Matriz de Incidência M!
CREATE TABLE IF NOT EXISTS equipamento_vulnerabilidade (
    id_ativo INTEGER NOT NULL,
    id_vul INTEGER NOT NULL,
    PRIMARY KEY (id_ativo, id_vul),
    FOREIGN KEY (id_ativo) REFERENCES equipamentos(id_ativo) ON DELETE CASCADE,
    FOREIGN KEY (id_vul) REFERENCES vulnerabilidades(id_vul) ON DELETE CASCADE
);

-- 4. Tabela de Dependências entre Equipamentos (representa a Matriz A de propagação de risco)
CREATE TABLE IF NOT EXISTS dependencias_equipamentos (
    id_origem INTEGER NOT NULL,
    id_destino INTEGER NOT NULL,
    peso REAL NOT NULL CHECK (peso > 0 AND peso < 1),
    PRIMARY KEY (id_origem, id_destino),
    FOREIGN KEY (id_origem) REFERENCES equipamentos(id_ativo) ON DELETE CASCADE,
    FOREIGN KEY (id_destino) REFERENCES equipamentos(id_ativo) ON DELETE CASCADE
);

-- =========================================================================
-- CONJUNTO DE CONSULTAS COM JUNÇÕES COMENTADAS
-- =========================================================================

-- Consulta 1 (INNER JOIN): Lista cada vulnerabilidade junto com os equipamentos afetados por ela
SELECT v.id_vul, v.descricao, v.severidade, e.id_ativo, e.nome AS nome_equipamento, e.tipo
FROM vulnerabilidades v
INNER JOIN equipamento_vulnerabilidade ev ON v.id_vul = ev.id_vul
INNER JOIN equipamentos e ON ev.id_ativo = e.id_ativo
ORDER BY v.severidade DESC, e.id_ativo ASC;

-- Consulta 2 (LEFT JOIN): Lista vulnerabilidades ainda não associadas a nenhum equipamento (órfãs)
SELECT v.id_vul, v.descricao, v.categoria, v.severidade
FROM vulnerabilidades v
LEFT JOIN equipamento_vulnerabilidade ev ON v.id_vul = ev.id_vul
WHERE ev.id_ativo IS NULL;

-- Consulta 3 (SELF JOIN / Autojunção): Lista as dependências entre equipamentos mostrando os nomes de origem e destino
SELECT e_orig.id_ativo AS id_dependente,
       e_orig.nome AS nome_dependente,
       e_dest.id_ativo AS id_fornecedor_risco,
       e_dest.nome AS nome_fornecedor_risco,
       d.peso AS fracao_risco
FROM dependencias_equipamentos d
INNER JOIN equipamentos e_orig ON d.id_origem = e_orig.id_ativo
INNER JOIN equipamentos e_dest ON d.id_destino = e_dest.id_ativo;

-- =========================================================================
-- S4_08: CRIAÇÃO DE ÍNDICES E ANÁLISE DE PLANO DE EXECUÇÃO (EXPLAIN QUERY PLAN)
-- =========================================================================

-- Antes do índice: realiza SCAN equipamentos (varredura sequencial O(n))
EXPLAIN QUERY PLAN SELECT id_ativo, nome, tipo FROM equipamentos WHERE setor = 'Data Center';

-- Criação dos índices aplicados ao Trabalho 02
CREATE INDEX IF NOT EXISTS idx_equipamentos_setor ON equipamentos(setor);
CREATE INDEX IF NOT EXISTS idx_equipamentos_tipo ON equipamentos(tipo);
CREATE INDEX IF NOT EXISTS idx_vulnerabilidades_severidade ON vulnerabilidades(severidade);

-- Depois do índice: realiza SEARCH equipamentos USING INDEX idx_equipamentos_setor (busca em árvore B O(log n))
EXPLAIN QUERY PLAN SELECT id_ativo, nome, tipo FROM equipamentos WHERE setor = 'Data Center';
