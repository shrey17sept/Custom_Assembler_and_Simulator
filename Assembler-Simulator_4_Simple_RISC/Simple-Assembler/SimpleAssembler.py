import math;import sys

def yellow(str):return f"\033\033[0;33m{str}\033[0;0m"
def red(str):return f"\033\033[31;1m{str}\033[0;0m"
def blue(str):return f"\033\033[0;36m{str}\033[0;0m"

def rCheck(Reg):
    global encode;global count;global hFlag;global error
    if Reg=="FLAGS":
        error.append(f"{red('ERROR ->')} {yellow('Illegal use')} of {blue('<')} {blue('FLAGS')} {blue('>')} at line {count}.\n\n");return False
    elif(Reg not in encode['R']):
        error.append(f"{red('ERROR ->')} {yellow('Unexpected')} register value  {blue('<')} {blue(Reg)} {blue('>')} at line {count}.\n\n");return False
    return True

def nCheck(Number):
    if Number>255 or Number<0:
        error.append(f"{red('ERROR ->')} {yellow('Overflowed')} immediate value {blue('<')} {blue(Number)} {blue('>')} at line {count}.\n\n");return False
    return True

def vCheck(variable):
    if(variable in encode['V']['var']):return True
    error.append(f"{red('ERROR ->')} {yellow('Undefined')} variable {blue('<')} {blue(variable)} {blue('>')} at line {count}.\n\n");return False

def lCheck(label):
    global count;global encode;global input
    if(label in encode['L']):return True
    else:
        skips=-1
        for data in input:
            skips+=1;lst=data.split()
            if lst[0]==label+':' :
                undeclared.append(label)
                encode['L'][label]=bin(skips-vCount).replace("0b",'0'*(8-math.floor(math.log2(skips-vCount)+1)));return True
        error.append(f"{red('ERROR ->')} {yellow('Undefined')} refference {blue('<')} {blue(label)} {blue('>')} at line {count}.\n\n");return False   
                
def memCheck():
    if count<=256:return True
    error.append(f"{red('ERROR ->')} {yellow('Memory limit exceeded')} at line {count}.\n\n");return False

def allocVariable(variable):
    global count;global encode;global vFlag;global vCount;global vIndex
    if vFlag==True:
        if(variable in encode['V']['var']):
            error.append(f"{red('ERROR ->')} {yellow('Multiple variable')} declaration for {blue('<')} {blue(variable)} {blue('>')} at line {count}.\n\n")
        elif(checkname(variable)):
            vCount+=1
            encode['V']['var'][variable]='00000000' if vIndex==0 else bin(vIndex).replace("0b",'0'*(8-math.floor(math.log2(vIndex)+1)));vIndex+=1
    else:
        error.append(f"{red('ERROR ->')} {yellow('Non header variable')} declaration for {blue('<')} {blue(variable)} {blue('>')} at line {count}.\n\n")  

def checklen(letter, l):
    if letter == 'A' and len(l) <= 4:return True
    elif (letter == 'B' or letter == 'C' or letter == 'D') and len(l) <= 3:return True
    elif letter == 'E' and len(l) <= 2:return True
    elif letter == 'F' and len(l) <= 1:return True
    elif(letter=='V' and len(l)<=2):return True
    elif(letter=='L'):return True
    else:error.append(f"{red('ERROR ->')} {yellow('Too many arguments')} for {blue('<')} {blue((l[0]))} {blue('>')} at line {count}.\n\n");return False

def checkname(name):
    if(name in (encode['A'] or encode['B'] or encode['C'] or encode['D'] or encode['E'] or encode['F']) or name=='var'):
        error.append(f"{red('ERROR ->')} {yellow('Reserved keyword')} declaration {blue('<')} {blue(name)} {blue('>')} at line {count} is forbidden.\n\n");return False    
    return True

def machine(line):
    global g;global count;global vFlag;global hFlag;global lFlag;global hltINDEX;global vCount;global undeclared
    try:
        l=[str(x) for x in line.split()]
        if(l==[]):
            count-=1;return
        if(hFlag):
            error.append(f"{red('ERROR ->')} {yellow('No instruction')} expected after {blue('<')} {blue('hlt')} {blue('>')} at line {hltINDEX}.\n\n");return
        if(':'in l[0]):
            vFlag=False
            label=l.pop(0);label=label[:len(label)-1:]
            if(label in undeclared):undeclared.remove(label)
            elif label not in encode['L']:
                if(label in encode['V']['var']):error.append(f"{red('ERROR ->')} {yellow('Redeclaring variable')} {blue('<')} {blue(label)} {blue('>')} as label at line {count}.\n\n");return
                elif(checkname(label)):encode['L'][label]='00000000' if count-1-vCount==0 else bin(count-1-vCount).replace("0b",'0'*(8-math.floor(math.log2(count-vCount-1)+1)))
            else:
                error.append(f"{red('ERROR ->')} {yellow('Multiple label')} declaration for {blue('<')} {blue(label)} {blue('>')} at line {count}.\n\n");return
        for letter in encode:
            if l==[]:return
            if l[0] in encode[letter]:
                if(letter!='V'):vFlag=False
                if(letter=='B' and '$' not in l[2]):letter='C'
                break      
            if(letter=='L'):
                if(':' in l[0]):
                    temp=l.pop(0);temp=temp[:len(temp)-1:]
                    if(temp in encode['L']):
                        error.append(f"{red('ERROR ->')} {yellow('Multiple label')} declaration for {blue('<')} {blue(label)} {blue('>')} at line {count}.\n\n");return
                    else:
                        encode['L'][temp]=encode['L'][label];machine(' '.join(l));return
                else:
                    if(l[0]+':' in encode['L']):
                        encode['L'][label]=encode['L'][l[0]]
                    else:
                        if(lCheck(l[0])):encode['L'][label]=encode['L'][l[0]];return                
        checklen(letter,l) 
        if(letter=='A'):
            if(rCheck(l[1]) and rCheck(l[2]) and rCheck(l[3])):
                code.append(encode[letter][l[0]]+'0'*2+encode['R'][l[1]]+encode['R'][l[2]]+encode['R'][l[3]]+'\n')
        elif(letter=='B'):
            if(rCheck(l[1]) and nCheck(int(l[2][1::]))):
                number='00000000'if int(l[2][1::])==0 else bin(int(l[2][1::])).replace("0b",'0'*(8-math.floor(math.log2(int(l[2][1::]))+1)))
                code.append(encode[letter][l[0]]+encode['R'][l[1]]+number+'\n')
        elif(letter=='C'):
            if l[1]=='FLAGS' and l[0]=='mov':
                if(rCheck(l[2])):
                    code.append(encode[letter][l[0]]+'0'*5+encode['R'][l[1]]+encode['R'][l[2]]+'\n')
            elif(rCheck(l[1]) and rCheck(l[2])):
                code.append(encode[letter][l[0]]+'0'*5+encode['R'][l[1]]+encode['R'][l[2]]+'\n')
        elif(letter=='D'):
            if(rCheck(l[1]) and vCheck(l[2])):
                code.append(encode[letter][l[0]]+encode['R'][l[1]]+encode['V']['var'][l[2]]+'\n')
        elif(letter=='E'):
            if(lCheck(l[1])):
                code.append(encode[letter][l[0]]+'0'*3+encode['L'][l[1]]+'\n')
        elif(letter=='F'):
            hltINDEX=count;hFlag=True;vFlag=False;lFlag=False
            code.append(encode[letter][l[0]]+'0'*11+'\n')  
        elif(letter=='V'):allocVariable(l[1])
        elif(letter=='L'):
            if(len(l)!=1):
                error.append(f"{red('ERROR ->')} {yellow('Multiple label declaration')} for {blue('<')} {blue(l[0])} {blue('>')} at line {count}.\n\n");return          
            else:encode['L'][label]=encode['L'][l[0]]
    except IndexError:error.append(f"{red('ERROR ->')} Missing {yellow('required arguments')} for {blue('<')} {blue(l[0])} {blue('>')} at line {count}.\n\n")
    except:error.append(f"{red('ERROR ->')} {yellow('General syntax error')} at line {count}.\n\n")

encode={'A':{'add':'10000','sub':'10001','mul':'10110','xor':'11010','or':'11011','and':'11100'},
        'B':{'mov':'10010','rs':'11000','ls':'11001'},
        'C':{'mov':'10011','div':'10111','not':'11101','cmp':'11110'},
        'D':{'ld':'10100','st':'10101'},
        'E':{'jmp':'11111','jlt':'01100','jgt':'01101','je':'01111'},
        'F':{'hlt':'01010'},
        'R':{'R0':'000','R1':'001','R2':'010','R3':'011','R4':'100','R5':'101','R6':'110','FLAGS':'111'},
        'V':{'var':{}},'L':{}}
        
error=[];code=[];count=0;vFlag=True;hFlag=False;lFlag=True;hltINDEX=0;vCount=0;input=[];undeclared=[];vIndex=0

for line in sys.stdin:
    if(line!='\n'):
        input.append(line.strip())
        l=[str(x) for x in line.split()]
        if(l[0]!='var'):vIndex+=1
        

for line in input:
    count+=1
    if memCheck():machine(line)
    else:break

if(count<=256-vCount)and(code==[] or count<=256-vCount and code[-1]!='01010'+'0'*11+'\n'):
        error.append(f"{red('ERROR ->')} Expected {yellow('EOF')} {blue('<')} {blue('hlt')} {blue('>')} at line {vIndex+1}.\n")  

print(*error,sep='') if (len(error)!=0) else print(*code,sep='')