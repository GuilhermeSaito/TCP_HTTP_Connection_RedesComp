#!/usr/bin/env python3  
import socket
import os
import threading
from io import BytesIO
import base64

HOST = '0.0.0.0'
PORT = 9999
BUFFER = 1024

#Create a Socket (connect two computers)
def create_socket():
    try:
        global server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return server_socket
    
    except socket.error as msg:
        print("Socket creation error:" + str(msg))

#Binding the socket and listening for connections
def bind_socket(server_socket):
    try:
        print("Binding the Port: "+ str(PORT))

        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

    except socket.timeout as msg:
        print("Socket Binding error" + str(msg) +"\n" + "Retrying...")
        bind_socket(server_socket)

def parse_http_request(request_data):
    # Split the request data into lines
    lines = request_data.split("\r\n")

    # Parse the request line
    method, path, _ = lines[0].split(" ")

    # Parse the query parameters for GET requests
    # query_params = {}
    # if "?" in path:
    #     url_parts = urllib.parse.urlparse(path)
    #     query_params = urllib.parse.parse_qs(url_parts.query)

    return method, path#, query_params

def return_html_text_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Text Page</title>
    </head>
    <body>
        <h1>Another Another World!</h1>
    </body>
    </html>
    """

def return_html_image_page():
    with open("send_image.jpg", "rb") as f:
        image_data = f.read()

    image_base64 = base64.b64encode(image_data).decode()

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Page</title>
    </head>
    <body>
        <img src="data:image/jpg;base64, {}" alt="Sample Image">
    </body>
    </html>
    """.format(image_base64)

def return_html_text_image_page():
    with open("moodle_format.jpg", "rb") as f:
        image_data = f.read()

    image_base64 = base64.b64encode(image_data).decode()

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image with Text Page</title>
    </head>
    <body>
        <h1>Another Another World!</h1>
        <img src="data:image/jpeg;base64,{}" alt="Sample Image">
    </body>
    </html>
    """.format(image_base64)

def return_html_error():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error Page</title>
    </head>
    <body>
        <h1>Cara, alguma coisa deu errado!</h1>
    </body>
    </html>
    """

#Recebe comandos do cliente
def get_commands(client_socket, adress):
    request_data = client_socket.recv(1024).decode("utf-8")
    # method, path, query_params = parse_http_request(request_data)
    method, path = parse_http_request(request_data)
    print("Method:", method)
    print("Path:", path)
    # print("Query Parameters:", query_params)

    if "text" in path:
        html_content = return_html_text_page()

        # Send the response headers
        response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n".format(len(html_content))
        client_socket.sendall(response_headers.encode("utf-8"))
        
        # Send the HTML content
        client_socket.sendall(html_content.encode("utf-8"))

    elif "image" in path:
        html_content = return_html_image_page()

        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html_content

        client_socket.sendall(response.encode("utf-8"))

    elif "both" in path:
        html_content = return_html_text_image_page()

        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html_content

        client_socket.sendall(response.encode("utf-8"))
    
    else:
        html_content = return_html_error()

        # Send the response headers
        "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n" + html_content
        client_socket.sendall(response.encode("utf-8"))


    # Close the connection
    print(f"Conexao fechada com: {adress}!")
    client_socket.close()

    
def main():
    server_socket = create_socket()
    bind_socket(server_socket)

    print("Servidor está ouvindo em ", (HOST, PORT))

    # ######################### Exemplo de request pelo browser quando o server tiver rodando
    # http://xxx.xxx.xxx.x:9999/both

    while True:
        # Aqui recebe o ip, port
        client_socket, adress = server_socket.accept()

        print(f"Recebido conexao desse cliente: {adress[0]}, port: {adress[1]}")

        client_thread = threading.Thread(target = get_commands, args = (client_socket, adress[1],))
        client_thread.start()


    # ################### Codigo para matar o processo que estah executando na porta especificada
        # sudo kill -9 `sudo lsof -t -i:9999`
        # Se nao der certo o comando de cima, usa esse:     sudo kill -9 $(sudo lsof -t -i:9999)
    # ###################

main()