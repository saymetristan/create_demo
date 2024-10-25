import requests
import openai
import json
import random
import datetime
from openai import OpenAI  # Añadido para usar la nueva interfaz


# Leer el token y los UUIDs del archivo generado en el primer script
try:
    with open("datos_usuario.txt", "r") as file:
        data = {}
        for line in file:
            key, value = line.strip().split(":")
            data[key] = value
    token = data['token']
    uuid_business = data['uuid_business']
    uuid_user = data['uuid_user']
    business_type = data['business_type']
    email = data['email']
except FileNotFoundError:
    print("Archivo de datos no encontrado. Asegúrate de haber ejecutado el primer script.")
    exit()

# Establecer el encabezado de autorización
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Función para generar datos ficticios usando OpenAI, con salida en formato JSON
def generar_datos(prompt, json_schema):
    messages = [
        {"role": "system", "content": "Eres un asistente que genera datos ficticios para una empresa."},
        {"role": "user", "content": f"{prompt}\nDevuelve la respuesta en formato JSON conforme al siguiente esquema:\n{json_schema}"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Cambiamos a gpt-4 para mejor manejo de JSON
        messages=messages,
        response_format={"type": "json_object"},  # Especificamos que queremos JSON
        temperature=0.7
    )
    
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        if "data" not in data:
            # Asegurarnos de que los datos estén en el formato correcto
            data = {"data": data}
        return data.get("data", [])
    except json.JSONDecodeError as e:
        print("Error al decodificar el JSON generado por OpenAI:", e)
        print("Contenido recibido:", content)
        return None

# Funciones para almacenar los UUIDs
clientes_uuid = []
proveedores_uuid = []
productos_uuid = []

# 1. Actualizar información del negocio
def actualizar_negocio():
    url = "https://api.somosoliver.com/onboarding/pro/step/one"
    business_data = {
        "uuid_business": uuid_business,
        "type_business": "32",  # Puedes ajustar este valor según el tipo de negocio
        "name": f"Demo {business_type}",
        "number_employees": 10,
        "country": "1"
    }
    response = requests.post(url, headers=headers, json=business_data)
    if response.status_code == 200:
        print("Información del negocio actualizada exitosamente.")
    else:
        print("Error al actualizar el negocio:", response.text)

# 2. Actualizar número telefónico
def actualizar_telefono():
    url = "https://api.somosoliver.com/profile/user/phone/update"
    phone_data = {
        "uuid_user": uuid_user,
        "phone": "521234567890"
    }
    response = requests.post(url, headers=headers, json=phone_data)
    if response.status_code == 200:
        print("Número telefónico actualizado exitosamente.")
    else:
        print("Error al actualizar el número telefónico:", response.text)

# 3. Crear clientes y proveedores
def crear_clientes_proveedores():
    url = "https://api.somosoliver.com/customer/create"
    
    # Generar datos ficticios para clientes
    prompt_clientes = f"Genera una lista de 20 clientes ficticios para una {business_type}, incluye nombre, email y teléfono."
    json_schema_clientes = '''
    {
        "data": [
            {
                "nombre": "string",
                "email": "string",
                "telefono": "string"
            }
        ]
    }
    '''
    clientes = generar_datos(prompt_clientes, json_schema_clientes)
    
    if not clientes or not isinstance(clientes, list):
        print("No se pudieron generar los clientes o el formato es incorrecto.")
        return
    
    for cliente in clientes:
        if isinstance(cliente, dict):
            cliente_data = {
                "uuid_business": uuid_business,
                "name": cliente.get('nombre', 'Nombre por defecto'),
                "email": cliente.get('email', 'email@dominio.com'),
                "phone": cliente.get('telefono', '0000000000'),
                "number_document": "",
                "date_birth": "",
                "electronic_invoice": 0,
                "country": "mx",
                "status": "active",
                "type": "client"
            }
            
            response = requests.post(url, headers=headers, json=cliente_data)
            if response.status_code == 200:
                response_data = response.json()
                # Verificar si la respuesta contiene los datos esperados
                if 'data' in response_data and 'uuid' in response_data['data']:
                    clientes_uuid.append(response_data['data']['uuid'])
                    print(f"Cliente '{cliente.get('nombre')}' creado exitosamente. UUID: {response_data['data']['uuid']}")
                else:
                    print(f"Cliente '{cliente.get('nombre')}' creado pero no se pudo obtener el UUID.")
                    print("Respuesta completa:", response_data)  # Para debugging
            else:
                print(f"Error al crear el cliente '{cliente.get('nombre')}':", response.text)
        else:
            print(f"Cliente inválido: {cliente}")

    # Generar datos ficticios para proveedores
    prompt_proveedores = f"Genera una lista de 20 proveedores ficticios para una {business_type}, incluye nombre, email y teléfono."
    json_schema_proveedores = '''
    {
        "data": [
            {
                "nombre": "string",
                "email": "string",
                "telefono": "string"
            }
        ]
    }
    '''
    proveedores = generar_datos(prompt_proveedores, json_schema_proveedores)

    if not proveedores or not isinstance(proveedores, list):
        print("No se pudieron generar los proveedores o el formato es incorrecto.")
        print("Tipo de datos recibido:", type(proveedores))
        print("Contenido:", proveedores)
        return

    for proveedor in proveedores:
        if isinstance(proveedor, dict):
            proveedor_data = {
                "uuid_business": uuid_business,
                "name": proveedor.get('nombre', 'Nombre por defecto'),
                "email": proveedor.get('email', 'email@dominio.com'),
                "phone": proveedor.get('telefono', '0000000000'),
                "number_document": "",
                "date_birth": "",
                "electronic_invoice": 0,
                "country": "mx",
                "status": "active",
                "type": "provider"
            }
            response = requests.post(url, headers=headers, json=proveedor_data)
            if response.status_code == 200:
                print(f"Proveedor '{proveedor.get('nombre')}' creado exitosamente.")
                proveedor_response = response.json()
                if 'uuid' in proveedor_response:
                    proveedores_uuid.append(proveedor_response['uuid'])
                else:
                    print("No se pudo obtener el UUID del proveedor.")
            else:
                print(f"Error al crear el proveedor '{proveedor.get('nombre')}':", response.text)
        else:
            print(f"Proveedor inválido: {proveedor}")

# 4. Crear productos/servicios
def crear_productos_servicios():
    url = "https://api.somosoliver.com/v2/product/create/short"
    # Generar datos ficticios para productos
    prompt_productos = f"Genera una lista de 20 productos que vendería una {business_type}, incluye nombre, precio y costo."
    json_schema_productos = '''
    {
        "data": [
            {
                "nombre": "string",
                "precio": "number",
                "costo": "number"
            }
        ]
    }
    '''
    productos = generar_datos(prompt_productos, json_schema_productos)
    
    if not productos or not isinstance(productos, list):
        print("No se pudieron generar los productos o el formato es incorrecto.")
        print("Tipo de datos recibido:", type(productos))
        print("Contenido:", productos)
        return
    
    for producto in productos:
        if isinstance(producto, dict):
            producto_data = {
                "uuid_business": uuid_business,
                "name": producto.get('nombre', 'Producto sin nombre'),
                "unit_metric": 970,
                "type": "product",
                "code": "",
                "unit_price": producto.get('precio', 0),
                "unit_cost": producto.get('costo', 0),
                "description": "",
                "priceList": [
                    {
                        "uuid_price_list": "a1bdb507-a51c-489d-80d8-07f8b6232c29",
                        "subtotal": producto.get('precio', 0),
                        "price": producto.get('precio', 0),
                        "tax_value": 0,
                        "tax_percentage": 0,
                        "taxes": [
                            {
                                "uuid_price_list": "a1bdb507-a51c-489d-80d8-07f8b6232c29",
                                "id_tax": 678,
                                "name": "EXENTO- 0.00% - 01 - No objeto de impuesto.",
                                "valueTax": 0
                            }
                        ]
                    }
                ],
                "warehouse": [
                    {
                        "uuid_warehouse": "952ca403-4297-4bbb-b30c-e30e70f21b7e",
                        "enable": 100,
                        "last_cost": "",
                        "avg_cost": ""
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=producto_data)
            if response.status_code == 200:
                response_data = response.json()
                if 'product' in response_data and 'uuid' in response_data['product']:
                    productos_uuid.append(response_data['product']['uuid'])
                    print(f"Producto '{producto.get('nombre')}' creado exitosamente. UUID: {response_data['product']['uuid']}")
                else:
                    print(f"Producto '{producto.get('nombre')}' creado pero no se pudo obtener el UUID.")
                    print("Respuesta completa:", response_data)
            else:
                print(f"Error al crear el producto '{producto.get('nombre')}':", response.text)
        else:
            print(f"Producto inválido: {producto}")

# 5. Crear caja registradora
def crear_caja_registradora():
    url = "https://api.somosoliver.com/cash_register/create"
    caja_data = {
        "uuid_business": uuid_business,
        "uuid_sucursal": uuid_business,
        "register_name": "Caja Principal",
        "description": "Caja principal de la tienda",
        "typePayments": [
            {
                "id_payment_method": 1005,
                "name": "Efectivo",
                "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=caja_data)
    if response.status_code == 200:
        print("Caja registradora creada exitosamente.")
        caja_response = response.json()
        global uuid_caja
        uuid_caja = caja_response['cash_register']['uuid']
    else:
        print("Error al crear la caja registradora:", response.text)

# 6. Abrir turno en el POS
def abrir_turno_pos():
    url = "https://api.somosoliver.com/turns/openturn"
    turno_data = {
        "uuid_caja": uuid_caja,
        "uuid_business": uuid_business,
        "start_cash": 0,
        "sales": 0,
        "status_caja": 1
    }
    response = requests.post(url, headers=headers, json=turno_data)
    if response.status_code == 200:
        print("Turno en POS abierto exitosamente.")
        turno_response = response.json()
        global uuid_turn
        uuid_turn = turno_response['Turn']['uuid']
    else:
        print("Error al abrir turno en el POS:", response.text)

# 7. Generar ventas en POS
def generar_ventas_pos():
    url_create = "https://api.somosoliver.com/transactions/pos/create"
    url_payment = "https://api.somosoliver.com/transactions/pos/payment"
    for i in range(20):
        # Seleccionar un cliente y un producto aleatoriamente
        if not clientes_uuid or not productos_uuid:
            print("No hay clientes o productos disponibles para generar ventas.")
            return
        uuid_client = random.choice(clientes_uuid)
        uuid_product = random.choice(productos_uuid)
        quantity = random.randint(1, 5)
        price = random.uniform(10, 100)
        total = round(price * quantity, 2)

        venta_data = {
            "value": total,
            "uuid_turn": uuid_turn,
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
                    "id_payment_method": 1005,
                    "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666",
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
        response = requests.post(url_create, headers=headers, json=venta_data)
        if response.status_code == 200:
            print(f"Venta {i+1} en POS generada exitosamente.")
            venta_response = response.json()
            uuid_sale = venta_response['data']['uuid']
            # Registrar el pago de la venta
            pago_data = {
                "uuid_business": uuid_business,
                "uuid_sale": uuid_sale,
                "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666",
                "uuid_contact": uuid_client,
                "complement_payment": 0,
                "amount": total,
                "currency": 95,
                "exchange_rate": 1,
                "uuid_payment_method": "79cdd26b-7354-47bc-90fe-2719bf19e4e9",
                "comments": "Pago en POS",
                "created_at": datetime.datetime.now().isoformat()
            }
            response_payment = requests.post(url_payment, headers=headers, json=pago_data)
            if response_payment.status_code == 200:
                print(f"Pago de la venta {i+1} registrado exitosamente.")
            else:
                print(f"Error al registrar el pago de la venta {i+1}:", response_payment.text)
        else:
            print(f"Error al generar la venta {i+1} en POS:", response.text)

# 9. Cerrar turno en el POS
def cerrar_turno_pos():
    url = "https://api.somosoliver.com/turns/closeturn"
    cierre_data = {
        "uuid_caja": uuid_caja,
        "cash_amount": 400,
        "amount_to_leave": 0,
        "destination": "821e43aa-5b74-48d0-87ce-417092560666",
        "status_caja": 0
    }
    response = requests.post(url, headers=headers, json=cierre_data)
    if response.status_code == 200:
        print("Turno en POS cerrado exitosamente.")
    else:
        print("Error al cerrar el turno en POS:", response.text)

# 10. Crear tipo de gasto
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
    
    response = requests.post(url, headers=headers, json=gasto_data)
    if response.status_code == 200:
        print("Tipo de gasto creado exitosamente.")
        global uuid_expense
        uuid_expense = response.json()['uuid']
    else:
        print("Error al crear el tipo de gasto:", response.text)

# 11. Registrar gastos
def registrar_gastos():
    url = "https://api.somosoliver.com/expenses/bybusiness/create"
    prompt_gastos = f"Genera una lista de 20 gastos típicos para una {business_type}, incluye nombre y valor."
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

    for i, gasto in enumerate(gastos):
        if isinstance(gasto, dict):
            if not proveedores_uuid:
                print("No hay proveedores disponibles para registrar gastos.")
                return
                
            uuid_provider = random.choice(proveedores_uuid)
            value = gasto.get('valor', round(random.uniform(50, 500), 2))
            
            gasto_data = {
                "uuid_business": uuid_business,
                "uuid_expense": uuid_expense,
                "uuid_client": uuid_provider,
                "type_transaction": 2,
                "expense_name": gasto.get('nombre', f'Gasto {i+1}'),
                "serie": "G",
                "folio": str(i+1),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": gasto.get('descripcion', ''),
                "value": value,
                "taxes": 0,
                "currency": 95,
                "exchange_rate": 1,
                "uuid_user": uuid_user,
                "products": [
                    {
                        "name": gasto.get('nombre', f'Gasto {i+1}'),
                        "expense": 1,
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
            
            response = requests.post(url, headers=headers, json=gasto_data)
            if response.status_code == 200:
                print(f"Gasto {i+1} registrado exitosamente.")
                gasto_response = response.json()
                uuid_gasto = gasto_response['data']['uuid']
                pagar_gasto(uuid_gasto, uuid_provider, value)
            else:
                print(f"Error al registrar el gasto {i+1}:", response.text)
        else:
            print(f"Gasto inválido: {gasto}")

# 12. Pagar el gasto
def pagar_gasto(uuid_gasto, uuid_provider, amount):
    url = "https://api.somosoliver.com/expenses/payment/create"
    pago_data = {
        "uuid_business": uuid_business,
        "uuid_sale": uuid_gasto,
        "uuid_bank": "821e43aa-5b74-48d0-87ce-417092560666",
        "uuid_contact": uuid_provider,
        "complement_payment": 0,
        "amount": amount,
        "currency": 95,
        "exchange_rate": 1,
        "uuid_payment_method": "79cdd26b-7354-47bc-90fe-2719bf19e4e9",
        "comments": "Pago de gasto",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    response = requests.post(url, headers=headers, json=pago_data)
    if response.status_code == 200:
        print(f"Pago del gasto registrado exitosamente.")
    else:
        print("Error al pagar el gasto:", response.text)

# Función principal
def main():
    actualizar_negocio()
    actualizar_telefono()
    crear_clientes_proveedores()
    crear_productos_servicios()
    crear_caja_registradora()
    abrir_turno_pos()
    generar_ventas_pos()
    cerrar_turno_pos()
    crear_tipo_gasto()
    registrar_gastos()
    print("Proceso completado exitosamente.")

if __name__ == "__main__":
    main()
