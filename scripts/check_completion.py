import os


for i in os.listdir('/hpc/users/sullim11/scripts/smrt_job_submit/bsubs'):
     if i.lower() != 'readme':
         ass_no = i[:-5]
         job = 'not found'
         for j in os.listdir('/sc/orga/projects/InfectiousDisease/igb/'):
             if j.endswith(ass_no):
                 if os.path.exists('/sc/orga/projects/InfectiousDisease/igb/' + j + '/index.html'):
                     job = j
                 break
         print ass_no, job
