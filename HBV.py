import JivaCalendar_FrontEnd as jcf
import parana as pn

class HBV:
	def __init__(self, curr_month, next_month):
		self.curr_month = curr_month
		self.next_month = next_month

	#def head(month, month_next, month_prev):

	def HVV_test(self): 
		def create_string(tit_seq,vrata_day):
			info_str_1 = f"tithi sequence is {tit_seq}. The sequence is "
			info_str_2 = f"(day1_tithi,day2_dawn_tithi,day2_tithi,day3_tithi,day4_tithi,day5_tithi,day6_tithi, " 
			info_str_3 = f"day7_tithi,day8_tithi,day9_tithi). Out of these, the vrata date is day {vrata_day}"
			return info_str_1 + info_str_2 + info_str_3
		def get_day(vrata_day,i,which_day):
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
			if day["tithi"]%15 in [9,10]:
				list_of_days = self.return_following_days(i) # i.e. the given day is day 2 in the list
				[day_1,day_2,day_3,day_4,day_5,day_6,day_7,day_8,day_9] = list_of_days
				vrata_day, scenario_num, tit_seq = vrata_scenario_check_1p1(day_1,day_2,day_3,day_4)
				if vrata_day is not None:
					vrata_day, scenario_num, tit_seq = vrata_scenario_check_1p2(list_of_days,vrata_day,scenario_num,tit_seq)

					parana_start,parana_end = pn.get_parana_times(get_day(vrata_day,i,'vrata'),get_day(vrata_day,i,'next'),
													scenario_num,None)
					vrata_date = list_of_days[vrata_day-1]["gregorian_date"]
					month_vrata_list += [{"date":vrata_date,"type":scenario_num,"info":create_string(tit_seq,vrata_day),
							"parana":(parana_start,parana_end)}]

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
		print("WARNING! something's wrong! There's no paksa end within the 9 following days from day1 (in func vrata_scenario_check_1p2)")
	if len(paksa_end_tithis)==1:
		return vrata_day,scenario_num,tit_seq_full
	if len(paksa_end_tithis)==2:
		if scenario_num[0:3]=='hvv' and tit_seq[vrata_day]==11:
			vrata_day = tit_seq[2:].index(12)+2 # This selects the first occurence of dvadasi, if dvadasi rules 2 days
			scenario_num = "pvm2" # pv stands for pakśa-vardhinī 
			return vrata_day, scenario_num, tit_seq_full
		if scenario_num[0:3] in ['unm','tsp','vnj']:
			scenario_num = scenario_num[0] + "pv4" # i.e. upv4, tpv4 or vpv4. "pv" stands for pakśa-vardhini
			return vrata_day,scenario_num, tit_seq_full

def pt(tithi):
	# Converts tithis from 1 to 30 into pakṣa-tithis from 1 to 15. 
	# pt stands for pakṣa-tithi
	return ((tithi-1)%15)+1


#-------------------User Facing functions Below----------------------------

def get_month_vrata(year,month,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=True):
	def get_prev_month_data():
		if month>1:
			return jcf.get_month_data(year=year,month=month-1,latitude=latitude,longitude=longitude,
							accuracy=accuracy,ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False)
		else:
			return jcf.get_month_data(year=year-1,month=12,latitude=latitude,longitude=longitude,
							accuracy=accuracy,ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False)

	def get_next_month_data():
		if month<12:
			return jcf.get_month_data(year=year,month=month+1,latitude=latitude,longitude=longitude,
							accuracy=accuracy,ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False)
		else:
			return jcf.get_month_data(year=year+1,month=1,latitude=latitude,longitude=longitude,
							accuracy=accuracy,ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False)

	if verbose: print('loading data...',end='')
	curr_month = jcf.get_month_data(year=year,month=month,latitude=latitude,longitude=longitude,
							accuracy=accuracy,ayanamsa=ayanamsa,dawn_duration=dawn_duration,verbose=False)
	prev_month = get_prev_month_data()
	next_month = get_next_month_data()
	if verbose: print("done.")
	h = HBV(curr_month=prev_month,next_month=curr_month)
	vratas1 = h.HVV_test()
	h = HBV(curr_month=curr_month,next_month=next_month)
	vratas2 = h.HVV_test()
	vratas = vratas1 + vratas2
	filtered_vratas = [v for v in vratas if v["date"].month==month] #Because some vratas of prev and next month also show up
	return filtered_vratas

def get_year_vrata(year,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=True):
	print("fetching data... ",end='')
	year_data = jcf.get_year_data(year=year,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=verbose)
	next_yr_1st_month = jcf.get_month_data(year=year+1,month=1,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=False)
	prev_yr_last_month = jcf.get_month_data(year=year-1,month=12,latitude=27.5650,longitude=77.6593,accuracy=0.0001,
		ayanamsa='citrapaksa', dawn_duration=96,verbose=False)
	if verbose: print('data ready.')
	if verbose: print('processing... ',end='')
	year_data = [prev_yr_last_month] + year_data + [next_yr_1st_month] 
	all_vratas = []
	for i in range(0,13):
		curr_month = year_data[i]
		next_month = year_data[i+1]
		h = HBV(curr_month=curr_month,next_month=next_month)
		vrata_instance = h.HVV_test()
		all_vratas += vrata_instance
	if verbose: print('done.')
	return all_vratas









