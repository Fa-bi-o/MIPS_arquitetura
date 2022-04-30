import json
import numpy
import os

# Recebendo nome dos arquivos na pasta input em forma de lista
caminho_entrada_json = 'input/'
arquivos_entrada = [pos_json[0:-11] for pos_json in os.listdir(caminho_entrada_json) if pos_json.endswith('.json')]

"""
    Código da terceira entrega. Espero que esteja correto!!
    
    Na memória, foram criados os 1024 slots, começando em 268500992 + os endereços mem que estiverem no input, 
    já que é o mínimo de 1024 e como nos exemplos demonstrados os endereços mem, estavam diferentes do data eu 
    acabei colocando eles como extra, então se algum endereço com o simulador já executando ficar fora desse
    range vai ser impresso "address not align on word boundary", no terminal, mas não será impresso nada na saída,
    ficará o comando como não executado.

    Só para reforçar os edereços do mem estão seguindo o MIPS do valor base 268500992, até 1024 slots + endereços
    de input do mem. Se forem diferentes provavelmente dará erro. Me baseei nos exemplos dados + requisitos.
    
    Terceiro e último ponto, o input de memória está int(mem) e string(data), então o código está baseado nessas
    entradas. Também baseado nos requisitos.
    
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
def criar_registradores():
    registradores = {
        '$0': 0, '$1': 0, '$2': 0, '$3': 0, '$4': 0, '$5': 0, '$6': 0, '$7': 0, '$8': 0, '$9': 0,
        '$10': 0, '$11': 0, '$12': 0, '$13': 0, '$14': 0, '$15': 0, '$16': 0, '$17': 0, '$18': 0,
        '$19': 0, '$20': 0, '$21': 0, '$22': 0, '$23': 0, '$24': 0, '$25': 0, '$26': 0, '$27': 0,
        '$28': 268468224, '$29': 2147479548, '$30': 0, '$31': 0, 'pc': 4194304, 'hi': 0, 'lo': 0
    }
    return registradores


# Memoria data com 1024 slots, valores escolhidos considerando a base do MIPS
def criar_mem():
    memoria = {}.fromkeys(range(268500992, 268505088, 4), 0)
    keys_data = memoria.items()
    memoria_formatada = {str(key): value for key, value in keys_data}
    return memoria_formatada


def remover_reg_zerados():
    """
        Função responsável por remover do dicionário os valores zerados
    """

    aux = {}

    for chave in regs:
        if regs[chave] != 0:
            aux[chave] = regs[chave]
    return aux


def remover_mem_zerados():
    """
        Função responsável por remover do dicionário os valores zerados
    """

    aux = {}

    for chave in mem:
        if mem[chave] != 0:
            aux[chave] = mem[chave]

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

        if soma > 2147483647:                                               # Simulando o MIPS, caso Overflow regs = 0
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

        if sub > 2147483647:                                                # Simulando o MIPS, caso Overflow regs = 0
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
        # Comparação bit a bit, um, não OR

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
        im = args[3]                                                        # Imediato

        soma = rs + im

        if soma > 2147483647:                                               # Simulando o MIPS, caso Overflow regs = 0
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

        rt = index[args[1]]
        rs = regs.get(f'${args[2]}')
        im = args[3]                                                        # Imediato

        if int(rs) < im:
            regs.update({rt: 1})
        else:
            regs.update({rt: 0})

        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'andi':
        # Igual ao and, mas comparando com o imediato

        rt = index[args[1]]
        rs = regs.get(f'${args[2]}')
        im = args[3]                                                        # Imediato

        regs.update({rt: (rs & im)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'ori':
        # Igual ao or, mas comparando com o imediato

        rt = index[args[1]]
        rs = regs.get(f'${args[2]}')
        im = args[3]                                                        # Imediato

        regs.update({rt: (rs | im)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'xori':
        # Igual ao xor, mas comparando com o imediato

        rt = index[args[1]]
        rs = regs.get(f'${args[2]}')
        im = args[3]  # Imediato

        regs.update({rt: (rs ^ im)})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'bltz':
        # Se número do registrador for < 0, vai para o label correspondente

        rs = regs.get(f'${args[1]}')

        label = args[2]

        if rs < 0:
            endereco = regs['pc'] + 4 + (label * 4)
        else:
            endereco = 'undefined'

        regs['pc'] = regs['pc'] + 4

        return endereco

    elif args[0] == 'sll':
        # Shift esquerda lógico

        rd = index[args[1]]
        rt = regs.get(f'${args[2]}')
        sh = args[3]                                                        # Shamt

        sll = int(numpy.left_shift(rt, sh))

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
        rt = regs.get(f'${args[2]}')
        sh = args[3]                                                        # Shamt

        srl = int(numpy.uint32(rt) >> numpy.uint32(sh))

        regs.update({rd: srl})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'sra':
        # Shift direita aritimético

        rd = index[args[1]]
        rt = regs.get(f'${args[2]}')
        sh = args[3]

        sra = int(numpy.int32(rt) >> numpy.int32(sh))

        regs.update({rd: sra})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'srlv':
        # Shift direita lógico variável

        rd = index[args[1]]
        rt = regs.get(f'${args[2]}')
        rs = regs.get(f'${args[3]}')

        srlv = int(numpy.uint(rt) >> numpy.uint(rs))

        regs.update({rd: srlv})
        regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'srav':
        # Shift direita aritimético variável

        rd = index[args[1]]
        rt = regs.get(f'${args[2]}')
        rs = regs.get(f'${args[3]}')

        srav = rt >> rs

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
        # O % não fucionava como no MIPS então improvisei

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
        # Se os números forem iguais, vai para o label

        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')
        im = args[3]

        if rs == rt:
            endereco = regs['pc'] + 4 + (im * 4)
        else:
            endereco = 'undefined'

        regs['pc'] = regs['pc'] + 4

        return endereco

    elif args[0] == 'bne':
        # Se os números forem diferentes, vai para o label

        rs = regs.get(f'${args[1]}')
        rt = regs.get(f'${args[2]}')
        im = args[3]

        if rs != rt:
            endereco = regs['pc'] + 4 + (im * 4)
        else:
            endereco = 'undefined'

        regs['pc'] = regs['pc'] + 4

        return endereco

    elif args[0] == 'lui':
        # Carrega imediato de 16bits para os 16bits superiores

        rt = index[args[1]]
        im = args[2]

        lui = im << 16

        if im > 32767:
            aux = bin(lui)[2:]
            lui = complemento_a_dois(aux)

        regs.update({rt: lui})
        regs['pc'] = regs['pc'] + 4

        return

    if args[0] == 'addu':
        # C = A + B

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
        # C = B + Imediato

        rt = index[args[1]]
        rs = regs.get(f'${args[2]}')
        im = args[3]

        regs.update({rt: int(rs) + im})
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

    elif args[0] == 'jal':
        # Pula para o label e coloca no RA o valor do pc

        valor_jal = regs['pc'] + 4
        regs.update({'$31': valor_jal})

        endereco = (regs['pc'] & 0xf0000000) | (args[1] << 2)

        regs['pc'] = regs['pc'] + 4

        return endereco

    elif args[0] == 'j':
        # Pula para o label

        endereco = (regs['pc'] & 0xf0000000) | (args[1] << 2)
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

    elif args[0] == 'jr':
        # PC recebe o endereço que está no registrador RS se multiplo de 4
        # Se valor for alto no MIPS da erro, mas o valor é copiado para o pc

        if regs[f'${args[1]}'] % 4 == 0:
            regs['pc'] = regs[f'${args[1]}']

        return

    elif args[0] == 'mfhi':
        # Recebe o registrador o valor do hi

        regs[f'${args[1]}'] = regs['hi']

        return

    elif args[0] == 'mflo':
        # Recebe no registrador o valor do lo

        regs[f'${args[1]}'] = regs['lo']

        return

    elif args[0] == 'lw':
        # RT recebe o valor em memória da soma entre o endereço de RS + IM(offset)

        rt = index[args[1]]
        im = args[2]
        rs = regs.get(f'${args[3]}')

        endereco = int(im) + int(rs)

        if endereco % 4 != 0:
            print("address not align on word boundary")
        else:
            if mem.get(f'{endereco}'):
                valor_endereco = mem.get(f'{endereco}')
                regs.update({rt: valor_endereco})

                regs['pc'] = regs['pc'] + 4
            else:
                print("address not align on word boundary")

        return

    elif args[0] == 'sw':
        # Guarda na memoria RT a soma do endereço no registrador RS + IM

        rt = regs.get(f'${args[1]}')
        im = args[2]
        rs = regs.get(f'${args[3]}')

        endereco = int(im) + int(rs)

        if endereco % 4 != 0:
            print("address not align on word boundary")
        else:
            chave = f'{str(endereco)}'
            if chave in mem:
                mem.update({f'{str(endereco)}': rt})

                regs['pc'] = regs['pc'] + 4
            else:
                print("address not align on word boundary")

        return

    elif args[0] == 'lb':
        # RT recebe o valor em memória da soma entre o endereço de RS + IM(offset)

        rt = index[args[1]]
        im = args[2]
        rs = regs.get(f'${args[3]}')

        endereco = int(im) + int(rs)

        if endereco % 4 != 0:
            print("address not align on word boundary")
        else:
            valor_endereco = int(mem.get(f'{endereco}'))
            valor_byte = int(numpy.byte(valor_endereco))
            regs.update({rt: valor_byte})

            regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'lbu':
        # RT recebe o valor em memória da soma entre o endereço de RS + IM(offset)

        rt = index[args[1]]
        im = args[2]
        rs = regs.get(f'${args[3]}')

        endereco = int(im) + int(rs)

        if endereco % 4 != 0:
            print("address not align on word boundary")
        else:
            valor_endereco = int(mem.get(f'{endereco}'))
            valor_byte = int(numpy.ubyte(valor_endereco))
            regs.update({rt: valor_byte})

            regs['pc'] = regs['pc'] + 4

        return

    elif args[0] == 'sb':
        # Guarda na memoria RT a soma do endereço no registrador RS + IM

        rt = regs.get(f'${args[1]}')
        im = args[2]
        rs = regs.get(f'${args[3]}')

        endereco = int(im) + int(rs)

        if endereco % 4 != 0:
            print("address not align on word boundary")
        else:
            chave = f'{str(endereco)}'
            if chave in mem:
                valor = int(numpy.byte(rt))
                mem.update({f'{str(endereco)}': valor})

                regs['pc'] = regs['pc'] + 4

        return


def registrador(op, num_bin, num_hexa):
    """
        Função responsável por receber o identificador do opcode, e suas representações binárias e hexadecimais,
        retornando a instrução correspondente, já está no padrão para a segunda entrega. os n1, n2, n3 representam os
        números dos registradores MIPS.
    """

    # SYSCALL
    if op == 'syscall':

        regs['pc'] = regs['pc'] + 4

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()
        stdout = {}

        text = 'syscall'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    # TIPOS J
    elif op == 'j' or op == 'jal':
        n1 = int(num_bin[7:32], 2)
        stdout = {}

        endereco = operacoes(op, n1)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} {endereco}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    # TIPOS I
    elif op == 'lui':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[16:32], 2)
        stdout = {}

        if operacoes(op, n1, n2):
            stdout = 'Overflow'

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, {n2}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'bltz':

        n1 = int(num_bin[6:11], 2)
        n2 = complemento_a_dois(num_bin[16:32])
        stdout = {}

        endereco = operacoes(op, n1, n2)
        text = f'{op} ${n1}, ${endereco}'

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'addi':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[6:11], 2)
        stdout = {}

        n3 = complemento_a_dois(num_bin[16:32])

        if operacoes(op, n1, n2, n3):
            stdout = 'Overflow'

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'slti' or op == 'andi' or op == 'ori' or op == 'xori' or op == 'addiu':

        n1 = int(num_bin[11:16], 2)
        n2 = int(num_bin[6:11], 2)
        stdout = {}

        n3 = complemento_a_dois(num_bin[16:32])

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'lw' or op == 'sw' or op == 'lb' or op == 'lbu' or op == 'sb':

        n1 = int(num_bin[11:16], 2)
        n2 = complemento_a_dois(num_bin[16:32])
        n3 = int(num_bin[6:11], 2)
        stdout = {}

        operacoes(op, n1, n2, n3)

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, {n2}(${n3})'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'beq' or op == 'bne':    # BEQ BNE

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = complemento_a_dois(num_bin[16:32])
        stdout = {}

        endereco = operacoes(op, n1, n2, n3)
        text = f'{op} ${n1}, ${n2}, {endereco}'

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}
        return dic

    # TIPOS R
    elif op == 'jr':

        n1 = int(num_bin[6:11], 2)
        stdout = {}

        operacoes(op, n1)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}
        return dic

    elif op == 'mfhi' or op == 'mflo':

        n1 = int(num_bin[16:21], 2)
        stdout = {}

        operacoes(op, n1)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'mult' or op == 'multu' or op == 'div' or op == 'divu':

        n1 = int(num_bin[6:11], 2)
        n2 = int(num_bin[11:16], 2)
        stdout = {}

        operacoes(op, n1, n2)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}
        return dic

    elif op == 'sll' or op == 'srl' or op == 'sra':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[21:26], 2)
        stdout = {}

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, {n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'sllv' or op == 'srlv' or op == 'srav':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[11:16], 2)
        n3 = int(num_bin[6:11], 2)
        stdout = {}

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}
        return dic

    elif op == 'slt' or op == 'and' or op == 'or':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)
        stdout = {}

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}
        return dic

    elif op == 'add' or op == 'sub':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)
        stdout = {}

        if operacoes(op, n1, n2, n3):
            stdout = 'Overflow'

        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    elif op == 'xor' or op == 'nor' or op == 'addu' or op == 'subu':

        n1 = int(num_bin[16:21], 2)
        n2 = int(num_bin[6:11], 2)
        n3 = int(num_bin[11:16], 2)
        stdout = {}

        operacoes(op, n1, n2, n3)
        regs_usados = remover_reg_zerados()
        mem_usados = remover_mem_zerados()

        text = f'{op} ${n1}, ${n2}, ${n3}'
        dic = {"hex": num_hexa, "text": text, "regs": regs_usados, "mem": mem_usados, "stdout": stdout}

        return dic

    else:
        return 'erro no registrador'


saida_json = []
lista_saida = []
base_data = 268500992

if not os.path.exists('output'):
    os.mkdir('output')

# Leitura e escrita dos arquivo JSON
for arquivo in range(len(arquivos_entrada)):

    # Leitura do arquivo
    with open(f'input/{arquivos_entrada[arquivo]}.input.json', encoding='utf8') as arquivo_entrada:
        lista_entrada = json.load(arquivo_entrada)
    arquivo_entrada.close()

    lista_saida.clear()

    mem = criar_mem()
    regs = criar_registradores()
    index = list(regs.keys())

    # Recebendo as informações do data e colocando na memoria antes de executar o simulador
    if lista_entrada['data']:
        index_data = list(lista_entrada['data'].keys())

        for data_address in index_data:
           mem.update({data_address: int(lista_entrada['data'][data_address])})

    # Recebendo as informações do mem e colocando na memoria antes de executar o simulador
    if lista_entrada['config']['mem']:
        index_mem = list(lista_entrada['config']['mem'].keys())

        # Caso o dado não tenha dentro dos 1024 slots, será criado um slot com o dado informado
        for mem_address in index_mem:
            if lista_entrada['config']['mem'][mem_address]:
                mem.update({mem_address: lista_entrada['config']['mem'][mem_address]})
            else:
                mem[mem_address] = lista_entrada['config']['mem'][mem_address]

    # Recebendo as informações dos regs e colocando nos registradores antes de executar o simulador
    if lista_entrada['config']['regs']:
        index_regs = list(lista_entrada['config']['regs'].keys())

        for item in index_regs:
            regs.update({item: lista_entrada['config']['regs'][item]})

    # Adicionando os dicionários a lista de saída
    if lista_entrada['text']:
        for hexa in lista_entrada['text']:
            lista_saida.append(identificar_formato(hexa))

    # Criação do arquivo de saída
    with open(f'output/GrupoE.{arquivos_entrada[arquivo]}.output.json', 'w') as arquivo_saida:
        json.dump(lista_saida, arquivo_saida, indent=4)
    arquivo_saida.close()
