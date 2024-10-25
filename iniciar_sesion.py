import requests

# Datos de inicio de sesión
email = "libreria@test.com"
password = "123456"

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
    
    # Guardar el token en un archivo
    with open("datos_usuario.txt", "w") as file:
        file.write(f"token:{token}\n")
        file.write(f"uuid_business:{uuid_business}\n")
        file.write(f"uuid_user:{uuid_user}\n")
        file.write(f"business_type:{business_type}\n")
        file.write(f"email:{email}\n")
    print("Token guardado exitosamente en datos_usuario.txt.")
else:
    print("Error al iniciar sesión:", response.text)

