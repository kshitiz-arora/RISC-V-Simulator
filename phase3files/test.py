memory = {i:100+i for i in range(1000)}

data_cache = dict()
instr_cache = dict()
cache_size = None # in Bytes
block_size = None # in Bytes
numSA = None
num_of_sets = None
num_of_blocks = None
hits = 0
misses = 0
accesses = 0
I_hits = 0
I_misses = 0
I_accesses = 0

def getSet(numSA):
    w = dict()
    l = [0, None, None]
    for i in range(numSA):
        w[i] = [0, None, None, []]
    return w


def intialise_data_cache():
    global data_cache
    global num_of_sets
    global num_of_blocks
    global block_size
    num_of_blocks = int(cache_size/block_size)
    num_of_sets = int(num_of_blocks/numSA)
    block_size = int(block_size/4)
    for i in range(num_of_sets):
        data_cache[i] = getSet(numSA)
    return

def intialise_instr_cache():
    global instr_cache
    global num_of_sets
    global num_of_blocks
    num_of_blocks = int(cache_size/block_size)
    num_of_sets = int(num_of_blocks/numSA)
    for i in range(num_of_sets):
        instr_cache[i] = getSet(numSA)
    return

def readInstrCache(address): # type(address) = int
    
    global data_cache
    global I_hits
    global I_misses
    global I_accesses

    I_accesses += 1

    startAddress = address - (address % block_size)
    numBlock = int (startAddress / num_of_blocks)
    numSet = numBlock % num_of_sets

    isHit = False
    index = -1
    reqMem = None

    for i in range(numSA):
        if (instr_cache[numSet][i][0] == 1):
            if (instr_cache[numSet][i][2] == startAddress):
                isHit = True
                index = i
                break
    
    if (isHit):
        I_hits += 1 
        reqMem = instr_cache[numSet][index][3][address-startAddress]
    
    else:
        I_misses += 1
        isAvailable = False
        index = -1
        for i in range(numSA):
            if (instr_cache[numSet][i][0] == 0):
                isAvailable = True
                index = i
                break
        if (isAvailable == False):
            for i in range(numSA):
                if (instr_cache[numSet][i][1] == 0):
                    instr_cache[numSet][i] = getSet(numSA)
                    index = i
                    break
        instr_cache[numSet][index][0] = 1
        instr_cache[numSet][index][1] = numSA-1
        instr_cache[numSet][index][2] = startAddress
        instr_cache[numSet][index][3] = [memory.get(startAddress + i, '00000000') for i in range(block_size)]
        reqMem = instr_cache[numSet][index][3][address-startAddress]
        
    for i in range(numSA):
        if (instr_cache[numSet][i][0] == 1):
            instr_cache[numSet][i][1] = max(instr_cache[numSet][i][1]-1, 0)
    instr_cache[numSet][index][1] = numSA-1

    return reqMem


def readDataCache(address): # type(address) = int
    
    global data_cache
    global hits
    global misses
    global accesses

    accesses += 1

    startAddress = address - (address % block_size)
    numBlock = int (startAddress / num_of_blocks)
    numSet = numBlock % num_of_sets

    isHit = False
    index = -1
    reqMem = None

    for i in range(numSA):
        if (data_cache[numSet][i][0] == 1):
            if (data_cache[numSet][i][2] == startAddress):
                isHit = True
                index = i
                break
    
    if (isHit):
        hits += 1 
        reqMem = data_cache[numSet][index][3][address-startAddress]
    
    else:
        misses += 1
        isAvailable = False
        index = -1
        for i in range(numSA):
            if (data_cache[numSet][i][0] == 0):
                isAvailable = True
                index = i
                break
        if (isAvailable == False):
            for i in range(numSA):
                if (data_cache[numSet][i][1] == 0):
                    data_cache[numSet][i] = getSet(numSA)
                    index = i
                    break
        data_cache[numSet][index][0] = 1
        data_cache[numSet][index][1] = numSA-1
        data_cache[numSet][index][2] = startAddress
        data_cache[numSet][index][3] = [memory.get(startAddress + i, '00000000') for i in range(block_size)]
        reqMem = data_cache[numSet][index][3][address-startAddress]
        
    for i in range(numSA):
        if (data_cache[numSet][i][0] == 1):
            data_cache[numSet][i][1] = max(data_cache[numSet][i][1]-1, 0)
    data_cache[numSet][index][1] = numSA-1

    return reqMem

def writeDataCache(address, data):

    global data_cache
    global hits
    global misses
    global accesses
    global memory

    accesses += 1

    startAddress = address - (address % block_size)
    numBlock = int (startAddress / num_of_blocks)
    numSet = numBlock % num_of_sets

    isHit = False
    index = -1
    reqMem = None

    for i in range(numSA):
        if (data_cache[numSet][i][0] == 1):
            if (data_cache[numSet][i][2] == startAddress):
                isHit = True
                index = i
                break
    
    if (isHit):
        hits += 1 
        # reqMem = data_cache[numSet][index][3][address-startAddress]
        data_cache[numSet][index][3][address-startAddress] = data
    
    else:
        misses += 1
        isAvailable = False
        index = -1
        for i in range(numSA):
            if (data_cache[numSet][i][0] == 0):
                isAvailable = True
                index = i
                break
        if (isAvailable == False):
            for i in range(numSA):
                if (data_cache[numSet][i][1] == 0):
                    data_cache[numSet][i] = getSet(numSA)
                    index = i
                    break
        data_cache[numSet][index][0] = 1
        data_cache[numSet][index][1] = numSA-1
        data_cache[numSet][index][2] = startAddress
        data_cache[numSet][index][3] = [memory.get(startAddress + i, '00000000') for i in range(block_size)]
        reqMem = data_cache[numSet][index][3][address-startAddress]
        data_cache[numSet][index][3][address-startAddress] = data
        
    for i in range(numSA):
        if (data_cache[numSet][i][0] == 1):
            data_cache[numSet][i][1] = max(data_cache[numSet][i][1]-1, 0)
    data_cache[numSet][index][1] = numSA-1

    memory[address] = data

    return None

cache_size = 360
block_size = 12
numSA = 4 

intialise_data_cache()

readDataCache(100)
readDataCache(300)
readDataCache(500)
readDataCache(110)
readDataCache(601)