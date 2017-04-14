# gym-sued-git.py
# Author: Moises Marin
# Date: April 14, 2017
# Purpose: To book a class in a gym website 
# This script should run at first minute of Tuesday or Thursday at Central European Time
# It will book a class the same day of it's execution

import requests 
import sys
from datetime import date
from datetime import timedelta
import calendar
reload(sys)
sys.setdefaultencoding('utf-8')

# Define constants
day_mardi=1
day_jeudi=3
cardio_pump=46
paris_10_chaudron=349
base_link_reserve='https://www.gymsuedoise.com/resa/bk/?id='
logon_link='https://www.gymsuedoise.com/lo/'
logout_link='https://www.gymsuedoise.com/lt/'
search_course_link='https://www.gymsuedoise.com/cours/list/'
time_of_class='19:30'

# Define user values
credentials = { 'em': 'e-mail@gmail.com', 'pw': 'password' } 
user_search_id=999999999

#Set date for the class
offset=5
my_date = date.today()+ timedelta(days=offset)
date_value= calendar.day_name[my_date.weekday()]
if date_value=='Monday':
    day_of_class=day_mardi
elif date_value=='Wednesday':
    day_of_class=day_jeudi
else:
    day_of_class=0


# These are parameters used to book a class
# Ideally these are retrieved after logon
# And need not be hardcoded
#
# Link to reserve class
# https://www.gymsuedoise.com/resa/bk/?id=337854
#
# Mardi 19:30
# Tue 4/18 is id 363837
# Tue 4/25 is id 363838
#
# Jeudi 19:30
# Thu 4/20 is id 337854
# Thu 4/27 is id 337855


if ( date_value=='Monday' or date_value=='Wednesday' ):    
    #log in, find id, reserve, log out 
    with requests.Session() as s:
        #login	
        print '[1]---------------------------------------------------------------------------'
        p = s.post(logon_link, data=credentials) 
        print p.text
    
        #find id of class
        print '[FINDID]---------------------------------------------------------------------------'
        searchload = {'class_search_locationid':paris_10_chaudron,
                             'class_search_day':day_of_class,
                    'class_user_search_recover':user_search_id,
                           'class_search_level':cardio_pump} 
        p = s.post(search_course_link, data=searchload) 
        print p.text 
        with open("/tmp/Output.txt", "w") as text_file:
            text_file.write(p.text)
        course_id=''  
        with open("/tmp/Output.txt") as f:
            for line in f:
                if time_of_class in line:
                    #print line
                    class_html=line.split('www.gymsuedoise.com/cours/detail/?id=' ) 
                    html_course_id=class_html[1].split('"') 
                    course_id=html_course_id[0]
        link_reserve=base_link_reserve+course_id
        print '\nUse link below to reserve\n<br>'
        print link_reserve
        print '<br>\nUse link above to reserve\n<br>'
                          
	    #Use link to book class
        print '[2]---------------------------------------------------------------------------'
        r = s.get(link_reserve) 
        print r.text
    
	    #logout
        print '[3]---------------------------------------------------------------------------'	
        r = s.get(logout_link) 
        print r.text
else:
    print 'Don\' run on ' + date_value
    
    

