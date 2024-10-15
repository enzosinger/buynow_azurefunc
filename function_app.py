import logging
import azure.functions as func
import pyodbc
import json

def connect_db():
    server = 'localhost'  # Substitua pelo endereço do seu servidor
    database = 'buynow_produtos'  # Substitua pelo nome do seu banco de dados

    # String de conexão usando autenticação do Windows
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    # Conecta ao banco de dados
    return pyodbc.connect(connection_string)


# Inicializando a função no Azure Functions
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Função principal CRUD
@app.route(route="crud_product")
def crud_product(req: func.HttpRequest) -> func.HttpResponse:
    # Conectando ao banco de dados
    conn = connect_db()
    cursor = conn.cursor()

    # Identificando o método HTTP
    method = req.method

    if method == "POST":
        # Criar um novo produto
        try:
            data = req.get_json()
            cursor.execute("INSERT INTO products (name, description) VALUES (?, ?)", (data['name'], data['description']))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto criado com sucesso!"}), status_code=201)
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao criar produto: {str(e)}", status_code=500)
    
    elif method == "GET":
        # Listar todos os produtos
        cursor.execute("SELECT * FROM products")
        columns = [column[0] for column in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return func.HttpResponse(json.dumps(products), status_code=200)
    
    elif method == "PUT":
        # Atualizar um produto existente
        try:
            data = req.get_json()
            cursor.execute("UPDATE products SET name=?, description=? WHERE pid=?", (data['name'], data['description'], data['pid']))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto atualizado com sucesso!"}), status_code=200)
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao atualizar produto: {str(e)}", status_code=500)
    
    elif method == "DELETE":
        # Deletar um produto
        try:
            data = req.get_json()
            cursor.execute("DELETE FROM products WHERE pid=?", (data['pid'],))
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
