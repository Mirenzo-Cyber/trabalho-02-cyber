-- =====================================================================
-- TRABALHO 02 - SPRINT S4_07: CONSULTAS DE RELATÓRIO E AGREGAÇÕES (GROUP BY)
-- =====================================================================
-- 1. Contar quantas vulnerabilidades afetam cada equipamento.
SELECT
    e.id AS equipamento_id,
    e.nome AS equipamento_nome,
    COUNT(v.id) AS total_vulnerabilidades
FROM
    equipamentos e
    LEFT JOIN vulnerabilidades v ON e.id = v.equipamento_id
GROUP BY
    e.id,
    e.nome;

-- 2. Classificar as vulnerabilidades nas faixas do CVSS (baixa, média, alta e crítica) com CASE e contar quantas há em cada faixa.
SELECT
    CASE
        WHEN v.cvss_score < 4.0 THEN 'Baixa'
        WHEN v.cvss_score >= 4.0
        AND v.cvss_score < 7.0 THEN 'Média'
        WHEN v.cvss_score >= 7.0
        AND v.cvss_score < 9.0 THEN 'Alta'
        ELSE 'Crítica'
    END AS faixa_cvss,
    COUNT(v.id) AS quantidade_vulnerabilidades
FROM
    vulnerabilidades v
GROUP BY
    faixa_cvss;

-- 3. Calcular a soma das notas CVSS por equipamento e comparar com o risco próprio calculado em Python.
SELECT
    e.id AS equipamento_id,
    e.nome AS equipamento_nome,
    SUM(v.cvss_score) AS soma_cvss
FROM
    equipamentos e
    LEFT JOIN vulnerabilidades v ON e.id = v.equipamento_id
GROUP BY
    e.id,
    e.nome;

-- 4. Listar apenas os equipamentos com soma CVSS acima de um limite (HAVING).
SELECT
    e.id AS equipamento_id,
    e.nome AS equipamento_nome,
    SUM(v.cvss_score) AS soma_cvss
FROM
    equipamentos e
    JOIN vulnerabilidades v ON e.id = v.equipamento_id
GROUP BY
    e.id,
    e.nome
HAVING
    SUM(v.cvss_score) > 15.0;

-- 5. Gerar um relatório com os cinco equipamentos de maior soma CVSS.
SELECT
    e.id AS equipamento_id,
    e.nome AS equipamento_nome,
    SUM(v.cvss_score) AS soma_cvss
FROM
    equipamentos e
    JOIN vulnerabilidades v ON e.id = v.equipamento_id
GROUP BY
    e.id,
    e.nome
ORDER BY
    soma_cvss DESC
LIMIT
    5;