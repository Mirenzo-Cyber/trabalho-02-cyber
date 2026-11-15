import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except AttributeError: pass
from dominio import (
    Vulnerabilidade, Equipamento, Computador, Notebook, Servidor, Switch, Firewall,
    FabricaEquipamento, fabricar_equipamento
)
from persistencia import InterfaceRepositorio, RepositorioJSON, RepositorioMemoria
from servicos import (
    CalculadoraRisco, ServicoInventario, EstrategiaOrdenacao,
    OrdenacaoPorRiscoEfetivo, OrdenacaoPorId,
    estrategia_ordenar_por_nome, estrategia_ordenar_por_risco_proprio
)
from interface import SistemaInventario, executar_menu_cli
if __name__ == "__main__": executar_menu_cli()
