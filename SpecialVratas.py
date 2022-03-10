
import JivaCalendar_Ecliptic as jce
import JivaCalendar_FrontEnd as jcf
from datetime import timezone as tmz
from datetime import timedelta

def main(data,hvv_date_list,accuracy=0.001,ayanamsa='citrapaksa',timezone_offset=None):
	# prepare data in a way that day dict has one more entry called 
	if type(data[0])==list: #flattening data if not already flat
		data = [d for sublist in data for d in sublist]
	sr = get_siva_ratri(data,accuracy=accuracy,timezone_offset=timezone_offset)
	rn = get_rama_navami(data,hvv_date_list,accuracy=accuracy,timezone_offset=timezone_offset)
	kj = get_krsna_janmastami(data,accuracy=accuracy,timezone_offset=timezone_offset,ayanamsa=ayanamsa)
	return {'siva_ratri':sr,'rama_navami':rn,'krsna_janmastami':kj}


def get_siva_ratri(data,muhurta=48,accuracy=0.001,timezone_offset=None):
	# muhurta is in minutes
	muhurta = timedelta(minutes=muhurta)

	all_vratas_list = []

	for i,day in enumerate(data):
		if day['adhika_masa']:
			continue
		if day['masa']!='phalguna':
			continue
		if i>len(data)-3:
			break

		day_seq = [day,data[i+1],data[i+2]]
		tit_seq = [d['tithi'] for d in day_seq]
		masa = day['masa']

		# Missing cases: Couldn't find any. Checked against general vratas in General_Vrata.py
		scenario = None
		if tit_seq == [28,29,30]: 
			day2_sunrise = day_seq[1]['sunrise']
			_,t_e = jcf.get_tithi_start_end_Ec(t=day2_sunrise,accuracy=accuracy,get_start=False,which_tithi='current')
			scenario = 1 if (t_e-day2_sunrise)>=2*muhurta else 101
		if tit_seq == [27,29,30]: 
			day2_sunrise = day_seq[1]['sunrise']
			_,t_e = jcf.get_tithi_start_end_Ec(t=day2_sunrise,accuracy=accuracy,get_start=False,which_tithi='current')
			if t_e - day2_sunrise<2*muhurta:
				print("WARNING! Something's off. 28th is ksaya but 29th doesn't span even 2 muhurtas.")
				print("Location of Error: Siva Ratri calculation scenario 2")
			scenario = 2
		if tit_seq == [28,29,29]: scenario = 3
		if tit_seq == [27,29,29]: scenario = 4
		if tit_seq == [28,30,30]: scenario = 5
		if tit_seq == [28,30,1]: scenario = 6
		if tit_seq == [28,29,1]: 
			day2_sunrise = day_seq[1]['sunrise']
			_,t_e = jcf.get_tithi_start_end_Ec(t=day2_sunrise,accuracy=accuracy,get_start=False,which_tithi='current')
			scenario = 7 if (t_e-day2_sunrise)>=2*muhurta else 107

		if scenario in [1,2,7]:
			vrata_day = day_seq[1]
			next_sunrise = day_seq[2]['sunrise']
			next_sunset = day_seq[2]['sunset']
			forenoon = next_sunrise + (next_sunset-next_sunrise)/3
			parana_start = next_sunrise
			_,t_e = jcf.get_tithi_start_end_Ec(t=next_sunrise,accuracy=accuracy,get_start=False,which_tithi='current')
			parana_end = t_e if t_e<forenoon else forenoon
		if scenario in [3,4]: 
			vrata_day = day_seq[1]
			next_sunrise = day_seq[2]['sunrise']
			next_sunset = day_seq[2]['sunset']
			forenoon = next_sunrise + (next_sunset-next_sunrise)/3
			_,t_e = jcf.get_tithi_start_end_Ec(t=next_sunrise,accuracy=accuracy,get_start=False,which_tithi='current')
			parana_start = t_e
			parana_end = forenoon # There's no way  30th is ending before forenoon, since it was 29th at sunrise
		if scenario in [5,6,101,107]: 
			vrata_day = day_seq[0]
			next_sunrise = day_seq[1]['sunrise']
			next_sunset = day_seq[1]['sunset']
			forenoon = next_sunrise + (next_sunset-next_sunrise)/3
			parana_start = next_sunrise
			parana_end = forenoon

		if timezone_offset is not None and scenario is not None:
			timezone = tmz(timedelta(hours=timezone_offset))
			parana_start = parana_start.astimezone(timezone)
			parana_end = parana_end.astimezone(timezone)

		if scenario is not None: 
			if parana_end<parana_start:
				print("WARNING! parana end is before parana start for siva ratri")
				print("parana start:",parana_start)
				print('parana end:',parana_end)
			all_vratas_list += [(vrata_day['gregorian_date'],parana_start,parana_end,scenario)]

	return all_vratas_list


def get_rama_navami(data,hvv_date_list,accuracy=0.001,timezone_offset=None):

	all_vratas_list = []

	for i,day in enumerate(data):
		if day['adhika_masa']:
			continue
		if day['masa']!='caitra':
			continue
		if i>len(data)-3:
			break

		day_seq = [day,data[i+1],data[i+2]]
		tit_seq = [d['tithi'] for d in day_seq]
		masa = day['masa']

		# Missing cases: Couldn't find any missing. This seems quite complete. Can check the rest against this.
		#
		#
		scenario = None
		if tit_seq==[8,9,10]: 
			scenario = 1
			vrata_index = 1
		if tit_seq==[7,9,10]: 
			scenario = 2
			vrata_index = 1
		if tit_seq==[8,9,9]:
			scenario = 3
			vrata_index = 1
		if tit_seq==[7,9,9]:
			scenario = 4
			vrata_index = 1
		if tit_seq==[8,10,11]: # i.e. day 3 is ekadasi 
			if day_seq[2]["gregorian_date"] in hvv_date_list:
				scenario = 5
				vrata_index = 0
			else:
				scenario = 6
				vrata_index = 1
		if tit_seq==[8,10,10]:
			scenario = 7
			vrata_index = 1
		if tit_seq==[8,9,11]: # i.e. day 3 is ekadasi 
			if day_seq[2]["gregorian_date"] in hvv_date_list:
				scenario = 8
				vrata_index = 0
			else:
				scenario = 9
				vrata_index = 1

		if scenario is not None: 
			vrata_day = day_seq[vrata_index]
			next_day = day_seq[vrata_index+1]
			next_sunrise = next_day['sunrise']
			next_sunset = next_day['sunset']
			forenoon = next_sunrise + (next_sunset-next_sunrise)/3

		if scenario in [1,2,5,6,8,9]:
			parana_start = next_sunrise
			parana_end = forenoon
		if scenario in [3,4,7]:
			_,t_e = jcf.get_tithi_start_end_Ec(t=next_sunrise,accuracy=accuracy,get_start=False,which_tithi='current')
			parana_start = t_e
			parana_end = forenoon

		if timezone_offset is not None and scenario is not None:
			timezone = tmz(timedelta(hours=timezone_offset))
			parana_start = parana_start.astimezone(timezone)
			parana_end = parana_end.astimezone(timezone)

		if scenario is not None: 
			if parana_end<parana_start:
				print("WARNING! parana end is before parana start for rama navami")
				print("parana start:",parana_start)
				print('parana end:',parana_end)
			all_vratas_list += [(vrata_day['gregorian_date'],parana_start,parana_end,scenario)]

	return all_vratas_list


def get_krsna_janmastami(data,accuracy=0.001,timezone_offset=None,ayanamsa='citrapaksa'):
	# Note that here we're cchecking only until len(data)-4

	all_vratas_list = []

	for i,day in enumerate(data):
		if day['adhika_masa']:
			continue
		if day['masa']!='bhadrapada':
			continue
		if i>len(data)-4:
			break

		day_seq = [day,data[i+1],data[i+2],data[i+3]]
		tit_seq = [d['tithi']-15 for d in day_seq[0:-1]] # converting so that we can call krsna paksa astami as 8th instead of 23rd
		masa = day['masa']

		scenario = None
		# Missing cases: [6,8,8], [7,8,10]
		#
		#
		if tit_seq==[7,8,9] or tit_seq==[6,8,9]:
			scenario = 1
			vrata_index = 1
		if tit_seq==[7,9,9]:
			scenario = 2
			vrata_index = 1
		if tit_seq==[7,9,10]:
			scenario = 3
			vrata_index = 1
		if tit_seq==[7,8,8]:
			scenario = 4
			vrata_index = 1
			d2 = day_seq[1]
			d3 = day_seq[2]
			# dow stands for day of the week
			d2_dow = d2['gregorian_date'].strftime("%A").lower() # this is day of the week as a lower case string
			d3_dow = d3['gregorian_date'].strftime("%A").lower()
			midnight = d2['sunset'] + (d3['sunrise'] - d2['sunset'])/2
			nak = jcf.get_naksatra(midnight,body='moon')
			if (d2['moon_naksatra']!='rohini' and
				d3_dow not in ['monday','wednesday'] and d3['moon_naksatra']!='rohini'):
				if nak!="rohini":
					scenario = 5 # both scenarios 5 and 6 are included here.
					vrata_index = 1
			if (d2_dow not in ['monday','wednesday'] and d2['moon_naksatra']!='rohini' and
				d3_dow in ['monday','wednesday'] and d3['moon_naksatra']!='rohini'):
				if nak!="rohini":
					scenario = 7 
					vrata_index = 2
			if (d2_dow not in ['monday','wednesday'] and d2['moon_naksatra']=='rohini' and
				d3_dow not in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak=="rohini":
					scenario = 8 
					vrata_index = 1
			if (d2_dow in ['monday','wednesday'] and d2['moon_naksatra']=='rohini' and
				d3_dow not in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak=="rohini":
					scenario = 9
					vrata_index = 1
			if (d2_dow not in ['monday','wednesday'] and d2['moon_naksatra']=='rohini' and
				d3_dow in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak=="rohini":
					scenario = 10
					vrata_index = 1
			if (d2_dow not in ['monday','wednesday'] and d2['moon_naksatra']!='rohini' and
				d3_dow in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak!="rohini":
					scenario = 11
					vrata_index = 2
			if (d2_dow not in ['monday','wednesday'] and d2['moon_naksatra']!='rohini' and
				d3_dow in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak=="rohini":
					scenario = 12
					vrata_index = 1
			if (d2_dow in ['monday','wednesday'] and d2['moon_naksatra']!='rohini' and
				d3_dow not in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak=="rohini":
					scenario = 13
					vrata_index = 2
			if (d2_dow in ['monday','wednesday'] and d2['moon_naksatra']!='rohini' and
				d3_dow not in ['monday','wednesday'] and d3['moon_naksatra']=='rohini'):
				if nak!="rohini":
					scenario = 14
					vrata_index = 2

		if scenario==4:
			print("WARNING! Scenario 4 is valid but nothing else fits the description")


		# parana calculation here on:
		if scenario is None:
			continue

		vrata_day = day_seq[vrata_index]
		next_day = day_seq[vrata_index+1]
		sunrise = vrata_day['sunrise']
		next_sunrise = next_day['sunrise']
		next_sunset = next_day['sunset']
		forenoon = next_sunrise + (next_sunset - next_sunrise)/3
		parana_start_alt = None

		if scenario==1 or scenario>=4:
			# i.e. the vrata is on astami
			roh_s,_ = jcf.get_sankramana_time_Ec(t=sunrise,body='moon',find='nearest',which_nak='rohini',
					start_end='start',accuracy=accuracy,ayanamsa=ayanamsa)
			tit,tit_s,tit_e = jcf.get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,get_start=True,which_tithi='current')
			if tit!=23:
				print("WARNING! Scenario 1 or >=4 for janmastami but the vrata day tithi is not astami. Tithi is",tit)

			if roh_s>tit_s and roh_s<tit_e:
				# i.e. rohini is present at some point in the tithi
				roh_e,_ = jcf.get_sankramana_time_Ec(t=sunrise,body='moon',find='nearest',which_nak='rohini',
					start_end='end',accuracy=accuracy,ayanamsa=ayanamsa)
				if tit_e<next_sunrise and roh_e<next_sunrise:
					parana_start = next_sunrise
					parana_end = forenoon
				if tit_e>next_sunrise and roh_e<next_sunrise:
					parana_start = tit_e
					parana_end = forenoon
				if tit_e<next_sunrise and roh_e>next_sunrise and roh_e<forenoon:
					parana_start = roh_e
					parana_end = forenoon
				if tit_e<next_sunrise and roh_e>forenoon and roh_e<next_sunset:
					parana_start = roh_e
					parana_end = next_sunset
				if tit_e<next_sunrise and roh_e>next_sunset:
					parana_start = next_sunrise
					parana_end = forenoon
				###### The next scenario (num 6) has major typo in Tyagi Maharaj's doc
				if tit_e>roh_e and roh_e>next_sunrise:
					parana_start = tit_e
					parana_start_alt = roh_e
					parana_end = forenoon
				if tit_e>next_sunrise and roh_e>tit_e and roh_e<forenoon:
					parana_start = roh_e
					parana_start_alt = tit_e
					parana_end = forenoon
				if tit_e>next_sunrise and roh_e>tit_e and roh_e>forenoon and roh_e<next_sunset:
					parana_start = roh_e
					parana_start_alt = tit_e
					parana_end = next_sunset
				if tit_e>next_sunrise and roh_e>tit_e and roh_e>next_sunset:
					parana_start = tit_e
					parana_end = forenoon
			else:
				_,tit_e = jcf.get_tithi_start_end_Ec(t=vrata_day['sunrise'],accuracy=accuracy,get_start=False,which_tithi='current')
				parana_start = tit_e if tit_e>next_sunrise else next_sunrise
				parana_end = forenoon

		else:
			_,tit_e = jcf.get_tithi_start_end_Ec(t=vrata_day['sunrise'],accuracy=accuracy,get_start=False,which_tithi='current')
			parana_start = tit_e if tit_e>next_sunrise else next_sunrise
			parana_end = forenoon


		if timezone_offset is not None:
			timezone = tmz(timedelta(hours=timezone_offset))
			parana_start = parana_start.astimezone(timezone)
			parana_end = parana_end.astimezone(timezone)

		if parana_end<parana_start:
			print("WARNING! parana end is before parana start for krsna janmastami")
			print("parana start:",parana_start)
			print('parana end:',parana_end)
		all_vratas_list += [(vrata_day['gregorian_date'],parana_start,parana_start_alt,parana_end,scenario)]

	return all_vratas_list










