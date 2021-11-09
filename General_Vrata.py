import JivaCalendar_FrontEnd as jcf
import JivaCalendar_Ecliptic as jce

from datetime import timedelta
from datetime import timezone as tmz

##### TO DOs----
# uncomment the adhika masa check

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

	for i,u in enumerate(utsava):
		utsava[i] = (u[0],jce.Masa_list.index(u[1]),u[2])
	
	all_vrata_days = {}
	for u in utsava:
		all_vrata_days[u[2]] = general_vrata(data,u[0],u[1],accuracy=accuracy,ayanamsa=ayanamsa,
											timezone_offset=timezone_offset)

	return all_vrata_days

def general_vrata(data,tithi,masa,accuracy=0.001,ayanamsa='citrapaksa',timezone_offset=None):
	# 
	def get_prev_tithi(tit_):
		tithi,masa = tit_
		if tithi>1:
			return (tithi-1,masa)
		else:
			prev_masa = masa-1 if masa>1 else 12
			return (30,prev_masa)

	def get_next_tithi(tit_):
		tithi,masa = tit_
		if tithi<30:
			return (tithi+1,masa)
		else:
			next_masa = masa+1 if masa<12 else 1
			return (1,next_masa)

	curr_ = (tithi,masa)
	prev_ = get_prev_tithi(curr_)
	prev2_ = get_prev_tithi(prev_)
	next_ = get_next_tithi(curr_)
	next2_ = get_next_tithi(next_)

	all_vrata_days = []
	for i,day in enumerate(data):
		if day['adhika_masa']:
			continue
		if i>len(data)-3:
			break
		day_seq = [data[i],data[i+1],data[i+2]]
		i_seq = [(d['tithi'],jce.Masa_list.index(d['masa'])) for d in day_seq]
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

		if scenario in [1,2,6]: 
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
		if scenario in [5,6]:
			parana_end = forenoon


		if timezone_offset is not None and scenario is not None:
			timezone = tmz(timedelta(hours=timezone_offset))
			parana_start = parana_start.astimezone(timezone)
			parana_end = parana_end.astimezone(timezone)

		if scenario is not None: 
			vrata_day = day_seq[1]
			all_vrata_days += [(vrata_day['gregorian_date'],parana_start,parana_end,scenario)]

	return all_vrata_days






# ----------------- REDO this code below in FrontEnd ----------------------------
def check_adhika_masa(data,accuracy=0.01,ayanamsa='citrapaksa'):
	dates_list = [d['gregorian_date'] for d in data]
	masa,t_s,t_e = jcf.get_masa_start_end_Ec(t=dates_list[0],get_end=True,accuracy=accuracy,ayanamsa=ayanamsa)
	start_times = [t_s]
	masa_list = [masa]
	prev_masa,t_s = jcf.get_masa_start_end_Ec(t=t_s-timedelta(days=1),get_end=False,accuracy=accuracy,ayanamsa=ayanamsa)
	start_times = [t_s] + start_times
	masa_list = [prev_masa] + masa_list
	
	while day_ in dates_list:
		day_ = t_e + timedelta(days=1)
		masa,t_s,t_e = jcf.get_masa_start_end_Ec(t=dates_list[0],get_end=True,accuracy=accuracy,ayanamsa=ayanamsa)
		masa_list += [masa]
		start_times += [t_s]
	next_masa,_,_ = jcf.get_masa_start_end_Ec(t=t_e+timedelta(days=1),get_end=False,accuracy=accuracy,ayanamsa=ayanamsa)
	masa_list += [next_masa]

	for i,m in enumerate(masa_list[0:-1]):
		if masa_list[i]==masa_list[i+1]:
			adhika_ = i


