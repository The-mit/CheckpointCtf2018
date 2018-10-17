import sys
from executor import *

in_file = None
stack = None
ip = None

def print_seperator():
    print '-'*15

def remaining_bytes(f):
    pos = f.tell()
    f.seek(0, 2)    #going to the end of te file
    size = f.tell() - pos
    f.seek(pos, 0)
    return size

def run_command(*args):
    b = in_file.read(1)
    while(b != ''):
        in_file.seek(-1, 1)
        execute_next_instruction(in_file, stack)
        b = in_file.read(1)
    
def step_command(*args):
    count = 1
    if(len(args) > 0):
        count = int(args[0])
    for i in range(count):
        execute_next_instruction(in_file, stack)
        
    show_command()          #show next lines after execution pauses
    print_seperator()
    stack_command()

def stack_command(*args):
    depth = 5               #default of 5 values unless asked for a different amount
    if(len(args) == 1):
        depth = int(args[0])
    elif len(args) == 2:
        depth = int(args[1])
        
    for i in stack[-depth:][::-1]:
        print i

def show_command(*args):
    loc = in_file.tell()          #saving the location on the file to rewind to it later
    amount = 5               #default of 5 next instructions unless asked for a different amount
    if(len(args) > 0):
        amount = int(args[0])
    amount = min(amount, remaining_bytes(in_file))
    
    parse_n_instructions(in_file, amount)
    in_file.seek(loc, 0)

def hex_command(*args):
    amount = 5
    if(len(args) > 0):
        amount = int(args[0])
        
    loc = in_file.tell()
    for i in range(amount):
        print in_file.read(1).encode("hex"),
    print ''
    in_file.seek(loc, 0)

def step_over_action(*args):
    next_instruction = ord(in_file.read(1))
    in_file.seek(-1, 1)
    if(next_instruction != 0x11):       #single step if the instruction wasn't a call
        step_command(*args)
        return

    execute_next_instruction(in_file, stack)    #execute the call
    next_instruction = ord(in_file.read(1))     #wait for ret
    in_file.seek(-1, 1)
    while next_instruction != 0x12:
        if next_instruction == 0x11:        #nested calls
            step_over_action()
        execute_next_instruction(in_file, stack)
        next_instruction = ord(in_file.read(1))
        in_file.seek(-1, 1)
    execute_next_instruction(in_file, stack)    #exeute the return

def step_over_command(*args):
    step_over_action(*args)
    show_command()          #show next lines after execution pauses
    print_seperator()
    stack_command()

def exit_command(*args):
    print "exiting"
    in_file.close()
    sys.exit(0)

def start(input_name):
    global in_file
    global stack
    global ip
    in_file = open(input_name, "rb")
    stack = []
    
    commands = {"run":run_command, "step":step_command, "stack":stack_command, "show":show_command, "hex":hex_command, "stepo":step_over_command, "exit":exit_command}
    print "possible commands:"
    print commands.keys()

    print '>',
    command = raw_input().strip().split()   #split on whitespaces
    while True:
        if command == [] or command[0] not in commands:
            print "invalid command"
            print '>',
            command = raw_input().strip().split()
            continue
        
        commands[command[0]](*command[1:])      #execute command and send parameters

        #continue to next action
        print '>',
        next_command = raw_input().strip().split()
        if next_command != []:
            command = next_command
            
if __name__ == "__main__":
    if(len(sys.argv) > 1):
        input_name = sys.argv[1]
    else:
        #print "executable:",
        #input_file = raw_input()
        input_name = "machine.bin"  #out of laziness, hardcoded unless need to be changed
    start(input_name)
