# Usa uma imagem oficial e leve do Python
FROM python:3.11-slim

# Define a pasta /app dentro do container como diretório principal
WORKDIR /app

# Copia a lista de dependências e instala o Flask e o NumPy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos da pasta Trabalho_02 (.py e .json) para o container
COPY . .

# Expõe a porta 5000 usada pelo Flask
EXPOSE 5000

# Inicia o servidor da API continuamente
CMD ["python", "app.py"]