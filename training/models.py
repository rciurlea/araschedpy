from django.db import models
from django.db.models import Sum
from training.helpers import min_to_hr_min

class Instructor(models.Model):
	code = models.CharField(max_length = 3)
	full_name = models.CharField(max_length = 50)
	def __unicode__(self):
		return self.code
	class Meta:
		ordering = ['code']

class Student(models.Model):
	code = models.CharField(max_length = 3)
	full_name = models.CharField(max_length = 50)
	def __unicode__(self):
		return self.code
	def dualRemaining(self, exercise):
		flown = Sortie.objects.filter(student = self, exercise = exercise, sortie_type = 'd').aggregate(Sum('duration'))['duration__sum']
		if flown != None: flown = int(flown)
		else: flown = 0
		return exercise.duration * exercise.sorties_dual - flown
	def spicRemaining(self, exercise):
		flown = Sortie.objects.filter(student = self, exercise = exercise, sortie_type = 'p').aggregate(Sum('duration'))['duration__sum']
		if flown != None: flown = int(flown)
		else: flown = 0
		return exercise.duration * exercise.sorties_spic - flown
	def soloRemaining(self, exercise):
		flown = Sortie.objects.filter(student = self, exercise = exercise, sortie_type = 's').aggregate(Sum('duration'))['duration__sum']
		if flown != None: flown = int(flown)
		else: flown = 0
		return exercise.duration * exercise.sorties_solo - flown
	class Meta:
		ordering = ['code']

class Exercise(models.Model):
	number = models.CharField(max_length = 10)
	description = models.CharField(max_length = 200)
	duration = models.IntegerField(default = 30)
	sorties_dual = models.IntegerField(default = 0)
	sorties_spic = models.IntegerField(default = 0)
	sorties_solo = models.IntegerField(default = 0)
	has_control = models.BooleanField(default = False)
	sequence = models.IntegerField(default = 0)
	def dual(self):
		return min_to_hr_min(self.duration * self.sorties_dual)
	def spic(self):
		return min_to_hr_min(self.duration * self.sorties_spic)
	def solo(self):
		return min_to_hr_min(self.duration * self.sorties_solo)
	def duration_pretty(self):
		return min_to_hr_min(self.duration)
	def __unicode__(self):
		return self.number
	class Meta:
		ordering = ['number']

class Sortie(models.Model):
	SORTIE_TYPES = (
		('d', 'Dual'),
		('p', 'SPIC'),
		('s', 'Solo')
	)
	HELICOPTER_CHOICES = (
		('G', 'YR-MDG'),
		('I', 'YR-MDI')
	)
	date = models.DateField()
	instructor = models.ForeignKey(Instructor)
	student = models.ForeignKey(Student)
	duration = models.IntegerField('Duration (minutes)')
	exercise = models.ForeignKey(Exercise)
	helicopter = models.CharField(max_length = 1, choices = HELICOPTER_CHOICES, default = 'G')
	sortie_type = models.CharField(max_length = 1, choices = SORTIE_TYPES, default = 'd')
	control = models.BooleanField(default = False)
	def __unicode__(self):
		return str(self.date)
	def duration_pretty(self):
		return min_to_hr_min(self.duration)
	def getMonth(self):
		return self.date.month
	class Meta:
		ordering = ['-date']

