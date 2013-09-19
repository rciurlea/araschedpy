from django.core.management import setup_environ
import ssavc.settings
setup_environ(ssavc.settings)
from django.db.models import Sum
from training.models import Instructor, Student, Exercise, Sortie
import datetime
import string
import codecs

def start_testing():
	logdata = {}
	print 'Analyzing SQL dump...'
	with codecs.open('training/elevi2.csv', 'r', 'utf-8-sig') as csvfile:
		for line in csvfile:
			fields = line.strip().split(',')
			fields = map(string.strip, fields)
			flight_date = datetime.datetime.strptime(fields[0], "%Y/%m/%d").date()
			instructor_code = fields[1]
			student_code = fields[2]
			duration = int(fields[3])
			if fields[4] == 'YR-MDI': registration = 'I'
			else: regisration = 'G'
			if student_code not in logdata:
				logdata[student_code] = []
			logdata[student_code].append({'date': flight_date, 'instructor': instructor_code, 'helicopter': registration, 'duration': duration})

	print 'Comparing with sortie database...'		
	for student,data in logdata.iteritems():
		total = 0
		for entry in data:
			total += entry['duration']

		hrs_total = Sortie.objects.filter(student__code = student).aggregate(Sum('duration'))['duration__sum']
		if hrs_total: hrs_totals = int(hrs_total)
		else: hrs_total = 0

		if total == hrs_total:
			print student + ' OK'
		else:
			print student + ' discrepancy'

if __name__=="__main__":
	start_testing()