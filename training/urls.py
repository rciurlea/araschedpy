from django.conf.urls import patterns, url

from training import views

urlpatterns = patterns('',
    url(r'^$', views.students_view, name='students'),
	url(r'^(?P<student_code>[A-Z]+)/exercises/$', views.exercises, name='exercises'),
	url(r'^(?P<student_code>[A-Z]+)/logbook/$', views.logbook, name='logbook'),
	url(r'^(?P<student_code>[A-Z]+)/statistics/$', views.statistics, name='statistics'),
	url(r'^(?P<student_code>[A-Z]+)/daily/$', views.daily, name='daily'),
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'training/login.html'}, name='login'),
	url(r'^logout$','django.contrib.auth.views.logout_then_login', name='logout'),
	url(r'students/$', views.students_view, name='students'),
	url(r'choppers/$', views.choppers_view, name='choppers'),
	url(r'instructors/$', views.instructors_view, name='instructors')
)