# JivaCalendar

JivaCalendar_Ecliptic.py is the backend file. It contains core calculations etc.

JivaCalendar_FrontEnd.py contains high level functions that you may want to use. Using the front end functions should be intuitive, 
and please let me know if it is not, so I can imporve it. We need to add functions to this file according to what Kamal Tyagi Maharaja says.

Look at Example.ipynb

Note: The code is almost complete. Usage example:

```python
import JivaCalendar_FrontEnd as jcf
# date = (y,m,d) and time in (h,m,s). location is (latitude,longitude), 
# lat and lon are both being in degrees. North is positive and East is positive.
cal = Pancanga(date=(2021,6,25),time=(14,0,0),location=(0,0),timezone='EST')
month_data = cal.get_pancanga_gregorian_month_Ec(verbose=True)
# month_data is a list of dictionaries. I'll probably change it to a dataframe later.
```

You can change the accuracy of the compute by ```accuracy``` parameter. This parameter is the error value in degrees that we tolerate. For example, ```accuracy=0.01``` would mean that the tithi starting time (and all other calculations) are computed with the locations of the moon coming within ```0.01 degrees``` of the actual correct position.

Ayanamsa is the difference between sidereal and synodic zodiac. This difference occurs because of the precession of the Earth's axis. Since the ayanamsa changes with time, the calibration of the ```ayanamsa``` parameter in the code is at J2000, i.e. at 1 Jan, 2000.
 




To Do's for Utkarsh

1. Check extensively for solve_moon_time_Ec(lon,t) and find_new_moon_time_Ec(t). Delete if not found anywhere.
2. Add more timezones

Cheers! Radhe!
