import JivaCalendar_Ecliptic as jce
from datetime import timedelta
from datetime import datetime as dt
from datetime import timezone as tmz
import pytz
import math
import numbers
#from astropy.coordinates import Angle

class Pancanga:

	def __init__(self,date=(2021,1,1),time=(0,0,0),latitude=27.5650,longitude=77.6593):
		# latitude,longitude are floats in degrees. East longitude is positive.
		# default location values of Vrindavan
		# date and time specify moment in UTC
		self.latitude = latitude
		self.longitude = longitude
		self.datetime = dt(date[0],date[1],date[2],time[0],time[1],time[2])
		self.datetime_local = utc_to_local(self.datetime,self.longitude)

	def get_pancanga_gregorian_month_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',verbose=True,update_attributes=True,
						sun_horizon=-0.8333,moon_horizon=-0.8333):
		month_start = local_to_utc(self.datetime_local.replace(day=1,hour=0,minute=0,second=0),self.longitude)
		month_middle = local_to_utc(self.datetime_local.replace(day=15,hour=0,minute=0,second=0),self.longitude)
		if self.datetime.month<12:
			month_end = local_to_utc(self.datetime_local.replace(hour = 0,minute=0,second=0,day=1,month=self.datetime.month+1),self.longitude)
		if self.datetime.month==12:
			month_end = local_to_utc(self.datetime_local.replace(hour = 0,minute=0,second=0,day=1,month=1,year=self.datetime.year+1),self.longitude)

		masa,_,masa_end = get_masa_start_end_Ec(month_start,accuracy=accuracy,ayanamsa=ayanamsa)
		sun_sankramana,sun_naksatra = get_sankramana_time_Ec(t=month_start,body='sun',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa,which_nak='current')
		sun_naksatra = jce.Naksatra_list[sun_naksatra]

		all_data = []
		date_ = month_start
		i = 1
		while date_<month_end:
			if verbose: print("running:",date_,' '*20,end='\r')

			temp_1 = dt.now() # temp
			sunrise,sunset,_,_ = jce.get_local_observations(location=(self.latitude,self.longitude),t=jce.datetime_to_astropy(date_),
				sun_horizon=sun_horizon,moon_horizon=moon_horizon,find=["next"]*4)
			_,_,moonrise,moonset = jce.get_local_observations(location=(self.latitude,self.longitude),t=sunrise,
				sun_horizon=sun_horizon,moon_horizon=moon_horizon,find=["next"]*4)
			temp_2 = dt.now() # temp
			sunrise_dt = jce.astropy_to_datetime(sunrise) # This is in utc.

			tithi,e_time = get_tithi_start_end_Ec(sunrise_dt,accuracy=accuracy,get_start=False,which_tithi='current')
			if sunrise_dt>masa_end:
				masa,_,masa_end = get_masa_start_end_Ec(sunrise_dt,accuracy=accuracy,ayanamsa=ayanamsa)
			moon_sankramana,moon_naksatra = get_sankramana_time_Ec(t=sunrise_dt,body='moon',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa)
			moon_naksatra = jce.Naksatra_list[moon_naksatra]
			if sunrise_dt>sun_sankramana:
					sun_sankramana,sun_naksatra = get_sankramana_time_Ec(t=sunrise_dt,body='sun',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa,which_nak='current')
					sun_naksatra = jce.Naksatra_list[sun_naksatra]
			sunrise = jce.astropy_to_datetime(sunrise)
			sunset = jce.astropy_to_datetime(sunset)
			print("moonrise",moonrise,type(moonrise))
			moonrise = jce.astropy_to_datetime(moonrise)
			moonset = jce.astropy_to_datetime(moonset)
			moon_sankramana = jce.astropy_to_datetime(moon_sankramana)
			sun_sankramana_dt = jce.astropy_to_datetime(sun_sankramana)
			dict_ = {"gregorian_date":date_.date(), "sunrise":sunrise, "sunset":sunset, "moonrise":moonrise, "moonset":moonset,
			"masa":masa, "tithi":tithi, "tithi_end_time":e_time, "moon_naksatra":moon_naksatra, "sun_naksatra":sun_naksatra,
			"next_moon_sankramana":moon_sankramana, "next_sun_sankramana":sun_sankramana_dt}
			all_data += [dict_]
			date_ += timedelta(days=1)
			i += 1
			temp_3 = dt.now() # temp
			print("time 1:",temp_2-temp_1) # temp
			print("time 2:",temp_3-temp_2) # temp
			print() # temp
		if verbose: print("finished running.",' '*20)

		if update_attributes:
			self.all_gregorian_month = all_data
			self.all_gregorian_month_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa}
		return all_data

	def get_pancanga_gregorian_month_full_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',
						verbose=True,dawn_duration=96): 
		# dawn_duration is in minutes
		# for the astral.sun module, default sun_horizon is 0.266 degrees
		month_start = self.datetime.date().replace(day=1)
		if self.datetime.month<12:
			month_end = self.datetime.date().replace(day=1,month=self.datetime.month+1)
		if self.datetime.month==12:
			month_end = self.datetime.date().replace(day=1,month=1,year=self.datetime.year+1)

		sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=month_start)
		masa,_,masa_end = get_masa_start_end_Ec(sun_data['sunrise'],accuracy=accuracy,ayanamsa=ayanamsa,
												get_end=True,system=system)
		#masa_end = masa_end.replace(tzinfo=pytz.UTC) # sunrise is timezone aware, so to compare I make this one aware too. Else error
		#Now made the above change in the fucntion get_masa_start_end_Ec()
		sun_sankramana,sun_nak_num = get_sankramana_time_Ec(t=month_start,body='sun',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa,which_nak='current')
		sun_nak = jce.Naksatra_list[sun_nak_num]
		moon_sankramana,moon_nak_num = get_sankramana_time_Ec(t=month_start,body='moon',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa,which_nak='current')
		moon_nak = jce.Naksatra_list[moon_nak_num]

		all_data = []
		date_ = month_start
		i = 1
		while date_<month_end:
			temp_1 = dt.now() # temp
			if verbose: print("running:",date_,' '*20,end='\r')
			sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=date_)
			sunrise,sunset,dawn_astro,dusk_astro = sun_data["sunrise"], sun_data["sunset"], sun_data["dawn"], sun_data["dusk"]
			 # This is in utc.

			_, tit_dawn, _, _ = get_dawn_info(sunrise,dawn_duration) 

			if sunrise>masa_end:
				masa,_,masa_end = get_masa_start_end_Ec(sunrise,accuracy=accuracy,ayanamsa=ayanamsa,
													get_end=True,system=system)
				#masa_end = masa_end.replace(tzinfo=pytz.UTC) #Now made this change in the fucntion get_masa_start_end_Ec()
			if sunrise>sun_sankramana:
				sun_sankramana,sun_nak_num = get_sankramana_time_Ec(t=sunrise,body='sun',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa,which_nak='current')
				sun_nak = jce.Naksatra_list[sun_nak_num]
			if sunrise>moon_sankramana:
				moon_sankramana,moon_nak_num = get_sankramana_time_Ec(t=sunrise,body='moon',start_end='end',
													accuracy=accuracy,ayanamsa=ayanamsa,which_nak='current')
				moon_nak = jce.Naksatra_list[moon_nak_num]

			tit,tit_end = get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,get_start=False,which_tithi='current')

			dict_ = {"gregorian_date":date_, "sunrise":sunrise, "sunset":sunset,
			"masa":masa, "tithi":tit, "tithi_end_time":tit_end, "tithi_at_dawn":tit_dawn,
			"sun_naksatra":sun_nak,"sun_naksatra_until":sun_sankramana,
			"moon_naksatra":moon_nak,"moon_naksatra_until":moon_sankramana}
			all_data += [dict_]
			date_ += timedelta(days=1)
			i += 1
		if verbose: print("finished running.",' '*20)
		self.month_data_lite = all_data

		return all_data

	def get_pancanga_gregorian_month_lite_Ec(self,accuracy=0.001,ayanamsa='citrapaksa',
						verbose=True,dawn_duration=96,section='full',prev_masa=None,system='amanta'): 
		# dawn_duration is in minutes
		# for the astral.sun module, default sun_horizon is 0.266 degrees
		# section can be 'full','first_half','second_half','first_third','second_third','third_third'
		# In prev_month you can optionally tell what the previous month was. Useful in determining adhika masa

		if section not in ['full','first_half','second_half','first_third','second_third','third_third']:
			raise ValueError("section should be in 'full','first_half','second_half','first_third','second_third','third_third'")

		if self.datetime.month<12:
			month_absolute_end = self.datetime.date().replace(day=1,month=self.datetime.month+1)
		if self.datetime.month==12:
			month_absolute_end = self.datetime.date().replace(day=1,month=1,year=self.datetime.year+1)

		# Now, month_start and month_end are not really the starting and ending dates of the month.
		# They are, instead, the starting and ending dates of the segment that the user wants.
		# Variable names were chosen before this feature was introduced
		if section=='full':
			month_start = self.datetime.date().replace(day=1)
			month_end = month_absolute_end
		if section=='first_half':
			month_start = self.datetime.date().replace(day=1)
			month_end = self.datetime.date().replace(day=16)
		if section=='second_half':
			month_start = self.datetime.date().replace(day=16)
			month_end = month_absolute_end
		if section=='first_third':
			month_start = self.datetime.date().replace(day=1)
			month_end = self.datetime.date().replace(day=11)
		if section=='second_third':
			month_start = self.datetime.date().replace(day=11)
			month_end = self.datetime.date().replace(day=21)
		if section=='third_third':
			month_start = self.datetime.date().replace(day=21)
			month_end = month_absolute_end

		sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=month_start)
		masa,masa_start,masa_end = get_masa_start_end_Ec(sun_data['sunrise'],accuracy=accuracy,ayanamsa=ayanamsa,
													get_end=True,system=system)
		adhika = check_adhika(masa,masa_start,prev_masa=prev_masa,accuracy=accuracy,ayanamsa=ayanamsa,system=system)
		prev_masa = masa
		#masa_end = masa_end.replace(tzinfo=pytz.UTC) # sunrise is timezone aware, so to compare I make this one aware too. Else error
		#Now made the above change in the fucntion get_masa_start_end_Ec()

		all_data = []
		date_ = month_start
		i = 1
		while date_<month_end:
			if verbose: print("running:",date_,' '*20,end='\r')
			sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=date_)
			sunrise,sunset,dawn_astro,dusk_astro = sun_data["sunrise"], sun_data["sunset"], sun_data["dawn"], sun_data["dusk"]
			 # This is in utc.
			dawn = sunrise - timedelta(minutes=dawn_duration)
			if sunrise>masa_end:
				masa,masa_start,masa_end = get_masa_start_end_Ec(sunrise,accuracy=accuracy,ayanamsa=ayanamsa,
														get_end=True,system=system)
				adhika = check_adhika(masa,masa_start,prev_masa=prev_masa,accuracy=accuracy,ayanamsa=ayanamsa,system=system)
				prev_masa = masa
				#masa_end = masa_end.replace(tzinfo=pytz.UTC) #Now made this change in the fucntion get_masa_start_end_Ec()

			_, tithi, m_ang, s_ang = get_angle_tithi_Ec(sunrise)
			tithi = math.ceil(tithi)
			m_nak = jce.find_naksatra_Ec(m_ang,ayanamsa=ayanamsa)
			s_nak = jce.find_naksatra_Ec(s_ang,ayanamsa=ayanamsa)
			samvat = get_samvat(date_,masa)

			dict_ = {"gregorian_date":date_, "sunrise":sunrise, "sunset":sunset,
			"masa":masa,'system':system,'adhika_masa':adhika,"masa_start":masa_start,"masa_end":masa_end,
			"tithi":tithi, "sun_naksatra":s_nak,"moon_naksatra":m_nak}
			dict_.update(samvat)
			all_data += [dict_]
			date_ += timedelta(days=1)
			i += 1

		if verbose: print("finished running.",' '*20)
		self.month_data_lite = all_data

		return all_data

	### ADD more data below comparing with drikpanchang----- ESPECIALLY MASA etc.
	def get_pancanga_day_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',
						verbose=True,dawn_duration=96,system='amanta'):
		sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=self.datetime.date())
		sunrise = sun_data['sunrise']
		_, _, m_ang, s_ang = get_angle_tithi_Ec(sunrise)
		m_nak = jce.find_naksatra_Ec(m_ang,ayanamsa=ayanamsa)
		s_nak = jce.find_naksatra_Ec(s_ang,ayanamsa=ayanamsa)
		tit,s_time,e_time = get_tithi_start_end_Ec(t=sunrise,accuracy=accuracy,get_start=True,which_tithi='current')
		dawn_time,dawn_tit,_,_ = get_dawn_info(sunrise,dawn_duration=dawn_duration)
		all_data = {'gregorian_date':self.datetime.date(),'sunrise':sunrise,'sunset':sun_data['sunset'],'tithi':tit,
				'tithi_start_time':s_time,'tithi_end_time':e_time,'sun_naksatra':s_nak,'moon_naksatra':m_nak,
				'dawn_time':dawn_time,'dawn_tithi':dawn_tit}
		return all_data



def get_dawn_info(sunrise,dawn_duration=96): 
	# Sunrise time (datetime object) is required instead of just date because it has additional info. Saves compute
	dawn_time = sunrise - timedelta(minutes=dawn_duration)
	_, tithi, m_ang, s_ang = jce.get_angle_tithi_Ec(jce.datetime_to_astropy(dawn_time),get_individual_angles=True)
	tithi = math.ceil(tithi)

	return dawn_time, tithi, None, None # Eventaully return the correct s_nak and m_nak
	return dawn_time, tithi, s_nak, m_nak

def get_angle_tithi_Ec(t=dt(2000,1,1,0,0,0)):
	# get angle and tithi for a specific moment
	ms_angle, tithi, m_ang, s_ang = jce.get_angle_tithi_Ec(jce.datetime_to_astropy(t),get_individual_angles=True)
	tithi = math.ceil(tithi)
	return ms_angle, tithi, m_ang, s_ang

def get_tithi_start_end_Ec(t=dt(2021,6,2,10,0,0),accuracy=0.01,get_start=True,which_tithi=None,find='next'): # Tithi info for a time, time in UTC datetime. return in UTC datetime
	dt_ = t # retaining a datetime copy for future use
	t = jce.datetime_to_astropy(t)
	if which_tithi in [None,'current']:
		ang,tit = jce.get_angle_tithi_Ec(t)
		s_lon = int(ang - ang%12) # start angle value for the tithi
		f_lon = int(s_lon + 12) # finish angle value for the tithi
		tit = int(s_lon/12)+1
		find = 'next'
	else:
		tit = which_tithi
		s_lon = 12*(tit-1)
		f_lon = s_lon+12

	f_time = jce.solve_body_time_Ec(lon=f_lon,t=t,find=find,body='moon_synodic',accuracy=accuracy) # find synodic location of the moon
	f_time = jce.astropy_to_datetime(f_time).replace(tzinfo=pytz.UTC)

	if get_start:
		if which_tithi in [None,'current']: find = 'previous'
		s_time = jce.solve_body_time_Ec(lon=s_lon,find=find,t=t,body='moon_synodic',accuracy=accuracy) # find synodic location of the moon
		s_time = jce.astropy_to_datetime(s_time).replace(tzinfo=pytz.UTC)
		return tit,s_time,f_time
	return tit,f_time

def get_masa_start_end_Ec(t=dt(2021,6,2,10,0,0),accuracy=0.001,ayanamsa='citrapaksa',
						get_end=True,system='amanta'): # Tithi info for a time, time in UTC datetime. return in UTC datetime
	if system not in ['amanta','purnimanta']:
		raise ValueError("system should be in 'amanta','purnimanta'")
	dt_ = t # retaining a datetime copy for future use
	t = jce.datetime_to_astropy(t)
	if system=='purnimanta': 
		find = 'nearest'
		b_lon = 180
	if system=='amanta': 
		find = 'previous'
		b_lon = 0
	time_s = jce.solve_body_time_Ec(lon=0,t=t,body='moon_synodic',accuracy=accuracy,find=find) # find new moon at start
			# This is new moon at the start only for amanta. For purnimanta this is the nearest new moon
	m,s = jce.get_sun_moon_Ec(time_s)
	num,_ = jce.find_rasi_Ec(s.lon,ayanamsa=ayanamsa)
	masa = jce.Masa_list[num]
	if system=='purnimanta': # for amanta the extisting time_s is the same.
		time_s = jce.solve_body_time_Ec(lon=b_lon,t=t,body='moon_synodic',accuracy=accuracy,find='previous')
	time_s = jce.astropy_to_datetime(time_s).replace(tzinfo=pytz.UTC)

	if get_end:
		time_e = jce.solve_body_time_Ec(lon=b_lon,t=t,find='next',body='moon_synodic',accuracy=accuracy) # find new moon at end
		time_e = jce.astropy_to_datetime(time_e).replace(tzinfo=pytz.UTC)
		return masa,time_s,time_e
	return masa,time_s

def check_adhika(curr_masa,t_start,prev_masa=None,accuracy=0.001,ayanamsa='citrapaksa',system='amanta'):
	# t_start is the start time of the current month
	if prev_masa is None:
		prev_masa,time_s = get_masa_start_end_Ec(t_start-timedelta(days=10),accuracy=accuracy,
												ayanamsa=ayanamsa,get_end=False,system=system)
	if curr_masa==prev_masa: return True
	else: return False

def get_samvat(date_,masa):
	# date is the gregorian date. masa is the pancanga masa
	# first doing vikram samvat
	year, month = date_.year, date_.month
	first_masa = 'caitra'
	masa_list = [jce.Masa_list[(jce.Masa_list.index(first_masa) + i)%12] for i in range(0,12)]
	first_half = masa_list[0:7]
	second_half = masa_list[8:]
	factor = 0 if month<6 and masa in second_half else 1
	vikram_samvat = year + 56 + factor
	return {"vikram_samvat":vikram_samvat}

def get_naksatra(t=dt(2021,6,2,10,0,0),body='moon',ayanamsa='citrapaksa'):
	t = jce.datetime_to_astropy(t)
	m,s = jce.get_sun_moon_Ec(t)
	if body=='sun':
		_,nak = jce.find_naksatra_Ec(s.lon.degree,ayanamsa=ayanamsa)
	if body=='moon':
		_,nak = jce.find_naksatra_Ec(m.lon.degree,ayanamsa=ayanamsa)
	return nak


def get_sankramana_time_Ec(t=dt(2021,6,2,10,0,0),body='moon',accuracy=0.01,ayanamsa='citrapaksa',
				find='previous',which_nak=None,start_end='end'):
	# Either have which_nak=None, in which case you can get the immediate last or immediate next sankramana,
	# whichever that may be
	# Else which_nak is an int from 0 to 26, for the 27 naksatras. 
	# if which_nak is not None, then start_end specifies if we want the start or end of the given naksatra
	if which_nak in [None,'current']:
		total_count = len(jce.Naksatra_list)
		def body_lon(t_):
			m,s = jce.get_sun_moon_Ec(t_)
			if body=='sun': return s.lon.degree
			if body=='moon': return m.lon.degree
			return "body not found"
		t = jce.datetime_to_astropy(t)
		nak_lon = jce.naksatra_lon_Ec(ayanamsa='citrapaksa')
		num_now,_ = jce.find_naksatra_Ec(body_lon(t)) # The naksatra the the body is in right now 

		if start_end=='start':
			time_ = jce.solve_body_time_Ec(lon=nak_lon[num_now],t=t,body=body,accuracy=accuracy,find='previous')
		if start_end=='end':
			time_ = jce.solve_body_time_Ec(lon=nak_lon[(num_now+1)%total_count],t=t,body=body,accuracy=accuracy,find='next')

		current_nak_num = num_now

	else: # Guves the starting/ending time of the naksatra given by which_nak
		if type(which_nak)==str:
			which_nak = jce.Naksatra_list.index(which_nak)
		t = jce.datetime_to_astropy(t)
		if start_end=='start':
			time_ = jce.solve_body_time_Ec(lon=jce.naksatra_lon_Ec(ayanamsa=ayanamsa)[which_nak],t=t,
											body=body,accuracy=accuracy,find=find)
		if start_end=='end':
			time_ = jce.solve_body_time_Ec(lon=jce.naksatra_lon_Ec(ayanamsa=ayanamsa)[(which_nak+1)%27],t=t,
											body=body,accuracy=accuracy,find=find)
		if start_end not in ['start','end']:
			raise ValueError("choose start_end to be 'start' or 'end'")

		current_nak_num = which_nak

	time_ = jce.astropy_to_datetime(time_).replace(tzinfo=pytz.UTC)
	return time_,current_nak_num

def local_to_utc(datetime,longitude):
	return datetime - timedelta(hours=longitude/360*24)

def utc_to_local(datetime,longitude):
	return datetime + timedelta(hours=longitude/360*24)


#-----------------------------Utils for Front end Functions----------------------------------
def convert_timezones(data,offset,data_type='month'):
	# data is a dictionary that may not all be dates
	try:
		timezone = tmz(timedelta(hours=offset))
	except:
		print("WARNING! Can't convert timezones. Make sure that timezone_offset is an int or float")
		return data
	if data_type=='month':
		new_data = []
		for d in data:
			new_dict = {}
			for (key,val) in d.items():
				if type(val) == dt:
					new_dict[key] = val.astimezone(timezone)
				else:
					new_dict[key] = val
			new_data += [new_dict]
		return new_data
#-------------------------------FRONT END FUNCTIONS-----------------------------------
def get_year_data(year=2021,latitude=27.5650,longitude=77.6593,accuracy=0.001,ayanamsa='citrapaksa',
				dawn_duration=96,system='amanta',verbose=True):
	# default location is Vrindavan
	year_data = []
	for i in range(1,13):
		date_ = (year,i,15) # middle of the month
		if verbose: print("running month",i)
		p = Pancanga(date=date_,latitude=latitude,longitude=longitude)
		month_data = p.get_pancanga_gregorian_month_lite_Ec(verbose=verbose,accuracy=accuracy,
											dawn_duration=dawn_duration,ayanamsa=ayanamsa,system=system)
		year_data += [month_data]
	return year_data

def get_month_data(year=2021,month=1,latitude=27.5650,longitude=77.6593,accuracy=0.001, ayanamsa='citrapaksa', 
			dawn_duration=96,verbose=True,comprehensive=False,timezone_offset=None,section='full',system='amanta'):
	# default location is Vrindavan
	date_ = (year,month,15) # middle of the month
	p = Pancanga(date=date_,latitude=latitude,longitude=longitude)

	if comprehensive:
		month_data = p.get_pancanga_gregorian_month_full_Ec(verbose=verbose,accuracy=accuracy,
											dawn_duration=dawn_duration,ayanamsa=ayanamsa,system=system)
	else:
		month_data = p.get_pancanga_gregorian_month_lite_Ec(verbose=verbose,accuracy=accuracy,ayanamsa=ayanamsa,
												dawn_duration=dawn_duration,section=section,system=system)
	if timezone_offset is not None:
		month_data = convert_timezones(month_data,offset=timezone_offset)
	return month_data

def get_day_data(year=2021,month=1,day=1,latitude=27.5650,longitude=77.6593,accuracy=0.001,
		ayanamsa='citrapaksa', dawn_duration=96,system='amanta',verbose=True):
	p = Pancanga(date=(year,month,day),latitude=latitude,longitude=longitude)
	day_data = p.get_pancanga_day_Ec(verbose=verbose,accuracy=accuracy,
											dawn_duration=dawn_duration,ayanamsa=ayanamsa,system=system)
	return day_data


# The func below works like get_year_data but uses arbitrary starting and ending month and year.
def get_data(year_s,month_s,year_e,month_e,latitude=27.5650,longitude=77.6593,accuracy=0.001,
			ayanamsa='citrapaksa',dawn_duration=96,system='amanta',verbose=True):
	year_data = []
	curr_year = year_s
	curr_month = month_s
	while curr_year<year_e or (curr_year==year_e and curr_month<=month_e):
		date_ = (curr_year,curr_month,15)
		if verbose: print("running year month:",curr_year,curr_month)
		p = Pancanga(date=date_,latitude=latitude,longitude=longitude)
		month_data = p.get_pancanga_gregorian_month_lite_Ec(verbose=verbose,accuracy=accuracy,
											dawn_duration=dawn_duration,ayanamsa=ayanamsa,system=system)
		year_data += [month_data]
		if curr_month<12:
			curr_month += 1
		else:
			curr_year += 1
			curr_month = 1
	return year_data




if __name__ == "__main__":
	moment = Pancanga(date=(2021,6,3),time=(21,17,0),location=(39.29,-76.61))
	month_data = moment.get_pancanga_gregorian_month_Ec(verbose=True)
	print(f"The data for each day of the month containing the date {(2021,6,3)} is generated.")
	print("Below is a sample showing the data for the first day")
	print(month_data[0])



################### TO DOs ##########################
""" 
get_pancanga_gregorian_month_full_Ec does not have 'section' option
also make sure to use that option where get_pancanga_gregorian_month_full_Ec is being called in month_data

Add comprehensive option to get_year_data

timezone option in year data and day data

"""