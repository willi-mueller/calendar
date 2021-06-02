# -*- coding: utf-8 -*-
"""JivaCalendar_Ecliptic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Az15wceEMXhHZUY9d5uqn9tCFAxfAEuW

# Introduction

The final calendar code will be contained in 2 files. One is labelled JivaCalendar_GCRS and the other JivaCalendar_Ecliptic. This is because there are two ways of doing calculation, and I'm not sure which one the Indian system uses. I think the Ecliptic one is the one we need but I'm keeping both intact for now.

# Dependencies and Utils
"""

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import solar_system_ephemeris, EarthLocation
from astropy.coordinates import get_body_barycentric, get_body, get_moon, get_sun
from astropy.coordinates import SkyCoord, GCRS, ICRS, Angle, GeocentricTrueEcliptic, GeocentricMeanEcliptic
import numpy as np
from scipy.optimize import fsolve
from datetime import date, timedelta, datetime, time

from astropy.coordinates import solar_system_ephemeris
solar_system_ephemeris.set('jpl')

from mathjspy import MathJS
mjs = MathJS()

## ----------UTILS------------
def str_to_astropy(t):
    return Time(t)

def datetime_to_astropy(date_):
  # date_ is a datetime.date object. We want to convert it to astropy.time.Time
    return Time(date_.strftime('%Y-%m-%d %H:%M:%S'))

def astropy_to_date(t): # Converts only to date. Truncates
    date_,time = t.value.split()
    year,month,day = [mjs.eval(s) for s in date_.split('-')]
    return date(year,month,day)

def astropy_to_datetime(t):
    date_,time = t.value.split()
    year,month,day = [mjs.eval(s) for s in date_.split('-')]
    hr,min,sec = [mjs.eval(s) for s in time.split(':')]
    return datetime(year,month,day,hr,min,int(sec))

Rasi_list = ["Mesa","Rsabha","Mithuna","Karkataka","Simha","Kanya","Tula","Vrscika","Dhanus","Makara","Kumbha","Meena"]

Maasa_list = ["Vaisakha","Jyestha","Asadha","Sravana","Bhadrapada","Asvina","Kartika","Mrgashirsha","Pausa","Magha","Phalguna","Caitra"]

Naksatra_list = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrighasira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 
                 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishaka', 'Anuradha', 'Jyestha', 'Moola', 
                 'Purvashada', 'Uttarashada', 'Sharavan', 'Dhanishta', 'Shatabisha', 'Purvabhadra', 'Uttarabhadra', 'Revati']

maasa_gaps = [28, 33, 34, 35] 
# NOTE: I don't actually use this at all. My method is more fundamental, so is more reliable. Read the documentation for more info
# The gaps in adhika maasa, in months. 
# I think they're actually lunar months though, since the mean of the list is exactly 32.5. Predictions also seem to be correct with this assumption.
# Source: "https://sriramgurujala.com/what-is-adhik-maasam-or-adhik-maas-how-do-we-calculate-it/"

lunar_month = 29.5306 #length of lunar month in days

coord_Revati_ICRS = SkyCoord(ra='01h13m45.17477s', dec='+7d34m31.2745s', frame='icrs', equinox=Time(2000, format='jyear')) 
coord_Revati_Ec = coord_Revati_ICRS.transform_to(GeocentricTrueEcliptic()) # Geocentric True Ecliptic coordinates of Revati (Zeta Piscium A)
ayanamsa_revati = coord_Revati_Ec.lon
#coord_Revati_ICRS = SkyCoord(ra='01h13m45.17477s', dec='+7d34m31.2745s', distance=170*u.lyr, frame='icrs', equinox=Time(2000, format='jyear')) 
# The coordinate conversions still work even if we don't specify any distance. 
# Maybe they treat the distance as infinity? Because the resulting GCRS was barely different from ICRS.

coord_Spica_ICRS = SkyCoord(ra='13h25m11.579s', dec='−11d09m40.75s', frame='icrs', equinox=Time(2000, format='jyear')) 
coord_Spica_Ec = coord_Spica_ICRS.transform_to(GeocentricTrueEcliptic())
ayanamsa_citrapaksa = coord_Spica_Ec.lon - Angle('180d')

"""# Getting Solar and Lunar Longitudes etc"""

def get_sun_moon_Ec(t = Time("J2000")): # Ec=Ecliptic
    m = get_body('moon',t)
    m_inf = SkyCoord(ra=m.ra, dec=m.dec, frame='gcrs')
    m_ec = m_inf.transform_to(GeocentricTrueEcliptic())

    s = get_body('sun',t) 
    s_inf = SkyCoord(ra=s.ra, dec=s.dec, frame='gcrs')
    s_ec = s_inf.transform_to(GeocentricTrueEcliptic())
    return m_ec,s_ec

def get_angle_tithi_Ec(t= Time("J2000")):
    m,s = get_sun_moon_Ec(t=t)

    m_ra = m.lon.degree
    m_dec = m.lat.degree

    s_ra = s.lon.degree
    s_dec = s.lat.degree

    ms_angle = m_ra - s_ra # moon-sun angle. 
    ms_angle = ms_angle%360 
    tithi = (ms_angle)/12

    return ms_angle,tithi

"""# Finding New Moon and Solving for time"""

def find_new_moon_Ec(t_approx):
    # Find the exact date (+/-1 day) of new moon, given an approximate date. 
    # Input either in astropy.time.Time or datetime.date
    date_ = astropy_to_date(t_approx) # Extracting only the date. No time
    t = datetime_to_astropy(date_)
    t_af = Time(datetime_to_astropy(date_+timedelta(days=1)))  # one day later
    t_af2 = Time(datetime_to_astropy(date_+timedelta(days=2)))  # 2 days later
    t_bef = Time(datetime_to_astropy(date_-timedelta(days=1))) # one day before
    ang,tit = get_angle_tithi_Ec(t) 
    ang_bef, tit_bef = get_angle_tithi_Ec(t_bef)
    ang_af, tit_af = get_angle_tithi_Ec(t_af)
    ang_af2, tit_af2 = get_angle_tithi_Ec(t_af2)

    if ang_bef>330 and ang<30:
      correct_date = t_bef
    elif ang>330 and ang_af<30:
      correct_date = t
    elif ang_af>330 and ang_af2<30:
      correct_date = t_af
    else:
      return 0
    return correct_date

def find_new_moon_date_before_Ec(t=Time("J2000")):
    # Given a date, find the date the month starts by calculating the nearest earler new_moon
    ang,_ = get_angle_tithi_Ec(t)
    approx_delta = timedelta(days=ang/360*lunar_month)
    approx_date = datetime_to_astropy(astropy_to_date(t)-approx_delta)
    exact_date = find_new_moon_Ec(approx_date)
    if exact_date==0:
        new_approx_date = datetime_to_astropy(astropy_to_date(approx_date) + timedelta(days=-3))
        exact_date = find_new_moon_Ec(new_approx_date)
    if exact_date==0:
        new_approx_date = datetime_to_astropy(astropy_to_date(approx_date) + timedelta(days=+3))
        exact_date = find_new_moon_Ec(new_approx_date)
    return exact_date

def find_new_moon_time_Ec(t=Time("J2000"),accuracy=0.1):
    # Using the above two functions,  this one finds the exact new moon date and time. 
    # accuracy is the maximum angle difference in degrees from 360deg 
    date_ = find_new_moon_date_before_Ec(t=t)
    ang,_ = get_angle_tithi_Ec(date_)
    ang = 360 - ang
    approx_time = datetime.combine(astropy_to_date(date_),time(0,0,0))
    iter = 0
    while abs(ang)>accuracy:
        iter += 1
        if iter>100:
            raise Exception("Exceeded 100 iterations inside find_new_moon_time")
        approx_delta = timedelta(seconds=ang/360*lunar_month*24*60*60)
        approx_time += approx_delta 
        ang,_ = get_angle_tithi_Ec(t=datetime_to_astropy(approx_time))
        
        if ang<100:
            ang = -ang
        else:
            ang = 360 - ang
        # This if else statement below is so that if moon longitude<sun, then ang>0, else ang>0. 
        # By default if moon is 2 degrees behind sun, then ang=358. We want that to be 2degrees
        # if moon-sun=2degrees then ang=-2
        # RETIRING THIS because if moon lon = 359deg, and sun=0.5deg, this causes problems. Eg for the new_moon around 21st Mar, 2099. 
        #m,s = get_sun_moon_Ec(datetime_to_astropy(approx_time))
        #if m.lon<s.lon:   
        #  ang = 360 - ang
        #else:
        #  ang = -ang

    return datetime_to_astropy(approx_time)

## --------------------NOTE:: Need to build in some method below to avoid error close to 360 degree.
def solve_moon_time_Ec(lon,t,accuracy=0.1):
    # in the month of t, solve for the time at which sun-moon=lon
    nm_date = find_new_moon_time_Ec(t=t) # new_moon date
    nm_date = astropy_to_datetime(nm_date)
    approx_time = nm_date + timedelta(hours=lon/360*lunar_month*24)
    ang,_ = get_angle_tithi_Ec(datetime_to_astropy(approx_time))
    del_ang = lon - ang
    iter = 0
    while abs(del_ang)>accuracy:
        iter += 1
        if iter>100:
            raise Exception("Exceeded 100 iterations inside find_new_moon_time")
        approx_delta = timedelta(seconds=del_ang/360*lunar_month*24*60*60)
        approx_time += approx_delta 
        ang,_ = get_angle_tithi_Ec(t=datetime_to_astropy(approx_time))
        del_ang = lon-ang
    return datetime_to_astropy(approx_time)
        # This if else statement below is so that if moon longitude<sun, then ang>0, else ang>0. 
        # By default if moon is 2 degrees behind sun, then ang=358. We want that to be 2degrees
        # if moon-sun=2degrees then ang=-2


### The func below is to do the same job but with fsolve. 
### It does't work because fsolve needs to pass arrays as the input, and datetime etc dont allow that.
def find_new_moon_time_fsolve_Ec(t=Time("J2000"),accuracy=1):
    # Using the above two functions, find the exact new moon date. 
    # Then use this one to find the time.
    # accuracy is the maximum angle difference in degrees from 360deg 
    ang,tit = get_angle_tithi_Ec(t)
    approx_date = astropy_to_datetime(t) - timedelta(days=ang/360*lunar_month)
    print(approx_date)
    def ang_solver(t_):
      del_ = timedelta(minutes=t_)
      ang_,_ = get_angle_tithi_Ec(approx_date+del_)
      print(ang_)
      return ang_a
    
    t_solution = fsolve(ang_solver, 0)
    datetime_solution =  approx_date + timedelta(t_solution)
    print(t_solution)
    print(datetime_solution)
    #return datetime_to_astropy(approx_time)



"""# Getting Naksatra and Rasi Longitudes, and Finding Naksatra and Rasi for a given Longitude"""

def get_ayanamsa(ayanamsa):
    # Ayanamsa lookup table
    if type(ayanamsa) in [float,int]: return Angle(f"{ayanamsa}d")
    elif type(ayanamsa)==Angle: return ayanamsa
    elif type(ayanamsa)==str: 
        ayanamsa = ayanamsa.lower()
        if ayanamsa in ['lahiri','chitra','citra','spica','citrapaksa','chitrapaksa','citrapaksha','chitrapaksha']:
            return ayanamsa_citrapaksa
        if ayanamsa in ['revati','zeta piscium','piscium']:
            return ayanamsa_revati
        else:
            raise Exception("ayanamsa can be 'citrapaksa' or 'revati'")
    else:
        raise Exception("ayanamsa must be float, int, string or astropy.coordinates.angles.Angle")

def naksatra_lon_Ec(ayanamsa='citrapaksa'):
    # List of Naksatra longitudes (in the ecliptic, so equally spaced). With J2000 equinox as coordinate axis. 
    # Ayanamsa is the starting point of the Naksatras
    ayanamsa = get_ayanamsa(ayanamsa)
    diff = Angle('13d20m')
    naksatra_lon_list = [(ayanamsa + n*diff)%Angle("360d") for n in range(27)]
    return naksatra_lon_list

def rasi_lon_Ec(ayanamsa='citrapaksa'):
    # List of Rāśi longitudes (in the ecliptic, so equally spaced). With J2000 equinox as coordinate axis, and geocentric origin.
    # Ayanamsa is the starting point of the Naksatras
    ayanamsa = get_ayanamsa(ayanamsa)
    diff = Angle('30d')
    rasi_lon = [(ayanamsa + n*diff)%Angle("360d") for n in range(12)]
    return rasi_lon

# Note that the below functions (to find Naksatra for a given longitude) don't use the above functions to generate a list of 
# Naksatra longitudes. Just because there is no need to, so just to save time and compute.
def find_naksatra_Ec(lon,ayanamsa='citrapaksa'):
    if type(lon) in [int,float]: lon = Angle(f"{lon}d")
    ayanamsa = get_ayanamsa(ayanamsa)
    lon = (lon-ayanamsa)%Angle("360d")
    num = int(lon/Angle("13d20m"))
    nak = Naksatra_list[num]
    return num, nak

def find_rasi_Ec(lon,ayanamsa='citrapaksa'):
    if type(lon) in [int,float]: lon = Angle(f"{lon}d")
    ayanamsa = get_ayanamsa(ayanamsa)
    lon = (lon-ayanamsa)%Angle("360d")
    num = int(lon/Angle("30d"))
    rasi = Rasi_list[num]
    return num, rasi

