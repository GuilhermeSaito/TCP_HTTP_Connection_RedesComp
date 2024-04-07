#!/usr/bin/env python3  

# Arrumar para colocar o checksum com o dado e a numeracao do pacote
# Pensar em fazer outra forma de perda de pacote

import socket
import hashlib

SERVER_IP = 'localhost'
SERVER_PORT = 9999
BUFFER = 2048
SERVER_BUFFER = 1024

def create_socket():
    try:
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    except socket.error as msg:
        print("Socket creation error:" + str(msg))  

def checksumSHA256(dados):
    #Inicializa um objeto hashlib com o algoritmo SHA-256
    hasher = hashlib.sha256()

    print("----------------- DADOS CLIENT SIDE -----------------")
    print(dados.encode('utf-8'))

    #Atualiza o hasher com os dados de entrada
    hasher.update(dados.encode('utf-8'))

    #Calcula o checksum SHA-256 e retorna em formato hexadecimal
    novo_checksum = hasher.hexdigest()
    
    return novo_checksum

def receive_file_data():
    recvFile = 'recvFile.txt'
    file_size = SERVER_BUFFER

    # Recebendo os dados
    with open(recvFile, 'wb') as file:
        while file_size == SERVER_BUFFER:
            file_info = client_socket.recv(BUFFER).decode('utf-8')
            print("--------------------- File info ---------------------")
            print(file_info)

            # if not file_info:
            #     print("Ta caindo aqui?")
            #     break

            file_info_split = file_info.split('\n')
            print("--------------------- File info split ---------------------")
            print(file_info_split)

            file_name = file_info_split[0]
            print("--------------------- File name ---------------------")
            print(file_name)
            file_size = int(file_info_split[1])
            print("--------------------- File size ---------------------")
            print(file_size)
            file_checksum = file_info_split[2]
            print("--------------------- File checksum ---------------------")
            print(file_checksum)
            data = file_info_split[3]
            print("--------------------- File data ---------------------")
            print(data)
            file_status = file_info_split[4]
            print("--------------------- File status ---------------------")
            print(file_status)


            # Arquivo não foi encontrado
            if file_status == "nok":
                print("Arquivo inexistente no servidor ou erro na abertura do arquivo.")
                return

            print("--------------------- Data Encode ---------------------")
            print(data.encode('utf-8'))

            file.write(data.encode('utf-8'))

            print("Vai fazer o checksum")

            data_checksum = checksumSHA256(data)


            if data_checksum == file_checksum:
                print(f'Arquivo {file_name} recebido e verificado com sucesso.')
                print(f'Nome: {file_name}\nTamanho: {file_size}\nHash: {file_checksum}\nStatus: {file_status}')
            else:
                print(f'Erro na integridade do arquivo: {file_checksum} != {data_checksum}')
        

def main():
    # Inicializa o socket TCP
    server_address = (SERVER_IP, SERVER_PORT)

    create_socket()
    client_socket.connect(server_address)

    print("Opções disponíveis:")
    print("1. Sair")
    print("2. Requisitar um arquivo")
    print("3. Modo Chat")

    while True:
        choice = input("Escolha uma opção (1 ou 2 ou 3): ")
        
        # 1 = Sair
        if choice == "1":
            client_socket.send("Sair".encode('utf-8'))
            break
        # 2 = Requisitar o arquivo
        elif choice == "2":
            file_request = input("Digite o nome do arquivo desejado: ")
            client_socket.send(f"Arquivo {file_request}".encode('utf-8'))
            receive_file_data()
        # 3 = Chat
        elif choice == "3":
            client_socket.send("Chat".encode('utf-8'))

            print(client_socket.recv(BUFFER).decode('utf-8'))

            while True:
                message = input("Digite sua mensagem (ou 'sair' para encerrar o chat): ")
                if message.lower() == "sair":
                    client_socket.send(message.encode('utf-8'))
                    break
                client_socket.send(message.encode('utf-8'))

            print(client_socket.recv(BUFFER).decode('utf-8'))
        # QualquerOutraCoisa = Tente novamente
        else:
            print("Opcao invalida. Tente novamente")

    print(client_socket.recv(BUFFER).decode('utf-8'))
    client_socket.close()

if __name__ == "__main__":
    main()