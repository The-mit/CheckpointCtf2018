from __future__ import print_function
from random import randint, shuffle
import sys
from struct import unpack as up, pack as pk


charset = "OE7AUKL}_GY#0FR{!HMTWS"
flag = ['']*64
flag_index = 0


class T(object):
    #block type
    image = 0
    graphicsControl = 1
    appplicationBlock = 2
    commentBlock = 3
    ET = 4

    
#returns (color table, background color index, color resolution?, height, width)
def parseGIFHeader(f):
    assert f.read(3) == 'GIF', ''   #verify GIF
    assert f.read(3) == '89a', ''
    w, h = up('HH', f.read(4))

    assert 32 <= w <= 500, ''
    assert 32 <= h <= 500, ''
    logflags = up('B', f.read(1))[0]   #color information
    
    assert logflags & 0x80, ''      #bit 7 is up
    size_count = logflags & 0x07    

    gct_count = 2**(size_count+1)   #color resolution?
    assert 4 <= gct_count <= 256, ''

    bgcoloridx = up('B', f.read(1))[0]  #background color index
    f.seek(1, 1)                        #skip pixel aspect ratio
    clrs = []
    #read global color table
    for i in xrange(gct_count):
        clr = (up('B', f.read(1))[0], up('B', f.read(1))[0], up('B', f.read(1))[0])
        clrs.append(clr)

    #assert len(clrs) > bgcoloridx, ''   #color idnex is in table
    return clrs, bgcoloridx, size_count, h, w


#read until a null byte(end of block)
#returns image block image data or applications block application data
def getBlockData(f):
    sbx = ''
    while True:
        rcb = f.read(1)
        sbx += rcb
        if rcb == '\x00':   #end of block
            break

        cb = up('B', rcb)[0]   #treats first byte as length of block
        blk = f.read(cb)    #read the block
        sbx += blk          #concat blocks' content

    return sbx              #return block contents


def nextBlock(f):
    rb = f.read(1)  #read current byte from file
    b = up('B', rb)[0]

    while b != 0x3B:    #while the byte is not the file end [trailer(0x3b)]
        buf = ''
        buf += rb
        if b == 0x2c:   #image block
            nbuf = f.read(2*4)  #read the image block header.
            eb = f.read(1)      #block flags
            assert (up('B', eb)[0] & 0x03) == 0, ''    #local color table, interlace flag
            nbuf += eb          #saving LZW minimus code size end of flag

            nbuf += f.read(1)   
            nbuf += getBlockData(f) #concat image data
            t = T.image
        elif b == 0x21:             #non image block
            rb = f.read(1)          #graphics control label
            buf += rb
            b = up('B', rb)[0]
            
            #checking block type
            if b == 0xF9:           #graphic control extension block
                nbuf = f.read(1)    #block size
                blksize = up('B', nbuf)[0]
                nbuf += f.read(blksize) #reading the rest of the block
                nbuf += f.read(1)       #read block termintor
                assert nbuf[-1] == '\x00', ''   #verifiying the size was OK
                t = T.graphicsControl
            elif b in [0xFF, 0x01]: #plain text or application extension block
                nbuf = f.read(1)    #block size
                blksize = up('B', nbuf)[0]
                nbuf += f.read(blksize) #read the block
                nbuf += getBlockData(f) #read the block data

                t = (b+3) & 0x0F    #block type is appplicationBlock or plaintext
            elif b == 0xFE:         #comment extension block
                nbuf = getBlockData(f)

                t = T.commentBlock
            else:                   #unsupported grapic control label
                raise Exception("unsupprted thing @{}".format(f.tell()))
            
        else:
            print (f.tell(), b)
            
        buf += nbuf

        yield t, buf        #yield the block type and content
        rb = f.read(1)      #read type again
        b = up('B', rb)[0]

    yield None, '\x3B'      #EOF

def decode_index(x, y, w, h):
    if x == 1:      #second case
        return y >> 1
    else:
        #x = 0
        if y == 1:  #first case
            return h >> 2
        else:       #third case
            #x = y = 0
            return w*h

def main(pic, encrypted_flag):
    global flag
    global flag_index
    
    try_decoding = False
    stage_two = True
    
    f = open(pic, 'rb')
    parseGIFHeader(f)
    
    offset = 0
    print("starting from:", f.tell())
    for t, buf in nextBlock(f):
        print('.', end='')

        if(try_decoding):
            if(stage_two):
                isupp = (ord(buf[6])%2 == 1) #read tidx from graphic block
                stage_two = False
                continue
            x = up('H', buf[1:3])[0]   #read x, y, w, h from the image block after the graphic block
            y = up('H', buf[3:5])[0]
            w = up('H', buf[5:7])[0]
            h = up('H', buf[7:9])[0]
            index = decode_index(x, y, w, h)
            flag[flag_index] = encrypted_flag[index].upper() if isupp else encrypted_flag[index].lower()
            if flag[flag_index] == '}':
                break
            
            flag_index += 1
            try_decoding = False
            stage_two = True
            offset = f.tell()
            continue
        #skipping comment block
        if t != T.image:
            offset = f.tell()
            continue
        else:
            ##skip the image block and get to the graphic block
            try_decoding = True
            #print(t, "image block at:", hex(offset))
            #offset = f.tell()
    f.close()
    
    print("".join(flag))
    
if __name__ == "__main__":
    pic = "secret.gif"
    main(pic, charset)
