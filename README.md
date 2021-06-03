# JivaCalendar

JivaCalendar_Ecliptic.py is the backend file. It contains core calculations etc.

JivaCalendar_FrontEnd.py contains high level functions that you may want to use. Using the front end functions should be intuitive, 
and please let me know if it is not, so I can imporve it. We need to add functions to this file according to what Kamal Tyagi Maharaja says.

Note: The code is almost complete. Usage example:

```python
import JivaCalendar_FrontEnd as jcf
# date = (y,m,d) and time in (h,m,s). location is (latitude,longitude), 
# lat and lon are both being in degrees. North is positive and East is positive.
cal = Pancanga(date=(2021,6,25),time=(14,0,0),location=(0,0),timezone='EST')
month_data = cal.get_pancanga_gregorian_month_Ec(verbose=True)
# month_data is a list of dictionaries. I'll probably change it to a dataframe later.
```
 




To Do's for Utkarsh

1. Write documentation.
2. Replace solve_moon_time_Ec(lon,t) and find_new_moon_time_Ec(t) with solve_body_time_Ec(lon,t,body='moon_synodic') and solve_body_time_Ec(lon=0,t,body='moon_synodic'). Check extensively.

Cheers! Radhe!
