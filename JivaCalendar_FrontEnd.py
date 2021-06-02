"""# High Level Pancanga Functions"""

import JivaCalendar_Ecliptic as jce
from datetime import timedelta

def get_tithi_start_end_Ec(t="J2000",accuracy=0.01):
    t = jce.str_to_astropy(t)
    datetime_ = jce.astropy_to_datetime(t)
    ang,tit = jce.get_angle_tithi_Ec(t)
    s_lon = ang - ang%12 # start angle value for the tithi
    f_lon = s_lon + 12 # finish angle value for the tithi
    if s_lon==0:
        s_time = jce.find_new_moon_time_Ec(t=t,accuracy=accuracy)
    else:
        s_time = jce.solve_moon_time_Ec(s_lon,t,accuracy=accuracy)
    f_time = jce.solve_moon_time_Ec(f_lon,t,accuracy=accuracy)
    tit = int(s_lon/12)+1
    info = f"tithi containing the time {t}"
    data = {"tithi":tit,"tithi start time":jce.astropy_to_datetime(s_time),
            "tithi end time":jce.astropy_to_datetime(f_time)}
    return {"info":info,"data":data}

def get_masa_start_end_Ec(t="J2000",accuracy=0.01,ayanamsa='citrapaksa'):
    t = jce.str_to_astropy(t)
    datetime_s = jce.astropy_to_datetime(t)
    time_s = jce.find_new_moon_time_Ec(t,accuracy=accuracy)
    datetime_e = jce.astropy_to_datetime(time_s) + timedelta(days=(jce.lunar_month+2)) 
    time_e = jce.find_new_moon_time_Ec(jce.datetime_to_astropy(datetime_e),accuracy=accuracy)
    m,s = jce.get_sun_moon_Ec(time_s)
    num,_ = jce.find_rasi_Ec(s.lon,ayanamsa=ayanamsa)
    masa = jce.Maasa_list[num]
    sun_naksatra = jce.find_naksatra_Ec(s.lon,ayanamsa=ayanamsa)[1]
    # sun_naksatra is only correct at the start of the month
    info = f"the masa containing the time {jce.astropy_to_datetime(t)}"
    data = {"masa start time":jce.astropy_to_datetime(time_s),"masa end time":jce.astropy_to_datetime(time_e),
            "masa": masa,"sun naksatra at month beginning": sun_naksatra}
    return {"info":info,"data":data}

def get_pancanga_instant_Ec(t="2021-5-31 10:00:00",accuracy=0.01,ayanamsa='citrapaksa'):
    t = jce.str_to_astropy(t)
    dict_ = get_masa_start_end_Ec(t=t,accuracy=accuracy,ayanamsa=ayanamsa)
    masa = dict_["data"]["masa"]
    dict_ = get_tithi_start_end_Ec(t=t,accuracy=accuracy)["data"]
    tithi, s_time, f_time = dict_["tithi"],dict_["tithi start time"],dict_["tithi end time"]
    m,s = jce.get_sun_moon_Ec(t)
    _,m_naksatra = jce.find_naksatra_Ec(lon=m.lon,ayanamsa=ayanamsa)
    _,s_naksatra = jce.find_naksatra_Ec(lon=s.lon,ayanamsa=ayanamsa)
    info = f"pancanga for the time {jce.astropy_to_datetime(t)}"
    data = {"tithi":tithi,"masa":masa,"moon naksatra":m_naksatra,"sun naksatra":s_naksatra}
    return {"info":info,"data":data}

# Combine the function below with the above function
def get_pancanga_day_Ec():
    return tithi, masa, m_naksatra, s_naksatra, sunrise, sunset, moonrise, moonset

def get_pancanga_lunar_month(t="2021-5-31 10:00:00",accuracy=0.01,ayanamsa='citrapaksa',verbose=True):
    t = jce.str_to_astropy(t)
    dict_ = get_masa_start_end_Ec(t=t,accuracy=accuracy,ayanamsa=ayanamsa)["data"]
    nm_time,masa,s_nm_nak = dict_["masa start time"],dict_["masa"],dict_["sun naksatra at month beginning"]
    data = [(1,nm_time)]
    for i in range(1,30):
      if verbose and i%5==0: 
        print("running tithi:",i+1," "*20)
      lon = 12*i
      time_ = jce.solve_moon_time_Ec(lon,t,accuracy=accuracy)
      data += [(i+1,jce.astropy_to_datetime(time_))]
    info = {"this file contains tithis and their start times, for the masa containing the time":jce.astropy_to_datetime(t),
            "sun naksatra at month beginning:":s_nm_nak,"masa:":masa}
    return info,data