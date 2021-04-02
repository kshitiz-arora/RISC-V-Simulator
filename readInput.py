file = open('input.mc', 'r')

input = dict()

for line in file:
    ls = line.split()
    input[ls[0]] = ls[1]

registers = dict()
data_memory = list()
stack_memory = list()
heap_memory = list()


def reset_all():

    registers = {i: 0x00000000 for i in range(32)}

    registers[2] = 0x7FFFFFF0  # stack pointer
    registers[3] = 0x10000000  # global pointer

    data_size = 1000
    # to be addressed starting from 0x10000000
    data_memory = list('00000000' for _ in range(data_size))

    stack_size = 1000
    # to be addressed starting from 0x7FFFFFFC
    stack_memory = list('00000000' for _ in range(stack_size))

    heap_size = 1000
    # to be addressed starting from 0x10007FE8
    heap_memory = list('00000000' for _ in range(heap_size))

    return


def extractR(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    rs2 = bin_instr[20:25]
    funct7 = bin_instr[25:32]
    return [opcode, rd, funct3, rs1, rs2, funct7]


def extractS(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[0:7]
    imm1 = bin_instr[7:12]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    rs2 = bin_instr[20:25]
    imm2 = bin_instr[25:32]
    imm = imm1+imm2
    return [opcode, funct3, rs1, rs2, imm]


def extractI(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    imm = bin_instr[20:32]

    return [opcode, rd, funct3, rs1, imm]


def extractSB(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[0:7]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    rs2 = bin_instr[20:25]
    imm = bin_instr[8:12]+bin_instr[25:31]+bin_instr[7]+bin_instr[31]

    return [opcode, funct3, rs1, rs2, imm]


def extractU(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    imm = bin_instr[12:32]

    return [opcode, rd, imm]


def extractUJ(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    imm = bin_instr[21:31]+bin_instr[20]+bin_instr[12:20]+bin_instr[31]

    return [opcode, rd, imm]


def decodeR(funct3, funct7):
    operation = 'error'
    if (funct3 == '000'):
        if (funct7 == '0000000'):
            operation = 'add'
        elif (funct7 == '0100000'):
            operation = 'sub'
    elif (funct3 == '001' and funct7 == '0000000'):
        operation = 'sll'
    elif (funct3 == '010' and funct7 == '0000000'):
        operation = 'slt'
    elif (funct3 == '100' and funct7 == '0000000'):
        operation = 'xor'
    elif (funct3 == '101'):
        if (funct7 == '0000000'):
            operation = 'srl'
        elif (funct7 == '0100000'):
            operation = 'sra'
    elif (funct3 == '110' and funct7 == '0000000'):
        operation = 'or'
    elif (funct3 == '111' and funct7 == '0000000'):
        operation = 'and'
    return operation

def decodeS(funct3):
    operation = 'error'
    if (funct3 == '000'):
        operation = 'sb'
    elif (funct3 == '001'):
        operation = 'sh'
    elif (funct3 == '010'):
        operation = 'sw'
    return operation

def decodeI(opcode, funct3):
    operation = 'error'
    if (opcode == "0000011"):
        if (funct3 == '000'):
            operation = 'lb'
        elif (funct3 == '001'):
            operation = 'lh'
        elif (funct3 == '010'):
            operation = 'lw'
    elif (opcode == "0010011"):
        if (funct3 == '111'):
            operation = 'andi'
        elif (funct3 == '110'):
            operation = 'ori'
        elif (funct3 == '000'):
            operation = 'andi'
    elif (opcode == "1100111"):
        if (funct3 == '000'):
            operation = 'jalr'
    return operation

def decodeSB(funct3):
    operation = 'error'
    if(funct3 == "000"):
        operation = "beq"
    elif(funct3 == "001"):
        operation = "bne"
    elif(funct3 == "100"):
        operation = "blt"
    elif(funct3 == "101"):
        operation = "bge"
    return operation

def decodeU(opcode):
    operation = 'error'
    if(opcode == "0010111"):
        operation = "auipc"
    elif(opcode == "0110111"):
        operation = "lui"
    return operation



# fetch

def fetch(pc):  # pc is of type string 0x0
    return input[pc]

# decode

def decode(instr):
    # 0xFFFFFFFF type of input
    bin_instr = bin(int(instr, 16))[2:]

    opcode = bin_instr[0:7]

    operation = 'error'

    if(opcode == "0110011"):
        code_list = extractR(instr)
        operation = decodeR(code_list[2], code_list[5])
        
    elif(opcode == "0100011"):
        code_list = extractS(instr)
        operation = decodeS(code_list[1])

    elif(opcode == "0000011" or opcode == "0010011" or opcode == "1100111"):
        code_list = extractI(instr)
        operation = decodeI(code_list[0], code_list[2])

    elif(opcode == "1100011"):
        code_list = extractSB(instr)
        operation = decodeSB(code_list[1])

    elif(opcode == "0010111" or opcode == "0110111"):
        code_list = extractU(instr)
        operation = decodeU(code_list[0])
        
    elif(opcode == "1101111"):
        code_list = extractUJ(instr)
        operation = 'jal'
    else:
        return "error"

