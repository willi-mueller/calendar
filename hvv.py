import JivaCalendar_FrontEnd as jcf
import JivaCalendar_Ecliptic as jce
import parana as pn
from datetime import timedelta
from datetime import timezone as tmz

class HBV:
	def __init__(self, curr_month, next_month, mata='tithi-mana',yama_mata='flexible',
				ayanamsa='citrapaksa',parana_method='common_sense'):
		self.curr_month = curr_month
		self.next_month = next_month
		self.mata = mata
		self.yama_mata = yama_mata
		self.ayanamsa = ayanamsa
		self.parana_method = parana_method

	#def head(month, month_next, month_prev):

	def HVV_test(self,accuracy=0.001): 
		def create_string(tit_seq,vrata_day):
			info_str_1 = f"tithi sequence is {tit_seq}. The sequence is "
			info_str_2 = f"(day1_tithi,day2_dawn_tithi,day2_tithi,day3_tithi,day4_tithi,day5_tithi,day6_tithi, " 
			info_str_3 = f"day7_tithi,day8_tithi,day9_tithi). Out of these, the vrata date is day {vrata_day}"
			return info_str_1 + info_str_2 + info_str_3
		def get_day(vrata_day,i,which_day):
			# if vrata is, for instance, 'day 2', then this method can return the day dict for that day or the next day
			if which_day=='vrata': factor = 0
			if which_day=='next': factor = 1
			index = i+vrata_day-1+factor # This is the required day index.
				# If index is within the month then great, else look for in next_month
			if index<len(self.curr_month):
				return self.curr_month[index]
			else:
				return self.next_month[index-len(self.curr_month)]

		# HVV stands for Hari-vāsara-vrata AKA ekādaśī
		month_vrata_list = []
		for i,day in enumerate(self.curr_month):

			if pt(day["tithi"]) in [9,10]:
				list_of_days = self.return_following_days(i) # i.e. the given day is day 2 in the list
				[day_1,day_2,day_3,day_4,day_5,day_6,day_7,day_8,day_9] = list_of_days
				vrata_day, scenario_num, tit_seq = vrata_scenario_check_1p1(day_1,day_2,day_3,day_4)
				if vrata_day is not None:
					vrata_day, scenario_num, tit_seq = vrata_scenario_check_1p2(list_of_days,vrata_day,scenario_num,tit_seq)
					naksatra_yoga,vrata_day = naksatra_yoga_check(list_of_days,vrata_day,accuracy=accuracy,
													ayanamsa=self.ayanamsa,mata=self.mata,yama_mata=self.yama_mata)
					parana_start,parana_end = pn.get_parana_times(get_day(vrata_day,i,'vrata'),get_day(vrata_day,i,'next'),
															scenario_num,naksatra_yoga,accuracy=accuracy,method=self.parana_method)
					vrata_date = list_of_days[vrata_day-1]["gregorian_date"]
					month_vrata_list += [{"date":vrata_date,"type":scenario_num,"naksatra yoga":naksatra_yoga,
									"info":create_string(tit_seq,vrata_day),"parana":(parana_start,parana_end)}]

		return month_vrata_list
				
	def return_following_days(self,day_number):
		# day_number is the index number in the list curr_month, i.e. it starts from 0, not 1
		total_days = len(self.curr_month)
		if total_days>day_number+8:
			list_of_days = self.curr_month[day_number:day_number+9]
			return list_of_days
		else:
			list_of_days = self.curr_month[day_number:]
			list_of_days += self.next_month[0:day_number+9-total_days]
			return list_of_days

def vrata_scenario_check_1p1(day_1,day_2,day_3,day_4,dawn_duration=96):
	# The tit_seq (tithi sequence) being returned is (day1,day2_dawn,day2,day3,day4).
	# Here "day1" means the tithi at sunrise of day1 etc.
	# The return is vrata_day, scenario_num, tithi_sequence. 
	# scenario_num is according to Kamala Tyagi Maharaj's document.
	tit1,tit2,tit3,tit4 = day_1["tithi"],day_2["tithi"],day_3["tithi"],day_4["tithi"]
	_, titd, _, _ = jcf.get_dawn_info(sunrise=day_2["sunrise"],dawn_duration=dawn_duration)

	tit_seq = (pt(tit1),pt(titd),pt(tit2),pt(tit3),pt(tit4)) 
	# Technically %15 is wrong, since 15 and 30 are mapped to 0. 
	# Correct is (tithi-1)%15+1 

	if tit_seq in [(9,11,11,12,13),(10,11,11,12,13),(9,11,11,12,14),(10,11,11,12,14)]:
		return 2, "hvv1", tit_seq
	if tit_seq in [(9,10,11,12,13),(10,10,11,12,13),(9,10,11,12,14),(10,10,11,12,14)]:
		return 3, "hvv2", tit_seq
	if tit_seq in [(9,10,11,11,12),(10,10,11,11,12)]:
		return 3, "hvv3", tit_seq
	if tit_seq in [(9,11,11,11,12),(10,11,11,11,12)]:
		return 3, "hvv4", tit_seq
	if tit_seq in [(9,10,11,12,12),(10,10,11,12,12)]:
		return 3, "hvv5", tit_seq
	if (tit_seq[0],tit_seq[2],tit_seq[3]) == (10,12,13):
		return 2, "hvv6", tit_seq
	if (tit_seq[0],tit_seq[2],tit_seq[3]) == (10,12,12):
		return 2, "hvv7", tit_seq

	if tit_seq == (10,11,11,11,13):
		return 3, "unm1", tit_seq # Unmīlanī Mahādvādaśī
	if (tit_seq[0],tit_seq[1],tit_seq[2],tit_seq[3]) == (10,11,11,13):
		return 2, "tsp1", tit_seq # Trispṛśā Mahādvādaśī 1
	if tit_seq == (10,10,11,11,13):
		return 3, "tsp2", tit_seq # Trispṛśā Mahādvādaśī 2
	if tit_seq == (10,11,11,12,12):
		return 3, "vnj1", tit_seq # Vāñjulī Mahādvādaśī 1

	return None,None,None


def vrata_scenario_check_1p2(l,vrata_day,scenario_num,tit_seq): 
	# l is the tuple containing (day_1...day_9)
	# Yes, there is redundant info since tit_seq has the first 4 tithis, but whatever.
	# Can't get rid of tit_seq because it has day_2 dawn info too.
	# for definitions of vradat_day, scenario_num, tit_seq check the comments in the function vrata_scenario_check_1p1
	# Notes: the list tit_seq = (day1,day2_dawn,day2,day3,day4), thus day2 onwards the index is the same as day number.
	day_1,day_2,day_3,day_4,day_5,day_6,day_7,day_8,day_9 = l
	tithis = [d["tithi"] for d in l]
	tit_seq_full = [t for t in tit_seq] + list(map(pt,tithis[4:])) # This is only for returning. Had to convert  
													 # tit_seq to list since tuples can't be concatenated with list
	paksa_end_tithis = [d for d in tithis if d==15 or d==30]
	if len(paksa_end_tithis)==0:
		print('\n',"WARNING! There's no paksa end within the 9 following days from day1")
		print("This could be harmless, because a tithi can be missing.")
		print("Warning info:")
		print("		day_1 date:",day_1['gregorian_date'])
		print("		tithi sequence:",tithis)
	if len(paksa_end_tithis) in [0,1]:
		return vrata_day,scenario_num,tit_seq_full
	if len(paksa_end_tithis)==2:
		if scenario_num[0:3]=='hvv' and tit_seq[vrata_day]==11:
			vrata_day = tit_seq[2:].index(12)+2 # This selects the first occurence of dvadasi, if dvadasi rules 2 days
			scenario_num = "pvm1" # pv stands for pakśa-vardhinī 
			return vrata_day, scenario_num, tit_seq_full
		if scenario_num[0:3] in ['unm','tsp','vnj']:
			scenario_num = scenario_num[0] + "pv1" # i.e. upv1, tpv1 or vpv1. "pv" stands for pakśa-vardhini
			return vrata_day,scenario_num, tit_seq_full


# Rohini = 3
# Sravana = 21
# Punaravasu = 6
# Pusya = 7
def naksatra_yoga_check(list_of_days,vrata_day,accuracy=0.001,ayanamsa='citrapaksa',
					mata='tithi-mana',yama_mata='flexible'):
	if mata not in ['suryodaya','dina-mana','tithi-mana']:
		raise ValueError("Choose mata from 'suryodaya','dina-mana','tithi-mana'")

	day_1 = None
	for i,d in enumerate(list_of_days):
		if d["tithi"]==12:
			day_1 = d
			day_2 = list_of_days[i+1]
			day_1_num = i # Since list_of_days=[day1,day2_dawn,day2,day3...], so day2 onwards the index is same as day number
			break
	if day_1 == None:
		# i.e. if not in sukla paksa
		return None,vrata_day

	sunrise1, sunset1 = day_1["sunrise"], day_1['sunset']
	sunrise2, sunset2 = day_2["sunrise"], day_2['sunset']
	ms_ang1,tit1,m_ang1,s_ang1 = jcf.get_angle_tithi_Ec(t=sunrise1)
	nak_sunrise1 = jce.find_naksatra_Ec(m_ang1,ayanamsa=ayanamsa)[0]
	nak_lons = jce.naksatra_lon_Ec(ayanamsa=ayanamsa,unit='degree')

	# if naksatra is not rohini, pusya, punaravasu or sravana, then no chance of naksatra yoga
	if nak_sunrise1 not in [3,6,7,21]:
		return None,vrata_day

	def get_yama():
		# Include various opinions about how much is a yama. This function return 1.5 yamas (not 1 yama)
		if yama_mata not in ['fixed','flexible']:
			raise ValueError("Choose yama_mata from 'fixed','flexible'")
		if yama_mata=='fixed':
			return timedelta(hours=4.5)
		if yama_mata=='flexible':
			return 3/8*(sunset1-sunrise1)

	dvadasi_test = False
		# For Rohini, Pusya, Punaravasu, the end time is sunset, while for Sravana it is 1.5 yamas after sunrise
	if nak_sunrise1 in [3,6,7]:
		end_time = sunset1
	if nak_sunrise1==21:
		end_time = sunrise1 + get_yama()
	_,tit_at_end_time,_,_ = jcf.get_angle_tithi_Ec(t=end_time)
	if tit_at_end_time==12:
		dvadasi_test = True
	# if dvadasi doesnt last until end time, then no naksatra yoga can occur. See above for end_time calculation
	if not dvadasi_test:
		return None,vrata_day

	# Now the basic tests are over. We can now proceed to detaile tests

	start_at_sunrise = False
	for i in [3,6,7,21]:
		# The moon covers about 0.0091 degrees in a minute (27.5 days for 360 degrees). Thus, 0.01 degree is about a minute of time
		if abs(m_ang1-nak_lons[i])<0.01:
			start_at_sunrise = True

	dvadasi_names = ['jyt','jya','ppn','vjy'] # Jayantī, Jayā, Pāpa-nāśinī, Sravana

	if mata == 'suryodaya':
		for i,nak_ in enumerate([3,6,7,21]):
			if nak_sunrise1==nak_: # Rohiṇī
				if start_at_sunrise:
					return dvadasi_names[i]+'1', day_1_num
				ms_ang2,tit2,m_ang2,s_ang2 = jcf.get_angle_tithi_Ec(t=sunrise2)
				nak_sunrise2 = jce.find_naksatra_Ec(m_ang2,ayanamsa=ayanamsa)[0]
				if nak_sunrise2==nak_:
					return dvadasi_names[i]+'2', day_1_num
		return None, vrata_day
	if mata == 'dina-mana':
		for i,nak_ in enumerate([3,6,7,21]):
			if nak_sunrise1==nak_: # Rohiṇī
				if start_at_sunrise:
					return dvadasi_names[i]+'1', day_1_num
				nak_start = jcf.get_sankramana_time_Ec(t=sunrise1,body='moon',accuracy=accuracy,ayanamsa=ayanamsa,
								which_nak='current',start_end='start')[0]
				nak_end = jcf.get_sankramana_time_Ec(t=sunrise1,body='moon',accuracy=accuracy,ayanamsa=ayanamsa,
								which_nak='current',start_end='end')[0]
				if (nak_end-nak_start)>=timedelta(hours=24):
					return dvadasi_names[i]+'2', day_1_num
		return None, vrata_day
	if mata == 'tithi-mana':
		for i,nak_ in enumerate([3,6,7,21]):
			if nak_sunrise1==nak_: # Rohiṇī
				if start_at_sunrise:
					return dvadasi_names[i]+'1', day_1_num
				ms_ang1,tit1,m_ang1,s_ang1 = jcf.get_angle_tithi_Ec(t=end_time)
				nak_yama = jce.find_naksatra_Ec(m_ang1,ayanamsa=ayanamsa)[0]
				if nak_yama==nak_:
					return dvadasi_names[i]+'2', day_1_num
		return None, vrata_day



def pt(tithi):
	# Converts tithis from 1 to 30 into pakṣa-tithis from 1 to 15. 
	# pt stands for pakṣa-tithi
	return ((tithi-1)%15)+1

#-----------------utils for user facing functions--------------------------
def convert_timezones(data,offset):
	# data_type is 'month' or 'year'
	timezone = tmz(timedelta(hours=offset))
	new_data = []
	for d in data:
		d['parana'] = (d['parana'][0].astimezone(timezone),d['parana'][1].astimezone(timezone))
		new_data += [d]
	return new_data

#-------------------User Facing functions Below----------------------------

def get_month_vrata(year,month,latitude=27.5650,longitude=77.6593,accuracy=0.001, ayanamsa='citrapaksa', 
					dawn_duration=96,verbose=True,mata='tithi-mana',yama_mata='flexible',
					parana_method='common_sense',timezone_offset=None):
	# timezone_offset is in hours. It does not affect the caculations at all, only the final data to be returned.
	def get_prev_month_data():
		if month>1:
			return jcf.get_month_data(year=year,month=month-1,latitude=latitude,longitude=longitude,accuracy=accuracy,
								ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False,section='third_third')
		else:
			return jcf.get_month_data(year=year-1,month=12,latitude=latitude,longitude=longitude,accuracy=accuracy,
								ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False,section='third_third')

	def get_next_month_data():
		if month<12:
			return jcf.get_month_data(year=year,month=month+1,latitude=latitude,longitude=longitude,accuracy=accuracy,
								ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False,section='first_third')
		else:
			return jcf.get_month_data(year=year+1,month=1,latitude=latitude,longitude=longitude,accuracy=accuracy,
								ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False,section='first_third')

	if verbose: print('loading data...',end='')
	curr_month = jcf.get_month_data(year=year,month=month,latitude=latitude,longitude=longitude,
							accuracy=accuracy,ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False)
	prev_month = get_prev_month_data()
	next_month = get_next_month_data()
	if verbose: print("done.")
	h = HBV(curr_month=prev_month,next_month=curr_month,mata=mata,yama_mata=yama_mata,parana_method=parana_method)
	vratas1 = h.HVV_test(accuracy=accuracy)
	h = HBV(curr_month=curr_month,next_month=next_month,mata=mata,yama_mata=yama_mata,parana_method=parana_method)
	vratas2 = h.HVV_test(accuracy=accuracy)
	vratas = vratas1 + vratas2
	filtered_vratas = [v for v in vratas if v["date"].month==month] #Because some vratas of prev and next month also show up
	if timezone_offset is not None: filtered_vratas = convert_timezones(filtered_vratas,timezone_offset)
	return filtered_vratas

def get_year_vrata(year,latitude=27.5650,longitude=77.6593,accuracy=0.001,ayanamsa='citrapaksa',
					dawn_duration=96,verbose=True,mata='tithi-mana',yama_mata='flexible',
					parana_method='common_sense',timezone_offset=5.5,start_time=None,end_time=None):
	if verbose: print("fetching data... ")
	year_data = jcf.get_year_data(year=year,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=verbose)
	if verbose: print("fetching supplementary data...")
	next_yr_1st_month = jcf.get_month_data(year=year+1,month=1,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=False,section='first_third')
	prev_yr_last_month = jcf.get_month_data(year=year-1,month=12,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=False,section='third_third')
	if verbose: print('data ready.')
	if verbose: print('processing... ',end='')
	year_data = [prev_yr_last_month] + year_data + [next_yr_1st_month] 
	all_vratas = []
	for i in range(0,13):
		curr_month = year_data[i]
		next_month = year_data[i+1]
		h = HBV(curr_month=curr_month,next_month=next_month,mata=mata,yama_mata=yama_mata,parana_method=parana_method)
		vrata_instance = h.HVV_test(accuracy=accuracy)
		all_vratas += vrata_instance
	if timezone_offset is not None: all_vratas = convert_timezones(all_vratas,timezone_offset)
	if verbose: print('done.')
	return all_vratas


# The function below takes arbitrary data (as a list of months, i.e. basically in the form of year data but not 
# necessarily spanning any one single calendar year)
# But you MUST have atleast 2 months. This is because hvv calculation uses a "next_month" variable.
# If you want only a single month, use function get_month_vrata above
def get_vrata(data,latitude=27.5650,longitude=77.6593,accuracy=0.001,ayanamsa='citrapaksa',
					dawn_duration=96,verbose=True,mata='tithi-mana',yama_mata='flexible',
					parana_method='common_sense',timezone_offset=5.5,start_time=None,end_time=None):
	all_vratas = []
	for i in range(0,len(data)-1):
		if verbose: print("running month",i+1)
		curr_month = data[i]
		next_month = data[i+1]
		h = HBV(curr_month=curr_month,next_month=next_month,mata=mata,yama_mata=yama_mata,parana_method=parana_method)
		vrata_instance = h.HVV_test(accuracy=accuracy)
		all_vratas += vrata_instance
	if timezone_offset is not None: all_vratas = convert_timezones(all_vratas,timezone_offset)
	if verbose: print('done.')
	return all_vratas


########################## TO DOs ##################################
"""
 Add option 'conprehensive' to return all data about the vrata day, like sunrise etc, since the data already exists

"""






