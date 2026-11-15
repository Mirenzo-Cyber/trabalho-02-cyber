# 🎨 Padrões de Projeto (Design Patterns) Adotados (S4_03)

Este documento descreve e justifica os padrões de projeto aplicados no **Trabalho 02**, o problema que cada um resolve e a análise crítica sobre o uso do padrão *Singleton*.

---

## 1. Factory (`FabricaEquipamento` em `dominio/`)
* **Problema que resolve:** Evita espalhar condicionais (`if/elif`) ou acoplar o repositório e a camada de serviço às subclasses concretas (`Computador`, `Notebook`, `Servidor`, `Switch`, `Firewall`) no momento de instanciar ativos ou reconstruí-los a partir do arquivo JSON.
* **Implementação:** A classe `FabricaEquipamento` possui os métodos `criar()` e `de_dicionario()`, que inspecionam o campo `tipo` do registro JSON e devolvem automaticamente a instância da subclasse correta com seu fator de exposição polimórfico.

---

## 2. Repository (`InterfaceRepositorio`, `RepositorioJSON` e `RepositorioMemoria` em `persistencia/`)
* **Problema que resolve:** Isola toda a lógica de leitura e escrita de dados (arquivos `.json` ou dicionários em RAM) das regras de negócio e do domínio.
* **Implementação:** `ServicoInventario` interage apenas com os métodos `salvar()` e `carregar()` do repositório injetado, sem saber se os dados estão em disco ou em memória.

---

## 3. Strategy (`EstrategiaOrdenacao` e Funções de Primeira Classe em `servicos/`)
* **Problema que resolve:** Permite variar o critério de ordenação e priorização dos relatórios de risco (`OrdenacaoPorRiscoEfetivo`, `OrdenacaoPorId`, ou por nome/risco próprio) dentro da mesma operação `calcular_analise_risco_api()`, sem modificar a lógica matemática da `CalculadoraRisco`.
* **Classes vs. Funções de Primeira Classe:** Além das classes que herdam de `EstrategiaOrdenacao`, as estratégias foram reescritas usando **funções de primeira classe** em Python (`estrategia_ordenar_por_nome` e `estrategia_ordenar_por_risco_proprio`), demonstrando que funções `callable` reduzem código repetitivo (*boilerplate*) quando a estratégia não precisa armazenar estado interno.

---

## 4. Discussão: O Padrão *Singleton* é adequado para o acesso ao arquivo de dados?
* **Justificativa:** **Não é recomendado** utilizar um *Singleton* rígido para o repositório de dados neste projeto. Embora pareça conveniente ter uma única instância de acesso ao arquivo JSON, o *Singleton* cria estado global oculto, viola o Princípio da Inversão de Dependência (DIP) e dificulta os testes automatizados (pois impede injetar instâncias limpas de `RepositorioMemoria` em cada teste do `pytest`). A abordagem adotada — **Injeção de Dependência** de uma instância única criada na inicialização da aplicação (`app.py`) — garante o compartilhamento seguro sem os problemas de acoplamento do *Singleton*.
