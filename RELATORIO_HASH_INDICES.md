# ⚡ Relatório de Tabelas Hash, Índices SQL e Otimização de Consultas (S4_08)

## 1. Objetos de Domínio como Chave de Dicionário (`__hash__` e `__eq__`)
* **Implementação no Trabalho 02:** As classes `Equipamento` (e suas subclasses) e `Vulnerabilidade` em `dominio/` implementam `__hash__` e `__eq__` baseados exclusivamente em seus identificadores únicos (`id_ativo` e `id_vul`).
* **Cuidados Necessários:**
  1. **Imutabilidade dos atributos do hash:** O cálculo de `__hash__` jamais deve depender de atributos mutáveis (como `nome`, `setor` ou `vulnerabilidades_ids`). Se o hash de um objeto mudar depois de ele ser inserido como chave de um `dict` ou elemento de um `set`, o Python procurará no *bucket* errado e o objeto se tornará "inencontrável".
  2. **Contrato de consistência (`a == b` implica `hash(a) == hash(b)`):** Sempre que dois objetos são considerados iguais pelo método `__eq__`, eles obrigatoriamente precisam produzir o mesmo valor inteiro em `__hash__`.

---

## 2. Comparação de Planos de Execução (`EXPLAIN QUERY PLAN`) no Trabalho 02
Ao consultar ativos filtrando pela coluna `setor` (`SELECT id_ativo, nome, tipo FROM equipamentos WHERE setor = ?`):

| Cenário | Saída do `EXPLAIN QUERY PLAN` (SQLite) | Complexidade | Explicação |
| :--- | :--- | :--- | :--- |
| **Antes do Índice** | `SCAN equipamentos` | $O(n)$ | O banco percorre todas as linhas da tabela sequencialmente (*Full Table Scan*). |
| **Depois do Índice** | `SEARCH equipamentos USING INDEX idx_equipamentos_setor (setor=?)` | $O(\log n)$ | O banco navega diretamente pela estrutura B-Tree do índice `idx_equipamentos_setor`. |

---

## 3. Comparação de Tempos de Busca (100.000 Elementos)
Os testes de desempenho para **100.000 elementos** comparando busca sequencial em `list` ($O(n)$) contra busca por chave em tabela hash / `dict` ($O(1)$ médio) demonstram:
* **Lista Sequencial (`list` - $O(n)$):** Percorre até 100.000 posições no pior caso (~3,5 ms a 6,0 ms por busca no final da lista).
* **Tabela Hash / Dicionário (`dict` - $O(1)$):** Calcula `hash(chave)` e acessa o índice diretamente (~0,0002 ms por busca — mais de **10.000x mais rápido**).
*(O script da Tabela Hash Simples e do benchmark de 100.000 elementos encontra-se desmembrado no repositório de Sprints em `S4_08_Tabelas_Hash/tabela_hash_e_benchmark.py`).*

---

## 4. Diferença entre Hash de Dicionários (Tabela Hash) e Hash de Senhas (Criptográfico)

| Característica | Hash para Dicionários (`__hash__` / SipHash) | Hash para Senhas (`bcrypt`, `Argon2`, `PBKDF2`) |
| :--- | :--- | :--- |
| **Objetivo Principal** | Velocidade máxima para indexação em memória RAM ($O(1)$). | Segurança e resistência contra ataques de força bruta e *Rainbow Tables*. |
| **Velocidade Ideal** | **Extremamente rápido** (nanossegundos). | **Propositalmente lento** e custoso em CPU/Memória (*Key Stretching*). |
| **Uso de Salt** | Usa semente aleatória por processo (`PYTHONHASHSEED`) contra DoS de colisão. | Usa um **Salt único por usuário** armazenado junto ao hash. |
| **Reversibilidade / Colisão** | Colisões são comuns e tratadas por encadeamento ou endereçamento aberto. | Deve ser **unidirecional (One-Way)** e resistente a colisões (custo inviável de inverter). |
