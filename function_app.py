import logging
import azure.functions as func
import pyodbc
import json
import os

def connect_db():
    connection_string = os.getenv("SQL_SERVER_CONNECTION_STRING")
    return pyodbc.connect(connection_string)

# Inicializando a função no Azure Functions
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="products", methods=["GET", "POST"])
def products(req: func.HttpRequest) -> func.HttpResponse:
    conn = connect_db()
    cursor = conn.cursor()
    method = req.method

    if method == "POST":
        try:
            data = req.get_json()
            cursor.execute("INSERT INTO products (name, description) VALUES (?, ?)", (data['name'], data['description']))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto criado com sucesso!"}), status_code=201)
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao criar produto: {str(e)}", status_code=500)

    elif method == "GET":
        cursor.execute("SELECT * FROM products")
        columns = [column[0] for column in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return func.HttpResponse(json.dumps(products), status_code=200)

    cursor.close()
    conn.close()

@app.route(route="products/{pid}", methods=["PUT", "DELETE"])
def product_by_id(req: func.HttpRequest) -> func.HttpResponse:
    conn = connect_db()
    cursor = conn.cursor()
    method = req.method
    pid = req.route_params.get('pid')

    if method == "PUT":
        try:
            data = req.get_json()
            fields_to_update = []
            values = []

            if 'name' in data:
                fields_to_update.append("name=?")
                values.append(data['name'])
            
            if 'description' in data:
                fields_to_update.append("description=?")
                values.append(data['description'])
            
            if 'compras' in data:
                fields_to_update.append("compras=?")
                values.append(data['compras'])

            if not fields_to_update:
                return func.HttpResponse(json.dumps({"error": "Nenhum campo para atualizar"}), status_code=400)

            values.append(pid)
            query = f"UPDATE products SET {', '.join(fields_to_update)} WHERE pid=?"
            cursor.execute(query, tuple(values))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto atualizado com sucesso!"}), status_code=200)
        
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao atualizar produto: {str(e)}", status_code=500)

    elif method == "DELETE":
        try:
            cursor.execute("DELETE FROM products WHERE pid=?", (pid,))
            conn.commit()
            return func.HttpResponse(json.dumps({"message": "Produto deletado com sucesso!"}), status_code=200)
        
        except Exception as e:
            logging.error(str(e))
            return func.HttpResponse(f"Erro ao deletar produto: {str(e)}", status_code=500)

    cursor.close()
    conn.close()

# Função que escuta o Service Bus e incrementa o campo 'compras' do produto
@app.function_name(name="IncrementProductPurchases")
@app.service_bus_queue_trigger(arg_name="msg", queue_name="purchase_events", connection="SERVICE_BUS_CONNECTION_STRING")
def increment_product_purchases(msg: func.ServiceBusMessage):
    try:
        message_body = msg.get_body().decode('utf-8')
        data = json.loads(message_body)
        product_id = data.get("product_id")
        
        if not product_id:
            logging.error("ID do produto não encontrado na mensagem.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        update_query = """
        UPDATE products 
        SET compras = compras + 1 
        WHERE pid = ?
        """
        cursor.execute(update_query, (product_id,))
        conn.commit()
        
        logging.info(f"Compra registrada para o produto ID {product_id}.")

    except Exception as e:
        logging.error(f"Erro ao processar a mensagem do Service Bus: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
