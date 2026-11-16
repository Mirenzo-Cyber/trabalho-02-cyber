import json
import os


def gerar_relatorio():
    print("==================================================")
    print("       RELATÓRIO DE VULNERABILIDADES - S4_07      ")
    print("==================================================\n")

    equipamentos = []
    vulnerabilidades = []

    if os.path.exists("equipamentos.json"):
        with open("equipamentos.json", "r", encoding="utf-8") as f:
            equipamentos = json.load(f)

    if os.path.exists("vulnerabilidades.json"):
        with open("vulnerabilidades.json", "r", encoding="utf-8") as f:
            vulnerabilidades = json.load(f)

    # Cria um dicionário de vulnerabilidades para consulta rápida por id_vul
    vuln_dict = {v.get("id_vul"): v for v in vulnerabilidades}

    print("--> 1. Total de Vulnerabilidades por Equipamento:")
    for eq in equipamentos:
        eq_nome = eq.get("nome", "Desconhecido")
        vuln_ids = eq.get("vulnerabilidades_ids", [])
        total_vulns = len(vuln_ids)
        print(f"  - Equipamento: {eq_nome} | Vulnerabilidades: {total_vulns}")

    print("\n--------------------------------------------------\n")

    print("--> 5. Relatório de Maior Risco (Soma CVSS por Equipamento):")
    ranking = []
    for eq in equipamentos:
        eq_nome = eq.get("nome", "Desconhecido")
        vuln_ids = eq.get("vulnerabilidades_ids", [])

        # Soma a severidade das vulnerabilidades vinculadas a este equipamento
        soma_cvss = 0.0
        for vid in vuln_ids:
            if vid in vuln_dict:
                soma_cvss += float(vuln_dict[vid].get("severidade", 0))

        ranking.append((eq_nome, soma_cvss))

    # Ordena do maior para o menor risco
    ranking.sort(key=lambda x: x[1], reverse=True)

    for i, (nome, soma) in enumerate(ranking[:5], 1):
        print(f"  {i}. {nome} - Soma CVSS: {soma:.2f}")

    print("\n==================================================")


if __name__ == "__main__":
    gerar_relatorio()
