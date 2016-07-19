import urllib2
import re



def run_new_jobs():
    pattern = re.compile("^[A-Za-z]{2}_[0-9]{5}_[0-9][A-Za-z]_HGAP3$")
    with open('data/job_prefixes') as job_pre:
        job_pre_list = []
        for line in job_pre:
            job_pre_list.append(line.rstrip())
    with open('data/jobs_run') as jobs_run_file:
        jobs_run = set()
        for line in jobs_run_file:
            jobs_run.add(line.rstrip())
    table = urllib2.urlopen("http://smrtportal.hpc.mssm.edu:8080/smrtportal/api/jobs/csv?options=%7B%22rows%22%3A5000%2C%22page%22%3A1%2C%22sortBy%22%3A%22jobId%22%2C%22sortOrder%22%3A%22desc%22%2C%22columnNames%22%3A%5B%22jobId%22%2C%22name%22%2C%22version%22%2C%22protocolName%22%2C%22referenceSequenceName%22%2C%22automated%22%2C%22whenStarted%22%2C%22createdBy%22%2C%22groupNames%22%2C%22jobStatus%22%2C%22comments%22%2C%22sampleName%22%2C%22instrumentName%22%2C%22inputCount%22%2C%22collectionProtocol%22%2C%22primaryProtocol%22%2C%22sequencingCondition%22%2C%22plateId%22%5D%7D&status=Completed%2CFailed%2CStopped")
    table.readline()
    to_submit = set()
    for line in table:
        automated, collectionProtocol, comments, createdBy, groupNames, inputCount, instrumentName, jobId, jobStatus, \
        name, plateId, primaryProtocol, protocolName ,referenceSequenceName, sampleName, sequencingCondition, version, \
        whenStarted = line.split('","')
        if jobStatus == 'Completed' and not pattern.match(name) is None and not jobId in jobs_run:
             to_submit.add((jobId, name))
    for i in to_submit:
        jobid = i[0]
        strain = i[1]
        strain = strain[:2] + strain[3:8] + '.' + strain[9:11]
        with open(jobid + '.bsub', 'w') as bsub:
            bsub.write('#!/bin/bash\n'
                       '#BSUB -J ' + jobid + '\n'
                       '#BSUB -P acc_InfectiousDisease\n' +
                       '#BSUB -n 12\n' +
                       '#BSUB -rusage[mem=4000]\n' +
                       '#BSUB span[hosts=1]\n' +
                       '#BSUB -m "bode mothra"\n' +
                       '#BSUB -W "23:00"\n' +
                       '#BSUB -L /bin/bash\n' +
                       '#BSUB -q premium\n' +
                       'SMRT_JOB_ID=' + jobid + ' STRAIN_NAME=' + jobid + ' '


#BSUB -J raxml
#BSUB -P acc_InfectiousDisease
#BSUB -q premium
#BSUB -n 4
#BSUB -R rusage[mem=50000]
#BSUB -W 23:00
#BSUB -m manda
#BSUB -o %J.stdout
#BSUB -eo %J.stderr
#BSUB -L /bin/bash

')
    #     subprocess.Popen('''bsub -R 'rusage[mem=4000] span[hosts=1]' -m "bode mothra" -P acc_PBG -W "24:00" \
    #     -L /bin/bash -q premium -n 12 -J CD00246 \
    #     -o "%J.stdout" -eo "%J.stderr" \
    # post-assemble-pathogen \
    #     SMRT_JOB_ID=020486 \
    #     STRAIN_NAME=CD00246 \
    #     SPECIES=Cdiff \
    #     OUT=scratch/out/CD00246_020486 \
    #     prokka_annotate''')



run_new_jobs()