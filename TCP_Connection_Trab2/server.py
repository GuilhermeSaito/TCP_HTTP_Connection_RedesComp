#!/usr/bin/env python3  
import socket
import hashlib
import os
import threading

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

def checksumSHA256(data):
    #Inicializa um objeto hashlib com o algoritmo SHA-256
    hasher = hashlib.sha256()

    #Atualiza o hasher com os dados de entrada
    hasher.update(data)

    #Calcula o checksum SHA-256 e retorna em formato hexadecimal
    checksum = hasher.hexdigest()
    return checksum

def request_file(client_socket, dataString):
    print("Funcao para mandar os arquivos caso escolhido")

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
            request_file(client_socket = client_socket, dataString = dataString)

        elif dataString == 'Chat':
            chat(client_socket = client_socket, adress = adress)
    
#Envia arquivo solicitado pelo cliente
def send_file(fileName, adress, packetNumber):
    packge_num = 0

    if not os.path.isfile(fileName):
        print("Arquivo nao encontrado: " + fileName)
        server_socket.sendto(b"1", adress)
    else:
        try:
            with open(fileName, 'rb') as f:
                while data := f.read(BUFFER):
                    packge_num += 1

                    # Calcula checksum com SHA-256
                    checksum = checksumSHA256(data)

                    check = 'NOK'

                    #Verifica se o pacote foi enviado corretamente
                    while check == 'NOK':
                        server_socket.sendto(checksum.encode('utf-8') + ";".encode('utf-8') + str(packge_num).encode('utf-8') + ">".encode('utf-8') + data, adress)
                        check = server_socket.recvfrom(BUFFER)
                        check = check[0].decode('utf-8')
                        if check == 'NOK':
                            print('NOK recebido. Reenviando parte do arquivo.')
                    
                    # Incrementa o número do pacote para o próximo
                    # packetNumber += 1

        #Se o arquivo não existir
        except FileNotFoundError as msg:
            print("Deu algum error:" + str(msg + "\n"))
            server_socket.sendto(b"ERRO!", adress)
            
        # Mensagem de finalização do arquivo
        print(f'Arquivo {fileName} enviado para {adress}')
        server_socket.sendto(b'', adress)

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