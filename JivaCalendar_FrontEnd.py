import JivaCalendar_Ecliptic as jce
from datetime import timedelta
from datetime import datetime as dt
from datetime import timezone as tmz
import pytz
from astropy.coordinates import Angle

class Pancanga:
	def __init__(self,date=(2021,1,1),time=(0,0,0),location=(None,None),timezone=None):
		# location is in (latitude,longitude), each being a float. self.location should be (Angle,Angle)
		self.location = (process_angle(location[0]),process_angle(location[1]))

		if timezone is not None:
			self.timezone = process_timezone(timezone)
		if timezone is None and self.location[1] is not None:
			self.timezone = timezone_lookup(self.location[1])
		if timezone is None and self.location[1] is None:
			self.timezone = tmz.utc

		self.datetime = dt(date[0],date[1],date[2],time[0],time[1],time[2],tzinfo=self.timezone)
		self._datetime_utc = self.datetime.astimezone(tz=tmz.utc)


	def get_pancanga_instant_Ec(self,accuracy=0.01,ayanamsa='citrapaksa',update_attributes=True,sun_horizon=Angle('-50m'),moon_horizon=Angle('-50m')):

		tithi,time_s,time_e = get_tithi_start_end_Ec(t=self._datetime_utc,accuracy=accuracy,get_start=True)
		time_s_tit = time_s.astimezone(tz=self.timezone)
		time_e_tit = time_e.astimezone(tz=self.timezone)

		sun_horizon = process_angle(sun_horizon)
		moon_horizon = process_angle(moon_horizon)
		midday = jce.datetime_to_astropy(self.datetime.replace(hour=12,minute=0,second=0).astimezone(tz=tmz.utc))
		sunrise,sunset,moonrise,moonset = jce.get_local_observations(location=self.location,t=midday,sun_horizon=sun_horizon,moon_horizon=moon_horizon)
		sunrise = jce.astropy_to_datetime(sunrise).astimezone(tz=self.timezone)
		sunset = jce.astropy_to_datetime(sunset).astimezone(tz=self.timezone)
		moonrise = jce.astropy_to_datetime(moonrise).astimezone(tz=self.timezone)
		moonset = jce.astropy_to_datetime(moonset).astimezone(tz=self.timezone)

		masa,time_s_masa,time_e_masa = get_masa_start_end_Ec(t=self._datetime_utc,accuracy=accuracy,ayanamsa=ayanamsa)

		m,s = jce.get_sun_moon_Ec(jce.datetime_to_astropy(self._datetime_utc))
		_,m_naksatra = jce.find_naksatra_Ec(lon=m.lon,ayanamsa=ayanamsa)
		_,s_naksatra = jce.find_naksatra_Ec(lon=s.lon,ayanamsa=ayanamsa)

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
			self.instant_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa,"sun_horizon":sun_horizon,"moon_horizon":moon_horizon}
		return {"tithi":(tithi,time_s_tit,time_e_tit),"masa":(masa,time_s_masa,time_e_masa),"sunrise/set":(sunrise,sunset),
				"moonrise/set":(moonrise,moonset),"sun_naksatra":s_naksatra,"moon_naksatra":m_naksatra}


	def get_pancanga_lunar_month_Ec(self,accuracy=0.01,ayanamsa='citrapaksa',verbose=True,update_attributes=True):
		masa,nm_time,_ = get_masa_start_end_Ec(self._datetime_utc,accuracy=accuracy,ayanamsa=ayanamsa)
		data = [(1,nm_time)]
		for i in range(1,30):
			if verbose and (i+1)%5==0: 
				print("running tithi:",i+1," "*20)
			lon = 12*i
			time_ = jce.solve_moon_time_Ec(lon,jce.datetime_to_astropy(self._datetime_utc),accuracy=accuracy)
			data += [(i+1,jce.astropy_to_datetime(time_).astimezone(tz=self.timezone))]
		if update_attributes:
			self.all_tithis_in_masa = data
			self.all_tithis_in_masa_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa}
		return masa,data

	def get_pancanga_gregorian_month_Ec(self,accuracy=0.01,ayanamsa='citrapaksa',verbose=True,update_attributes=True):
		month_start = self.datetime.replace(day=1,hour=0,minute=0,second=0).astimezone(tz=tmz.utc)
		month_middle = self.datetime.replace(day=15,hour=0,minute=0,second=0).astimezone(tz=tmz.utc)
		if self.datetime.month<12:
			month_end = self.datetime.replace(hour = 0,minute=0,second=0,day=1,month=self.datetime.month+1).astimezone(tz=tmz.utc)
		if self.datetime.month==12:
			month_end = self.datetime.replace(hour = 0,minute=0,second=0,day=1,month=1,year=self.datetime.year+1).astimezone(tz=tmz.utc)

		tithi,time_e = get_tithi_start_end_Ec(month_start,accuracy=accuracy,get_start=False)
		masa,_,_ = get_masa_start_end_Ec(month_start,accuracy=accuracy,ayanamsa=ayanamsa)
		all_tithis = [(masa,tithi,time_e)]
		i = 1
		while time_e<month_end:
			if verbose and i%5==0: 
				print("running date:",i," "*20)
			tithi,time_e = get_tithi_start_end_Ec(time_e+timedelta(hours=2),accuracy=accuracy,get_start=False)
			if tithi==1:
				masa,_,_ = get_masa_start_end_Ec(time_e+timedelta(days=2),accuracy=accuracy,ayanamsa=ayanamsa)
			all_tithis += [(masa,tithi,time_e)]
			i += 1

		if update_attributes:
			self.all_tithis_in_gregorian_month = all_tithis
			self.all_tithis_in_gregorian_month_calc_info = {"accuracy":accuracy,"ayanamsa":ayanamsa}
		return all_tithis


def get_tithi_start_end_Ec(t=dt(2021,6,2,10,0,0),accuracy=0.01,get_start=True): # Tithi info for a time, time in UTC datetime. return in UTC datetime
	dt_ = t # retaining a datetime copy for future use
	t = jce.datetime_to_astropy(t)
	ang,tit = jce.get_angle_tithi_Ec(t)
	s_lon = int(ang - ang%12) # start angle value for the tithi
	f_lon = int(s_lon + 12) # finish angle value for the tithi

	if get_start:
		if s_lon==0:
			s_time = jce.find_new_moon_time_Ec(t=t,accuracy=accuracy)
		else:
			s_time = jce.solve_moon_time_Ec(s_lon,t,accuracy=accuracy)
	if f_lon==360:
		f_time = jce.find_new_moon_time_Ec(t=jce.datetime_to_astropy(dt_+timedelta(days=2)),accuracy=accuracy)
	else:
		f_time = jce.solve_moon_time_Ec(f_lon,t,accuracy=accuracy)
	tit = int(s_lon/12)+1

	if get_start: 
		s_time = jce.astropy_to_datetime(s_time)
	f_time = jce.astropy_to_datetime(f_time)
	if get_start: 
		return tit,s_time,f_time
	return tit,f_time

def get_masa_start_end_Ec(t=dt(2021,6,2,10,0,0),accuracy=0.01,ayanamsa='citrapaksa'):
	t = jce.datetime_to_astropy(t)
	time_s = jce.find_new_moon_time_Ec(t,accuracy=accuracy)
	datetime_e = jce.astropy_to_datetime(time_s) + timedelta(days=(jce.lunar_month+2)) 
	time_e = jce.find_new_moon_time_Ec(jce.datetime_to_astropy(datetime_e),accuracy=accuracy)
	m,s = jce.get_sun_moon_Ec(time_s)
	num,_ = jce.find_rasi_Ec(s.lon,ayanamsa=ayanamsa)
	masa = jce.Maasa_list[num]
	time_s = jce.astropy_to_datetime(time_s)
	time_e = jce.astropy_to_datetime(time_e)
	return masa,time_s,time_e

def timezone_lookup(location):
	#return timezone
	return pytz.timezone('US/Eastern')

def process_timezone(timezone):
	timezone = timezone.lower()

	if timezone=='est':
		return pytz.timezone('US/Eastern')
	if timezone=='pst':
		return pytz.timezone('US/Pacific')

	return timezone

def process_angle(angle):
	if angle is None: return None
	if type(angle)==str: return Angle(angle)
	if type(angle) in [int,float]: return Angle(f"{angle}d")
	if type(angle)==Angle: return angle