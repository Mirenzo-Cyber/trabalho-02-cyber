# 🛡️ API de Inventário e Análise de Risco (Trabalho 02)

Sistema desenvolvido em Python utilizando Programação Orientada a Objetos (POO) e Álgebra Linear para gerir inventários de ativos de cibersegurança. O sistema calcula o risco efetivo de vulnerabilidades através da resolução de sistemas lineares, sendo disponibilizado via API RESTful com Flask e empacotado em container Docker.

## 🚀 Tecnologias Utilizadas
* **Python 3.11**
* **Flask** (API RESTful)
* **NumPy** (Cálculo matricial e validação de invertibilidade)
* **Docker** (Containerização)
* **Pytest & Unittest** (Testes automatizados)

## ⚙️ Funcionalidades
* **CRUD Completo:** Gestão de equipamentos (Computadores, Notebooks, Servidores, Switches) com aplicação de Polimorfismo no fator de exposição ao risco.
* **Cálculo de Risco Matricial:** Resolução matemática do sistema $(I - A)x = b$ utilizando NumPy para encontrar o risco efetivo com base na dependência entre ativos.
* **Validação Numérica:** Verificação do determinante e da invertibilidade da matriz $(I - A)$ antes da resolução.

## 🐳 Como Executar com Docker
Certifique-se de que possui o Docker instalado e a rodar. No terminal, dentro da pasta do projeto, execute:

1. **Construir a imagem da API:**
   ```bash
   docker build -t api-inventario .