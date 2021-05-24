PC = 0x0
PC_temp = 0x0
clock = 0
instructions = dict()
registers = dict()
registers_bool = dict()
memory = dict()
# for data forwarding
data_frwd = 0

# variable = dict()
message = ['' for _ in range(5)]
#queues for buffers 
fetch_buffer= []
decode_buffer= []
execute_buffer= []
memory_buffer= []

#counters
fetch_counter= -1
decode_counter= -1
execute_counter= -1
memory_counter= -1
register_counter= -1



def reset_all():

    global PC
    global registers
    global memory
    # global variable
    global fetch_buffer
    global decode_buffer
    global execute_buffer
    global memory_buffer
    global registers_bool
    PC = 0x0

    decode_buffer= []
    execute_buffer= []
    fetch_buffer= []
    memory_buffer= []

    registers = {i: '0x00000000' for i in range(32)}
    registers_bool = {i: 0 for i in range(32)}
    
    registers[2] = '0x7FFFFFF0'  # stack pointer
    registers[3] = '0x10000000'  # global pointer

    data_size = 1000
    # to be addressed starting from 0x10000000
    memory = {(0x10000000+(4*i)): '00000000' for i in range(data_size)}

    stack_size = 1000
    # to be addressed starting from 0x7FFFFFFC

    for i in range(0x7FFFFFFC, 0x7FFFFFFC-4000, -4):
        memory[i] = '00000000'

    heap_size = 1000
    # to be addressed starting from 0x10007FE8

    for i in range(0x10007FE8, 0x10007FE8+4000, 4):
        memory[i] = '00000000'

    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}

    return


def readfile(filename):  # assuming input.mc has instructions > data > stack > heap

    global instructions
    global registers
    global memory

    file = open(filename, 'r')

    input_list = dict()

    for line in file:
        a, b = line.split()
        if (b == 'text_end'):
            instructions[int(a, 16)] = b
            break
        instructions[int(a, 16)] = b

    for line in file:
        a, b = line.split()
        if (b == 'data_end'):
            break
        if (b[:2] == '0x'):
            b = b[2:]
        memory[int(a, 16)] = b

    for line in file:
        a, b = line.split()
        if (b == 'stack_end'):
            break
        if (b[:2] == '0x'):
            b = b[2:]
        memory[int(a, 16)] = b

    for line in file:
        a, b = line.split()
        if (b == 'heap_end'):
            break
        if (b[:2] == '0x'):
            b = b[2:]
        memory[int(a, 16)] = b

    return


def extractR(instr):  # instruction is of type string, for ex, 0x00011101
    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    variable['opcode'] = bin_instr[25:32]
    variable['rd'] = bin_instr[20:25]
    variable['funct3'] = bin_instr[17:20]
    variable['rs1'] = bin_instr[12:17]
    variable['rs2'] = bin_instr[7:12]
    variable['funct7'] = bin_instr[0:7]
    return variable # [opcode, rd, funct3, rs1, rs2, funct7]


def extractS(instr):  # instruction is of type string, for ex, 0x00011101
    # global variable
    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    variable['opcode'] = bin_instr[25:32]
    imm1 = bin_instr[20:25]
    variable['funct3'] = bin_instr[17:20]
    variable['rs1'] = bin_instr[12:17]
    variable['rs2'] = bin_instr[7:12]
    imm2 = bin_instr[0:7]
    variable['imm'] = imm2+imm1
    return variable # [opcode, funct3, rs1, rs2, imm]


def extractI(instr):  # instruction is of type string, for ex, 0x00011101
    # global variable
    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    variable['opcode'] = bin_instr[25:32]
    variable['rd'] = bin_instr[20:25]
    variable['funct3'] = bin_instr[17:20]
    variable['rs1'] = bin_instr[12:17]
    variable['imm'] = bin_instr[0:12]

    return variable # [opcode, rd, funct3, rs1, imm]


def extractSB(instr):  # instruction is of type string, for ex, 0x00011101
    # global variable
    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    variable['opcode'] = bin_instr[25:32]
    variable['funct3'] = bin_instr[17:20]
    variable['rs1'] = bin_instr[12:17]
    variable['rs2'] = bin_instr[7:12]

    variable['imm'] = bin_instr[0] + bin_instr[7] + \
        bin_instr[1:7] + bin_instr[20:24] + '0'

    return variable # [opcode, funct3, rs1, rs2, imm]


def extractU(instr):  # instruction is of type string, for ex, 0x00011101
    # global variable
    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    variable['opcode'] = bin_instr[25:32]
    variable['rd'] = bin_instr[20:25]
    variable['imm'] = bin_instr[0:20]+'0'*12

    return variable # [opcode, rd, imm]


def extractUJ(instr):  # instruction is of type string, for ex, 0x00011101
    # global variable
    variable = {'opcode': '', 'funct3': '', 'funct7': '', 'rd': '',
                'rs1': '', 'rs2': '', 'instr_type': '', 'operation': ''}
    bin_instr = bin(int(instr, 16))[2:].zfill(32)
    variable['opcode'] = bin_instr[25:32]
    variable['rd'] = bin_instr[20:25]

    variable['imm'] = bin_instr[0]+bin_instr[12:20] + \
        bin_instr[11]+bin_instr[1:11]+'0'

    return variable # [opcode, rd, imm]


def decodeR(variable):  # funct3, funct7):

    funct3 = variable['funct3']
    funct7 = variable['funct7']

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


def decodeS(variable):  # funct3):
    funct3 = variable['funct3']
    operation = 'error'
    if (funct3 == '000'):
        operation = 'sb'
    elif (funct3 == '001'):
        operation = 'sh'
    elif (funct3 == '010'):
        operation = 'sw'
    return operation


def decodeI(variable):  # opcode, funct3):
    opcode = variable['opcode']
    funct3 = variable['funct3']
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


def decodeSB(variable):  # funct3):
    funct3 = variable['funct3']
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


def decodeU(variable):  # opcode):
    opcode = variable['opcode']
    operation = 'error'
    if(opcode == "0010111"):
        operation = "auipc"
    elif(opcode == "0110111"):
        operation = "lui"
    return operation


# fetch

def fetch(P):  # PC is of type string 0x0
    global message
    global PC_temp
    global fetch_buffer

    PC_temp = P + 4
    message[0] = "FETCH:           \nPC_temp -> " + hex(P+4) + "    \nFetched instruction - " + instructions[P]
    
    fetch_buffer.append(instructions[P]) ##now adding it to queue instead of returning
    ##return instructions[PC]  # string or int


# decode


def get_reg_val(reg):
    return get_signed(registers[get_signed(reg)])


def decode(instr):
    global message
    global decode_buffer
    bin_instr = "{0:032b}".format(int(instr, 16))

    opcode = bin_instr[25:32]

    operation = 'error'
    instr_type = 'error'

    reg_list = []

    

    if(opcode == "0110011"):
        instr_type = 'R'
        variable = extractR(instr)
        operation = decodeR(variable)
        reg_list = [get_reg_val(variable['rs1']), get_reg_val(variable['rs2'])]

    elif(opcode == "0100011"):
        instr_type = 'S'
        variable = extractS(instr)
        operation = decodeS(variable)
        reg_list = [get_reg_val(variable['rs1'])]

    elif(opcode == "0000011" or opcode == "0010011" or opcode == "1100111"):
        instr_type = 'I'
        variable = extractI(instr)
        operation = decodeI(variable)
        reg_list = [get_reg_val(variable['rs1'])]

    elif(opcode == "1100011"):
        instr_type = 'SB'
        variable = extractSB(instr)
        operation = decodeSB(variable)
        reg_list = [get_reg_val(variable['rs1']), get_reg_val(variable['rs2'])]

    elif(opcode == "0010111" or opcode == "0110111"):
        instr_type = 'U'
        variable = extractU(instr)
        operation = decodeU(variable)  # code_list[0])
        reg_list = []

    elif(opcode == "1101111"):
        instr_type = 'UJ'
        variable = extractUJ(instr)  # code_list = extractUJ(instr)
        operation = 'jal'
        reg_list = []
    
        
    variable['instr_type'] = instr_type
    variable['operation'] = operation

    #check for data hazard in rs1 and rs2
    if(data_frwd ==1):
        if(variable["rs1"]!=variable["rs2"]):
            # E to E
            if(variable["rs1"]!="" and  registers_bool[int("0b"+variable["rs1"],2)] ==2):
                variable["rs1"]= execute_buffer[0][1]["rd"]
            if(variable["rs2"]!="" and  registers_bool[int("0b"+variable["rs2"],2)] ==2):
                variable["rs2"]= execute_buffer[0][1]["rd"]
            # M to E
            if(variable["rs1"]!="" and registers_bool[int("0b"+variable["rs1"],2)] ==1):
                 variable["rs1"]= memory_buffer[0][2]["rd"]
            if(variable["rs2"]!="" and registers_bool[int("0b"+variable["rs2"],2)] ==1):
                 variable["rs2"]= memory_buffer[0][2]["rd"]
    
            # M to M ------------------
        else:
            # E to E
            if(variable["rs1"]!="" and  registers_bool[int("0b"+variable["rs1"],2)] ==2):
                variable["rs1"]= execute_buffer[0][1]["rd"]
                variable["rs2"]= execute_buffer[0][1]["rd"]
            # M to E
            if(variable["rs1"]!="" and registers_bool[int("0b"+variable["rs1"],2)] ==1):
                 variable["rs1"]= memory_buffer[0][2]["rd"]
                 variable["rs2"]= memory_buffer[0][2]["rd"]
    
            # M to M ------------------
        ############################ CHANGED ######################################    
        ##yaha agr purani instr execute me se just nikli hai to register 
        #me execute se aae hui value dalegi na ki already stored value
        if(instr_type=="R" or instr_type=="SB"):
            if(variable["rs1"]!=variable["rs2"]):
                # E to E
                if(registers_bool[int("0b"+variable["rs1"],2)] ==2):
                    reg_list[0]= execute_buffer[0][0]
                    
                if(registers_bool[int("0b"+variable["rs1"],2)] ==2):
                    reg_list[1]= execute_buffer[0][0]
                # M to E
                if(registers_bool[int("0b"+variable["rs1"],2)] ==1):
                     reg_list[0]= memory_buffer[0][0]
                     
                if(registers_bool[int("0b"+variable["rs2"],2)] ==1):
                     reg_list[1]= memory_buffer[0][0]
        
                # M to M ------------------
            else:
                # E to E
                if(registers_bool[int("0b"+variable["rs1"],2)] ==2):
                    reg_list[0]= execute_buffer[0][0]
                    reg_list[1]= execute_buffer[0][0]
                # M to E
                if(registers_bool[int("0b"+variable["rs1"],2)] ==1):
                     reg_list[0]= memory_buffer[0][0]
                     reg_list[1]= memory_buffer[0][0]
            
            #reg_list = [get_reg_val(variable['rs1']), get_reg_val(variable['rs2'])]
            
            
       
        elif(instr_type=="I" or instr_type=="S"):
            
            if(registers_bool[int("0b"+variable["rs1"],2)] ==2):
                    reg_list[0]= execute_buffer[0][0]
                   
            # M to E
            if(variable["rs1"]!="" and registers_bool[int("0b"+variable["rs1"],2)] ==1):
                 reg_list[0]= memory_buffer[0][0]
            
        
            
        ##############################################################################
        
    if(variable["rd"]!="" ):
        registers_bool[int("0b"+variable["rd"],2)]=3
    message[1] = "\nDECODE:          \nIntruction Type - " + instr_type + "    \nOperation - " + operation + "    \nRegister values are read."
    
    decode_buffer.append([reg_list, variable])
    ##return reg_list


def get_signed(value):
    val = value
    if(val==""):
        return 0
    if (len(val) == 5):  # registers
        return int('0b'+val, 2)
    if (value[:2] == '0b'):
        val = value[2:].zfill(32)
    if (value[:2] == '0x'):
        val = bin(int(value, 16))[2:].zfill(32)
    if (val[0] == '0'):
        return int('0b'+val, 2)
    else:
        inv = ''
        for bit in val:
            inv += str(1 ^ int(bit))
        return -1*(int('0b'+inv, 2)+1)


def shiftRightLogical(n, m):  # shift n right by m bits
    if (n >= 0):
        return n >> m
    s = ''
    b = bin(-n)[2:].zfill(32)
    ns = ''
    for bit in b:
        ns += str(1 ^ int(bit))
    ns = bin(int(ns, 2)+1)[-32:]
    shifted = '0'*m + ns[:32-m]
    return int('0b'+shifted, 2)

# execute


def executeR(reg_list, variable):

    operation = variable['operation']

    op1 = reg_list[0]
    op2 = reg_list[1]

    val = 0

    if (operation == 'add'):
        val = op1 + op2

    elif (operation == 'and'):
        val = op1 & op2

    elif (operation == 'or'):
        val = op1 | op2

    elif (operation == 'sll'):
        val = op1 << op2

    elif (operation == 'slt'):
        if(op1 < op2):
            val = 1
        else:
            val = 0

    elif (operation == 'sra'):  # arithmetic shift right
        val = op1 >> op2

    elif (operation == 'srl'):  # logical shift right
        # val= op1 >> op2
        val = shiftRightLogical(op1, op2)

    elif (operation == 'sub'):
        val = op1 - op2

    elif (operation == 'xor'):
        val = op1 ^ op2

    elif (operation == 'mul'):
        val = op1 * op2

    elif (operation == 'div'):
        val = op1 // op2

    elif (operation == 'rem'):
        val = op1 % op2

    return val


def executeU(reg_list, variable):  # rd imm

    # --U type dont use signed

    operation = variable['operation']

    imm = int('0b'+variable['imm'], 2)

    if(operation == 'auipc'):
        val = PC + imm

    elif(operation == 'lui'):

        val = imm

    return val


def executeSB(reg_list, variable):  # rs1, rs2, imm
    global PC_temp

    operation = variable['operation']

    imm = get_signed(variable['imm'])

    op1 = reg_list[0]
    op2 = reg_list[1]

    if(operation == "beq"):
        if(op1 == op2):
            PC_temp = imm+PC
            return imm+PC-4

    if(operation == "bne"):
        if(op1 != op2):
            PC_temp = imm+PC
            return imm+PC-4

    if(operation == "blt"):
        if(op1 < op2):
            PC_temp = imm+PC
            return imm+PC-4

    if(operation == "bge"):
        if(op1 >= op2):
            PC_temp = imm+PC
            return imm+PC-4

    # PC_temp = PC
    return PC  # -----


def executeUJ(reg_list, variable):  # rd imm
    global PC_temp
    # [rd, imm] = [get_signed(i) for i in reg_list]
    imm = get_signed(variable['imm'])
    PC_temp = PC+imm
    return PC+4


def executeI(reg_list, variable):  # rd rs1 imm
    
    global PC_temp
    operation = variable['operation']
    op1 = reg_list[0]
    op2 = get_signed(variable['imm'])
    ans = 0
    if (operation == 'addi'):
        ans = op1 + op2
    elif (operation == 'andi'):
        ans = op1 & op2
    elif (operation == 'ori'):
        ans = op1 | op2
    elif (operation in ['lb', 'lh', 'lw']):
        ans = op1 + op2  # calculating address
    elif (operation == 'jalr'):
        ans = PC + 4
        PC_temp = op1 + op2
    return ans


def executeS(reg_list, variable):  # rs1 rs2 imm

    ans = reg_list[0] + get_signed(variable['imm'])
    return ans


def execute(parameters):
    [reg_list, variable] = parameters
    global PC
    global PC_temp
    global message
    global execute_buffer
    # PC_temp = PC
    instr_type = variable['instr_type']
    var = 0
    if (instr_type == 'R'):
        var = executeR(reg_list, variable)  # returns value to be stored in rd
    elif (instr_type == 'S'):
        # returns effective address imm(rs1) whose value is to be stored in rs2
        var = executeS(reg_list, variable)
    elif (instr_type == 'I'):
        # returns value to be stored in rd or effective address imm(rs1)
        var = executeI(reg_list, variable)
    elif (instr_type == 'SB'):
        var = executeSB(reg_list, variable)  # return PC temp
    elif (instr_type == 'U'):
        var = executeU(reg_list, variable)  # returns required value
    elif (instr_type == 'UJ'):
        # returns PC temp and return address of jump instruction %list%
        var = executeUJ(reg_list, variable)
    
    if(variable["rd"]!="" and registers_bool[int("0b"+variable["rd"],2)]==3):
        registers_bool[int("0b"+variable["rd"],2)] -= 1
    
    PC = PC_temp
    message[2] = "\nEXECUTE:         \nPC -> " + hex(PC) + "    \nReturned value - " + str(var)
    execute_buffer.append([var, variable])
    #return var


# memory access

def sign_extend_hex(s):  # '12031312' returns '210481200'
    sign = '0'
    num = int('0x'+s[0], 16)
    if (num > 7):
        sign = 'F'
    ne = 8-len(s)
    return (sign*ne)+s


def memoryAccess(parameters):
    [var, variable] = parameters
    # global PC
    global memory
    global message
    global memory_buffer

    if(variable["rd"]!="" and registers_bool[int("0b"+variable["rd"],2)]==2):
        registers_bool[int("0b"+variable["rd"],2)] -= 1

    operation = variable['operation']
    instr_type = variable['instr_type']
    memread = ""
    # (instr_type == 'R') NO ACTION
    if (instr_type == 'S'):
        message[3] = '\nMEMORY ACCESS:   \nMemory at ' + hex(var) + ' is updated.'
        if (operation == 'sb'):
            memory[var] = memory.get(var, '00000000')[
                :6] + registers[get_signed(variable['rs2'])][-2:]
        elif (operation == 'sh'):
            memory[var] = memory.get(var, '00000000')[
                :4] + registers[get_signed(variable['rs2'])][-4:]
        elif (operation == 'sw'):
            memory[var] = registers[get_signed(variable['rs2'])][-8:]
    elif (instr_type == 'I'):
        message[3] = '\nMEMORY ACCESS:   \nData at ' + hex(var) + ' is accessed.'
        if (operation == 'lb'):
            memread = '0x' + sign_extend_hex(memory.get(var, '00000000')[-2:])
        elif (operation == 'lh'):
            memread = '0x' + sign_extend_hex(memory.get(var, '00000000')[-4:])
        elif (operation == 'lw'):
            memread = '0x' + sign_extend_hex(memory.get(var, '00000000')[-8:])
    else:
        message[3] = '\nMEMORY ACCESS:   \nNo Action'

    memory_buffer.append([var, memread, variable])
    ##return memread

# register update


def int_to_signed(val):
    if (val < 0):
        s = bin(-1*val)[2:].zfill(32)
        s = s[-32:]
        rs = '0b'
        for bit in s:
            rs += str(int(1 ^ int(bit)))
        return '0x'+hex(int(rs, 2)+1)[2:].zfill(8)
        # return hex(val+(1<<32))
    return '0x'+hex(val)[2:].zfill(8)


def registerUpdate(parameters):
    [var, memread, variable] = parameters
    global registers
    global message

    if(variable["rd"]!="" and registers_bool[int("0b"+variable["rd"],2)]==1):
        registers_bool[int("0b"+variable["rd"],2)] -= 1

    operation = variable['operation']
    instr_type = variable['instr_type']
    reg = get_signed(variable['rd'])

    if (instr_type == 'R'):
        registers[reg] = int_to_signed(var)
        message[4] = '\nREGISTER UPDATE: \nRegister x' + str(reg) + ' is updated.'
    elif (instr_type == 'S'):
        message[4] = '\nREGISTER UPDATE: \nNo Action'
    elif (instr_type == 'I'):
        message[4] = '\nREGISTER UPDATE: \nRegister x' + str(reg) + ' is updated.'
        if (operation == 'jalr'):
            registers[reg] = '0x' + \
                hex(var)[2:].zfill(8)
        elif (operation in ['lb', 'lh', 'lw']):
            registers[reg] = memread
        elif (operation in ['andi', 'ori', 'addi']):
            registers[reg] = int_to_signed(var)
    elif (instr_type == 'SB'):
        message[4] = '\nREGISTER UPDATE: \nNo Action'
    elif (instr_type == 'U'):
        message[4] = '\nREGISTER UPDATE: \nRegister x' + str(reg) + ' is updated.'
        registers[reg] = '0x' + hex(var)[2:].zfill(8)
    elif (instr_type == 'UJ'):
        message[4] = '\nREGISTER UPDATE: \nRegister x' + str(reg) + ' is updated.'
        registers[reg] = '0x' + hex(var)[2:].zfill(8)

    # ----------------------------------------------
    registers[0] = '0x00000000'
    return

# main function

reset_all()
readfile('test.txt')

def data_forwarding():
    global data_frwd
    data_frwd = 1


def main1():
    global PC
    global register_counter
    global memory_counter
    global execute_counter
    global decode_counter
    global fetch_counter
    
    data_forwarding()

    f = -4
    key = 0
    while(1):
        #fetch()
        print(PC)
        if(f!=-4 and f!=-2 and instructions[f]=="text_end"):
            print("end of code")
            f=-2
            # break

        register_counter = memory_counter
        memory_counter = execute_counter
        execute_counter = decode_counter
        decode_counter = fetch_counter
        fetch_counter = f

        if (f!=-2):
            f= PC#fetch_buffer.pop(0)

        
        
        if(register_counter>=0 ):
            registerUpdate(memory_buffer.pop(0))

        if(memory_counter>=0 ):
            memoryAccess(execute_buffer.pop(0))

        if(execute_counter>=0 ):
            execute(decode_buffer.pop(0))

        if(decode_counter>=0):
            decode(fetch_buffer.pop(0))

        if(fetch_counter>=0 ):
            fetch(fetch_counter)
            
        if (register_counter == -2):
            break

        
        if(execute_counter < 0 and key<3):   ## do only if execute operation is not performed
            PC= PC +4
            key +=1
        #print(PC)
        

    print(registers)
    print(memory[0x10000000])

main1()

def main():
    
    ##instr = fetch()
    fetch()
    if(fetch_buffer.pop(0)=="text_end"):
        print("end of code")

    ##reg_list = decode(fetch_buffer.pop(0))
    decode(fetch_buffer.pop(0))

    # if(variable['operation'] == "error"):
    #     print("error in machine code")
    
    ##var = execute(reg_list)
    execute(decode_buffer.pop(0))
    ##memread = memoryAccess(var)
    # parameters = execute_buffer.pop(0)
    memoryAccess(execute_buffer.pop(0))
    ##registerUpdate(var, memread)
    registerUpdate(memory_buffer.pop(0))
    return
