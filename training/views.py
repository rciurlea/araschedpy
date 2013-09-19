from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from training.models import Instructor, Student, Exercise, Sortie
from training.helpers import min_to_hr_min, enough_time, strip_leading_zero

def get_totals(student_code):
	''' not a view, but meh '''
	hrs_dual = Sortie.objects.filter(student__code = student_code, sortie_type = 'd').aggregate(Sum('duration'))['duration__sum']
	hrs_spic = Sortie.objects.filter(student__code = student_code, sortie_type = 'p').aggregate(Sum('duration'))['duration__sum']
	hrs_solo = Sortie.objects.filter(student__code = student_code, sortie_type = 's').aggregate(Sum('duration'))['duration__sum']
	hrs_total = Sortie.objects.filter(student__code = student_code).aggregate(Sum('duration'))['duration__sum']
	if hrs_dual: hrs_dual = int(hrs_dual)
	else: hrs_dual = 0
	if hrs_spic: hrs_spic = int(hrs_spic)
	else: hrs_spic = 0
	if hrs_solo: hrs_solo = int(hrs_solo)
	else: hrs_solo = 0
	if hrs_total: hrs_totals = int(hrs_total)
	else: hrs_total = 0
	totals = {}
	totals['dual'] = min_to_hr_min(hrs_dual)
	totals['pic'] = min_to_hr_min(hrs_spic + hrs_solo)
	totals['solo'] = min_to_hr_min(hrs_solo)
	totals['total'] = min_to_hr_min(hrs_total)
	return totals

def night_hours(student_code):
	''' fucking kludge, i swear '''
	hrs = Sortie.objects.filter(Q(student__code = student_code), Q(exercise__number = '28a' ) or Q(exercise__number = '28b')).aggregate(Sum('duration'))['duration__sum']
	if hrs: hrs = int(hrs)
	else: hrs = 0
	return min_to_hr_min(hrs)

@login_required
def index(request):
	''' Index page, instuctiuni de utilizare etc '''
	return render(request, 'training/index.html', {})

@login_required
def exercises(request, student_code):
	''' Iesirile fiecarui elev, pe exercitii '''
	ex_list = Exercise.objects.all()
	data = []
	for ex in ex_list:
		data.append({'exercise':ex})
	for d in data:
		dual = Sortie.objects.filter(exercise = d['exercise'], student__code = student_code, sortie_type = 'd').aggregate(Sum('duration'))['duration__sum']
		spic = Sortie.objects.filter(exercise = d['exercise'], student__code = student_code, sortie_type = 'p').aggregate(Sum('duration'))['duration__sum']
		solo = Sortie.objects.filter(exercise = d['exercise'], student__code = student_code, sortie_type = 's').aggregate(Sum('duration'))['duration__sum']
		d['dual'] = min_to_hr_min(dual)
		d['spic'] = min_to_hr_min(spic)
		d['solo'] = min_to_hr_min(solo)		
		d['dual_ok'] = enough_time(d['exercise'].duration * d['exercise'].sorties_dual, dual)
		d['spic_ok'] = enough_time(d['exercise'].duration * d['exercise'].sorties_spic, spic)
		d['solo_ok'] = enough_time(d['exercise'].duration * d['exercise'].sorties_solo, solo)
		d['sorties'] = Sortie.objects.filter(exercise = d['exercise'], student__code = student_code).reverse()
	students = Student.objects.all()
	return render(request, 'training/exercises.html', {'code': student_code,
													'students': students,
													'totals': get_totals(student_code),
													'data': data})

@login_required
def logbook(request, student_code):
	''' Logbook listing pentru fiecare elev '''
	students = Student.objects.all()
	sorties = Sortie.objects.filter(student__code = student_code).reverse()
	quality = {'Dual':'', 'SPIC':'SPIC', 'Solo':'PIC'}
	log_entries = []
	for s in sorties:
		if log_entries:
			if log_entries[-1]['date'] != s.date or log_entries[-1]['type'] != s.get_sortie_type_display() or log_entries[-1]['instructor'] != s.instructor.full_name.split()[1]:
				#insert new row
				log_entries.append({'date': s.date,
									'instructor':s.instructor.full_name.split()[1],
									'duration':s.duration,
									'helicopter': s.get_helicopter_display(),
									'exercise':strip_leading_zero(s.exercise.number),
									'type':s.get_sortie_type_display()})
			else:
				log_entries[-1]['duration'] += s.duration
				log_entries[-1]['exercise'] += ', ' + strip_leading_zero(s.exercise.number)
		else:
			log_entries.append({'date': s.date,
								'instructor':s.instructor.full_name.split()[1],
								'duration':s.duration,
								'helicopter': s.get_helicopter_display(),
								'exercise':strip_leading_zero(s.exercise.number),
								'type':s.get_sortie_type_display()})
	for entry in log_entries:
		entry['duration'] = min_to_hr_min(entry['duration'])
		if entry['type'] == 'SPIC' or entry['type'] == 'Solo':
			entry['exercise'] += ' (semnat de %s)' % (entry['instructor'],)
		if entry['type'] == 'Solo':
			entry['instructor'] = 'SELF'
		entry['type'] = quality[entry['type']]

	return render(request, 'training/logbook.html', {'code': student_code,
													'students': students,
													'logbook': log_entries,
													'totals': get_totals(student_code)})

@login_required
def statistics(request, student_code):
	''' Statistici mai mult sau mai putin utile pentru fiecare elev '''
	students = Student.objects.all()
	instructor_pie = Sortie.objects.filter(student__code = student_code).values('instructor__code').order_by('instructor__code').annotate(minutes=Sum('duration'))
	helicopter_pie = Sortie.objects.filter(student__code = student_code).values('helicopter').order_by('helicopter').annotate(minutes=Sum('duration'))
	for heli in helicopter_pie:
		heli['helicopter'] = 'MD' + heli['helicopter']
	return render(request, 'training/statistics.html', {'code': student_code,
													'students': students,
													'instructor_pie': instructor_pie,
													'helicopter_pie': helicopter_pie})

@login_required
def daily(request, student_code):
	''' Ore zburate zilnic de elev '''
	sorties = Sortie.objects.filter(student__code = student_code).values('date').annotate(minutes=Sum('duration')).reverse()
	for s in sorties:
		s['minutes'] = min_to_hr_min(s['minutes'])
	students = Student.objects.all()
	return render(request, 'training/daily.html', {'code': student_code,
													'students': students,
													'sorties': sorties,
													'totals': get_totals(student_code)})

@login_required
def students_view(request):
	students = Student.objects.all()
	student_data = []
	for s in students:
		student_data.append({'student':s, 'hours':get_totals(s.code), 'night': night_hours(s.code)})
	months = Sortie.objects.dates('date', 'month')
	monthly_totals = []
	for m in months:
		row = {}
		row['luna'] = m
		row['hours'] = []
		for s in students:
			row['hours'].append(min_to_hr_min(Sortie.objects.filter(date__month = m.month, student = s).aggregate(Sum('duration'))['duration__sum']))
		row['hours'].append(min_to_hr_min(Sortie.objects.filter(date__month = m.month).aggregate(Sum('duration'))['duration__sum']))
		monthly_totals.append(row)
	return render(request, 'training/students.html', {'students': students,
													'student_data': student_data,
													'time_flown':min_to_hr_min(Sortie.objects.all().aggregate(Sum('duration'))['duration__sum']),
													'monthly_totals': monthly_totals})

@login_required
def choppers_view(request):
	students = Student.objects.all()
	months = Sortie.objects.dates('date', 'month')
	monthly_totals = []
	for m in months:
		row = {}
		row['luna'] = m
		row['hours'] = []
		for heli in 'GI':
			row['hours'].append(min_to_hr_min(Sortie.objects.filter(date__month = m.month, helicopter = heli).aggregate(Sum('duration'))['duration__sum']))
		row['hours'].append(min_to_hr_min(Sortie.objects.filter(date__month = m.month).aggregate(Sum('duration'))['duration__sum']))
		monthly_totals.append(row)
	return render(request, 'training/choppers.html', {'students':students,
													'helicopters':('YR-MDG', 'YR-MDI'),
													'monthly_totals': monthly_totals})

@login_required
def instructors_view(request):
	students = Student.objects.all()
	months = Sortie.objects.dates('date', 'month')
	instructors = Instructor.objects.all()
	monthly_totals = []
	for m in months:
		row = {}
		row['luna'] = m
		row['hours'] = []
		for inst in instructors:
			row['hours'].append(min_to_hr_min(Sortie.objects.filter(date__month = m.month, instructor = inst).aggregate(Sum('duration'))['duration__sum']))
		monthly_totals.append(row)
	
	return render(request, 'training/instructors.html', {'students':students,
													'instructors':instructors,
													'monthly_totals': monthly_totals})



def login_view(request):
	''' self explanatory'''
	return render(request, 'training/login.html')


def logout_view(request):
	''' yeah, comment here'''
	logout(request)
	return redirect('index')

