import requests
import openai
import json
import random
import datetime
import time


# Leer los datos del archivo datos_usuario.txt
def leer_datos_usuario(file_path="datos_usuario.txt"):
    try:
        with open(file_path, "r") as file:
            data = {}
            for line in file:
                if ':' in line:
                    key, value = line.strip().split(":", 1)
                    data[key.strip()] = value.strip()
        return data
    except FileNotFoundError:
        print("Archivo de datos no encontrado. Asegúrate de haber ejecutado el script crear_cuenta_demo.py.")
        exit()

datos = leer_datos_usuario()

token = datos.get('token')
uuid_business = datos.get('uuid_business')
uuid_user = datos.get('uuid_user')

if not all([token, uuid_business, uuid_user]):
    print("Faltan datos necesarios en datos_usuario.txt.")
    exit()

# Establecer los encabezados de autorización
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Función para manejar errores de la API
def manejar_error_api(response):
    status_code = response.status_code
    if status_code == 400:
        print("BadRequestError: La solicitud está mal formada o le faltan parámetros.")
    elif status_code == 401:
        print("AuthenticationError: API key inválida o expirada.")
    elif status_code == 403:
        print("PermissionDeniedError: No tienes permiso para acceder al recurso solicitado.")
    elif status_code == 404:
        print("NotFoundError: El recurso solicitado no existe.")
    elif status_code == 429:
        print("RateLimitError: Has alcanzado el límite de tasa de la API. Intenta nuevamente más tarde.")
    elif 500 <= status_code < 600:
        print("InternalServerError: Error interno en el servidor de la API. Intenta nuevamente más tarde.")
    else:
        print(f"Error inesperado {status_code}: {response.text}")

# Función para generar datos ficticios usando OpenAI, con salida en formato JSON
def generar_datos(prompt, json_schema):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera datos ficticios para una empresa."},
                {"role": "user", "content": f"{prompt}\nDevuelve la respuesta en formato JSON conforme al siguiente esquema:\n{json_schema}"}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        if "data" not in data:
            data = {"data": data}
        return data.get("data", [])
    except openai.error.OpenAIError as e:
        print("Error con la API de OpenAI:", e)
        return None
    except json.JSONDecodeError as e:
        print("Error al decodificar el JSON generado por OpenAI:", e)
        print("Contenido recibido:", content)
        return None

# Función para obtener productos existentes
def obtener_productos():
    productos = []
    url = "https://api.somosoliver.com/product/get/all"
    params = {
        "uuid_business": uuid_business
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            datos = response.json().get('data', [])
            productos.extend(datos)
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print("Error al obtener productos:", e)
    return productos

# Función para obtener clientes existentes
def obtener_clientes():
    clientes = []
    url = "https://api.somosoliver.com/customer/get/all"
    params = {
        "uuid_business": uuid_business
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            datos = response.json().get('data', [])
            # Filtrar solo clientes
            clientes = [cliente for cliente in datos if cliente.get('type') == 'client']
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print("Error al obtener clientes:", e)
    return clientes

# Función para obtener proveedores existentes
def obtener_proveedores():
    proveedores = []
    url = "https://api.somosoliver.com/provider/get/all"
    params = {
        "uuid_business": uuid_business
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            datos = response.json().get('data', [])
            # Filtrar solo proveedores
            proveedores = [proveedor for proveedor in datos if proveedor.get('type') == 'provider']
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print("Error al obtener proveedores:", e)
    return proveedores

# Función para obtener o crear un tipo de gasto
def obtener_o_crear_tipo_gasto():
    # Primero, intentar obtener tipos de gastos existentes
    url = "https://api.somosoliver.com/business/expense/list"
    params = {
        "uuid_business": uuid_business
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            gastos = response.json().get('data', [])
            if gastos:
                return gastos[0].get('uuid')  # Retornar el primero encontrado
    except requests.exceptions.RequestException as e:
        print("Error al obtener tipos de gasto existentes:", e)
    
    # Si no hay tipos de gasto, crear uno nuevo
    crear_tipo_gasto()
    if 'uuid_expense' in globals():
        return uuid_expense
    return None

# Función para crear un tipo de gasto
def crear_tipo_gasto():
    url = "https://api.somosoliver.com/business/expense/create"
    prompt_gasto = f"Genera un tipo de gasto común para una {business_type}"
    json_schema_gasto = '''
    {
        "data": {
            "name": "string",
            "icon": "string"
        }
    }
    '''
    tipo_gasto = generar_datos(prompt_gasto, json_schema_gasto)
    
    if not tipo_gasto or not isinstance(tipo_gasto, dict):
        print("No se pudo generar el tipo de gasto o el formato es incorrecto.")
        return
    
    gasto_data = {
        "uuid_business": uuid_business,
        "name": tipo_gasto.get('name', 'Gasto General'),
        "icon": tipo_gasto.get('icon', 'utilities')
    }
    
    try:
        response = requests.post(url, headers=headers, json=gasto_data)
        if response.status_code == 200:
            print("Tipo de gasto creado exitosamente.")
            uuid_expense = response.json().get('data', {}).get('uuid')
            if uuid_expense:
                globals()['uuid_expense'] = uuid_expense
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print("Error al crear el tipo de gasto:", e)

# Función para registrar gastos
def registrar_gastos(proveedores, uuid_expense, cantidad=50):
    if not uuid_expense:
        print("No se tiene un UUID de tipo de gasto válido.")
        return
    
    url = "https://api.somosoliver.com/expenses/bybusiness/create"
    prompt_gastos = f"Genera una lista de {cantidad} gastos típicos para una {business_type}, incluye nombre, valor y descripción."
    json_schema_gastos = '''
    {
        "data": [
            {
                "nombre": "string",
                "valor": "number",
                "descripcion": "string"
            }
        ]
    }
    '''
    gastos = generar_datos(prompt_gastos, json_schema_gastos)
    
    if not gastos or not isinstance(gastos, list):
        print("No se pudieron generar los gastos o el formato es incorrecto.")
        return

    for i, gasto in enumerate(gastos, start=1):
        if isinstance(gasto, dict):
            if not proveedores:
                print("No hay proveedores disponibles para registrar gastos.")
                return
                
            uuid_provider = random.choice(proveedores).get('uuid')
            value = gasto.get('valor', round(random.uniform(50, 500), 2))
            
            gasto_data = {
                "uuid_business": uuid_business,
                "uuid_expense": uuid_expense,
                "uuid_client": uuid_provider,
                "type_transaction": 2,
                "expense_name": gasto.get('nombre', f'Gasto {i}'),
                "serie": "G",
                "folio": str(i),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": gasto.get('descripcion', ''),
                "value": value,
                "taxes": 0,
                "currency": 95,
                "exchange_rate": 1,
                "uuid_user": uuid_user,
                "products": [
                    {
                        "name": gasto.get('nombre', f'Gasto {i}'),
                        "expense": 1,
                        "price": value,
                        "cantidad": 1,
                        "cost": 0,
                        "discount": 0,
                        "comments": gasto.get('descripcion', ''),
                        "type": "service",
                        "detail_taxes": 0,
                        "detail_retentions": 0
                    }
                ]
            }
            
            try:
                response = requests.post(url, headers=headers, json=gasto_data)
                if response.status_code == 200:
                    uuid_gasto = response.json().get('data', {}).get('uuid')
                    if uuid_gasto:
                        print(f"Gasto {i} registrado exitosamente. UUID: {uuid_gasto}")
                        # Opcional: Pagar el gasto inmediatamente
                        # pagar_gasto(uuid_gasto, uuid_provider, value)
                else:
                    manejar_error_api(response)
            except requests.exceptions.RequestException as e:
                print(f"Error al registrar el gasto {i}: {e}")
            
            time.sleep(0.1)  # Evitar exceder límites de tasa
        else:
            print(f"Gasto inválido: {gasto}")

# Función para pagar gastos (Opcional)
def pagar_gasto(uuid_gasto, uuid_provider, amount):
    url = "https://api.somosoliver.com/expenses/payment/create"
    pago_data = {
        "uuid_business": uuid_business,
        "uuid_sale": uuid_gasto,
        "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666",  # Reemplazar con UUID válido
        "uuid_contact": uuid_provider,
        "complement_payment": 0,
        "amount": amount,
        "currency": 95,
        "exchange_rate": 1,
        "uuid_payment_method": 1005,  # Reemplazar con método de pago válido
        "comments": "Pago automático",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        response = requests.post(url, headers=headers, json=pago_data)
        if response.status_code == 200:
            print(f"Gasto '{uuid_gasto}' pagado exitosamente.")
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al pagar el gasto '{uuid_gasto}': {e}")

# Función para registrar ventas
def registrar_ventas(clientes, productos, cantidad=50):
    for i in range(cantidad):
        if not clientes or not productos:
            print("No hay suficientes clientes o productos para registrar ventas.")
            return
        
        uuid_client = random.choice(clientes).get('uuid')
        producto = random.choice(productos)
        uuid_product = producto.get('uuid')
        price = round(random.uniform(10, 100), 2)
        quantity = random.randint(1, 5)
        total = round(price * quantity, 2)
        
        venta_data = {
            "value": total,
            "uuid_turn": abrir_turno_pos(),
            "description": "",
            "comments": "",
            "concept": "",
            "uuid_client": uuid_client,
            "pos": 1,
            "uuid_business": uuid_business,
            "status": "paid",
            "type_sale": 1,
            "enable": 1,
            "type": 15,
            "amount_return": 0,
            "payments": [
                {
                    "id_payment_method": 1005,  # Reemplazar con método de pago válido
                    "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666",  # Reemplazar con UUID válido
                    "amount": total
                }
            ],
            "products": [
                {
                    "price": price,
                    "discount": 0,
                    "quantity": quantity,
                    "observations": "",
                    "total": total,
                    "uuid": uuid_product,
                    "uuid_product": uuid_product,
                    "cantidad": quantity,
                    "taxes": 0,
                    "type_discount": 1,
                    "discont": 0,
                    "status": 1,
                    "detail_taxes": [
                        {
                            "uuid_business": uuid_business,
                            "uuid_product": uuid_product,
                            "id_tax": 678,
                            "nameTax": "EXENTO- 0.00% - 01 - No objeto de impuesto.",
                            "valueTax": 0
                        }
                    ],
                    "detail_retentions": []
                }
            ]
        }
        
        url = "https://api.somosoliver.com/transactions/pos/create"
        try:
            response = requests.post(url, headers=headers, json=venta_data)
            if response.status_code == 200:
                uuid_sale = response.json().get('data', {}).get('uuid')
                print(f"Venta {i+1} registrada exitosamente. UUID: {uuid_sale}")
                # Opcional: Registrar pago de la venta
                # registrar_pago_venta(uuid_sale)
            else:
                manejar_error_api(response)
        except requests.exceptions.RequestException as e:
            print(f"Error al registrar la venta {i+1}: {e}")
        
        time.sleep(0.1)  # Evitar exceder límites de tasa

# Función para registrar pagos de ventas (Opcional)
def registrar_pago_venta(uuid_sale):
    url = "https://api.somosoliver.com/transactions/pos/payment"
    pago_data = {
        "uuid_business": uuid_business,
        "uuid_sale": uuid_sale,
        "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666",  # Reemplazar con UUID válido
        "uuid_contact": "UUID_DEL_CLIENTE",  # Reemplazar con UUID del cliente
        "complement_payment": 0,
        "amount": 100,  # Reemplazar con el monto adecuado
        "currency": 95,
        "exchange_rate": 1,
        "uuid_payment_method": 1005,  # Reemplazar con método de pago válido
        "comments": "Pago de venta registrada automáticamente",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        response = requests.post(url, headers=headers, json=pago_data)
        if response.status_code == 200:
            print(f"Pago para la venta '{uuid_sale}' registrado exitosamente.")
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al registrar el pago para la venta '{uuid_sale}': {e}")

# Función para obtener el UUID de una caja registradora existente
def obtener_uuid_caja():
    url = "https://api.somosoliver.com/cash_register/list"
    params = {
        "uuid_business": uuid_business
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            cajas = response.json().get('data', [])
            if cajas:
                return cajas[0].get('uuid')  # Seleccionar la primera caja disponible
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print("Error al obtener cajas registradoras:", e)
    return None

# Función para abrir un turno en el POS
def abrir_turno_pos():
    uuid_caja = obtener_uuid_caja()
    if not uuid_caja:
        print("No se encontró una caja registradora válida. Intentando crear una nueva caja.")
        uuid_caja = crear_caja_registradora()
        if not uuid_caja:
            print("No se pudo crear una caja registradora. Abortando apertura de turno.")
            return None

    turno_data = {
        "uuid_caja": uuid_caja,
        "uuid_business": uuid_business,
        "start_cash": round(random.uniform(100, 500), 2),
        "sales": 0,
        "status_caja": 1
    }
    url = "https://api.somosoliver.com/turns/openturn"
    try:
        response = requests.post(url, headers=headers, json=turno_data)
        if response.status_code == 200:
            uuid_turn = response.json().get('data', {}).get('uuid')
            if uuid_turn:
                print(f"Turno abierto exitosamente. UUID: {uuid_turn}")
                return uuid_turn
            else:
                print("No se pudo obtener el UUID del turno abierto.")
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al abrir turno en el POS: {e}")
    return None

# Función para cerrar un turno en el POS
def cerrar_turno_pos():
    uuid_caja = obtener_uuid_caja()
    if not uuid_caja:
        print("No se encontró una caja registradora válida.")
        return
    cierre_data = {
        "uuid_caja": uuid_caja,
        "cash_amount": round(random.uniform(200, 1000), 2),
        "amount_to_leave": round(random.uniform(0, 100), 2),
        "destination": "821e43aa-5b74-48d0-87ce-417092560666",  # Reemplazar con un UUID válido de tu banco
        "status_caja": 0
    }
    url = "https://api.somosoliver.com/turns/closeturn"
    try:
        response = requests.post(url, headers=headers, json=cierre_data)
        if response.status_code == 200:
            print("Turno cerrado exitosamente.")
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al cerrar turno en el POS: {e}")

# Función para crear una caja registradora
def crear_caja_registradora():
    url = "https://api.somosoliver.com/cash_register/create"
    caja_data = {
        "uuid_business": uuid_business,
        "uuid_sucursal": uuid_business,  # Asegúrate de que este es el UUID correcto de la sucursal
        "register_name": "Caja Principal",
        "description": "Caja principal de la tienda",
        "typePayments": [
            {
                "id_payment_method": 1005,  # Reemplazar con métodos de pago válidos
                "name": "Efectivo",
                "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666"  # Reemplazar con UUID válido
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=caja_data)
        if response.status_code == 200:
            caja_response = response.json().get('data', {})
            uuid_caja = caja_response.get('uuid')
            if uuid_caja:
                print("Caja registradora creada exitosamente.")
                return uuid_caja
        else:
            manejar_error_api(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al crear la caja registradora: {e}")
    return None

# Función principal
def main():
    print("Consultando productos existentes...")
    productos = obtener_productos()
    print(f"Total de productos obtenidos: {len(productos)}")
    
    print("Consultando clientes existentes...")
    clientes = obtener_clientes()
    print(f"Total de clientes obtenidos: {len(clientes)}")
    
    print("Consultando proveedores existentes...")
    proveedores = obtener_proveedores()
    print(f"Total de proveedores obtenidos: {len(proveedores)}")
    
    if not all([productos, clientes, proveedores]):
        print("Faltan datos necesarios para continuar.")
        return
    
    print("Obteniendo o creando tipo de gasto...")
    uuid_expense = obtener_o_crear_tipo_gasto()
    if not uuid_expense:
        print("No se pudo obtener o crear un tipo de gasto. Abortando.")
        return
    
    print("Registrando gastos...")
    registrar_gastos(proveedores, uuid_expense, cantidad=50)
    
    print("Registrando ventas...")
    registrar_ventas(clientes, productos, cantidad=50)
    
    print("Proceso completado.")

if __name__ == "__main__":
    main()
