import sys
import ctypes

BYTE_MAX = 0xFF
#ctypes.c_byte(0xFF).value      #for future reference

def run_add(executable, stack, ip, opcode):
    a = stack.pop()
    b = stack.pop()
    stack.append(ctypes.c_byte((a + b)&BYTE_MAX).value)

def run_sub(executable, stack, ip, opcode):
    a = stack.pop()
    b = stack.pop()
    stack.append(ctypes.c_byte((a - b)&BYTE_MAX).value)

def run_div(executable, stack, ip, opcode):
    a = stack.pop()
    b = stack.pop()
    stack.append(a / b)
    stack.append(a % b)

def run_mul(executable, stack, ip, opcode):
    a = stack.pop()
    b = stack.pop()
    stack.append(ctypes.c_byte((a * b)&BYTE_MAX).value)

def run_pop(executable, stack, ip, opcode):
    stack.pop()

def run_swap(executable, stack, ip, opcode):
    a = stack[-(opcode - 0x20 + 1)]
    b = stack[-1]
    stack[-1] = a
    stack[-(opcode - 0x20 + 1)] = b

def run_load(executable, stack, ip, ins):
    offset = ins - 0x40
    if(offset > len(stack)):
        print "stack access out of range"
        sys.exit(1)
    stack.append(stack[-offset - 1])

def run_push(executable, stack, ip, ins):
    value = ins - 0x80
    stack.append(value)

def run_jmp(executable, stack, ip, ins):
    offset = ctypes.c_byte(stack.pop()).value
    executable.seek(offset, 1)
    
def run_call(executable, stack, ip, ins):
    offset = ctypes.c_byte(stack.pop()).value
    stack.append(ip)
    executable.seek(offset, 1)
    
def run_ret(executable, stack, ip, ins):
    target = stack.pop()
    executable.seek(target, 0)

def run_cje(executable, stack, ip, ins):
    offset = ctypes.c_byte(stack.pop()).value
    a = stack.pop()
    b = stack.pop()
    if a == b:
        executable.seek(offset, 1)

def run_jse(executable, stack, ip, ins):
    offset = ctypes.c_byte(stack.pop()).value
    if len(stack) == 0:
        executable.seek(offset, 1)

def run_read(executable, stack, ip, ins):
    sys.stdout.write("#")
    inp = sys.stdin.read(1)[0]
    stack.append(ord(inp))

def run_write(executable, stack, ip, ins):
    sys.stdout.write(chr(stack.pop()))

def execute_next_instruction(executable, stack):
    b = executable.read(1)
    if(b == ''):
        return
    ins = ord(b)
    #ip = executable.tell()
    if ins == 0x00:             #add
        run_add(executable, stack, executable.tell(), ins)
    elif ins == 0x01:           #sub
        run_sub(executable, stack, executable.tell(), ins)
    elif ins == 0x02:           #div
        run_div(executable, stack, executable.tell(), ins)
    elif ins == 0x03:           #mul
        run_mul(executable, stack, executable.tell(), ins)
    elif ins == 0x20:           #pop
        run_pop(executable, stack, executable.tell(), ins)
    elif 0x21 <= ins <= 0x40:   #swap
        run_swap(executable, stack, executable.tell(), ins)
    elif 0x40 <= ins <= 0x7f:   #load
        run_load(executable, stack, executable.tell(), ins)
    elif 0x80 <= ins <= 0xFF:   #push
        run_push(executable, stack, executable.tell(), ins)
    elif ins == 0x10:           #jmp
        run_jmp(executable, stack, executable.tell(), ins)
    elif ins == 0x11:           #call
        run_call(executable, stack, executable.tell(), ins)
    elif ins == 0x12:           #ret
        run_ret(executable, stack, executable.tell(), ins)
    elif ins == 0x14:           #cje
        run_cje(executable, stack, executable.tell(), ins)
    elif ins == 0x18:           #jse
        run_jse(executable, stack, executable.tell(), ins)
    elif ins == 0x08:           #read
        run_read(executable, stack, executable.tell(), ins)
    elif ins == 0x09:           #write
        run_write(executable, stack, executable.tell(), ins)
    else:
        print "failed to parse instruction @ %x" % (executable.tell()-1)

def parse_n_instructions(executable, n):
    for _ in range(n):
        i = executable.tell()
        ins = ord(executable.read(1))
        #ip = executable.tell()
        if ins == 0x00:    #add
            print i, "add"
        elif ins == 0x01:    #sub
            print i, "sub"
        elif ins == 0x02:    #div
            print i, "div"
        elif ins == 0x03:
            print i, "mul"
        elif ins == 0x20:
            print i, "pop"
        elif 0x21 <= ins <= 0x40:
            print i, "swap", ins - 0x20
        elif 0x40 < ins <= 0x7f:
            print i, "load", ins - 0x40
        elif 0x80 <= ins <= 0xFF:
            print i, "push", ins - 0x80
        elif ins == 0x10:
            print i, "jmp"
        elif ins == 0x11:
            print i, "call"
        elif ins == 0x12:
            print i, "Ret"
        elif ins == 0x14:
            print i, "cje"
        elif ins == 0x18:
            print i, "jse"
        elif ins == 0x08:
            print i, "read"
        elif ins == 0x09:
            print i, "write"
        else:
            print "failed to parse instruction @ %x" % (executable.tell()-1)
