# Camada de Interface: Lida com a interação com o usuário no terminal (menus, inputs e prints)
from servicos import ServicoInventario


class SistemaInventario(ServicoInventario):
    def cadastrar_ativo(self):
        print("\n--- Cadastro de Novo Equipamento ---")
        try:
            id_ativo = int(input("ID do equipamento (apenas números): "))
            if id_ativo in self.equipamentos:
                print("Erro: ID já cadastrado.")
                return

            nome = input("Nome: ").strip()
            resp = input("Responsável: ").strip()
            setor = input("Setor: ").strip()

            print(
                "Categorias disponíveis: 1. COMPUTADORES | 2. NOTEBOOKS | 3. SERVIDORES | 4. SWITCHES"
            )
            opcoes = {
                1: "COMPUTADORES",
                2: "NOTEBOOKS",
                3: "SERVIDORES",
                4: "SWITCHES",
            }
            tipo = opcoes.get(int(input("Escolha o número da categoria: ")))

            if not tipo or not nome:
                print("Erro: Dados inválidos.")
                return

            self.registrar_equipamento(id_ativo, nome, resp, setor, tipo)
            print(f"Equipamento '{nome}' registrado e salvo em JSON com sucesso!")
        except ValueError as e:
            print(f"Erro: {e}")

    def cadastrar_vulnerabilidade(self):
        print("\n--- Cadastrar e Associar Vulnerabilidade ---")
        try:
            id_vul = int(input("ID da Vulnerabilidade (apenas números): "))
            if id_vul not in self.vulnerabilidades:
                desc = input("Descrição da vulnerabilidade: ").strip()
                cat = input(
                    "Categoria (ex: Software desatualizado, Senha fraca): "
                ).strip()
                sev = float(input("Severidade numérica CVSS (ex: 7.5): "))
            else:
                vul_existente = self.vulnerabilidades[id_vul]
                print(
                    f"Vulnerabilidade existente selecionada: {vul_existente.descricao}"
                )
                desc, cat, sev = (
                    vul_existente.descricao,
                    vul_existente.categoria,
                    vul_existente.severidade,
                )

            id_eq = int(input("ID do Equipamento afetado por esta vulnerabilidade: "))
            self.associar_vulnerabilidade(id_vul, id_eq, desc, cat, sev)
            print("Vulnerabilidade associada e salva no arquivo JSON!")
        except (ValueError, LookupError) as e:
            print(f"Erro: {e}")

    def cadastrar_dependencia(self):
        print("\n--- Cadastrar Dependência entre Equipamentos ---")
        try:
            id_origem = int(
                input("ID do equipamento dependente (o que recebe o risco): ")
            )
            id_destino = int(
                input("ID do equipamento do qual depende (origem do risco): ")
            )
            peso = float(input("Fração de risco transmitida (ex: 0.25 para 25%): "))

            self.registrar_dependencia(id_origem, id_destino, peso)
            print(
                f"Sucesso: Equipamento {id_origem} agora herda {peso * 100:.1f}% do risco do Equipamento {id_destino}!"
            )
        except (ValueError, LookupError) as e:
            print(f"Erro: {e}")

    def listar_ativos(self):
        print("\n--- Lista de Equipamentos Cadastrados ---")
        if not self.equipamentos:
            print("Nenhum equipamento cadastrado.")
            return

        for eq in self.equipamentos.values():
            print(
                f"\n[ID: {eq.id_ativo}] {eq.nome} | Tipo: {eq.tipo} | Fator Exposição: {eq.fator_exposicao()}"
            )
            print(f"  Responsável: {eq.responsavel} | Setor: {eq.setor}")
            print(
                f"  Vulnerabilidades (IDs): {eq.vulnerabilidades_ids if eq.vulnerabilidades_ids else 'Nenhuma'}"
            )

            if eq.dependencias:
                deps_formatadas = [
                    f"Ativo {alvo} ({peso * 100:.1f}%)"
                    for alvo, peso in eq.dependencias.items()
                ]
                print(f"  Depende de: {', '.join(deps_formatadas)}")
            else:
                print("  Depende de: Nenhuma dependência registrada.")

    def calcular_analise_risco(self):
        print("\n--- Análise de Risco com Álgebra Linear ---")
        resultado = self.calcular_analise_risco_api()

        if "erro" in resultado:
            print(f"Erro: {resultado['erro']}")
            return

        print(
            f"Matriz (I - A) Invertível: Sim | Determinante: {resultado['determinante']} | Nº de Condição: {resultado['numero_condicao']}"
        )
        print(
            f"\n{'ID':<5} | {'Equipamento':<20} | {'Risco Próprio (b)':<18} | {'Risco Efetivo (x)'}"
        )
        print("-" * 68)
        for item in resultado["equipamentos"]:
            print(
                f"{item['id_ativo']:<5} | {item['nome']:<20} | {item['risco_proprio']:<18.2f} | {item['risco_efetivo']:.2f}"
            )


def executar_menu_cli():
    sistema = SistemaInventario()
    while True:
        print("\n--- Sistema de Inventário e Análise de Risco ---")
        print("1. Cadastrar Equipamento")
        print("2. Cadastrar / Associar Vulnerabilidade")
        print("3. Cadastrar Dependência entre Equipamentos")
        print("4. Listar Equipamentos e Dependências")
        print("5. Calcular Análise de Risco")
        print("6. Sair")

        opcao = input("Escolha uma opção (1 a 6): ").strip()

        if opcao == "1":
            sistema.cadastrar_ativo()
        elif opcao == "2":
            sistema.cadastrar_vulnerabilidade()
        elif opcao == "3":
            sistema.cadastrar_dependencia()
        elif opcao == "4":
            sistema.listar_ativos()
        elif opcao == "5":
            sistema.calcular_analise_risco()
        elif opcao == "6":
            print("\nEncerrando o sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")
