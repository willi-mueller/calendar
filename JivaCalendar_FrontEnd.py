import JivaCalendar_Ecliptic as jce
from datetime import timedelta
from datetime import datetime as dt
from datetime import timezone as tmz
import pytz
import math
#from astropy.coordinates import Angle

class Pancanga:

	def __init__(self,date=(2021,1,1),time=(0,0,0),latitude=0.0,longitude=0.0):
		# latitude,longitude are floats in degrees. East longitude is positive.
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
		sun_sankramana,sun_naksatra = get_sankramana_time(t=month_start,body='sun',find='next',
													accuracy=accuracy,ayanamsa=ayanamsa)
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

			tithi,e_time = get_tithi_start_end_Ec(sunrise_dt,accuracy=accuracy,get_start=False)
			if sunrise_dt>masa_end:
				masa,_,masa_end = get_masa_start_end_Ec(sunrise_dt,accuracy=accuracy,ayanamsa=ayanamsa)
			moon_sankramana,moon_naksatra = get_sankramana_time(t=sunrise_dt,body='moon',find='next',
													accuracy=accuracy,ayanamsa=ayanamsa)
			moon_naksatra = jce.Naksatra_list[moon_naksatra]
			if sunrise_dt>sun_sankramana:
					sun_sankramana,sun_naksatra = get_sankramana_time(t=sunrise_dt,body='sun',find='next',
													accuracy=accuracy,ayanamsa=ayanamsa)
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


	def get_pancanga_gregorian_month_lite_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',verbose=True,dawn_duration=96): 
		# dawn_duration is in minutes
		# for the astral.sun module, default sun_horizon is 0.266 degrees
		month_start = self.datetime.date().replace(day=1)
		if self.datetime.month<12:
			month_end = self.datetime.date().replace(day=1,month=self.datetime.month+1)
		if self.datetime.month==12:
			month_end = self.datetime.date().replace(day=1,month=1,year=self.datetime.year+1)

		sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=month_start)
		masa,_,masa_end = get_masa_start_end_Ec(sun_data['sunrise'],accuracy=accuracy,ayanamsa=ayanamsa)
		masa_end = masa_end.replace(tzinfo=pytz.UTC) # sunrise is timezone aware, so to compare I make this one aware too. Else error

		all_data = []
		date_ = month_start
		i = 1
		while date_<month_end:
			if verbose: print("running:",date_,' '*20,end='\r')
			temp_1 = dt.now() # temp
			sun_data = jce.get_sunrise_sunset_astral(location=(self.latitude,self.longitude),date_=date_)
			sunrise,sunset,dawn_astro,dusk_astro = sun_data["sunrise"], sun_data["sunset"], sun_data["dawn"], sun_data["dusk"]
			temp_2 = dt.now() # temp
			 # This is in utc.
			dawn = sunrise - timedelta(minutes=dawn_duration)
			temp_3 = dt.now() # temp
			print("ME:",masa_end)
			print("SR:",sunrise)
			if sunrise>masa_end:
				masa,_,masa_end = get_masa_start_end_Ec(sunrise,accuracy=accuracy,ayanamsa=ayanamsa)
				masa_end = masa_end.replace(tzinfo=pytz.UTC)

			_,tithi = jce.get_angle_tithi_Ec(jce.datetime_to_astropy(sunrise))
			_,tithi_at_dawn = jce.get_angle_tithi_Ec(jce.datetime_to_astropy(dawn))
			tithi = math.ceil(tithi)
			tithi_at_dawn = math.ceil(tithi_at_dawn)
			temp_4 = dt.now() # temp

			print("time 1:",temp_2-temp_1) # temp
			print("time 2:",temp_3-temp_2) # temp
			print("time 3:",temp_4-temp_3) # temp
			print() # temp

			dict_ = {"gregorian_date":date_, "sunrise":sunrise, "sunset":sunset,
			"masa":masa, "tithi":tithi, "tithi_at_dawn":tithi_at_dawn}
			all_data += [dict_]
			date_ += timedelta(days=1)
			i += 1
		if verbose: print("finished running.",' '*20)

		return all_data

def get_tithi_start_end_Ec(t=dt(2021,6,2,10,0,0),accuracy=0.01,get_start=True): # Tithi info for a time, time in UTC datetime. return in UTC datetime
	dt_ = t # retaining a datetime copy for future use
	t = jce.datetime_to_astropy(t)
	ang,tit = jce.get_angle_tithi_Ec(t)
	s_lon = int(ang - ang%12) # start angle value for the tithi
	f_lon = int(s_lon + 12) # finish angle value for the tithi
	tit = int(s_lon/12)+1
	f_time = jce.solve_body_time_Ec(lon=f_lon,t=t,find='next',body='moon_synodic',accuracy=accuracy) # find synodic location of the moon
	f_time = jce.astropy_to_datetime(f_time)
	if get_start:
		s_time = jce.solve_body_time_Ec(lon=s_lon,t=t,body='moon_synodic',accuracy=accuracy) # find synodic location of the moon
		s_time = jce.astropy_to_datetime(s_time)
		return tit,s_time,f_time
	return tit,f_time

def get_masa_start_end_Ec(t=dt(2021,6,2,10,0,0),accuracy=0.01,ayanamsa='citrapaksa'): # Tithi info for a time, time in UTC datetime. return in UTC datetime
	dt_ = t # retaining a datetime copy for future use
	t = jce.datetime_to_astropy(t)
	time_s = jce.solve_body_time_Ec(lon=0,t=t,body='moon_synodic',accuracy=accuracy) # find new moon at start
	time_e = jce.solve_body_time_Ec(lon=0,t=t,find='next',body='moon_synodic',accuracy=accuracy) # find new moon at end
	m,s = jce.get_sun_moon_Ec(time_s)
	num,_ = jce.find_rasi_Ec(s.lon,ayanamsa=ayanamsa)
	masa = jce.Maasa_list[num]
	time_s = jce.astropy_to_datetime(time_s)
	time_e = jce.astropy_to_datetime(time_e)
	return masa,time_s,time_e

def get_sankramana_time(t=dt(2021,6,2,10,0,0),body='sun',accuracy=0.01,ayanamsa='citrapaksa',find='all'):
	total_count = len(jce.Naksatra_list)
	def body_lon(t_):
		m,s = jce.get_sun_moon_Ec(t_)
		if body=='sun': return s.lon.degree
		if body=='moon': return m.lon.degree
		return "body not found"
	t = jce.datetime_to_astropy(t)
	nak_lon = jce.naksatra_lon_Ec(ayanamsa='citrapaksa')
	num_now,_ = jce.find_naksatra_Ec(body_lon(t)) # The naksatra the the body is in right now 

	if find=='all':
		time_ = [jce.solve_body_time_Ec(lon=lon,t=t,body=body,accuracy=accuracy,find='previous') for lon in nak_lon[0:num_now+1]]
		if num_now<total_count-1:
			time_ += [jce.solve_body_time_Ec(lon=lon,t=t,body=body,accuracy=accuracy,find='next') for lon in nak_lon[num_now+1:]]
	if find=='previous':
		time_ = jce.solve_body_time_Ec(lon=nak_lon[num_now],t=t,body=body,accuracy=accuracy,find='previous')
	if find=='next':
		time_ = jce.solve_body_time_Ec(lon=nak_lon[(num_now+1)%total_count],t=t,body=body,accuracy=accuracy,find='next')
	current_nak_num = num_now
	return time_,current_nak_num

def local_to_utc(datetime,longitude):
	return datetime - timedelta(hours=longitude/360*24)

def utc_to_local(datetime,longitude):
	return datetime + timedelta(hours=longitude/360*24)

if __name__ == "__main__":
	moment = Pancanga(date=(2021,6,3),time=(21,17,0),location=(39.29,-76.61))
	month_data = moment.get_pancanga_gregorian_month_Ec(verbose=True)
	print(f"The data for each day of the month containing the date {(2021,6,3)} is generated.")
	print("Below is a sample showing the data for the first day")
	print(month_data[0])
