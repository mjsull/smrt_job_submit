import re
import subprocess
import os
import sys
import urllib2
import _mysql

def get_jobs(pp_path):
	pattern = re.compile("^[A-Za-z]{2}_[0-9]{5}_[0-9][A-Za-z]")
	table = urllib2.urlopen("http://smrtportal.hpc.mssm.edu:8080/smrtportal/api/jobs/csv?options=%7B%22rows%22%3A5000%2C%22page%22%3A1%2C%22sortBy%22%3A%22jobId%22%2C%22sortOrder%22%3A%22desc%22%2C%22columnNames%22%3A%5B%22jobId%22%2C%22name%22%2C%22version%22%2C%22protocolName%22%2C%22referenceSequenceName%22%2C%22automated%22%2C%22whenStarted%22%2C%22createdBy%22%2C%22groupNames%22%2C%22jobStatus%22%2C%22comments%22%2C%22sampleName%22%2C%22instrumentName%22%2C%22inputCount%22%2C%22collectionProtocol%22%2C%22primaryProtocol%22%2C%22sequencingCondition%22%2C%22plateId%22%5D%7D&status=Completed%2CFailed%2CStopped")
	table.readline()
	to_submit = set()
	jobs_run = set()
	with open('data/jobs_run') as jr:
		for line in jr:
			jobs_run.add(line.rstrip())
	for line in table:
		automated, collectionProtocol, comments, createdBy, groupNames, inputCount, instrumentName, jobId, jobStatus, \
		name, plateId, primaryProtocol, protocolName ,referenceSequenceName, sampleName, sequencingCondition, version, \
		whenStarted = line.split('","')

		if jobStatus == 'Completed' and not pattern.match(name) is None and not jobId in jobs_run:
			to_submit.add((jobId, name))			
			
	path = os.path.expanduser('~') + '/.my.cnf'
	with open(path) as cnf_file:
		for line in cnf_file:
			if line.startswith('user='):
				user = line.rstrip()[5:]
			if line.startswith('password='):
				pw = line.rstrip()[9:]
			if line.startswith('host='):
				host = line.rstrip()[5:]
			if line.startswith('database='):
				database = line.rstrip()[9:]

	db = _mysql.connect(host=host,user=user,passwd=pw,db=database)
	to_q = []
	rejected = []
	for i in to_submit:
		with open('data/jobs_run', 'a') as jr:
			jr.write(i[0] + '\n')
			 
		smrtjob, sample = i
		
		smrtjob = smrtjob.zfill(6)
		sample = sample[:2] + sample[3:8] + '.' + sample[9:11]
		try:
			db.query("""select STOCK_ID from tExtracts where EXTRACT_ID='""" + sample + "'")
			val = db.store_result()
			stock_id = val.fetch_row()[0][0]
			db.query("select ISOLATE_ID from tStocks where STOCK_ID='" + stock_id + "'")
			val = db.store_result()
			isolate_id = val.fetch_row()[0][0]
			db.query("select ORGANISM_ID from tIsolates where ISOLATE_ID='" + isolate_id + "'")
			val = db.store_result()
			organism_id = val.fetch_row()[0][0]
			db.query("select abbreviated_name from tOrganisms where ORGANISM_ID='" + organism_id + "'")
			val = db.store_result()
			species = val.fetch_row()[0][0]
			if species == 'MRSA' or species == 'MSSA':
				species = 'S_aureus'
		except IndexError:
			rejected.append(i[1])
			with open('data/rejected', 'a') as rejects:
				rejects.write(smrtjob + ' : ' + sample + ' not in pathogendb.\n')
			continue
		sample = sample.replace('.', '_')
		if os.path.isdir('/sc/orga/projects/InfectiousDisease/post-assembly-output/' + sample + '_' + smrtjob):
			rejected.append(i[1])
			with open('data/rejected', 'a') as rejects:
				rejects.write(smrtjob + ' : ' + sample + ' already in post-assembly-output.\n')
			continue
        
		with open('bsubs/' + i[0] + '.bsub', 'w') as bsub:
			to_q.append(i[1])
			bsub.write('#!/bin/bash\n'
			'#BSUB -J ' + smrtjob + '\n'
			'#BSUB -P acc_InfectiousDisease\n'
			'#BSUB -q premium\n'
			'#BSUB -n 12\n'
			'#BSUB -R span[hosts=1]\n'
			'#BSUB -R rusage[mem=4000]\n'
			'#BSUB -W 23:00\n'			
			'#BSUB -o %J.stdout\n'
			'#BSUB -eo %J.stderr\n'
			'#BSUB -L /bin/bash\n'
			'cd ' + pp_path + '\n'
			'./post-assemble-pathogen  OUT=/sc/orga/projects/InfectiousDisease/post-assembly-output/' + sample + '_' + smrtjob +
			' SMRT_JOB_ID=' + smrtjob + ' STRAIN_NAME=' + sample + ' SPECIES=' + species + ' LSF_DISABLED=1 CLUSTER=BASH igb_to_pathogendb\n')
		subprocess.Popen('git add bsubs/' + i[0] + '.bsub', shell=True).wait()
		subprocess.Popen('bsub < ' + 'bsubs/' + i[0] + '.bsub', shell=True).wait()
	if len(to_q) + len(rejected) >= 1:
		subprocess.Popen('git commit -m "submitting ' + str(len(to_submit)) + ' jobs. ' + ', '.join(to_q) + ' : ' + str(len(rejected)) + ' jobs not submitted."', shell=True).wait()
		subprocess.Popen('git push origin master', shell=True).wait()

get_jobs(os.path.abspath(sys.argv[1]))
