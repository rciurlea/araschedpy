from django.contrib import admin
from training.models import Instructor, Student, Exercise, Sortie



class InstructorAdmin(admin.ModelAdmin):
	 list_display = ('code', 'full_name')
	 ordering = ['code']
admin.site.register(Instructor, InstructorAdmin)

class ExerciseAdmin(admin.ModelAdmin):
	 list_display = ('number', 'description', 'duration', 'sorties_dual', 'sorties_spic', 'sorties_solo','has_control')
	 ordering = ['number']
admin.site.register(Exercise, ExerciseAdmin)

class SortieAdmin(admin.ModelAdmin):
	 list_display = ('date', 'student', 'duration', 'exercise', 'sortie_type', 'helicopter', 'instructor', 'control')
	 ordering = ['-date']
	 list_filter = ['date', 'student', 'instructor', 'helicopter', 'control','exercise']
	 date_hierarchy = 'date'
admin.site.register(Sortie, SortieAdmin)

class SortieInline(admin.TabularInline):
	model = Sortie
	fields = ('date', 'student', 'duration', 'exercise', 'sortie_type', 'helicopter', 'instructor', 'control')
	extra = 1
	can_delete = False

class StudentAdmin(admin.ModelAdmin):
	 list_display = ('code', 'full_name')
	 ordering = ['code']
	 inlines = [SortieInline]
admin.site.register(Student, StudentAdmin)
