#!/usr/bin/python2
import os, sys, struct
import marshal

SD_FUNCTIONS = 0
SD_MAIN_SCRIPT = 3
SD_EXTRA_BINARY_DATA = 4
FN_POS = 0
FN_ID = 1
FN_ARGS = 2

opcodes = {
    0x01: ['b', 'b'],   # unknown
    0x02: ['d'],        # call function
    0x03: ['w'],        # unknown
    0x04: [],           # retn?
    0x05: [],           # retn?
    0x06: ['d'],        # jump?
    0x07: ['d'],        # cond jump?
    0x08: [],           # unknown
    0x09: [],           # unknown
    0x0a: ['d'],        # unknown
    0x0b: ['w'],        # unknown
    0x0c: ['b'],        # unknown
    0x0e: ['s'],        # string
    0x0f: ['w'],        # unknown
    0x10: ['b'],        # unknown
    0x11: ['w'],        # unknown
    0x12: ['b'],        # unknown
    0x14: [],           # unknown
    0x15: ['w'],        # unknown
    0x16: ['b'],        # unknown
    0x17: ['w'],        # unknown
    0x18: ['b'],        # unknown
    0x19: [],           # unknown
    0x1a: [],           # unknown
    0x1b: [],           # unknown
    0x1c: [],           # unknown
    0x1d: [],           # unknown
    0x1e: [],           # unknown
    0x1f: [],           # unknown
    0x20: [],           # unknown
    0x21: [],           # unknown
    0x22: [],           # unknown
    0x23: [],           # unknown
    0x24: [],           # unknown
    0x25: [],           # unknown
    0x26: [],           # unknown
    0x27: [],           # unknown
}

def get_data(filename):
    totalbytes = os.path.getsize(filename)
    infile = open(filename, 'rb')
    totalfile_data = infile.read(totalbytes)
    return totalfile_data

def decompile(filename):
    file_data = get_data(filename)
    script_len = struct.unpack('<I', file_data[:0x4])[0]
    main_script_start = struct.unpack('<I', file_data[script_len:script_len+0x4])[0]

    script_data = {
        SD_FUNCTIONS: [],
        SD_MAIN_SCRIPT: [],
        SD_EXTRA_BINARY_DATA: None,
    }
    strings = []

    pos = 4
    strcount = 0
    target = script_data[SD_FUNCTIONS]
    while pos < script_len:
        if pos == main_script_start:
            target = script_data[SD_MAIN_SCRIPT]
        opcode_id = struct.unpack('<B', file_data[pos:pos+1])[0]

        if opcode_id not in opcodes:
            raise RuntimeError('Unknown opcode: %x at loc: %x' % (opcode_id, pos))

        func = {
            FN_POS: pos,
            FN_ID: opcode_id,
            FN_ARGS: []
        }
        pos += 1
        for type in opcodes[opcode_id]:
            if type == 'b':
                func[FN_ARGS].append(struct.unpack('<B', file_data[pos:pos+1])[0])
                pos += 1
            elif type == 'w':
                func[FN_ARGS].append(struct.unpack('<H', file_data[pos:pos+2])[0])
                pos += 2
            elif type == 'd':
                func[FN_ARGS].append(struct.unpack('<I', file_data[pos:pos+4])[0])
                pos += 4
            elif type == 's':
                stringlen = struct.unpack('<B', file_data[pos:pos+1])[0]
                pos += 1
                func[FN_ARGS].append(strcount)
                strings.append(file_data[pos:pos+stringlen-1])
                pos += stringlen
                strcount += 1
            else:
                print 'Variable type error for opcode %x at loc %x' % (opcode_id, pos)
                sys.exit()

        target.append(func)

    script_data[SD_EXTRA_BINARY_DATA] = file_data[script_len+0x4:len(file_data)]

    script_file = open('script.dat', 'wb')
    marshal.dump(script_data, script_file)
    script_file.close()
    strings_file = open('strings.txt', 'wb')
    strings_file.write("\n".join(strings).decode('sjis').encode('utf8'))
    strings_file.close()

def compile(filename):
    script_data = marshal.loads(get_data('script.dat'))
    strings = get_data('strings.txt').decode('utf8').encode('sjis').splitlines()
    new_file_data = struct.pack('<I', 0x0)

    pos = len(new_file_data)
    full_script = {}

    #prepare jump translation table
    for section in [SD_FUNCTIONS, SD_MAIN_SCRIPT]:
        for func in script_data[section]:
            opcode_id = func[FN_ID]
            if opcode_id not in opcodes:
                raise RuntimeError('Unknown script opcode: %s' % opcode_id)
            full_script[func[FN_POS]] = pos
            pos += 1

            for i, type in enumerate(opcodes[opcode_id]):
                arg = func[FN_ARGS][i]
                if type == 'b':
                    pos += 1
                elif type == 'w':
                    pos += 2
                elif type == 'd':
                    pos += 4
                elif type == 's':
                    pos += 1
                    pos += len(strings[arg]) + 1

    for section, functions in script_data.iteritems():
        if section == SD_MAIN_SCRIPT:
            main_script_start = len(new_file_data)
        elif section == SD_EXTRA_BINARY_DATA:
            break

        for func in functions:
            opcode_id = func[FN_ID]
            if opcode_id not in opcodes:
                raise RuntimeError('Unknown script opcode: %s' % opcode_id)
            new_file_data += struct.pack('<B', opcode_id)

            for i, type in enumerate(opcodes[opcode_id]):
                arg = func[FN_ARGS][i]
                if type == 'b':
                    new_file_data += struct.pack('<B', arg)
                elif type == 'w':
                    new_file_data += struct.pack('<H', arg)
                elif type == 'd':
                    if opcode_id == 0x2 or opcode_id == 0x6 or opcode_id == 0x7:
                        new_file_data += struct.pack('<I', full_script[arg])
                    elif opcode_id == 0xa:
                        if arg in full_script:
                            new_file_data += struct.pack('<I', full_script[arg])
                        else:
                            new_file_data += struct.pack('<I', arg)
                    else:
                        new_file_data += struct.pack('<I', arg)
                elif type == 's':
                    new_file_data += struct.pack('<B', len(strings[arg]) + 1)
                    new_file_data += strings[arg]
                    new_file_data += b'\0'
                else:
                    print 'Variable type error for opcode %x' % (opcode_id)
                    sys.exit()

    new_file_data = struct.pack('<I', len(new_file_data)) + new_file_data[4:]
    new_file_data += struct.pack('<I', main_script_start)
    new_file_data += script_data[SD_EXTRA_BINARY_DATA]

    hcb_file = open(filename, 'wb')
    hcb_file.write(new_file_data)
    hcb_file.close()

def main():
    if len(sys.argv) == 3:
        if sys.argv[1] == '-e':
            decompile(sys.argv[2])
            return
        elif sys.argv[1] == '-c':
            compile(sys.argv[2])
            return
    print 'Usage: script.py -e input.hcb'
    print 'Usage: script.py -c output.hcb'
    print '-e: extracts strings.txt + script.dat from the input.hcb script file'
    print '-c: compiles strings.txt + script.dat back into a output.hcb to use in game'

if __name__ == '__main__':
    main()
