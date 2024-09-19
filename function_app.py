import logging
import azure.functions as func
import mysql.connector
import json

# Função para conectar ao banco de dados MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",  # Substitua pelo seu host MySQL
        user="root",     # Substitua pelo seu usuário MySQL
        password="",   # Substitua pela sua senha MySQL
        database="produtos_db"    # Substitua pelo nome do banco de dados
    )

# Inicializando a função no Azure Functions
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Função principal CRUD
@app.route(route="crud_product")
def crud_product(req: func.HttpRequest) -> func.HttpResponse:
    # Conectando ao banco de dados
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    # Identificando o método HTTP
    method = req.method

    if method == "POST":
        # Criar um novo produto
        try:
            data = req.get_json()
            cursor.execute("INSERT INTO products (name, description) VALUES (%s, %s)", (data['name'], data['description']))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto criado com sucesso!"}), status_code=201)
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao criar produto: {str(e)}", status_code=500)
    
    elif method == "GET":
        # Listar todos os produtos
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return func.HttpResponse(json.dumps(products), status_code=200)
    
    elif method == "PUT":
        # Atualizar um produto existente
        try:
            data = req.get_json()
            cursor.execute("UPDATE products SET name=%s, description=%s WHERE pid=%s", (data['name'], data['description'], data['pid']))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto atualizado com sucesso!"}), status_code=200)
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao atualizar produto: {str(e)}", status_code=500)
    
    elif method == "DELETE":
        # Deletar um produto
        try:
            data = req.get_json()
            cursor.execute("DELETE FROM products WHERE pid=%s", (data['pid'],))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto deletado com sucesso!"}), status_code=200)
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao deletar produto: {str(e)}", status_code=500)
    
    else:
        return func.HttpResponse("Método HTTP não suportado.", status_code=405)

    # Fechando a conexão
    cursor.close()
    conn.close()
