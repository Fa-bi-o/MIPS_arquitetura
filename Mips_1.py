import json

"""
    O código não trata os valores negativos, registro e mem, já que isso será na entrega 2, apenas tem o objetivo
    de encontrar o formato correto dos códigos hexadecimais de entrada e suas saídas "text" dos registradores
    utilizados. 
    
    A leitura foi baseada no documento "Requisitos Simulador MIPS.pdf", com {"config": {}, "data": {},
    "text": [lista com hexadecimais]}, na segunda entrega o código será adaptado para os registradores.
    
    Editei o arquivo de "exemplos.input.json" para "Mips_1.input.json" e deixei com os códigos hexadecimais de todas as 
    instruções que foram pedidas, basta que o arquivo.json esteja no mesmo diretório que o arquivo.py python para ser 
    corretamente executado, ou alterar o nome do arquivo no no código, atualmente linha 21.    
    
    Em relação a grupo, se não tiver problema continuarei fazendo só, se for obrigatória a formação de um grupo,
    fico a disposição de me colocarem no grupo que tiver vaga, favor avisar. 
    
"""

# Leitura do arquivo JSON
with open('Mips_1.input.json', encoding='utf8') as arquivo_entrada:
    lista_entrada = json.load(arquivo_entrada)

arquivo_entrada.close()

# Dicionários para os formatos R I J
dic_i = {
    '001111': 'lui', '001000': 'addi', '001010': 'slti', '001100': 'andi', '001101': 'ori', '001110': 'xori',
    '100011': 'lw', '101011': 'sw', '000001': 'bltz', '000100': 'beq', '000101': 'bne', '001001': 'addiu',
    '100000': 'lb', '100100': 'lbu', '101000': 'sb'
}

dic_r = {
    '100000': 'add', '100010': 'sub', '101010': 'slt', '100100': 'and', '100101': 'or', '100110': 'xor',
    '100111': 'nor', '100001': 'addu', '100011': 'subu', '000000': 'sll', '000010': 'srl', '000011': 'sra',
    '000100': 'sllv', '000110': 'srlv', '000111': 'srav', '001100': 'syscall', '001000': 'jr', '010000': 'mfhi',
    '010010': 'mflo', '011000': 'mult', '011001': 'multu', '011010': 'div', '011011': 'divu'
}

dic_j = {'000010': 'j', '000011': 'jal'}

lista_saida = []


def identificar_formato(num_hexa):
    """
        Função responsável por receber o número hexadecimal, trata-lo e pelos bits responsáveis equivalentes ao opcode,
        identificar qual o formato correto, passando as informações para a função registrador.
    """

    num_bin = bin(int(num_hexa, 16))[2:]                                        # Removendo 0x do hexadecimal

    while len(num_bin) < 32:                                                    # Completando o número com 0 até 32 bits
        num_bin = '0' + num_bin

    if num_bin[0:6] == '000010' or num_bin[0:6] == '000011':                    # Formatos J
        return registrador(dic_j.get(num_bin[0:6]), num_bin, num_hexa)

    elif num_bin[0:6] == '000000':                                              # Formatos R
        return registrador(dic_r.get(num_bin[26:32]), num_bin, num_hexa)

    else:
        return registrador(dic_i.get(num_bin[0:6]), num_bin, num_hexa)          # Formatos I


def registrador(op, num_bin, num_hexa):
    """
        Função responsável por receber o identificador do opcode, e suas representações binárias e hexadecimais,
        retornando a instrução correspondente, já está no padrão para a segunda entrega. os n1, n2, n3 representam os
        números dos registradores MIPS.
    """

    # SYSCALL
    if op == 'syscall':
        text = 'syscall'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}
        return dic

    # TIPOS J
    elif op == 'j' or op == 'jal':

        text = f'{op} start'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    # TIPOS I
    elif op == 'lui':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[16:32], 2)

        text = f'{op} ${n1}, {n2}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'bltz':

        n1 = int(num_bin[6:11], 2)

        text = f'{op} ${n1}, start'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'addi' or op == 'slti' or op == 'andi' or op == 'ori' or op == 'xori' or op == 'addiu':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[16:32], 2)

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'lw' or op == 'sw' or op == 'lb' or op == 'lbu' or op == 'sb':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[16:32], 2)
        n3 = int(num_bin[6:11], 2)

        text = f'{op} ${n1}, {n2}(${n3})'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'beq' or op == 'bne':

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[11:16], 2)

        text = f'{op} ${n1}, ${n2}, start'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    # TIPOS R
    elif op == 'jr':

        n1 = int(num_bin[6:11], 2)

        text = f'{op} ${n1}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'mfhi' or op == 'mflo':

        n1 = int(num_bin[16:21], 2)

        text = f'{op} ${n1}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'mult' or op == 'multu' or op == 'div' or op == 'divu':

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[11:16], 2)

        text = f'{op} ${n1}, ${n2}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'sll' or op == 'srl' or op == 'sra':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[21:26], 2)

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'sllv' or op == 'srlv' or op == 'srav':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[6:11], 2)

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'add' or op == 'sub' or op == 'slt' or op == 'and' or op == 'or':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    elif op == 'xor' or op == 'nor' or op == 'addu' or op == 'subu':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": {}, "mem": {}, "output": ""}

        return dic

    else:
        return 'erro do registrador'


# Adicionando os dicionários a lista de saída
for hexadecimal in lista_entrada.values():
    for item in hexadecimal:
        lista_saida.append(identificar_formato(item))

# Gravando a lista no formato JSON
with open('GrupoE.Mips_1.output.json', 'w') as arquivo_saida:
    json.dump(lista_saida, arquivo_saida, indent=4)
