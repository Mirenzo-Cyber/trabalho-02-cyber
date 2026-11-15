# Relatório SOLID (S4_02)
1. **SRP**: `CalculadoraRisco` separada de `ServicoInventario`.
2. **OCP**: Novo ativo `Firewall` adicionado sem modificar o cálculo de risco.
3. **LSP**: Todas as subclasses (`Computador`, `Notebook`, `Servidor`, `Switch`, `Firewall`) substituem `Equipamento` sem quebrar contratos.
4. **DIP**: Criada `InterfaceRepositorio` com implementações `RepositorioJSON` e `RepositorioMemoria`.
