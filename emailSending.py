############################################################
# Title: emailSending.py
# Author: Joshua Eastman
#
# Description:
#   This script sends personalized emails to each
#   email address in a list of email addresses with
#   corresponding text and figures.
#
# Input args:
#   [1] name of data file (e.g. gardenData.csv)
#
# Input directory structure:
#   root
#   |-  emailSending.py
#   |-  gardenData.csv (or your datafile)
#   |-  yyyy-mm-dd_out # which contains figues
#       |-1_fig.png
#       |-2_fig.png
#       ...
#
#   No change in directory structure will be effected
#
############################################################

# (1) Import packages

import smtplib, ssl # for sending emails
import getpass # for collecting email password securely
import pandas as pd # for reading .csv with emails
from datetime import datetime # for getting the current date
import sys # for reading command-line arguments
import LCAutils # for LCA-specific dataframe manipulations
import numpy as np # for data manipulation
from email.message import EmailMessage # see below
from email.utils import make_msgid # for building message
import mimetypes # see above

############################################################

# (2) Set email configuration

port = 465  # For SSL
password = getpass.getpass(prompt='Email password: ')
sender_email = "jeastman@princeton.edu"  # Enter your email

# Create a secure SSL context for email sending
context = ssl.create_default_context()

############################################################

# (3) Get email addresses and dates info from dataframe

dat = pd.read_csv('./GardenDataTest.csv')

dat = LCAutils.removeUnwantedColumns(dat)
dates = LCAutils.dates(dat)
lastDate = dates[-1]

participants = [str(i) for i in dat.Participant.unique()]
emails = dat.Email.unique()

############################################################

# (4) Get participant figure dictionary and statistics

outDir = lastDate.strftime(r'%Y-%m-%d')+'_out'
figureDict = LCAutils.figureDict(outDir, participants)
statsDict = LCAutils.statsDict(dat)

############################################################

# (5) Craft the message, with placeholders for figures
#     and personalized information


# 0: figure with line graph of water and produce
# 1: name of participant
# 2: percent change in produce yield in last week
# 3: percent change in water use in last week
# 4: total water used
# 5: total produce yielded
# 6: average water usage
# 7: increasing or decreasing
# 8: rate of increase or decrease per week

message = """\
<html>
    <body>
        <img src="cid:{0}" width="100%">

        <p> Dear {1},</p>
    
    <p>Your garden yielded {2} produce and used {3} water this week than last week. Until now, you've used a total of {4} Gallons of water and gathered a total of {5} kg produce.</p>
    
    <p>You use an average of {6} Gallons of water per week. During your involvement in our study, your water use has been {7} overall at a rate of {8} Gallons per week.</p>
    </body>
</html>"""

############################################################

# (6) Send messages

# connect to the server and log in to send emails
with smtplib.SMTP_SSL("smtp.gmail.com", port, \
                      context=context) as server:
    
    server.login(sender_email, password)

    # iterate through the participants, conditionally
    # customizing the message for each
    for i in range(len(participants)):

        # name of participant
        p = participants[i]

        # conditionally format
        dWater = statsDict[p]['Dif water']

        if dWater > 0:
            dWater = '{:.1f}'.format(np.abs(dWater))+\
                r'% more'
        elif dWater < 0:
            dWater = '{:.1f}'.format(np.abs(dWater))+\
                r'% less'
        else:
            dWater = 'no difference in'

        dProduce = statsDict[p]['Dif produce']

        if dProduce > 0:
            dProduce = '{:.1f}'.format(np.abs(dProduce))+\
                r'% more'
        elif dProduce < 0:
            dProduce = '{:.1f}'.format(np.abs(dProduce))+\
                r'% less'
        else:
            dProduce = 'no difference in'

        dW_dt = statsDict[p]['dWater/dt']
        if dW_dt > 0:
            dW_dt_trend = 'increasing'
        else:
            dW_dt_trend = 'decreasing'

        # build the email message
        msg = EmailMessage()

        # Email subject
        msg['Subject'] = 'Princeton SUS Lab | Garden Life-Cycle Assesment Statistics'
        
        # Configure image type
        lineplot_cid = make_msgid(domain='xyz.com')

        # Add participant-specific data to email
        # [0] lineplot_cid[1:-1] is the image placeholder
        # [1] participant name
        # [2] change in produce yield this week
        # [3] change in water input this week
        # [4] total water input
        # [5] total produce yield
        # [6] average water input
        # [7] linear regression increasing or decreasing
        # [8] linear regression slope for water input

        message_personalization = [
            lineplot_cid[1:-1], # [0]
            p, # [1]
            dProduce, # [2]
            dWater, # [3] 
            '{:.1f}'.format(statsDict[p]['Total water']), # [4] 
            '{:.1f}'.format(statsDict[p]['Total produce']), # [5] 
            '{:.1f}'.format(statsDict[p]['Mean water']), # [6] 
            dW_dt_trend, # [7] 
            '{:.1f}'.format(np.abs(dW_dt)) # [8] 
        ]

        # attach the html content to the message with
        # personalized info
        msg.add_alternative(message.format(
            *message_personalization
        ), subtype='html')

        # write to output, to know what's going on
        print('Sending email to ',p)

        # Embed lineplot to email at placeholder location
        with open(figureDict[p]['line'], 'rb') as img:

            # know the Content-Type of the image
            maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')

            # attach it
            msg.get_payload()[0].add_related(img.read(), 
                                                maintype=maintype, 
                                                subtype=subtype, 
                                                cid=lineplot_cid)

        # send it
        server.sendmail(sender_email, emails[i],msg.as_bytes())