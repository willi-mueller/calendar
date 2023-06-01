import JivaCalendar_Ecliptic as jce
from datetime import timedelta
from datetime import datetime as dt
from datetime import timezone as tmz
import pytz
from astropy.coordinates import Angle

class Pancanga:
	def __init__(self,date=(2021,1,1),time=(0,0,0),location=(None,None),timezone=pytz.timezone('UTC')):
		# location is in (latitude,longitude), each being a float. self.location should be (Angle,Angle)
		self.location = (process_angle(location[0]),process_angle(location[1]))

		if timezone is not None:
			self.timezone = process_timezone(timezone)
		if timezone is None and self.location[1] is not None:
			self.timezone = timezone_lookup(self.location[1])
		if timezone is None and self.location[1] is None:
			self.timezone = pytz.timezone('UTC')

		# self.datetime = dt(date[0],date[1],date[2],time[0],time[1],time[2],tzinfo=self.timezone)
		# Don't use the above to specify timezone. There's a bug between datetime and pytz. 
		# Therefore I'm using the localize method below.
		self.datetime = self.timezone.localize(dt(date[0],date[1],date[2],time[0],time[1],time[2]))
		self._datetime_utc = self.datetime.astimezone(tz=tmz.utc)


	def get_pancanga_instant_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',update_attributes=True,
				sun_horizon=Angle('-50m'),moon_horizon=Angle('-50m')):

		tithi,time_s,time_e = get_tithi_start_end_Ec(t=self._datetime_utc,accuracy=accuracy,get_start=True)
		time_s_tit = time_s.astimezone(tz=self.timezone)
		time_e_tit = time_e.astimezone(tz=self.timezone)

		sun_horizon = process_angle(sun_horizon)
		moon_horizon = process_angle(moon_horizon)
		#t = jce.datetime_to_astropy(self._datetime_utc)
		date_start = jce.datetime_to_astropy(self.datetime.replace(hour=0,minute=0,second=0).astimezone(tz=tmz.utc))
		sunrise,sunset,moonrise,moonset = jce.get_local_observations(location=self.location,t=date_start,
				sun_horizon=sun_horizon,moon_horizon=moon_horizon,find=["next"]*4) # Get the 4 parameters in the current date or beyond
		sunrise = jce.astropy_to_datetime(sunrise).astimezone(tz=self.timezone)
		sunset = jce.astropy_to_datetime(sunset).astimezone(tz=self.timezone)
		moonrise = jce.astropy_to_datetime(moonrise).astimezone(tz=self.timezone)
		moonset = jce.astropy_to_datetime(moonset).astimezone(tz=self.timezone)

		masa,time_s_masa,time_e_masa = get_masa_start_end_Ec(t=self._datetime_utc,accuracy=accuracy,ayanamsa=ayanamsa)

		t_ = jce.datetime_to_astropy(self._datetime_utc)
		m,s = jce.get_sun_moon_Ec(t_)
		_,m_naksatra = jce.find_naksatra_Ec(lon=m.lon,ayanamsa=ayanamsa)
		_,s_naksatra = jce.find_naksatra_Ec(lon=s.lon,ayanamsa=ayanamsa)
		next_moon_sankramana,_ = get_sankramana_time(t=t_,body='moon',accuracy=accuracy,ayanamsa=ayanamsa,find='next')

		if update_attributes:
			self.tithi_start = time_s_tit
			self.tithi_end = time_e_tit
			self.tithi = tithi
			self.masa_start = time_s
			self.masa_end = time_e
			self.masa = masa
			self.sunrise = sunrise
			self.sunset = sunset
			self.moonrise = moonrise
			self.moonset = moonset
			self.sun_naksatra_now = s_naksatra
			self.moon_naksatra_now = m_naksatra
			self.next_moon_sankramana = next_moon_sankramana
			self.instant_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa,"sun_horizon":sun_horizon,"moon_horizon":moon_horizon}
		return {"tithi":(tithi,time_s_tit,time_e_tit),"masa":(masa,time_s_masa,time_e_masa),"sunrise/set":(sunrise,sunset),
				"moonrise/set":(moonrise,moonset),"sun_naksatra":s_naksatra,"moon_naksatra":m_naksatra,"next_moon_sankramana":next_moon_sankramana}


	def get_pancanga_lunar_month_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',verbose=True,update_attributes=True):
		masa,nm_time,_ = get_masa_start_end_Ec(self._datetime_utc,accuracy=accuracy,ayanamsa=ayanamsa)
		data = [(1,nm_time)]
		for i in range(1,30):
			if verbose and (i+1)%5==0: 
				print("running tithi:",i+1," "*20)
			lon = 12*i
			_,time_ = get_tithi_start_end_Ec(t=self._datetime_utc,get_start=False,accuracy=accuracy)
			#time_ = jce.solve_moon_time_Ec(lon,jce.datetime_to_astropy(self._datetime_utc),accuracy=accuracy)
			data += [(i+1,jce.astropy_to_datetime(time_).astimezone(tz=self.timezone))]
		if update_attributes:
			self.all_tithis_in_masa = data
			self.all_tithis_in_masa_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa}
		return masa,data

	def get_pancanga_gregorian_month_Ec(self,accuracy=0.0001,ayanamsa='citrapaksa',verbose=True,update_attributes=True,
						sun_horizon=Angle('-50m'),moon_horizon=Angle('-50m')):
		month_start = self.datetime.replace(day=1,hour=0,minute=0,second=0).astimezone(tz=tmz.utc)
		month_middle = self.datetime.replace(day=15,hour=0,minute=0,second=0).astimezone(tz=tmz.utc)
		if self.datetime.month<12:
			month_end = self.datetime.replace(hour = 0,minute=0,second=0,day=1,month=self.datetime.month+1).astimezone(tz=tmz.utc)
		if self.datetime.month==12:
			month_end = self.datetime.replace(hour = 0,minute=0,second=0,day=1,month=1,year=self.datetime.year+1).astimezone(tz=tmz.utc)

		masa,_,masa_end = get_masa_start_end_Ec(month_start,accuracy=accuracy,ayanamsa=ayanamsa)
		sun_sankramana,sun_naksatra = get_sankramana_time(t=month_start,body='sun',find='next',
													accuracy=accuracy,ayanamsa=ayanamsa)
		sun_naksatra = jce.Naksatra_list[sun_naksatra]

		all_data = []
		date_ = month_start
		i = 1
		while date_<month_end:
			if verbose: print("running:",date_.astimezone(tz=self.timezone).strftime('%Y-%m-%d'),' '*20,end='\r')

			sunrise,sunset,_,_ = jce.get_local_observations(location=self.location,t=jce.datetime_to_astropy(date_),
				sun_horizon=sun_horizon,moon_horizon=moon_horizon,find=["next"]*4)
			_,_,moonrise,moonset = jce.get_local_observations(location=self.location,t=sunrise,
				sun_horizon=sun_horizon,moon_horizon=moon_horizon,find=["next"]*4)
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
			sunrise = jce.astropy_to_datetime(sunrise).astimezone(tz=self.timezone)
			sunset = jce.astropy_to_datetime(sunset).astimezone(tz=self.timezone)
			moonrise = jce.astropy_to_datetime(moonrise).astimezone(tz=self.timezone)
			moonset = jce.astropy_to_datetime(moonset).astimezone(tz=self.timezone)
			moon_sankramana = jce.astropy_to_datetime(moon_sankramana).astimezone(tz=self.timezone)
			sun_sankramana_dt = jce.astropy_to_datetime(sun_sankramana).astimezone(tz=self.timezone)
			dict_ = {"gregorian_date":date_, "sunrise":sunrise, "sunset":sunset, "moonrise":moonrise, "moonset":moonset,
			"masa":masa, "tithi":tithi, "tithi_end_time":e_time, "moon_naksatra":moon_naksatra, "sun_naksatra":sun_naksatra,
			"next_moon_sankramana":moon_sankramana, "next_sun_sankramana":sun_sankramana_dt}
			all_data += [dict_]
			date_ += timedelta(days=1)
			i += 1
		if verbose: print("finished running.",' '*20)

		if update_attributes:
			self.all_gregorian_month = all_data
			self.all_gregorian_month_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa}
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

def timezone_lookup(location):
	#return timezone
	return pytz.timezone('EST')

def process_timezone(timezone):
	if isinstance(timezone, str):
		timezone = timezone.lower()
		if timezone=='est':
			return pytz.timezone('US/Eastern')
		if timezone=='pst':
			return pytz.timezone('PST')
		if timezone=='utc':
			return pytz.timezone('UTC')

	return timezone

def process_angle(angle):
	if angle is None: return None
	if type(angle)==str: return Angle(angle)
	if type(angle) in [int,float]: return Angle(f"{angle}d")
	if type(angle)==Angle: return angle


if __name__ == "__main__":
	moment = Pancanga(date=(2021,6,3),time=(21,17,0),location=(39.29,-76.61),timezone=pytz.timezone('US/Eastern'))
	month_data = moment.get_pancanga_gregorian_month_Ec(verbose=True)
	print(f"The data for each day of the month containing the date {(2021,6,3)} is generated.")
	print("Below is a sample showing the data for the first day")
	print(month_data[0])
