import requests

url ="https://github.com/AlexSilvan12/SistemasATM/blob/main/version.txt"

try:
    response = requests.get(url)
    if response.status_code == 200:
        nueva_version = response.text.strip()
        print("Versión disponible:", nueva_version)
    else:
        print("Error al obtener la versión:", response.status_code)
except Exception as e:
    print("Error de conexión:", e)
