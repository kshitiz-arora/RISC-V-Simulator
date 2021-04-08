PC = 0x0
instructions = dict()
registers = dict()
data_memory = dict()
stack_memory = dict()
heap_memory = dict()

def reset_all():

    global PC
    global registers 
    global data_memory
    global stack_memory
    global heap_memory
    
    PC = 0x0

    
    registers = {i: '0x00000000' for i in range(32)}
    
    registers[2] = '0x7FFFFFF0'  # stack pointer
    registers[3] = '0x10000000'  # global pointer

    data_size = 1000
    # to be addressed starting from 0x10000000
    data_memory = {(0x10000000+(4*i)):'00000000' for i in range(data_size)}

    stack_size = 1000
    # to be addressed starting from 0x7FFFFFFC
    # stack_memory = {(0x7FFFFFFC+(4*i)):'00000000' for i in range(stack_size)}
    for i in range(0x7FFFFFFC, 0x7FFFFFFC-4000, -4):
        data_memory[i] = '00000000'

    heap_size = 1000
    # to be addressed starting from 0x10007FE8
    # heap_memory = {(0x10007FE8+(4*i)):'00000000' for i in range(heap_size)}
    for i in range(0x10007FE8, 0x10007FE8+4000, 4):
        data_memory[i] = '00000000'

    return


def readfile(filename): # assuming input.mc has instructions > data > stack > heap
    
    global instructions
    global registers 
    global data_memory
    global stack_memory
    global heap_memory

    file = open(filename, 'r')

    input_list = dict()

    for line in file:
        a, b = line.split()
        if (b == 'text_end'):
            instructions[int(a,16)] = b
            break
        instructions[int(a,16)] = b
    
    for line in file:
        a, b = line.split()
        if (b == 'data_end'):
            break
        if (b[:2] == '0x'):
            b = b[2:]
        data_memory[int(a,16)] = b

    for line in file:
        a, b = line.split()
        if (b == 'stack_end'):
            break
        if (b[:2] == '0x'):
            b = b[2:]
        data_memory[int(a,16)] = b

    for line in file:
        a, b = line.split()
        if (b == 'heap_end'):
            break
        if (b[:2] == '0x'):
            b = b[2:]
        data_memory[int(a,16)] = b

    return
    


def extractR(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[25:32]
    rd = bin_instr[20:25]
    funct3 = bin_instr[17:20]
    rs1 = bin_instr[12:17]
    rs2 = bin_instr[7:12]
    funct7 = bin_instr[0:7]
    return [opcode, rd, funct3, rs1, rs2, funct7]


def extractS(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[25:32]
    imm1 = bin_instr[20:25]
    funct3 = bin_instr[17:20]
    rs1 = bin_instr[12:17]
    rs2 = bin_instr[7:12]
    imm2 = bin_instr[0:7]
    imm = imm2+imm1 #--------------------------------
    return [opcode, funct3, rs1, rs2, imm]


def extractI(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[25:32]
    rd = bin_instr[20:25]
    funct3 = bin_instr[17:20]
    rs1 = bin_instr[12:17]
    imm = bin_instr[0:12]

    return [opcode, rd, funct3, rs1, imm]


def extractSB(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[25:32]
    funct3 = bin_instr[17:20]
    rs1 = bin_instr[12:17]
    rs2 = bin_instr[7:12]
    # imm = bin_instr[20:24]+bin_instr[1:7]+bin_instr[24]+bin_instr[0]
    imm = bin_instr[0] + bin_instr[7] + bin_instr[1:7] + bin_instr[20:24] + '0'

    return [opcode, funct3, rs1, rs2, imm]


def extractU(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[25:32]
    rd = bin_instr[20:25]
    imm = bin_instr[0:20]+'0'*12

    return [opcode, rd, imm]


def extractUJ(instr):  # instruction is of type string, for ex, 0x00011101
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    opcode = bin_instr[25:32]
    rd = bin_instr[20:25]
    # imm = bin_instr[1:11]+bin_instr[11]+bin_instr[12:20]+bin_instr[0]------------------------------------------
    imm = bin_instr[0]+bin_instr[12:20]+bin_instr[11]+bin_instr[1:11]+'0'

    return [opcode, rd, imm]


def decodeR(funct3, funct7):
    operation = 'error'
    if (funct3 == '000'):
        if (funct7 == '0000000'):
            operation = 'add'
        elif (funct7 == '0100000'):
            operation = 'sub'
        elif (funct7 == '0000001'):
            operation = 'mul'
    elif (funct3 == '001' and funct7 == '0000000'):
        operation = 'sll'
    elif (funct3 == '010' and funct7 == '0000000'):
        operation = 'slt'
    elif (funct3 == '100' and funct7 == '0000000'):
        operation = 'xor'
    elif (funct3 == '100' and funct7 == '0000001'):
        operation = 'div'
    elif (funct3 == '101'):
        if (funct7 == '0000000'):
            operation = 'srl'
        elif (funct7 == '0100000'):
            operation = 'sra'
    elif (funct3 == '110' and funct7 == '0000000'):
        operation = 'or'
    elif (funct3 == '110' and funct7 == '0000001'):
        operation = 'rem'
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
            operation = 'addi'
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

def fetch():  # PC is of type string 0x0

    global PC
    
    PC += 4
    
    return instructions[(PC-4)] # string or int-------------------------------------------------------

# decode

def decode(instr):
    # 0xFFFFFFFF type of input
    bin_instr = "{0:032b}".format(int(instr,16))

    opcode = bin_instr[25:32]

    operation = 'error'
    oper_type = 'error'

    reg_list = []

    if(opcode == "0110011"):
        oper_type = 'R'
        code_list = extractR(instr)
        operation = decodeR(code_list[2], code_list[5])
        reg_list = [code_list[1], code_list[3], code_list[4]] # rd, rs1, rs2

    elif(opcode == "0100011"):
        oper_type = 'S'
        code_list = extractS(instr)
        operation = decodeS(code_list[1])
        reg_list = [code_list[2], code_list[3], code_list[4]] # rs1, rs2, immm

    elif(opcode == "0000011" or opcode == "0010011" or opcode == "1100111"):
        oper_type = 'I'
        code_list = extractI(instr)
        operation = decodeI(code_list[0], code_list[2])
        reg_list = [code_list[1], code_list[3], code_list[4]] # rd, rs1, imm

    elif(opcode == "1100011"):
        oper_type = 'SB'
        code_list = extractSB(instr)
        operation = decodeSB(code_list[1])
        reg_list = [code_list[2], code_list[3], code_list[4]] # rs1, rs2, imm

    elif(opcode == "0010111" or opcode == "0110111"):
        oper_type = 'U'
        code_list = extractU(instr)
        operation = decodeU(code_list[0])
        reg_list = [code_list[1], code_list[2]] # rd, imm

    elif(opcode == "1101111"):
        oper_type = 'UJ'
        code_list = extractUJ(instr)
        operation = 'jal'
        reg_list = [code_list[1], code_list[2]] # rd, imm

    return oper_type, operation, reg_list


def get_signed(value):
    val = value
    if (value[:2] == '0b'):
        val = value[2:].zfill(32)
    if (value[:2] == '0x'):
        val = bin(int(value, 16))[2:].zfill(32)
    if (val[0] == '0'):
        return int('0b'+val, 2)
    else:
        inv = ''
        for bit in val:
            inv += str(1^int(bit))
        return -1*(int('0b'+inv, 2)+1)

def shiftRightLogical(n, m): # shift n right by m bits
    if (n >= 0):
        return n>>m
    s = ''
    b = bin(-n)[2:].zfill(32)
    ns = ''
    for bit in b:
        ns += str(1^int(bit))
    ns = bin(int(ns,2)+1)[-32:]
    shifted = '0'*m + ns[:32-m]
    return int('0b'+shifted,2)

# execute

def executeR(operation, reg_list):

    rd= get_signed(reg_list[0])
    rs1= get_signed(reg_list[1])
    rs2= get_signed(reg_list[2])

    op1 = get_signed(registers[rs1])
    op2 = get_signed(registers[rs2])

    val = 0

    if (operation=='add'):
        val= op1 + op2

    elif (operation=='and'):
        val= op1 & op2

    elif (operation=='or'):
        val= op1 | op2

    elif (operation=='sll'):
        val= op1 << op2

    elif (operation=='slt'):
        if(op1<op2):
            val= 1
        else:
            val=0

    elif (operation=='sra'): #arithmetic shift right
        val = op1 >> op2

    elif (operation=='srl'): #logical shift right
        # val= op1 >> op2
        val = shiftRightLogical(op1, op2)

    elif (operation=='sub'):
        val= op1 - op2

    elif (operation=='xor'):
        val= op1 ^ op2

    elif (operation=='mul'):
        val= op1 * op2

    elif (operation=='div'):
        val= op1 // op2 #floor division? --> YES ~kshitiz

    elif (operation=='rem'):
        val= op1 % op2

    return val


def executeU(operation, reg_list): # rd imm

    rd= get_signed(reg_list[0])
    # imm= get_signed(reg_list[1]) ----------------------------U type dont use signed
    imm = int('0b'+reg_list[1], 2)

    if(operation=='auipc'):
        val= PC + imm - 4

    elif(operation=='lui'):
        # imm_final= reg_list[1] # + '000000000000'
        # imm_int= get_signed(imm_final)
        imm_int = int('0b'+reg_list[1], 2)
        val= imm_int

    return val

def executeSB(operation,reg_list): #rs1, rs2, imm

    [rs1, rs2, imm] = [get_signed(i) for i in reg_list]
    
    op1 = get_signed(registers[rs1])
    op2 = get_signed(registers[rs2])
    # print(registers[rs1],registers[rs2],op1,op2,"=======================")
    if(operation=="beq"):
        if(op1==op2):
            return imm+PC-4

    if(operation=="bne"):
        if(op1!=op2):
            return imm+PC-4

    if(operation=="blt"):
        if(op1<op2):
            return imm+PC-4

    if(operation=="bge"):
        if(op1>=op2):
            return imm+PC-4

    return PC #--------------------------------------------------------

def executeUJ(operation,reg_list): # rd imm
    [rd, imm] = [get_signed(i) for i in reg_list]
    return [PC+imm-4, PC+4-4] #-------------------------------------------------------------



def executeI(operation, reg_list): # rd rs1 imm
    [rd, rs1, imm] = [get_signed(i) for i in reg_list]
    ans = 0
    if (operation == 'addi'):
        ans = get_signed(registers[rs1]) + imm
    elif (operation == 'andi'):
        ans = get_signed(registers[rs1]) & imm
    elif (operation == 'ori'):
        ans = get_signed(registers[rs1]) | imm
    elif (operation in ['lb', 'lh', 'lw', 'jalr']):
        ans = get_signed(registers[rs1]) + imm # calculating address
    return ans

def executeS(operation, reg_list): # rs1 rs2 imm
    [rs1, rs2, imm] = [get_signed(i) for i in reg_list]
    ans = get_signed(registers[rs1]) + imm
    return ans

def execute(oper_type, operation, reg_list):
    var = 0
    if (oper_type == 'R'):
        var = executeR(operation, reg_list) # returns value to be stored in rd
    elif (oper_type == 'S'):
        var = executeS(operation, reg_list) # returns effective address imm(rs1) whose value is to be stored in rs2
    elif (oper_type == 'I'):
        var = executeI(operation, reg_list) # returns value to be stored in rd or effective address imm(rs1)
    elif (oper_type == 'SB'):
        var = executeSB(operation, reg_list) # return PC temp
    elif (oper_type == 'U'):
        var = executeU(operation, reg_list) # returns required value
    elif (oper_type == 'UJ'):
        var = executeUJ(operation, reg_list) # returns PC temp and return address of jump instruction %list%
    return var



# memory access 

def sign_extend_hex(s): # '12031312' returns '210481200'
    sign = '0'
    num = int('0x'+s[0],16)
    if (num > 7):
        sign = 'F'
    ne = 8-len(s)
    return (sign*ne)+s

def memoryAccess(oper_type, operation, reg_list, var):
    global PC
    global data_memory
    
    memread = 0
    # (oper_type == 'R') NO ACTION
    if (oper_type == 'S'):
        if (operation == 'sb'):
            data_memory[var] = data_memory.get(var,'00000000')[:6] + registers[get_signed(reg_list[1])][-2:]
        elif (operation == 'sh'):
            data_memory[var] = data_memory.get(var,'00000000')[:4] + registers[get_signed(reg_list[1])][-4:]
        elif (operation == 'sw'):
            data_memory[var] = registers[get_signed(reg_list[1])][-8:]
    elif (oper_type == 'I'): # registers[get_signed(reg_list[0])]
        if (operation == 'lb'):
            memread = '0x' + sign_extend_hex(data_memory.get(var,'00000000')[-2:])
        elif (operation == 'lh'):
            memread = '0x' + sign_extend_hex(data_memory.get(var,'00000000')[-4:])
        elif (operation == 'lw'):
            memread = '0x' + sign_extend_hex(data_memory.get(var,'00000000')[-8:])
        elif (operation == 'jalr'):
            # memread = '0x' + hex(PC+4)[2:].zfill(8)
            PC = var
        # others NO ACTION
    elif (oper_type == 'SB'):
        PC = var
    # elif (oper_type == 'U'):
    #     memread = '0x' + hex(var)[2:].zfill(8)
    elif (oper_type == 'UJ'):
        # memread = '0x' + hex(PC+4)[2:].zfill(8)
        PC = var[0]

    return memread

# register update

def int_to_signed(val):
    print(val)
    if (val < 0):
        return hex(val+(1<<32))
    return '0x'+hex(val)[2:].zfill(8)

def registerUpdate(oper_type, operation, reg_list, var, memread):
    global registers
    
    if (oper_type == 'R'):
        registers[get_signed(reg_list[0])] = int_to_signed(var)
    # (oper_type == 'S') NO ACTION
    elif (oper_type == 'I'):
        if (operation == 'jalr'):
            registers[get_signed(reg_list[0])] = '0x' + hex(PC+4)[2:].zfill(8)
        elif (operation in ['lb', 'lh', 'lw']):
            registers[get_signed(reg_list[0])] = memread
        elif (operation in ['andi', 'ori', 'addi']):
            registers[get_signed(reg_list[0])] = int_to_signed(var)
    # (oper_type == 'SB') NO ACTION
    elif (oper_type == 'U'):
        registers[get_signed(reg_list[0])] = '0x' + hex(var)[2:].zfill(8)
    elif (oper_type == 'UJ'):
        registers[get_signed(reg_list[0])] = '0x' + hex(var[1])[2:].zfill(8)

    registers[0] = '0x00000000' #--------------------------------------------------
    return


# main function

def main():
    reset_all()
    readfile('inp2.mc')   
    
    while (1):
        instr = fetch()
        if(instr=="text_end" ):
            print("end of code")
            break
        oper_type, operation, reg_list = decode(instr)
        if(operation=="error"):
            print("error in machine code")
            continue
    
        var = execute(oper_type, operation, reg_list)
        memread = memoryAccess(oper_type, operation, reg_list, var)
        registerUpdate(oper_type, operation, reg_list, var, memread)
    return

main()
