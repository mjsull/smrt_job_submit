import os, sys
for i in os.listdir(sys.argv[1]):
   with open(sys.argv[1] + '/' + i) as bsub, open(sys.argv[1] +'/'+ i[:-5] + '.rm.bsub', 'w') as outb:
       for line in bsub:
           if line.startswith('./post-assemble-pathogen'):
               for j in line.split():
                   if j.startswith('SMRT_JOB_ID'):
                      sji = j.split('=')[1]
                   if j.startswith('SPECIES'):
                      species = j.split('=')[1]
                   if j.startswith('STRAIN_NAME'):
                      sn = j.split('=')[1]
               outdir = '/sc/orga/projects/InfectiousDisease/igb/' + species + '_' + sn + '_' + sji + '/'
               outb.write('rm -rf ' + outdir + '\n')
           outb.write(line)
