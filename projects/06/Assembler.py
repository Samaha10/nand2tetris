import re
import sys

class Assembler():
    def __init__(self):
        self.symbol_table = {'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4, 
                            'R0':0, 'R1':1, 'R2':2, 'R3':3, 
                            'R4':4, 'R5':5, 'R6':6, 'R7':7, 
                            'R8':8, 'R9':9, 'R10':10, 
                            'R11':11, 'R12':12, 'R13':13, 
                            'R14':14, 'R15':15, 
                            'SCREEN':16384, 'KBD':24576} 
        
        self.jumps = ['', "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"]
        
        self.comp_codes = {'0': '101010', '1': '111111', '-1':'111010', 
                          'D':'001100', 'A': '110000', '!D': '001101', 
                          '!A': '110001', '-D': '001111', '-A': '110011', 
                          'D+1': '011111', 'A+1': '110111', 
                          'D-1': '001110', 'A-1': '110010', 
                          'D+A': '000010', 'D-A': '010011', 'A-D':'000111', 
                          'D&A': '000000', 'D|A': '010101'}             
        
        self.var_counter = 16
    

    def assemble(self, file_content):
        # delete white lines and comments
        content = []
        for line in file_content:
            w = re.sub('[ \n]', '', line).split('/')[0]
            if w:
                content.append(w)
        
        # first pass (labels)
        # A label can be defined only once
        i = 0
        for line in content:
            if line[0] == '(':
                self.symbol_table[self.extract_label(line)] = i
                continue
            i += 1

        # second pass
        bin_code = []
        for line in content:
            if line[0] != '(':
                if line[0] == '@':
                    bin_code.append(self.a_instruct(line))
                else:
                    bin_code.append(self.c_instruct(line))
        
        return bin_code


    def a_instruct(self, instruct):
        x = instruct[1:]        
        # number literal case 
        if x.isdigit():
            # 15- bit digits , guarenteed 0 16th
            val = int(x)
        # label / variable
        else:
            # first time variable
            if x not in self.symbol_table:
                self.symbol_table[x] = self.var_counter
                self.var_counter += 1
            
            val = self.symbol_table[x]

        return '{0:016b}'.format(val) + '\n'
    
    def c_instruct(self, instruct):
        dest_split = instruct.split('=')
        if len(dest_split) == 2:
            d = dest_split[0]
            remain = dest_split[1]
        else:
            d = ''
            remain = dest_split[0]
        destination = self.dest_process(d)

        jump_split = remain.split(';')
        j = jump_split[1] if len(jump_split) == 2 else ''
        jump = '{0:03b}'.format(self.jumps.index(j))
                
        compute = self.comp_process(jump_split[0])

        return ''.join(["111", compute, destination, jump, '\n'])  
        
    def dest_process(self, dest):
        d1 = '1' if 'A' in dest else '0'
        d2 = '1' if 'D' in dest else '0'
        d3 = '1' if 'M' in dest else '0'
        return d1 + d2 + d3

    def comp_process(self, comp):
        a = '1' if 'M' in comp else '0'
        code = self.comp_codes[comp.replace('M', 'A')]
        return a + code

    def extract_label(self, lab):
        return re.sub('[()]','', lab)



def main():
    assembler = Assembler() 
    if len(sys.argv) != 2:
        print("No file provided")
        return

    with open(sys.argv[1], 'r') as file:
        content = file.readlines()
    
    machine = assembler.assemble(content)

    fname = sys.argv[1].split('.')[0] + '.hack'

    with open(fname, 'w') as f:
        f.writelines(machine)


if __name__=="__main__":
    main()
