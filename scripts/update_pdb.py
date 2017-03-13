import os, sys
for i in os.listdir(sys.argv[1]):
   if i.endswith('.bsub'):
       with open(sys.argv[1] + '/' + i) as bsub, open(sys.argv[1] +'/'+ i[:-5] + '.pdb.bsub', 'w') as outb:
           for line in bsub:
               if line.startswith('./post-assemble-pathogen'):
                   outb.write(' '.join(line.split()[:-1]) + ' igb_to_pathogendb\n')
               else:
                   outb.write(line)
