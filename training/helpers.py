def min_to_hr_min(minutes):
	if minutes is None:
		return '0:00'
	else:
		minutes = int(minutes)
		h = minutes / 60
		m = minutes % 60
		return "%d:%02d" % (h,m)

def enough_time(required, actual):
	if required == 0:
		return True
	else:
		if actual is None:
			return False
		else:
			return actual >= required

def strip_leading_zero(s):
	if s[0] == '0':
		return s[1:]
	else:
		return s
