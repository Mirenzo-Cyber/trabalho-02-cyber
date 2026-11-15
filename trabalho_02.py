import sys

# Força o terminal a ler e escrever em UTF-8 para evitar erros de acentuação
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except AttributeError:
    pass

# Reexporta as classes das camadas para manter compatibilidade com os testes e com a API
from dominio import (
    Vulnerabilidade,
    Equipamento,
    Computador,
    Notebook,
    Servidor,
    Switch,
)
from persistencia import RepositorioJSON
from servicos import ServicoInventario
from interface import SistemaInventario, executar_menu_cli

if __name__ == "__main__":
    executar_menu_cli()
