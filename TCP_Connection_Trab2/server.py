#!/usr/bin/env python3  
import socket
import hashlib
import os
import threading

HOST = '0.0.0.0'
PORT = 9990
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

def checksumSHA256(data):
    #Inicializa um objeto hashlib com o algoritmo SHA-256
    hasher = hashlib.sha256()

    print("----------------- DATA SERVER SIDE -----------------")
    print(data)

    #Atualiza o hasher com os dados de entrada
    hasher.update(data)

    #Calcula o checksum SHA-256 e retorna em formato hexadecimal
    checksum = hasher.hexdigest()
    return checksum

def request_file(client_socket, dataString, adress):
    file_name = dataString.split(' ')[1] # Nome
    print(f'Recebendo arquivo {file_name}!')

    # Verifica se arquivo existe
    if os.path.isfile(file_name):
        try:
            with open(file_name, 'rb') as f:
                cont = 0
                while data := f.read(BUFFER):
                    size = len(data)                        # Tamanho
                    checksum = checksumSHA256(data = data)  # Hash
                    status = "ok"                           # Status

                    # client_socket.send(send_data)
                    client_socket.send(file_name.encode('utf-8') +
                                       str(cont).encode('utf-8') +
                                       ">".encode('utf-8') +
                                       str(size).encode('utf-8') +
                                       ">".encode('utf-8') +
                                       checksum.encode('utf-8') +
                                       ">".encode('utf-8') +
                                       status.encode('utf-8') +
                                       ">".encode('utf-8') +
                                       data)
                    print("-------------- TESTE")
                    print(data)
                    print(f"Arquivo enviado para {adress}! Part {cont}")

                    cont += 1
            
        except FileNotFoundError as msg:
            print(f"Problema ao abrir o arquivo: {adress}! {msg}")
            client_socket.send('1'.encode('utf-8'))
    else:
        print(f"Arquivo não existente {adress}!")
        client_socket.send('1'.encode('utf-8'))

def chat(client_socket, adress):
    client_socket.send("Modo Chat ".encode('utf-8'))
    print(f'{adress} conectado ao Chat!')

    while True:
        message = client_socket.recv(1024).decode('utf-8')

        if message.lower() == "sair":
            print(f"{adress} Saiu do Chat!")
            break

        print(f"Mensagem ({adress}): {message}")
    
    client_socket.send("Saindo do modo chat.".encode('utf-8'))

#Recebe comandos do cliente
def get_commands(client_socket, adress):
    while True:
        dataString = client_socket.recv(BUFFER).decode('utf-8').strip()

        if dataString == 'Sair':
            print(f'{adress} saiu da conexao com o servidor!')

            client_socket.send('Fechando conexão. '.encode('utf-8'))
            client_socket.close()
            break
        
        elif dataString.startswith('Arquivo'):
            request_file(client_socket = client_socket, dataString = dataString, adress = adress)

        elif dataString == 'Chat':
            chat(client_socket = client_socket, adress = adress)
    
def main():
    server_socket = create_socket()
    bind_socket(server_socket)

    print("Servidor está ouvindo em ", (HOST, PORT))

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