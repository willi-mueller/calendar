
import JivaCalendar_FrontEnd as jcf
from datetime import timedelta

def get_parana_times(vrata_day,next_day,scenario_num,nak_yog_scenario):
	# The vrata_day and next_day are not gragorian dates. They are the full dict containing tithi, sunrise etc.
	print(vrata_day['gregorian_date'],scenario_num)
	return standard(vrata_day,next_day,method='common_sense')


def standard(vrata_day,next_day,accuracy=0.01,method='common_sense'):
	# The vrata_day and next_day are not gragorian dates. They are the full dict containing tithi, sunrise etc.
	# method can be 'common_sense' or 'tika'. Refer to Kamal Tyagi Maharaj's document part 1 section 2.2
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, ddsi_start, ddsi_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
												get_start=True) # dvadasi start & end times
	tit = pt(tit)
	if tit!=12:
		print("WARNING! Using standard pāraṇa calculation but tithi next day is not dvādaśī. Tithi is",tit)
		print("with start,end:",ddsi_start,ddsi_end)
	if method=='tika':
		span = ddsi_end - sunrise # Span of dvādaśī on the day it rules
		if span>timedelta(hours=18):
			parana_start = sunrise + span - timedelta(hours=18)
		else:
			parana_start = sunrise
	if method=='common_sense':
		quarter_tithi = (ddsi_end - ddsi_start)/4
		end_of_quarter = ddsi_start + quarter_tithi
		if end_of_quarter>sunrise:
			parana_start = end_of_quarter
		else:
			parana_start = sunrise
	if method not in ['common_sense','tika']:
		raise ValueError("ErROR! choose method from 'common_sense' or 'tika'")

	# parana_end calculation begins here
	forenoon = sunrise + (sunset-sunrise)/3
	if ddsi_end>forenoon:
		parana_end = forenoon
	else:
		parana_end = ddsi_end

	# Below we acccount for the case where parana_end<parana_start
	if parana_end<parana_start:
		parana_end = sunset

	return parana_start,parana_end


def alternate(vrata_day,next_day,accuracy=0.01):
	# The vrata_day and next_day are not gragorian dates. They are the full dict containing tithi, sunrise etc.
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, next_start, next_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
												get_start=True) # next day's tithi's start & end times
	tit = pt(tit)
	if tit==12: # i.e. if dvādaśī hasn't ended before sunrise next morning
		parana_start = next_end 
	else:
		if tit!=13: print("WARNING! USing alternate pāraṇa calculation but tithi at sunrise next morning is neither 12 nor 13. Tithi is", tit)
		parana_start = sunrise

	forenoon = sunrise + (sunset-sunrise)/3
	if tit==13:
		tdsi_end = next_end # if next morning's tithi is trayodaśī, then we already have the data
		if tdsi_end>forenoon:
			parana_end = forenoon
		else:
			parana_end = tdsi_end
	else: # if 13th starts after sunrise, there's no way it is ending before forenoon
		parana_end = forenoon

	return parana_start, parana_end



def vanjuli():
	# The vrata_day and next_day are not gragorian dates. They are the full dict containing tithi, sunrise etc.
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, ddsi_start, ddsi_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
												get_start=True) # next day's tithi's start & end times
	parana_start = sunrise

	forenoon = sunrise + (sunset-sunrise)/3
	if tit!=12:
		print("WARNING! Using vañjulī pāraṇa calculation but tithi at sunrise next morning is not 12. Tithi is", tit)
	if forenoon<ddsi_end:
		parana_end = forenoon
	else:
		parana_end = ddsi_end

	return parana_start, parana_end

def jayanti_vijaya():
	return parana_start, parana_end

def jaya_papa_nasini():
	return parana_start, parana_end

# -----------------------------------------tools--------------------------------------------
def pt(tithi):
	# Converts tithis from 1 to 30 into pakṣa-tithis from 1 to 15. 
	# pt stands for pakṣa-tithi
	return ((tithi-1)%15)+1

