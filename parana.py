
import JivaCalendar_FrontEnd as jcf
from datetime import timedelta

['jyt','jya','ppn','vjy']

def get_parana_times(vrata_day,next_day,scenario_num,nak_yoga_scenario,accuracy=0.001,method='common_sense'):
	# The vrata_day and next_day are not gragorian dates. They are the full dict containing tithi, sunrise etc.
	choice = None

	if scenario_num in ['hvv1','hvv3','hvv4'] and nak_yoga_scenario is None:
		choice = 'std'
	if scenario_num in ['hvv2','hvv5','hvv6','hvv7'] and nak_yoga_scenario is None:
		choice = 'alt'
	if scenario_num in ['unm1','tsp1','tsp2','pvm1'] and nak_yoga_scenario is None:
		choice = 'alt'
	if scenario_num in ['vnj1'] and nak_yoga_scenario is None:
		choice = 'vnj'
	if scenario_num[0:3]=='hvv' and nak_yoga_scenario in ['jyt1','vjy1','jyt2','vjy2']:  # Jayanti and Vijaya
		choice = 'jv' 
	if scenario_num[0:3]=='hvv' and nak_yoga_scenario in ['jya1','ppn1','jya2','ppn2']:  # Jaya and Papa-nasini
		choice = 'jpn' 
	if scenario_num in ['upv1','tpv1'] and nak_yoga_scenario is None:
		choice = 'alt'
	if scenario_num is 'vpv1' and nak_yoga_scenario is None:
		choice = 'vnj'
	if scenario_num is 'vnj1' and nak_yoga_scenario in ['jyt1','vjy1','jyt2','vjy2']:
		choice = 'jv' 
	if scenario_num is 'vnj1' and nak_yoga_scenario in ['jya1','ppn1','jya2','ppn2']:
		choice = 'jpn' 
	if scenario_num is 'pvm1' and nak_yoga_scenario in ['jyt1','vjy1','jyt2','vjy2']:
		choice = 'jv' 
	if scenario_num is 'pvm1' and nak_yoga_scenario in ['jya1','ppn1','jya2','ppn2']:
		choice = 'jpn' 
	if scenario_num is 'vpv1' and nak_yoga_scenario in ['jyt1','vjy1','jyt2','vjy2']:
		choice = 'jv' 
	if scenario_num is 'vpv1' and nak_yoga_scenario in ['jya1','ppn1','jya2','ppn2']:
		choice = 'jpn' 

	if choice=='std':
		return standard(vrata_day,next_day,method=method,accuracy=accuracy)
	if choice=='alt':
		return alternate(vrata_day,next_day,accuracy=accuracy)
	if choice=='vnj':
		return vanjuli(vrata_day,next_day,accuracy=accuracy)
	if choice=='jv':
		return jayanti_vijaya(vrata_day,next_day,accuracy=accuracy)
	if choice=='jpn':
		return jaya_papa_nasini(vrata_day,next_day,accuracy=accuracy)
	if choice==None:
		raise ValueError(f"No pāraṇa scenario fits the vrata. Vrata Scenario is {scenario_num} and nakṣatra yoga {nak_yoga_scenario}")



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
	if vrata_day["tithi"]<15: 
		trayodasi = 13
	else:
		trayodasi = 28
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, ddsi_end, tdsi_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
												which_tithi=trayodasi,find='nearest',get_start=True) # dvādaśī ends when trayodaśī starts
	tit = pt(tit)

	if ddsi_end<sunrise:
		parana_start = sunrise
	else:
		parana_start = ddsi_end

	forenoon = sunrise + (sunset-sunrise)/3

	if tdsi_end>forenoon:
		parana_end = forenoon
	else:
		parana_end = tdsi_end

	return parana_start, parana_end


def vanjuli(vrata_day,next_day,accuracy=0.01):
	# The vrata_day and next_day are not gragorian dates. They are the full dict containing tithi, sunrise etc.
	if vrata_day["tithi"]<15: 
		dvadasi = 12
	else:
		dvadasi = 27
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, ddsi_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
												get_start=False,which_tithi=dvadasi,find='nearest') # dvādaśī's start & end times
	tit = pt(tit)

	parana_start = sunrise

	forenoon = sunrise + (sunset-sunrise)/3

	if forenoon<ddsi_end:
		parana_end = forenoon
	else:
		parana_end = ddsi_end

	return parana_start, parana_end

def jayanti_vijaya(vrata_day,next_day,accuracy=0.01):
	if vrata_day["tithi"]<15: 
		dvadasi = 12
	else:
		dvadasi = 27
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, ddsi_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
										get_start=False,which_tithi=dvadasi,find='nearest') # dvādaśī's start & end times

	nak_end_r, nak_num_r = jcf.get_sankramana_time_Ec(t=sunrise,body='moon',accuracy=accuracy,
										find='nearest',which_nak=3,start_end='end') # Loading Rohini end time
	nak_end_s, nak_num_s = jcf.get_sankramana_time_Ec(t=sunrise,body='moon',accuracy=accuracy,
										find='nearest',which_nak=21,start_end='end') # Loading Sravana end time

	# Below we decide which Naksatra it is, Rohini or Sravana
	if abs(nak_end_r-sunrise)>abs(nak_end_s-sunrise): 
		nak_end = nak_end_s
		nak_num = nak_num_s # which has the value 21
	else:
		nak_end = nak_end_r
		nak_num = nak_num_r # which has the value 3

	forenoon = sunrise + (sunset-sunrise)/3

	# Scenario 1
	if nak_end<sunrise and ddsi_end<sunrise: 
		parana_start = sunrise
		parana_end = forenoon

	# Scenario 2
	if nak_end<sunrise and ddsi_end>sunrise: 
		parana_start = sunrise
		parana_end = ddsi_end

	# Scenario 3
	if nak_end>sunrise and ddsi_end<sunrise: 
		parana_start = sunrise
		if nak_end<forenoon: parana_end = nak_end
		else: parana_end = forenoon

	# Scenario 4
	if nak_end>ddsi_end and ddsi_end>sunrise: 
		parana_start = sunrise
		if ddsi_end<forenoon: parana_end = ddsi_end
		else: parana_end = forenoon

	# Scenario 5
	if nak_end>sunrise and nak_end<ddsi_end: 
		parana_start = nak_end
		if ddsi_end<forenoon: parana_end = ddsi_end
		else: parana_end = forenoon

	return parana_start, parana_end

def jaya_papa_nasini(vrata_day,next_day,accuracy=0.01):
	if vrata_day["tithi"]<15: 
		dvadasi = 12
	else:
		dvadasi = 27
	sunrise, sunset = next_day["sunrise"], next_day['sunset']
	tit, ddsi_end = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,
										get_start=False,which_tithi=dvadasi,find='nearest') # dvādaśī's start & end times

	nak_end_1, nak_num_1 = jcf.get_sankramana_time_Ec(t=sunrise,body='moon',accuracy=accuracy,
										find='nearest',which_nak=6,start_end='end') # Loading Punaravasu end time
	nak_end_2, nak_num_2 = jcf.get_sankramana_time_Ec(t=sunrise,body='moon',accuracy=accuracy,
										find='nearest',which_nak=7,start_end='end') # Loading Puṣyā end time

	# Below we decide which Naksatra it is, Rohini or Sravana
	if abs(nak_end_1-sunrise)>abs(nak_end_2-sunrise): 
		nak_end = nak_end_2
		nak_num = nak_num_2 # which has the value 21
	else:
		nak_end = nak_end_1
		nak_num = nak_num_1 # which has the value 3

	forenoon = sunrise + (sunset-sunrise)/3

	# Scenario 1
	if nak_end<sunrise and ddsi_end<sunrise: 
		parana_start = sunrise
		parana_end = forenoon

	# Scenario 2
	if nak_end<sunrise and ddsi_end>sunrise: 
		parana_start = sunrise
		parana_end = ddsi_end

	# Scenario 3
	if nak_end>sunrise and ddsi_end<sunrise: 
		parana_start = nak_end
		if nak_end<forenoon: parana_end = forenoon
		else: parana_end = sunset

	# Scenario 4
	if nak_end>ddsi_end and ddsi_end>sunrise: 
		parana_start = sunrise
		if ddsi_end<forenoon: parana_end = ddsi_end
		else: parana_end = forenoon

	# Scenario 5
	if nak_end>sunrise and nak_end<ddsi_end: 
		parana_start = nak_end
		if ddsi_end<forenoon: parana_end = ddsi_end
		else: parana_end = forenoon

	return parana_start, parana_end

# -----------------------------------------tools--------------------------------------------
def pt(tithi):
	# Converts tithis from 1 to 30 into pakṣa-tithis from 1 to 15. 
	# pt stands for pakṣa-tithi
	return ((tithi-1)%15)+1

