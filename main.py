import os
import struct
import random

# Ler o nome. Controla para que no máximo seja de 20 caracteres
def ler_nome() -> str:
    while True:
        entrada = "{:<20}".format(input('Digite o nome: '))
        if len(entrada) <= 20:
            return entrada
        else:
            print('Entrada invalida. Tamanho maximo permitido: 20 caracteres')


# Le numeros, pede entrada do usuario até que seja um inteiro válido
def ler_numero() -> int:
    while True:
        try:
            n: int = int(input('Informe o numero: '))
            return n
        except ValueError:
            print('Valor nao e um numero. Tente novamente')


# Recebe os dados em formato int, texto, int, int e devolve uma struct de 32 bytes
def criar_registro(numero:int, nome:str, idade:int, salario:int):
    registro = struct.pack('i30sii', numero, nome.encode('utf-8'), idade, salario)
    return registro


# Chama as funções de entrada e cria o registro
def criar_registro_helper():
    numero = ler_numero()
    nome = ler_nome()
    idade = ler_numero()
    salario = ler_numero()
    registro = criar_registro('i30sii',numero, nome, idade, salario)
    return registro


# Recebe uma lista de structs e escreve os bytes para o arquivo
def gravar_arquivo(lista_structs, caminho_arquivo: str):
    with open(caminho_arquivo, 'ab') as arq:
        for reg in lista_structs:
            arq.write(reg)


# Recebe uma struct de bytes e mostra seus campos
def mostrar_registro(registro: bytes):
    tupla = struct.unpack('i30sii', registro)
    print('Numero: ', tupla[0])
    print('Nome: ', tupla[1].decode('utf-8'))
    print('Idade: ', tupla[2])
    print('Salario: ', tupla[3])


# Percorre o arquivo e mostra os registros
def mostrar_registros_arquivo(caminho_arquivo):
    tamanho_registro = struct.calcsize('i30sii')
    with open(caminho_arquivo, 'rb') as arq:
        entrada = arq.read(tamanho_registro)
        while entrada != b'':
            mostrar_registro(entrada)
            entrada = arq.read(tamanho_registro)


def busca_binaria(file, l, r, chave: int):
    tamanho_registro = struct.calcsize('i30sii')

    if r >= l:
        mid = ((l + (r - l) // 2) // tamanho_registro) * tamanho_registro
        file.seek(mid)
        print('Posição: ', file.tell())
        file_read = file.read(tamanho_registro)
        if len(file_read) < tamanho_registro:
            return -1
        print('Bytes lidos:', len(file_read))
        registro = struct.unpack('i30sii', file_read)

        if registro[0] == chave:
            return mid
        elif registro[0] > chave:
            return busca_binaria(file, l, mid - tamanho_registro, chave)
        else:
            return busca_binaria(file, mid + tamanho_registro, r, chave)
    else:
        return -1


def busca_binaria_indice(file, l, r, chave: int):
    tamanho_registro = struct.calcsize('ii')

    if r >= l:

        mid = ((l + (r - l) // 2) // tamanho_registro) * tamanho_registro
        # print('Mid', mid)
        file.seek(mid)
        # print('Posição: ', file.tell())
        file_read = file.read(tamanho_registro)
        if len(file_read) < tamanho_registro:
            return -1
        # print('Bytes lidos:', len(file_read))
        registro = struct.unpack('ii', file_read)

        if registro[0] == chave:
            return registro[1]
        elif registro[0] > chave:
            return busca_binaria_indice(file, l, mid - tamanho_registro, chave)
        else:
            return busca_binaria_indice(file, mid + tamanho_registro, r, chave)

    else:
        return -1


# Busca binaria no bloco escolhido
def busca_hash_binaria(file, l, r, chave):
    tamanho_registro = struct.calcsize('ii')

    if r >= l:

        mid = ((l + (r - l) // 2) // tamanho_registro) * tamanho_registro
        # print('Mid', mid)
        file.seek(mid)
        # print('Posição: ', file.tell())
        file_read = file.read(tamanho_registro)
        if len(file_read) < tamanho_registro:
            return -1
        # print('Bytes lidos:', len(file_read))
        registro = struct.unpack('ii', file_read)

        if registro[0] == chave:
            return registro[1]
        elif registro[0] > chave:
            return busca_hash_binaria(file, l, mid - tamanho_registro, chave)
        else:
            return busca_hash_binaria(file, mid + tamanho_registro, r, chave)

    else:
        return -1


def busca_hash_binaria_helper(caminho, chave):
    index = open(caminho, 'rb')
    l = (chave % 200) * 400
    r = l + 399
    posicao = busca_hash_binaria(index, l, r, chave)
    return posicao



# Criar índices NORMAIS para a chave.
def criar_indices(caminho_dados):
    tamanho_registro = struct.calcsize('i30sii')
    endereco = 0
    with open(caminho_dados, 'rb') as dados, open('index', 'wb') as index:
        while True:
            registro = dados.read(tamanho_registro)
            if len(registro) > 0:
                registro = struct.unpack('i30sii', registro)
                index.write(struct.pack('ii', registro[0], endereco))
                endereco += tamanho_registro
            else:
                break


# Inicializar índice hash vazio
def inicializar_indice_hash():

    vazio = struct.pack('i', 0)
    with open('index_hash', 'wb') as index:
        for i in range(0, 20000):
            index.write(vazio)


# Criar índices HASH para a chave primária.
def criar_indices_hash(caminho_dados):

    # Criar o índice zerado
    inicializar_indice_hash()

    tamanho_registro = struct.calcsize('i30sii')
    endereco = 0
    tamanho_registro_index = struct.calcsize('ii')
    qtde_blocos = 200
    vazio = 0

    with open(caminho_dados, 'rb') as dados, open('index_hash', 'r+b') as index:
        index.seek(0)
        while True:
            # Lê um bloco do tamanho de um registro no arquivo de dados
            registro = dados.read(tamanho_registro)
            # Se o tamanho do bloco lido for maior que 0, significa que conseguiu ler um registro
            if len(registro) > 0:
                # Criar uma tupla a partir dos bytes lidos no arquivo de dados
                registro = struct.unpack('i30sii', registro)
                # Calcula o bloco onde a chave primária deve ir
                hash_index = registro[0] % qtde_blocos

                # Calcula o deslocamento para o bloco
                deslocamento = hash_index * 400
                # Desloca o cursor do arquivo para o início do bloco selecionado
                index.seek(deslocamento)

                posicao_lida = struct.unpack('ii', index.read(tamanho_registro_index))
                # Enquanto a posicao lida nao estiver vazia
                # procurar a próxima posicao vazia
                while posicao_lida[0] != vazio:
                    posicao_lida = struct.unpack('ii', index.read(tamanho_registro_index))

                # Volta uma posição
                index.seek(-tamanho_registro_index, 1)
                # Escreve chave e endereco do registro no arquivo de dados
                index.write(struct.pack('ii', registro[0], endereco))
                # Atualiza o endereço para a posição do próximo do registro
                endereco += tamanho_registro
            else:
                break


# Busca hash sequencial. Procura a chave no bloco. Se não achar na primeira, pesquisa sequencialmente
def busca_hash_linear(chave):

    posicao_inicial = (chave % 200) * 400
    with open('index_hash', 'rb') as index:
        index.seek(posicao_inicial)
        for i in range(0, 50):
            registro = struct.unpack('ii', index.read(8))
            if registro[0] == chave:
                return registro[1]
        return -1



# Mostra o arquivo de índice
def ler_indices(caminho_indice):
    tamanho_linha_indice = struct.calcsize('ii')
    with open(caminho_indice, 'rb') as index:
        while True:
            registro = index.read(tamanho_linha_indice)
            if len(registro) > 0:
                registro = struct.unpack('ii', registro)
                for item in registro:
                    print(item)
            else:
                break


def busca_binaria_helper(caminho: str, chave: int):
    r = os.stat(caminho).st_size
    arq = open(caminho, 'rb')
    posicao = busca_binaria_indice(arq, 0, r, chave)
    arq.close()
    return posicao




def buscar_registro_posicao(caminho: str, posicao: int):

    file = open(caminho, 'rb')
    file.seek(posicao)
    tamanho = struct.calcsize('i30sii')
    registro = file.read(tamanho)
    file.close()
    return registro



def mostrar_menu_principal():
    print('1. CRIAR BASE DE DADOS')
    print('2. MOSTRAR REGISTROS NO ARQUIVO')
    print('3. CRIAR INDICE (COMUM)')
    print('4. PESQUISA BINARIA COM INDICE COMUM')
    print('5. MOSTRAR ARQUIVO INDICE COMUM')
    print('6. CRIAR INDICE HASH')
    print('7. MOSTRAR INDICE HASH')
    print('8. BUSCA HASH LINEAR')
    print('9. BUSCA HASH BINARIA')
    print('10. SAIR')


def popular_base_dados():

    chaves = range(0, 100000)
    random.shuffle(chaves)
    lista_nomes = []
    lista_sobrenomes = []

    with open('lista_nomes.txt', 'rb') as nomes:
        for linha in nomes:
            lista_nomes.append(linha.decode('utf-8').rstrip() + ' ')

    with open('lista_sobrenomes.txt', 'rb') as sobrenomes:
        for linha in sobrenomes:
            lista_sobrenomes.append(linha.decode('utf-8').rstrip())


    lista_nome_sobrenome = []
    for nome in lista_nomes:
        for sobrenome in lista_sobrenomes:
            lista_nome_sobrenome.append("{:<30}".format(nome + sobrenome))

    random.shuffle(lista_nome_sobrenome)
    with open('dados', 'wb') as dados:
        i = 0
        for nome in lista_nome_sobrenome:
            idade = random.randrange(18, 65)
            salario = random.randrange(1000, 7000)
            registro = struct.pack('i30sii', chaves[i], nome.encode('utf-8'), idade, salario)
            i += 1
            dados.write(registro)






def main():
    lista_registros = []

    caminho = './dados'
    while True:
        mostrar_menu_principal()
        opcao = input('Informe a opcao desejada: ')
        if opcao == '10':
            break
        elif opcao == '1':
            popular_base_dados()
        elif opcao == '2':
            mostrar_registros_arquivo('dados')
        elif opcao == '3':
            criar_indices('dados')
        elif opcao == '4':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao: int = busca_binaria_helper(caminho, chave)
            if posicao != -1:
                print('Registro encontrado na posicao: ', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro não localizado')
        elif opcao == '5':
            ler_indices('index')
        elif opcao == '6':
            criar_indices_hash('dados')
        elif opcao == '7':
            ler_indices('index_hash')
        elif opcao == '8':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao = busca_hash_linear(chave)
            if posicao != -1:
                print('Registro localizado na posicao', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro nao localizado')
        elif opcao == '9':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao = busca_hash_binaria_helper('index_hash', chave)
            if posicao != -1:
                print('Registro localizado na posicao', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro nao localizado')




if __name__ == "__main__":
    main()