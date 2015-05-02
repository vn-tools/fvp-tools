#!/usr/bin/python2
import os,sys,struct,re

opcodes = [
    [0x01,['b','b']],    # unknown
    [0x02,['d']],        # call function
    [0x03,['w']],        # unknown
    [0x04,[]],           # retn?
    [0x05,[]],           # retn?
    [0x06,['d']],        # jump?
    [0x07,['d']],        # cond jump?
    [0x08,[]],           # unknown
    [0x09,[]],           # unknown
    [0x0a,['d']],        # unknown
    [0x0b,['w']],        # unknown
    [0x0c,['b']],        # unknown
    [0x0e,['b','s']],    # string
    [0x0f,['w']],        # unknown
    [0x10,['b']],        # unknown
    [0x11,['w']],        # unknown
    [0x12,['b']],        # unknown
    [0x14,[]],           # unknown
    [0x15,['w']],        # unknown
    [0x16,['b']],        # unknown
    [0x17,['w']],        # unknown
    [0x18,['b']],        # unknown
    [0x19,[]],           # unknown
    [0x1a,[]],           # unknown
    [0x1b,[]],           # unknown
    [0x1c,[]],           # unknown
    [0x1d,[]],           # unknown
    [0x1e,[]],           # unknown
    [0x1f,[]],           # unknown
    [0x20,[]],           # unknown
    [0x21,[]],           # unknown
    [0x22,[]],           # unknown
    [0x23,[]],           # unknown
    [0x24,[]],           # unknown
    [0x25,[]],           # unknown
    [0x26,[]],           # unknown
    [0x27,[]],           # unknown
]

def get_data(filename):
    totalbytes = os.path.getsize(filename)
    infile = open(filename, 'rb')
    totalfiledata = infile.read(totalbytes)
    return totalfiledata

def extract(filename):
    filedata = get_data(filename)
    outdata = '### Functions ###\n\n'
    outstrings = ''
    scriptlen = struct.unpack('<I',filedata[:0x4])[0]
    mainscriptstart = struct.unpack('<I',filedata[scriptlen:scriptlen+0x4])[0]
    pos = 4
    strcount = 0
    retncnt = 0
    pushcnt = 0
    pushcnt2 = 0

    while pos < scriptlen:
        if pos == mainscriptstart:
            outdata += '\n### Main Script ###\n\n'
        elif filedata[pos:pos+0xc] == '\x01\x04\x00\x10\xfb\x10\xfc\x10\xfd\x10\xfe\x02':
            if pushcnt == 1:
                outdata += '\n### Push text 1 ###\n\n'
                pushcnt += 1
            else:
                pushcnt += 1
        elif filedata[pos:pos+0x4] == '\x01\x00\x00\x02':
            if pushcnt2 == 4:
                outdata += '\n### Push text 2 ###\n\n'
                pushcnt2 += 1
            else:
                pushcnt2 += 1
        opcode = struct.unpack('<B',filedata[pos:pos+1])[0]

        c = 0
        while c != len(opcodes):
            if opcodes[c][0] == opcode:
                variablecount = opcodes[c][1]
                name = opcodes[c][0]
                break;
            if c+1 == len(opcodes):
                print 'Unknown script opcode: %x at loc: %x' % (opcode,pos)
                sys.exit()
            c += 1
        outdata += '%x :: %s { ' % (pos,name)
        pos += 1
        stringlen = 0
        for i in xrange(0,len(variablecount)):
            if variablecount[i] == 'b':
                if opcode != 0xe:
                    outdata += '%x ' % struct.unpack('<B',filedata[pos:pos+1])[0]
                pos += 1
            elif variablecount[i] == 'w':
                outdata += '%x ' % struct.unpack('<H',filedata[pos:pos+2])[0]
                pos += 2
            elif variablecount[i] == 'd':
                outdata += '%x ' % struct.unpack('<I',filedata[pos:pos+4])[0]
                pos += 4
            elif variablecount[i] == 's':
                if opcode == 0xe:
                    stringlen = struct.unpack('<B',filedata[pos-1:pos])[0]
                    outdata += '<string %d> ' % strcount
                    outstrings += '%d: %s\n' % (strcount,filedata[pos:pos+stringlen-1])
                    pos += stringlen
                    strcount += 1
            else:
                print 'Variable type error for opcode %x at loc %x' % (opcode,pos)
                sys.exit()

        outdata += '}\n'
        if opcode == 0x4 and struct.unpack('<B',filedata[pos:pos+1])[0] != 0x4:
            outdata += '\n'

    outdata += '\n' + '### Extra Binary Data ###\n\n' + filedata[scriptlen+0x4:len(filedata)]

    outfile = open('script.txt','wb')
    outfile.write(outdata)
    outfile.close()
    outfile = open('strings.txt','wb')
    outfile.write(outstrings)
    outfile.close()

def comp():
    scriptdata = get_data('script.txt').splitlines()
    stringdata = re.split('\n',get_data('strings.txt'))
    newfiledata = struct.pack('<I',0x0)

    strings = {}
    strcnt = 0
    fullstr = ''
    for i in range(0,len(stringdata)):
        if stringdata[i][:1] != '#' and stringdata[i] != '':
            if fullstr != '':
                strings[strcnt-1] = strings[strcnt-1] + '##' + fullstr[:-2]
                fullstr = ''
            strings[strcnt] = stringdata[i].split(':',1)[1]
            strcnt += 1
        else:
            if stringdata[i] != '':
                fullstr += stringdata[i][1:] + '##'
    scriptdata.pop(0)
    fullstr = None
    stringdata = None

    #build dicts first otherwise this takes WAY too long
    pos = 4
    fullscript = {}
    jumpstofix = {}
    for i in range(0,len(scriptdata)):
        if scriptdata[i] != '':
            if scriptdata[i].find('### Main') != -1:
                pass;
            elif scriptdata[i].find('### Extra') != -1:
                break;
            elif scriptdata[i].find('### Push text 1') != -1:
                pass;
            elif scriptdata[i].find('### Push text 2') != -1:
                pass;
            else:
                line = scriptdata[i].split(' ')
                c = 0
                while c != len(opcodes):
                    if opcodes[c][0] == int(line[2]):
                        fullscript[int(line[0],16)] = pos
                        variables = opcodes[c][1]
                        break;
                    if c+1 == len(opcodes):
                        print 'Unknown script opcode: %s on line: %d' % (line[2],i)
                        sys.exit()
                    c += 1
                pos += 1
                line.pop(0)
                line.pop(0)
                line.pop(0)
                line.pop(0)
                for a in range(0,len(variables)):
                    if variables[a] == 'b':
                        if opcodes[c][0] != 0xe:
                            line.pop(0)
                            pos += 1
                    elif variables[a] == 'w':
                        pos += 2
                        line.pop(0)
                    elif variables[a] == 'd':
                        if opcodes[c][0] == 0x2 or opcodes[c][0] == 0x6 or opcodes[c][0] == 0x7:
                            jumpstofix[pos] = int(line[0],16)
                        line.pop(0)
                        pos += 4
                    elif variables[a] == 's':
                        if opcodes[c][0] == 0xe:
                            stringnum = int(line[1][:len(line[1])-1])
                            strings1 = strings[stringnum].split('##')
                            for b in range(0,len(strings1)):
                                if strings1[b][0] == ' ':
                                    strings1[b] = strings1[b][1:]
                                if b > 0:
                                    pos += 1
                                pos += 1
                                pos += len(strings1[b]) + 1
                                if len(strings1) > 0 and b < len(strings1)-1:
                                    pos += 13


    for i in range(0,len(scriptdata)):
        if scriptdata[i] != '':
            if scriptdata[i].find('### Main') != -1:
                mainscriptstart = len(newfiledata)
            elif scriptdata[i].find('### Extra') != -1:
                break;
            elif scriptdata[i].find('### Push text 1') != -1:
                pushloc1 = len(newfiledata)
            elif scriptdata[i].find('### Push text 2') != -1:
                pushloc2 = len(newfiledata)
            else:
                line = scriptdata[i].split(' ')

                c = 0
                while c != len(opcodes):
                    if opcodes[c][0] == int(line[2]):
                        newfiledata += struct.pack('<B',opcodes[c][0])
                        variables = opcodes[c][1]
                        break;
                    if c+1 == len(opcodes):
                        print 'Unknown script opcode: %s on line: %d' % (line[2],i)
                        sys.exit()
                    c += 1

                line.pop(0)
                line.pop(0)
                line.pop(0)
                line.pop(0)
                for a in range(0,len(variables)):
                    if variables[a] == 'b':
                        if opcodes[c][0] != 0xe:
                            newfiledata += struct.pack('<B',int(line[0],16))
                            line.pop(0)
                    elif variables[a] == 'w':
                        newfiledata += struct.pack('<H',int(line[0],16))
                        line.pop(0)
                    elif variables[a] == 'd':
                        if opcodes[c][0] == 0x2 or opcodes[c][0] == 0x6 or opcodes[c][0] == 0x7:
                            newjumploc = jumpstofix[len(newfiledata)]
                            if not newjumploc in fullscript:
                                #print 'bad opcode %x on line %d' % (opcodes[c][0],i)
                                while newjumploc not in fullscript:
                                    newjumploc += 1
                            newfiledata += struct.pack('<I',fullscript[newjumploc])
                        elif opcodes[c][0] == 0xa:
                            if int(line[0],16) in fullscript:
                                newfiledata += struct.pack('<I',fullscript[int(line[0],16)])
                            else:
                                newfiledata += struct.pack('<I',int(line[0],16))
                        else:
                            newfiledata += struct.pack('<I',int(line[0],16))
                        line.pop(0)
                    elif variables[a] == 's':
                        if opcodes[c][0] == 0xe:
                            stringnum = int(line[1][:len(line[1])-1])
                            strings1 = strings[stringnum].split('##')
                            for b in range(0,len(strings1)):
                                if strings1[b][0] == ' ':
                                    strings1[b] = strings1[b][1:]
                                if b > 0:
                                    newfiledata += struct.pack('<B',0xe)
                                newfiledata += struct.pack('<B',len(strings1[b])+1)
                                newfiledata += strings1[b] + '\x00'
                                if len(strings1) > 0 and b < len(strings1)-1:
                                    newfiledata += '\x08\x08\x08\x02' + struct.pack('<I',pushloc1) + '\x02' + struct.pack('<I',pushloc2)

                    else:
                        print 'Variable type error for opcode %x on line %d' % (opcodes[c][0],i)
                        sys.exit()
                line = None
                strings1 = None

    scriptdata = None

    newfiledata = struct.pack('<I',len(newfiledata)) + newfiledata[4:]
    newfiledata += struct.pack('<I',mainscriptstart)

    scriptdata = get_data('script.txt')
    extrapos = scriptdata.find('### Extra Binary Data ###')+0x1b
    newfiledata += scriptdata[extrapos:extrapos+0x801]

    outfile = open('Snow.hcb.new','wb')
    outfile.write(newfiledata)
    outfile.close()

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-e':
            extract(sys.argv[2])
            return
        elif sys.argv[1] == '-c':
            comp()
            return
    print 'Usage: script.py -e Snow.hcb'
    print 'Usage: script.py -c'
    print '-e: extracts the .hcb script file (Snow.hcb)'
    print '-c: compile strings.txt + script.txt back into a Snow.hcb.new to use in game'

if __name__ == '__main__':
    main()
