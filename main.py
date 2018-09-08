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
        print('Mid', mid)
        file.seek(mid)
        print('Posição: ', file.tell())
        file_read = file.read(tamanho_registro)
        if len(file_read) < tamanho_registro:
            return -1
        print('Bytes lidos:', len(file_read))
        registro = struct.unpack('ii', file_read)

        if registro[0] == chave:
            return registro[1]
        elif registro[0] > chave:
            return busca_binaria_indice(file, l, mid - tamanho_registro, chave)
        else:
            return busca_binaria_indice(file, mid + tamanho_registro, r, chave)

    else:
        return -1


def criar_indices(caminho_dados):
    tamanho_registro = struct.calcsize('i30sii')
    endereco = 0
    with open(caminho_dados, 'rb') as dados, open('./index', 'wb') as index:
        while True:
            registro = dados.read(tamanho_registro)
            if len(registro) > 0:
                registro = struct.unpack('i30sii', registro)
                index.write(struct.pack('ii', registro[0], endereco, b'\n'))
                endereco += tamanho_registro
            else:
                break


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
    posicao = busca_binaria(arq, 0, r, chave)
    arq.close()
    return posicao


def mostrar_menu_principal():
    print('1. NOVO REGISTRO')
    print('2. GRAVAR REGISTROS NO ARQUIVO')
    print('3. MOSTRAR REGISTROS NO ARQUIVO')
    print('4. PESQUISA BINARIA')
    print('5. CRIAR INDICE')
    print('6. MOSTRAR ARQUIVO INDICE')
    print('7. PESQUISA BINARIA COM INDICE')
    print('10. SAIR')


def popular_base_dados():

    chave = 1
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


    with open('dados', 'wb') as dados:
        for nome in lista_nome_sobrenome:
            idade = random.randrange(18, 65)
            salario = random.randrange(1000, 7000)
            registro = struct.pack('i30sii', chave, nome.encode('utf-8'), idade, salario)
            chave += 1
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
            lista_registros.append(criar_registro_helper())
        elif opcao == '2':
            gravar_arquivo(lista_registros, caminho)
            lista_registros = []
        elif opcao == '3':
            mostrar_registros_arquivo(caminho)
        elif opcao == '4':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao: int = busca_binaria_helper(caminho, chave)
            if posicao != -1:
                print('Registro encontrado na posicao: ', posicao)
            else:
                print('Registro não localizado')
        elif opcao == '5':
            criar_indices('./dados')
        elif opcao == '6':
            ler_indices('./index')
        elif opcao == '7':
            chave: int = int(input('Informe a chave que deseja procurar:  '))
            caminho_indice = './index'
            r = os.stat(caminho_indice).st_size
            print('Tamanho do arquivo indice', r)
            with open('./index', 'rb') as index_file:
                endereco: int = busca_binaria_indice(index_file, 0, r, chave)
                if endereco != -1:
                    print('A chave', chave, 'esta no endereco', endereco)
                    with open('./dados', 'rb') as file_dados:
                        file_dados.seek(endereco)
                        tamanho_registro = struct.calcsize('i30sii')
                        registro = file_dados.read(tamanho_registro)
                        mostrar_registro(registro)
                else:
                    print('Chave', chave, 'nao localizada')


if __name__ == "__main__":
    main()