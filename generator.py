from django.core.management import setup_environ
import ssavc.settings
setup_environ(ssavc.settings)
from training.models import Instructor, Student, Exercise, Sortie
import datetime
import string
import codecs

# algoritm:
# time left = duration
# while time left > 0:
# 	get first exercise which still has dual time in sequence 1,2,4
# 	compute sortie time: min(time_left, dual time left)
# 	add the sortie
# 	decrease time left by added duration
#   if no exercises have dual time left:
# 	get first exercise which still has SPIC time in sequence 2,4
# 	compute sortie time: min(time_left, dual time left)
# 	add the sortie
# 	decrease time left by added duration

def add_flight(date, student, instructor, registration, duration):
	print "- addflight %s, %s, %s, %s, %d" % (date, student, instructor, registration, duration)
	time_left = duration
	while time_left > 0:
		print "in while loop"
		inserted = False
		for ex in Exercise.objects.filter(sequence__in =(1,2,4)):
			if student.dualRemaining(ex) > 0:
				print "    exercise %s time left: %d, dual remaining: %d" % (ex.number, time_left, student.dualRemaining(ex),)
				if ex.sequence == 1:
					sortie_time = min(time_left, student.dualRemaining(ex))
				else:
					if time_left > student.dualRemaining(ex):
						if time_left - student.dualRemaining(ex) > 15:
							sortie_time = student.dualRemaining(ex)
						else:
							sortie_time = time_left
					else:
						sortie_time = time_left
				print "insert time: ", sortie_time		
				s = Sortie(date = date, 
					instructor = instructor, 
					student = student,
					duration = sortie_time,
					exercise = ex,
					helicopter = registration,
					sortie_type = 'd')
				s.save()
				inserted = True
				time_left -= sortie_time
				print "    %d minutes left" % (time_left,)
				break
		if not inserted:
			for ex in Exercise.objects.filter(sequence__in =(2,4)):
				if student.spicRemaining(ex) > 0:
					print "    exercise %s time left: %d, spic remaining: %d" % (ex.number, time_left, student.spicRemaining(ex),)
					if time_left > student.spicRemaining(ex):
						if time_left - student.spicRemaining(ex) > 15:
							sortie_time = student.spicRemaining(ex)
						else:
							sortie_time = time_left
					else:
						sortie_time = time_left
					print "insert time: ", sortie_time		
					s = Sortie(date = date, 
						instructor = instructor, 
						student = student,
						duration = sortie_time,
						exercise = ex,
						helicopter = registration,
						sortie_type = 'p')
					s.save()
					time_left -= sortie_time
					print "    %d minutes left" % (time_left,)
					break

def populate_database_from_file():
	# clean shit up
	Sortie.objects.all().delete()
	# solo trick
	ex12 = Exercise.objects.get(number='12')
	ex12.sorties_dual = 3
	ex12.save()

	with codecs.open('training/elevi2.csv', 'r', 'utf-8-sig') as csvfile:
		for line in csvfile:
			fields = line.strip().split(',')
			fields = map(string.strip, fields)
			flight_date = datetime.datetime.strptime(fields[0], "%Y/%m/%d").date()
			instructor_code = fields[1]
			student_code = fields[2]
			duration = int(fields[3])
			if fields[4] == 'YR-MDI': registration = 'I'
			else: registration = 'G'
			add_flight(flight_date,
				student = Student.objects.get(code = student_code),
				instructor = Instructor.objects.get(code = instructor_code),
				registration = registration,
				duration = duration)
	# undo solo trick
	ex12 = Exercise.objects.get(number='12')
	ex12.sorties_dual = 0
	ex12.save()
	# set ex12 sorties to solo
	for s in Sortie.objects.filter(exercise__number='12'):
		s.sortie_type = 's'
		s.save()

if __name__=="__main__":
	populate_database_from_file()