import JivaCalendar_FrontEnd as jcf
import JivaCalendar_Ecliptic as jce

from datetime import timedelta
from datetime import timezone as tmz

#Skipping the vrata if the masa is adhika

##### TO DOs----
# uncomment the adhika masa check Update: I think this is complete

def calculate_vrata(data,accuracy=0.001,ayanamsa='citrapaksa',timezone_offset=None):
	# Need to filter adhika masa. Will do later
	# data is a list of days, where each day is a dict. Make sure a few days before and 
	# after are included

	if type(data[0])==list:
		# if the data is year_data, then it is a list of list. Here I flatten it.
		data = [d for sub_list in data for d in sub_list]

	with open('general_vrata.txt') as f:
		lines = [line.rstrip() for line in f]
	utsava = []
	for l in lines:
		utsava += [[eval(t) for t in l.split(',')]]

	all_vrata_days = {}
	for u in utsava:
		all_vrata_days[u[2]] = general_vrata(data,u[0],u[1],accuracy=accuracy,ayanamsa=ayanamsa,
											timezone_offset=timezone_offset)

	return all_vrata_days

def general_vrata(data,tithi,masa,accuracy=0.001,ayanamsa='citrapaksa',timezone_offset=None):
	# 
	def get_prev_tithi(tit_):
		return tit_-1 if tit_>1 else 30 

	def get_next_tithi(tit_):
		return tit_+1 if tit_<30 else 1

	curr_ = tithi # curr doesn't really mean the current date. It just means the one that we're looking for
	prev_ = get_prev_tithi(curr_)
	prev2_ = get_prev_tithi(prev_)
	next_ = get_next_tithi(curr_)
	next2_ = get_next_tithi(next_)

	all_vrata_days = []
	for i,day in enumerate(data):
		if day['adhika_masa']:
			continue
		if day['masa']!=masa:
			continue
		if i>len(data)-3:
			break
		day_seq = [data[i],data[i+1],data[i+2]]
		i_seq = [d['tithi'] for d in day_seq]

		# Missing Cases: Couldn't find any. Checked against rama navami in SpecialVratas.py
		vrata_day,scenario = None,None
		if i_seq==[prev_,curr_,next_]:
			scenario = 1
		if i_seq==[prev2_,curr_,next_]:
			scenario = 2
		if i_seq==[prev_,curr_,curr_]:
			scenario = 3
		if i_seq==[prev2_,curr_,curr_]:
			scenario = 4
		if i_seq==[prev_,next_,next_]:
			scenario = 5
		if i_seq==[prev_,next_,next2_]:
			scenario = 6
		if i_seq==[prev_,curr_,next2_]:
			scenario = 7

		if scenario in [1,2,6,7]: 
			parana_start = day_seq[2]['sunrise']
		if scenario in [3,4,5]: 
			_,t_e = jcf.get_tithi_start_end_Ec(t=day_seq[2]['sunrise'],accuracy=accuracy,get_start=False,which_tithi='current')
			parana_start = t_e

		sunrise, sunset = day_seq[2]['sunrise'], day_seq[2]['sunset']
		forenoon = sunrise + (sunset-sunrise)/3
		if scenario in [3,4]: # if tithi is vrddhi, then the next tithi can't end before forenoon
			parana_end = forenoon
		if scenario in [1,2]:
			_,t_e = jcf.get_tithi_start_end_Ec(t=day_seq[2]['sunrise'],accuracy=accuracy,get_start=False,which_tithi='current')
			parana_end = forenoon if t_e>forenoon else t_e
		if scenario in [5,6,7]:
			parana_end = forenoon


		if timezone_offset is not None and scenario is not None:
			timezone = tmz(timedelta(hours=timezone_offset))
			parana_start = parana_start.astimezone(timezone)
			parana_end = parana_end.astimezone(timezone)

		if scenario is not None: 
			vrata_day = day_seq[1]
			all_vrata_days += [(vrata_day['gregorian_date'],parana_start,parana_end,scenario)]

	return all_vrata_days









