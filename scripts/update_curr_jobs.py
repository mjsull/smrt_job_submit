import urllib2
import re
import subprocess

def get_jobs():
    pattern = re.compile("^[A-Za-z]{2}_[0-9]{5}_[0-9][A-Za-z]")
    table = urllib2.urlopen("http://smrtportal.hpc.mssm.edu:8080/smrtportal/api/jobs/csv?options=%7B%22rows%22%3A5000%2C%22page%22%3A1%2C%22sortBy%22%3A%22jobId%22%2C%22sortOrder%22%3A%22desc%22%2C%22columnNames%22%3A%5B%22jobId%22%2C%22name%22%2C%22version%22%2C%22protocolName%22%2C%22referenceSequenceName%22%2C%22automated%22%2C%22whenStarted%22%2C%22createdBy%22%2C%22groupNames%22%2C%22jobStatus%22%2C%22comments%22%2C%22sampleName%22%2C%22instrumentName%22%2C%22inputCount%22%2C%22collectionProtocol%22%2C%22primaryProtocol%22%2C%22sequencingCondition%22%2C%22plateId%22%5D%7D&status=Completed%2CFailed%2CStopped")
    table.readline()
    to_submit = set()
    for line in table:
        automated, collectionProtocol, comments, createdBy, groupNames, inputCount, instrumentName, jobId, jobStatus, \
        name, plateId, primaryProtocol, protocolName ,referenceSequenceName, sampleName, sequencingCondition, version, \
        whenStarted = line.split('","')
        if jobStatus == 'Completed' and not pattern.match(name) is None:
            to_submit.add((jobId, name))
            print name
    to_q = []
    rejected = []
    for i in to_submit:

        with open('data/jobs_run', 'a') as jobs_run:
            jobs_run.write(i[0] + '\n')
        with open('bubs/' + i[0] + '.bsub') as bsub:
            to_q.append(i[1])
            bsub.write('test')
            subprocess.Popen('git add ' + 'bsubs/' + i[0] + '.bsub', shell=True).wait()
    if len(to_q) + len(rejected) >= 1:
        subprocess.Popen('git commit -m "submitting ' + str(len(to_submit)) + ' jobs. ' + ', '.join(to_q) + ' : ' + str(len(rejected)) + ' jobs not submitted.')
        subprocess.Popen('git push origin master')



get_jobs()