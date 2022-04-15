import json
import numpy
import os

# Recebendo nome dos arquivos na pasta input em forma de lista
caminho_entrada_json = 'input/'
arquivos_entrada = [pos_json[0:-11] for pos_json in os.listdir(caminho_entrada_json) if pos_json.endswith('.json')]

"""
    Código segunda entrega, revisado. Foi enviado em formato zip no AVA o arquivo.py e a pasta input,
    é necessária estar criada na mesma pasta do arquivo para funcionar corretamenteEspero que esteja correto!!
"""

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

# Registradores
regs = {
    '$0': 0, '$1': 0, '$2': 0, '$3': 0, '$4': 0, '$5': 0, '$6': 0, '$7': 0, '$8': 0, '$9': 0,
    '$10': 0, '$11': 0, '$12': 0, '$13': 0, '$14': 0, '$15': 0, '$16': 0, '$17': 0, '$18': 0,
    '$19': 0, '$20': 0, '$21': 0, '$22': 0, '$23': 0, '$24': 0, '$25': 0, '$26': 0, '$27': 0,
    '$28': 268468224, '$29': 2147479548, '$30': 0, '$31': 0, 'pc': 4194304, 'hi': 0, 'lo': 0,
}


def remover_reg_zerados():
    """
        Função responsável por remover do dicionário os registradores quem estão com o valor zero
    """
    aux = {}

    for chave in regs:
        if regs[chave] != 0:
            aux[chave] = regs[chave]
    return aux


def identificar_formato(num_hexa):
    """
        Função responsável por receber o número hexadecimal, trata-lo e pelos bits responsáveis equivalentes ao opcode,
        identificar qual o formato correto, passando as informações para a função registrador.
    """

    num_bin = bin(int(num_hexa, 16))[2:]                                    # Removendo 0x do hexadecimal

    while len(num_bin) < 32:                                                # Completando o número com 0 até 32 bits
        num_bin = '0' + num_bin

    if num_bin[0:6] == '000010' or num_bin[0:6] == '000011':                # Formatos J
        return registrador(dic_j.get(num_bin[0:6]), num_bin, num_hexa)

    elif num_bin[0:6] == '000000':                                          # Formatos R
        return registrador(dic_r.get(num_bin[26:32]), num_bin, num_hexa)

    else:
        return registrador(dic_i.get(num_bin[0:6]), num_bin, num_hexa)      # Formatos I


def complemento_a_dois(num):
    """
        Função responsável por "realizar" o complemento a 2 nos casos que são necessários.
    """

    if num[0] == '1':
        return -1 * (int(''.join('1' if x == '0' else '0' for x in num), 2) + 1)
    else:
        return int(num, 2)


def operacoes(*args):
    """
        A função irá receber o opcode, e os args[0], args[1], args[2], args[3], irá trabalhar diferente
        dependendo da operação (a quantidade de argumentos irá variar) que será feita. Acessando e alterando
        os registradores.
    """

    if args[0] == 'add':
        # C = A + B

        rd = index[args[1]]                                                 # Recebendo a chave do registrador rd
        rs = regs.get(f'${args[2]}')                                        # Recebendo o valor do registrador rs
        rt = regs.get(f'${args[3]}')                                        # Recebendo o valor do registrador rt

        soma = int(rs) + int(rt)

        if soma > 2147483647:                         # Simulando o MIPS, caso Overflow regs = 0
            regs.update({rd: 0})
            regs.update({'$1': 2147418112})
        elif soma < -2147483647:
            regs.update({rd: 0})
            regs.update({'$1': -2147483648})
        else:
            regs.update({rd: soma})                                         # Atualizando o registrador rd

        regs['pc'] = regs['pc'] + 4                                         # Atualizando o PC

        return soma > 2147483647 or soma < -2147483648                      # Retornando True em caso de Overflow

    elif args[0] == 'sub':
        # C = A - B

        rd = index[args[1]]                                                 # Recebendo a chave do registrador rd
        rs = regs.get(f'${args[2]}')                                        # Recebendo o valor do registrador rs
        rt = regs.get(f'${args[3]}')                                        # Recebendo o valor do registrador rt

        sub = int(rs) - int(rt)

        if sub > 2147483647:                               # Simulando o MIPS, caso Overflow regs = 0
            regs.update({rd: 0})
            regs.update({'$1': 2147418112})
        elif sub < -2147483648:
            regs.update({rd: 0})
            regs.update({'$1': -2147483648})
        else:
            regs.update({rd: sub})                                          # Atualizando o registrador rd

        regs['pc'] = regs['pc'] + 4                                         # Atualizando o PC

        return sub > 2147483647 or sub < -2147483648                        # Retornando True em caso de Overflow

    elif args[0] == 'slt':
        # C = 1 se A < B
        # C = 0 se A >= B

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        if int(rs) < int(rt):
            regs.update({rd: 1})
        else:
            regs.update({rd: 0})

        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'and':
        # Comparação bit a bit, quando os dois bits forem 1: saída = 1, senão, saída = 0

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        regs.update({rd: (rs & rt)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'or':
        # Comparação bit a bit, quando um dos bits for 1: saída = 1, senão, saída = 0

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        regs.update({rd: (rs | rt)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'xor':
        # Comparação bit a bit, um bit = 1 e o outro = 0: saída = 1, senão, saída = 0

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        regs.update({rd: (rs ^ rt)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'nor':
        # Comparação bit a bit, um não OR

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        regs.update({rd: ~(rs | rt)})
        regs['pc'] = regs['pc'] + 4

        return

    if args[0] == 'addi':
        # B = A + Imediato

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]                                                        # Imediato

        soma = rs + rt

        if soma > 2147483647:                         # Simulando o MIPS, caso Overflow regs = 0
            regs.update({rd: 0})
            regs.update({'$1': 2147418112})
        elif soma < -2147483647:
            regs.update({rd: 0})
            regs.update({'$1': -2147483648})
        else:
            regs.update({rd: soma})                                         # Atualizando o registrador rd

        regs.update({'pc': regs['pc'] + 4})

        return soma > 2147483647 or soma < -2147483648

    elif args[0] == 'slti':
        # B = 1 se A < Imediato
        # B = 0 se A >= Imediato

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]                                                        # Imediato

        if int(rs) < rt:
            regs.update({rd: 1})
        else:
            regs.update({rd: 0})

        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'andi':
        # Igual ao and, mas comparando com o imediato

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]                                                        # Imediato

        regs.update({rd: (rs & rt)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'ori':
        # Igual ao or, mas comparando com o imediato

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]                                                        # Imediato

        regs.update({rd: (rs | rt)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'xori':
        # Igual ao xor, mas comparando com o imediato

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]  # Imediato

        regs.update({rd: (rs ^ rt)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'bltz':
        # Condição = True (label = 4 últimos hex)
        # Condição = False (label = False)

        rs = regs.get(f'${args[1]}')
        regs['pc'] = regs['pc'] + 4

        return rs < 0

    elif args[0] == 'sll':
        # Shift esquerda lógico
        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]

        sll = int(numpy.left_shift(rs, rt))

        regs.update({rd: sll})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'sllv':
        # Shift esquerda lógico variável
        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        sllv = rs << rt

        if sllv > 2147483647:                                               # Apenas para ficar como no MIPS
            regs.update({rd: 2147483647})
        elif sllv < -2147483648:
            regs.update({rd: -2147483648})
        else:
            regs.update({rd: sllv})

        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'srl':
        # Shift direita lógico
        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]

        srl = int(numpy.uint32(rs) >> numpy.uint32(rt))

        regs.update({rd: srl})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'sra':
        # Shift direita aritimético
        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]

        sra = int(numpy.int32(rs) >> numpy.int32(rt))

        regs.update({rd: sra})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'srlv':
        # Shift direita lógico variável
        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        srlv = int(numpy.uint(rs) >> numpy.uint(rt))

        regs.update({rd: srlv})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'srav':
        # Shift direita aritimético variável
        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        srav = rs >> rt

        regs.update({rd: srav})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'div':
        """
            Embora o div tenha overflow, na parte do resto, não achei necessário implementar isso já que no MIPS é
            usado o break e por padrão só pega o primeiro dígito antes do ponto.
        """
        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')

        lo = int(rs / rt)
        # O % não fucionava como no MIPS então improvisei, nem sei se alguma coisa que faça isso fácil, mas funciona
        if rs > 0 and rt < 0 and abs(rs) < abs(rt):
            hi = (rs % abs(rt))
        elif rs > 0 and rt < 0:
            hi = (rs % abs(rt))
        elif rs < 0 and rt > 0:
            hi = (abs(rs) % rt) * - 1
        else:
            hi = rs % rt

        regs.update({'lo': lo})
        regs.update({'hi': hi})

        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'beq':
        # Se igual vai para o label
        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')

        regs['pc'] = regs['pc'] + 4

        return rs == rt

    elif args[0] == 'bne':
        # Se diferente vai para o label
        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')

        regs['pc'] = regs['pc'] + 4

        return rs != rt

    elif args[0] == 'lui':
        # Carrega imediato de 16bits para os 16bits superiores
        rd = index[args[1]]
        rt = args[2]

        lui = rt << 16

        if rt > 32767:
            aux = bin(lui)[2:]
            lui = complemento_a_dois(aux)

        regs.update({rd: lui})
        regs['pc'] = regs['pc'] + 4

        return

    if args[0] == 'addu':
        # C= A + B

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        soma = int(rs) + int(rt)

        regs.update({rd: soma})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'subu':
        # C = A - B

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = regs.get(f'${args[3]}')

        regs.update({rd: int(rs) - int(rt)})
        regs['pc'] = regs['pc'] + 4

        return

    if args[0] == 'addiu':
        # C = B + imediato

        rd = index[args[1]]
        rs = regs.get(f'${args[2]}')
        rt = args[3]

        regs.update({rd: int(rs) + rt})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'divu':
        # A / B
        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')

        rsu = numpy.uint32(rs)
        rtu = numpy.uint32(rt)

        if rs < 0 and rt < 0 and abs(rs) > abs(rt):

            hi = rs
            lo = 0
        else:
            lo = int(rsu / rtu)
            hi = int(rsu % rtu)

        regs.update({'lo': lo})
        regs.update({'hi': hi})

        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'jal':  # 3 ENTREGA, apenas testando

        regs.update({'$31': regs['pc']})
        endereco = (regs['pc'] & 0xf0000000) | (args[1] & 0x03FFFFFF)
        regs['pc'] = regs['pc'] + 4

        return endereco

    elif args[0] == 'j':  # 3 ENTREGA, apenas testando
        endereco = (regs['pc'] & 0xf0000000) | (args[1] & 0x03FFFFFF)
        regs['pc'] = regs['pc'] + 4

        return endereco

    elif args[0] == 'mult':
        # A * B
        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')

        mult = numpy.int64(rs) * numpy.int64(rt)

        regs['hi'] = int(mult) >> 32

        lo = int(mult) & 0xFFFFFFFF

        if lo & 0x80000000:
            lo = -0x100000000 + lo

        regs['lo'] = lo
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'multu':
        # A * B
        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')

        rsu = numpy.uint32(rs)
        rtu = numpy.uint32(rt)

        multu = numpy.compat.long(rsu) * numpy.compat.long(rtu)

        hi = int(multu) >> 32
        lo = int(multu) & 0xFFFFFFFF

        if hi & 0x80000000:
            hi = -0x100000000 + hi
        if lo & 0x80000000:
            lo = -0x100000000 + lo

        regs['lo'] = lo
        regs['hi'] = hi
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'jr':   # 3 ENTREGA

        regs[f'${args[1]}'] = regs['pc']

        return

    elif args[0] == 'mfhi':
        # Recebe o registrador o valor do hi
        regs[f'${args[1]}'] = regs['hi']

        return

    elif args[0] == 'mflo':
        # Recebe no registrador o valor do lo
        regs[f'${args[1]}'] = regs['lo']

        return


def registrador(op, num_bin, num_hexa):
    """
        Função responsável por receber o identificador do opcode, e suas representações binárias e hexadecimais,
        retornando a instrução correspondente, já está no padrão para a segunda entrega. os n1, n2, n3 representam os
        números dos registradores MIPS.
    """

    # SYSCALL
    if op == 'syscall':

        regs_usados = remover_reg_zerados()
        stdout = ""

        regs['pc'] = regs['pc'] + 4

        text = 'syscall'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    # TIPOS J
    elif op == 'j' or op == 'jal':

        hex_int = int(num_hexa, 16)
        stdout = ""

        endereco = operacoes(op, hex_int)
        regs_usados = remover_reg_zerados()

        text = f'{op} {endereco}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    # TIPOS I
    elif op == 'lui':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[16:32], 2)
        stdout = ""

        if operacoes(op, n1, n2):
            stdout = 'Overflow'

        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, {n2}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'bltz':

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[16:32], 2)
        stdout = ""

        if operacoes(op, n1):
            text = f'{op} ${n1}, ${n2}'
        else:
            text = f'{op} ${n1}, False'

        regs_usados = remover_reg_zerados()

        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'addi':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[6:11], 2)
        stdout = ""

        n3 = complemento_a_dois(num_bin[16:32])

        if operacoes(op, n1, n2, n3):
            stdout = 'Overflow'

        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'slti' or op == 'andi' or op == 'ori' or op == 'xori' or op == 'addiu':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[6:11], 2)
        stdout = ""

        n3 = complemento_a_dois(num_bin[16:32])

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'lw' or op == 'sw' or op == 'lb' or op == 'lbu' or op == 'sb':  # 3 ENTREGA

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[16:32], 2)
        n3 = int(num_bin[6:11], 2)
        stdout = ""

        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, {n2}(${n3})'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'beq' or op == 'bne':

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[16:32], 2)
        stdout = ""

        if operacoes(op, n1, n2):
            text = f'{op} ${n1}, ${n2}, {n3}'
        else:
            text = f'{op} ${n1}, ${n2}, False'

        regs_usados = remover_reg_zerados()

        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    # TIPOS R
    elif op == 'jr':

        n1 = int(num_bin[6:11], 2)
        stdout = ""

        operacoes(op, n1)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'mfhi' or op == 'mflo':

        n1 = int(num_bin[16:21], 2)
        stdout = ""

        operacoes(op, n1)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'mult' or op == 'multu' or op == 'div' or op == 'divu':

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[11:16], 2)
        stdout = ""

        operacoes(op, n1, n2)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'sll' or op == 'srl' or op == 'sra':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[21:26], 2)
        stdout = ""

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'sllv' or op == 'srlv' or op == 'srav':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[6:11], 2)
        stdout = ""

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'slt' or op == 'and' or op == 'or':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)
        stdout = ""

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'add' or op == 'sub':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)
        stdout = ""

        if operacoes(op, n1, n2, n3):
            stdout = 'Overflow'

        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    elif op == 'xor' or op == 'nor' or op == 'addu' or op == 'subu':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)
        stdout = ""

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": {}, "stdout": stdout}

        return dic

    else:
        return 'erro no registrador'


saida_json = []
lista_saida = []
index = list(regs.keys())

if not os.path.exists('output'):
    os.mkdir('output')

# Leitura e escrita dos arquivo JSON
for arquivo in range(len(arquivos_entrada)):
    # Leitura do arquivo
    with open(f'input/{arquivos_entrada[arquivo]}.input.json', encoding='utf8') as arquivo_entrada:
        lista_entrada = json.load(arquivo_entrada)
    arquivo_entrada.close()

    lista_saida.clear()
    index_regs = list(lista_entrada['config']['regs'].keys())
    index_mem = list(lista_entrada['config']['mem'].keys())

    for item in index_regs:
        regs.update({item: lista_entrada['config']['regs'][item]})

    # Adicionando os dicionários a lista de saída
    for hexa in lista_entrada['text']:
        lista_saida.append(identificar_formato(hexa))

    with open(f'output/GrupoE.{arquivos_entrada[arquivo]}.output.json', 'w') as arquivo_saida:
        json.dump(lista_saida, arquivo_saida, indent=4)
    arquivo_saida.close()

    # Zerando registradores para próximo arquivo
    for item in index:
        regs.update({item: 0})

    index_regs.clear()
    index_mem.clear()

    # Recolocando informação padrão dos registradores após terem zerado
    regs['$28'] = 268468224
    regs['$29'] = 2147479548
    regs['pc'] = 4194304
