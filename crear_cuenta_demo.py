import requests

# Solicitar datos al usuario
email = input("Introduce el correo electrónico del nuevo usuario: ")
business_type = input("Introduce el tipo de negocio: ")
password = "123456"

# Endpoint para crear una nueva cuenta
signup_url = "https://api.somosoliver.com/signup/user/pass"

# Datos para crear la cuenta
signup_data = {
    "user": email,
    "password": password
}

# Crear la cuenta
response = requests.post(signup_url, json=signup_data)
if response.status_code == 200:
    print("Cuenta creada exitosamente.")
    signup_response = response.json()
    uuid_business = signup_response['data']['uuid_business']
    uuid_user = signup_response['data']['uuid_user']
else:
    print("Error al crear la cuenta:", response.text)
    exit()

# Endpoint para iniciar sesión y obtener el token
signin_url = "https://api.somosoliver.com/signin/password"

signin_data = {
    "user": email,
    "password": password
}

# Iniciar sesión
response = requests.post(signin_url, json=signin_data)
if response.status_code == 200:
    print("Inicio de sesión exitoso.")
    signin_response = response.json()
    token = signin_response['token']
else:
    print("Error al iniciar sesión:", response.text)
    exit()

# Guardar el token y los UUIDs en un archivo para usarlos en el siguiente script
with open("datos_usuario.txt", "w") as file:
    file.write(f"token:{token}\n")
    file.write(f"uuid_business:{uuid_business}\n")
    file.write(f"uuid_user:{uuid_user}\n")
    file.write(f"business_type:{business_type}\n")
    file.write(f"email:{email}\n")

print("Datos guardados exitosamente para el siguiente script.")

