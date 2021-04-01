file = open('input.mc', 'r')

input = []

for line in file:
    input.append(line.split())

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
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    rs2 = bin_instr[20:25]
    funct7 = bin_instr[25:32]
    return opcode, rd, funct3, rs1, rs2, funct7


def extractS(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    imm1 = bin_instr[7:12]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    rs2 = bin_instr[20:25]
    imm2 = bin_instr[25:32]
    imm = imm1+imm2
    return opcode, funct3, rs1, rs2, imm


def extractI(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    imm = bin_instr[20:32]

    return opcode, rd, funct3, rs1, imm


def extractSB(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    funct3 = bin_instr[12:15]
    rs1 = bin_instr[15:20]
    rs2 = bin_instr[20:25]
    imm = bin_instr[8:12]+bin_instr[25:31]+bin_instr[7]+bin_instr[31]

    return opcode, funct3, rs1, rs2, imm


def extractU(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    imm = bin_instr[12:32]

    return opcode, rd, imm


def extractUJ(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    rd = bin_instr[7:12]
    imm = bin_instr[21:31]+bin_instr[20]+bin_instr[12:20]+bin_instr[31]

    return opcode, rd, imm


def instruction_checker(instr):
    # 0xFFFFFFFF type of input
    bin_instr = bin(int(instr, 16))[2:]
    opcode = bin_instr[0:7]
    if(opcode == "0110011"):
        extractR(instr)
    elif(opcode == "0100011"):
        extractS(instr)
    elif(opcode == "0000011" or opcode == "0010011" or opcode == "1100111"):
        extractI(instr)
    elif(opcode == "1100011"):
        extractSB(instr)
    elif(opcode == "0010111" or opcode == "0110111"):
        extractU(instr)
    elif(opcode == "1101111"):
        extractUJ(instr)
    else:
        print("error")
