#!/usr/bin/env python3  

# Arrumar para colocar o checksum com o dado e a numeracao do pacote
# Pensar em fazer outra forma de perda de pacote

import socket
import hashlib

SERVER_IP = 'localhost'
SERVER_PORT = 9999
BUFFER = 2048

def create_socket():
    try:
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return client_socket
    
    except socket.error as msg:
        print("Socket creation error:" + str(msg))  

def confere_checksum(dados, hash_received):
    #Inicializa um objeto hashlib com o algoritmo SHA-256
    hasher = hashlib.sha256()

    #Atualiza o hasher com os dados de entrada
    hasher.update(dados.encode('utf-8'))

    #Calcula o checksum SHA-256 e retorna em formato hexadecimal
    novo_checksum = hasher.hexdigest()

    #retorna True se os checksum forem iguais e False, caso contrário
    return hash_received == novo_checksum

def receive_file_data():
    # Recebendo os dados
    file_info = client_socket.recv(BUFFER).decode('utf-8').split('\n')
    file_name = file_info[0]
    file_size = int(file_info[1])
    file_hash = file_info[2]
    file_status = file_info[3]

    # Arquivo não foi encontrado
    if file_status == "nok":
        print("Arquivo inexistente no servidor.")
        return
    
    # Escreve o arquivo no diretório local
    with open('Novo_Arquivo.txt', 'wb') as file:
        received_data = 0
        while received_data < file_size:
            data = client_socket.recv(BUFFER)
            received_data += len(data)
            file.write(data)

    # Verifica o hash do arquivo
    hash_sha256 = hashlib.sha256()
    with open (file_name, 'rb') as file:
        while True:
            data = file.read(BUFFER)
            if not data:
                break
            hash_sha256.update(data)
    received_hash = hash_sha256.hexdigest()

    if received_hash == file_hash:
        print(f'Arquivo {file_name} recebido e verificado com sucesso.')
        print(f'Nome: {file_name}\nTamanho: {file_size}\nHash: {file_hash}\nStatus: {file_status}')
    else:
        print(f'Erro na integridade do arquivo: {file_hash} != {received_hash}')
    

def main():
    # Inicializa o socket TCP
    server_address = (SERVER_IP, SERVER_PORT)

    socket = create_socket()
    client_socket.connect(server_address)

    recvFile = 'recvFile.txt'
    backupFile = 'bckFile.txt'

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
            # receive_file_data()
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














    # package_count = 0

    # arquivo = input('Insira o nome do arquivo + extensão \".txt\"\n')
    # bytesEnviados = str.encode('GET ' + arquivo)

    # # Envia a mensagem de solicitação para o servidor
    # client_socket.sendto(bytesEnviados, server_address)

    # try:
    #     flag_error = 1
        
    #     # Recebe os dados do servidor em blocos e os imprime
    #     with open(recvFile, 'wb') as recv_file, open (backupFile, 'wb') as bck_file:
    #         while True:
    #             package_received, _ = socket.recvfrom(BUFFER)

    #             package_received_decoded = package_received.decode("utf-8")

    #             hash_received = package_received_decoded[ :package_received_decoded.find(";")]
    #             num_pack = package_received_decoded[package_received_decoded.find(";") + 1: package_received_decoded.find(">")]
    #             data = package_received_decoded[package_received_decoded.find(">") + 1: ]

    #             print("Num pack recebido: ")
    #             print(num_pack)

    #             if data == "1":
    #                 print('Arquivo nao encontrado')
    #                 flag_error = 0
    #                 break
    #             elif data.startswith('ERRO!'):
    #                 print(data)
    #                 flag_error = 0
    #                 break
    #             elif not data:
    #                 print('Arquivo finalizado!')
    #                 break  # Se não há mais dados, sai do loop
                
    #             bck_file.write(data.encode('utf-8'))

    #             #Opção para o usuário descartar uma parte do arquivo (Simular perda de pacotes)
    #             discard = input("Deseja descartar uma parte do arquivo? (s/n): ")
    #             if discard.lower() == 's':
    #                 percent_to_discard = float(input("Informe a porcentagem do arquivo a ser descartada (0-100): "))

    #                 bytes_to_discard = int(len(data) * ((100 - percent_to_discard) / 100))
    #                 data_dicard = data[:bytes_to_discard]
    #                 data = data_dicard

    #             # Verifica o checksum e solicita reenvio em caso de falha
    #             if confere_checksum(data, hash_received):
    #                 recv_file.write(data.encode('utf-8'))
    #                 print(f'Pacote {package_count} enviado!')
    #                 check = 'OK'.encode('utf-8')
    #             else:
    #                 print(f'Erro de checksum no pacote {package_count}. Uma parte do arquivo foi perdida.\nRequisitando reenvio.')
    #                 check = 'NOK'.encode('utf-8')
    
    #             socket.sendto(check, server_address)
    #         if flag_error:
    #             print(f'Todos os dados recebidos do servidor escritos em: {backupFile}')
    #             print(f'Somente os dados validos (excluido os dados que vieram faltando) {recvFile}')
    
    # except Exception as e:
    #     print(f"Ocorreu um erro durante a comunicação com o servidor: {e}")
    
    # finally:
    #     # Fecha o socket do cliente
    #     print("Finalizado. Fechando conexão com o servidor.")
    #     socket.close()

if __name__ == "__main__":
    main()