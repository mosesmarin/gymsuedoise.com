
# gym-sued.py
# Author: Moises Marin
# Date: April 14, 2017
# Purpose: To book a class in a gym website 
# This script should run at first minute of Tuesday or Thursday at Central European Time
# It will book a class the same day of it's execution
##
# Change log
# 2017-Jun-03	Moises	Simplify Notification
#
#
#

import requests 
import sys
from datetime import date
from datetime import timedelta
import calendar
import time
import boto3
import os

reload(sys)
sys.setdefaultencoding('utf-8')

    
print('Loading function')

def lambda_handler(event, context):
    #fetch env variables
    pw_env=os.environ['pw']
    em_env=os.environ['em']
    user_search_id_env=os.environ['user_search_id']
    topic_arn_env=os.environ['topic_arn']
    




    # Define constants
    day_lundi=0
    day_mardi=1
    day_mercredi=2
    day_jeudi=3
    day_vendredi=4
    day_samedi=5
    day_dimanche=6

    cardio_pump=46
    cardio_famille=60
    paris_10_chaudron=349
    paris_9_bergere=1

    base_link_reserve='https://www.gymsuedoise.com/resa/bk/?id='
    logon_link='https://www.gymsuedoise.com/lo/'
    logout_link='https://www.gymsuedoise.com/lt/'
    search_course_link='https://www.gymsuedoise.com/cours/list/'

    # Define user values
    credentials = { 'em': em_env, 'pw': pw_env } 
    user_search_id=user_search_id_env

    
    #Define vars for SNS message
    text_reserve=''
    client = boto3.client('sns')

    #Set date for the class
    offset=0
    my_date = date.today()+ timedelta(days=offset)
    date_value= calendar.day_name[my_date.weekday()]
    if date_value=='Monday':
        day_of_class=day_mardi
        time_of_class='19:30'
        place_of_class=paris_10_chaudron
        cardio_class=cardio_pump
    elif date_value=='Wednesday':
        day_of_class=day_jeudi
        time_of_class='19:30'
        place_of_class=paris_10_chaudron
        cardio_class=cardio_pump
    elif date_value=='Saturday':
        day_of_class=day_dimanche
        time_of_class='10:15'
        place_of_class=paris_10_chaudron
        cardio_class=cardio_famille
    else:
        day_of_class=0
        time_of_class='00:00'
        cardio_class=0
        place_of_class=0


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


    if ( date_value=='Monday' or date_value=='Wednesday' or date_value=='Saturday' ):    
        #log in, find id, reserve, log out 
        with requests.Session() as s:
            #login	
            print '[1]---------------------------------------------------------------------------'
            p = s.post(logon_link, data=credentials) 
            #print p.text
    
            #find id of class
            print '[FINDID]---------------------------------------------------------------------------'
            searchload = {'class_search_locationid':place_of_class,
                                 'class_search_day':day_of_class,
                        'class_user_search_recover':user_search_id,
                               'class_search_level':cardio_class} 
            p = s.post(search_course_link, data=searchload) 
            #print p.text 
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
            link_reserve=link_reserve.replace("&amp;","&")

            print '\nUse link below to reserve\n<br>'
            print link_reserve
            print '<br>\nUse link above to reserve\n<br>'
            text_reserve=p.text
            text_reserve=''

    
            #response = client.publish(
            #TopicArn=topic_arn_env,
            #Message='1\n'+link_reserve+'\n'+text_reserve
            #)
                          
	        #Use link to go to book class page
            print '[2]---------------------------------------------------------------------------'
            r = s.get(link_reserve) 
            #print r.text
            with open("/tmp/Output2.txt", "w") as text_file:
                text_file.write(r.text)
            course_id=''  
            with open("/tmp/Output2.txt") as f:
                for line in f:
                    if 'resa/bk2' in line:
                        #print line
                        class_html=line.split('action="' ) 
                        html_course_id=class_html[1].split('"') 
                        course_id=html_course_id[0]
            link_reserve=course_id
            print '\nUse link below to reserve\n<br>'
            print link_reserve
            print '<br>\nUse link above to reserve\n<br>'
            text_reserve=r.text
            
            #Send post confirmation page
            #response = client.publish(
            #TopicArn=topic_arn_env,
            #Message='2\n'+link_reserve+'\n'+text_reserve
            #)
            
            #Fetch confirmation results
            date_value=''
            time_value=''
            with open("/tmp/Output2.txt") as f:
                for line in f:
                    if 'cours a bien' in line:
                        line_56=line.split('<th colspan="6" class="big">' ) 
                        line_56_after=line_56[1].split('</th></tr></thead><tbody>') 
                        date_value=line_56_after[0]
                        line_56=line.split('</td><td><b>' ) 
                        line_56_after=line_56[1].split('</b></td><td>') 
                        time_value=line_56_after[0]

            response = client.publish(
            TopicArn=topic_arn_env,
            Message='Reservation done for:\n'+date_value+'\n'+time_value
            )


	        #Reserve a place
            print '[3]---------------------------------------------------------------------------'	
            #r = s.get(link_reserve) 
            #print r.text   
            #text_reserve=r.text
    
            #response = client.publish(
            #TopicArn=topic_arn_env,
            #Message='3\n'+link_reserve+'\n'+text_reserve
            #)

            #logout
            print '[4]---------------------------------------------------------------------------'	
            r = s.get(logout_link) 
            #print r.text
    else:
        print 'Don\'t run on ' + date_value
        link_reserve='Don\'t run on ' + date_value
    
    #time_indicator=time.strftime("%d/%m/%Y %H:%M:%S")

    return link_reserve