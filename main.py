import os
import struct
import random
import pickle
import sys
import pdb

global_comparacoes = 0


def mostrar_comparacoes():
    global global_comparacoes
    print('Total de comparacoes:', global_comparacoes)


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


# Busca binaria no bloco escolhido
def busca_hash_binaria(file, l, r, chave):
    global global_comparacoes
    global_comparacoes += 1
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
    global global_comparacoes
    global_comparacoes = 0
    l = (chave % 200) * 400
    r = l + 399
    posicao = busca_hash_binaria(index, l, r, chave)
    return posicao



# Criar índices NORMAIS para a chave.
def criar_indice_comum(caminho_dados):
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
    global global_comparacoes

    posicao_inicial = (chave % 200) * 400
    with open('index_hash', 'rb') as index:
        index.seek(posicao_inicial)
        for i in range(0, 50):
            registro = struct.unpack('ii', index.read(8))
            global_comparacoes += 1
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



def busca_binaria_indice(file, l, r, chave: int):
    tamanho_registro = struct.calcsize('ii')
    global global_comparacoes
    global_comparacoes += 1
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


def busca_binaria_indice_helper(caminho:str, chave:int):
    global global_comparacoes
    global_comparacoes = 0
    r = os.stat(caminho).st_size
    arq = open(caminho, 'rb')
    posicao = busca_binaria(arq, 0, r, chave)
    arq.close()
    return posicao




def busca_binaria(file, l, r, chave: int):
    tamanho_registro = struct.calcsize('i30sii')
    global global_comparacoes

    global_comparacoes += 1
    if r >= l:
        mid = ((l + (r - l) // 2) // tamanho_registro) * tamanho_registro
        file.seek(mid)
        #print('Posição: ', file.tell())
        file_read = file.read(tamanho_registro)
        if len(file_read) < tamanho_registro:
            return -1
        #print('Bytes lidos:', len(file_read))
        registro = struct.unpack('i30sii', file_read)

        if registro[0] == chave:
            return mid

        elif registro[0] > chave:
            return busca_binaria(file, l, mid - tamanho_registro, chave)

        else:
            return busca_binaria(file, mid + tamanho_registro, r, chave)

    else:
        return -1


def busca_binaria_helper(caminho: str, chave: int):
    global global_comparacoes
    global_comparacoes = 0
    r = os.stat(caminho).st_size
    arq = open(caminho, 'rb')
    posicao = busca_binaria(arq, 0, r, chave)
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
    print('4. MOSTRAR INDICE (COMUM)')
    print('5. PESQUISA BINARIA (SEM INDICE)')
    print('6. PESQUISA BINARIA (COM INDICE COMUM)')
    print('7. CRIAR INDICE (HASH)')
    print('8. MOSTRAR INDICE (HASH)')
    print('9. PESQUISA HASH (LINEAR)')
    print('10. PESQUISA HASH (BINARIA)')
    print('11. CRIAR INDICE (ARVORE - NOME)')
    print('12. MOSTRAR INDICE (ARVORE - CAMINHAMENTO CENTRAL)')
    print('13. PESQUISA POR NOME (INDICE ARVORE)')
    print('14. SAIR')


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

    random.shuffle(lista_nome_sobrenome)
    with open('dados', 'wb') as dados:
        for nome in lista_nome_sobrenome:
            idade = random.randrange(18, 65)
            salario = random.randrange(1000, 7000)
            registro = struct.pack('i30sii', chave, nome.encode('utf-8'), idade, salario)
            chave += 1
            dados.write(registro)


class Nodo:

    def __init__(self, nome:str, endereco:int):
        self.nome = nome
        self.endereco = endereco
        self.l = None
        self.r = None

    def insert(self, nome:str, endereco:int):
        if self.nome:
            if nome < self.nome:
                if self.l is None:
                    self.l = Nodo(nome, endereco)
                else:
                    self.l.insert(nome, endereco)
            elif nome > self.nome:
                if self.r is None:
                    self.r = Nodo(nome, endereco)
                else:
                    self.r.insert(nome, endereco)
        else:
            self.nome = nome
            self.data = data


    def mostrar_arvore(self):
        if self.l:
            self.l.mostrar_arvore()
        print('Nome:', self.nome, 'Endereco:',self.endereco)
        if self.r:
            self.r.mostrar_arvore()

    def pesquisar_nome(self, nome:str):
        global global_comparacoes
        #pdb.set_trace()
        if self:
            #print('nodo atual:',self.nome)
            global_comparacoes += 1
            if self.nome == nome:
                return self.endereco
            elif nome < self.nome:
                if self.l:
                    return self.l.pesquisar_nome(nome)
            else:
                if self.r:
                    return self.r.pesquisar_nome(nome)
        else:
            return -1


    def size_arvore(self):
        cont = sys.getsizeof(self)
        if self.l:
            cont += self.l.size_arvore()
        if self.r:
            cont += self.r.size_arvore()
        return cont
            


def mostrar_arvore_helper():
    with open('index_arvore', 'rb') as index:
        arvore = pickle.load(index)
        arvore.mostrar_arvore()
        print('Tamanho da árvore em memória:', arvore.size_arvore() / 1000, 'KB')


def criar_indice_bst(caminho_dados):
    with open(caminho_dados, 'rb') as dados, open('index_arvore', 'wb') as index:
        tamanho_registro = struct.calcsize('i30sii')
        leitura = dados.read(tamanho_registro)
        registro = struct.unpack('i30sii', leitura)
        endereco = 0
        arvore = Nodo(registro[1].decode('utf-8').rstrip(), endereco)

        while True:
            leitura = dados.read(tamanho_registro)
            if leitura == b'':
                break
            registro = struct.unpack('i30sii', leitura)
            endereco += tamanho_registro
            arvore.insert(registro[1].decode('utf-8').rstrip(), endereco)

        pickle.dump(arvore, index)


def pesquisar_nome_helper(nome:str):
    posicao = 0
    global global_comparacoes
    global_comparacoes = 0
    with open('index_arvore', 'rb') as index:
        arvore = pickle.load(index)
        print('Tamanho da arvore em memoria: ', arvore.size_arvore(), 'bytes')
        posicao = arvore.pesquisar_nome(nome)
        return posicao


def buscar_posicao(caminho_dados:str, posicao:int):
    with open(caminho_dados, 'rb') as dados:
        tamanho_registro = struct.calcsize('i30sii')
        dados.seek(posicao)
        leitura = dados.read(tamanho_registro)
        return leitura



def main():
    lista_registros = []

    caminho = './dados'
    while True:
        mostrar_menu_principal()
        opcao = input('Informe a opcao desejada: ')
        if opcao == '14':
            break
        elif opcao == '1':
            popular_base_dados()
        elif opcao == '2':
            mostrar_registros_arquivo('dados')
        elif opcao == '3':
            criar_indice_comum('dados')
        elif opcao == '5':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao: int = busca_binaria_helper(caminho, chave)
            if posicao != -1:
                print('Registro encontrado na posicao: ', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro não localizado')
            mostrar_comparacoes()
        elif opcao == '6':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao: int = busca_binaria_indice_helper('dados', chave)
            if posicao != -1:
                print('Registro encontrado na posicao: ', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro não localizado')
            mostrar_comparacoes()

        elif opcao == '4':
            ler_indices('index')
        elif opcao == '7':
            criar_indices_hash('dados')
        elif opcao == '8':
            ler_indices('index_hash')
        elif opcao == '9':
            chave: int = int(input('Qual chave deseja buscar: '))
            global global_comparacoes
            global_comparacoes = 0
            posicao = busca_hash_linear(chave)
            if posicao != -1:
                print('Registro localizado na posicao', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro nao localizado')
            mostrar_comparacoes()
        elif opcao == '10':
            chave: int = int(input('Qual chave deseja buscar: '))
            posicao = busca_hash_binaria_helper('index_hash', chave)
            if posicao != -1:
                print('Registro localizado na posicao', posicao)
                registro = buscar_registro_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro nao localizado')
            mostrar_comparacoes()
        elif opcao == '11':
            criar_indice_bst('dados')
        elif opcao == '12':
            mostrar_arvore_helper()
        elif opcao == '13':
            nome = input('Informe o nome que deseja procurar    ')
            nome ="{:<30}".format(nome).rstrip()
            posicao = pesquisar_nome_helper(nome)
            if posicao != -1:
                print('Registro localizado na posicao', posicao)
                registro = buscar_posicao('dados', posicao)
                mostrar_registro(registro)
            else:
                print('Registro nao localizado')
            mostrar_comparacoes()




if __name__ == "__main__":
    main()