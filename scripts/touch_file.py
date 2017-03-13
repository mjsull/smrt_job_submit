import sys
import os


odlist = []
for i in os.listdir(sys.argv[1]):
    with open(sys.argv[1] + '/' + i) as bsub:
        for line in bsub:
            if "OUT=" in line:
                args = line.split()
                for i in args:
                    if i.startswith('OUT='):
                        outdir = i[4:]
                        odlist.append(outdir)


loc = sys.argv[2]
for i in odlist:
    if os.path.exists(i + '/' + loc):
        os.utime(i + '/' + loc, None)
        print i + '/' + loc
