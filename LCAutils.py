import pandas as pd
import sys
from datetime import datetime
import glob
import numpy as np
from sklearn.linear_model import LinearRegression as LR

############################################################
# Function: removeUnwantedColumns
# 
# Input arguments:
#   (1) pandas DataFrame
#
# Returns:
#   pandas Dataframe
#
# Description:
#   Returns pandas DataFrame with unnamed columns removed
############################################################

def removeUnwantedColumns(dat):
    keys = dat.keys()
    for key in keys:
        if 'Unnamed'in key:
            dat = dat.drop(columns=key)
    return dat

############################################################
# Function: dates
# 
# Input arguments:
#   (1) pandas DataFrame
#
# Returns:
#   [datetime datetime]
#
# Description:
#   Returns list of dates, columns of input DataFrame
############################################################

def dates(dat): 
    return \
    [datetime.strptime(
        str(datetime.now().year)+r'/'+key,r'%Y/%m/%d') 
    for key in dat.keys()[3:]]

############################################################
# Function: figureDict
#
# Input arguments:
#   (1) str (figure directory)
#   (2) [str] (participants)
#
# Returns:
#   {str (participant): [str] (figures relative addresses)}
############################################################

def figureDict(figdir, parts):
    fd = {}
    for p in parts:
        fd[p] = {}
        fd[p]['line'] = glob.glob(figdir+'/'+p+'_line.png')[0]
    return fd

############################################################
# Function: statsDict
#
# Input arguments:
#   (1) pandas DataFrame (data)
#
# Returns:
#   {str (participant): {str (stat): number (value)}}
#
# Description:
#   Present statistics include
#       • Total Water (Gal)
#       • Total Produce (kg)
#       • Mean Water (Gal)
#       • Mean Produce (kg)
#       • Percent change in water from last week
#       • Percent change in produce from last week
#       • Change in water use over time (Gal/week)
#       • Yield produce per unit water (kg/Gal)
############################################################

def statsDict(dat):

    sd = {}

    participants = dat.Participant.unique()
    
    dates_ = dates(dat)

    for p in participants:
        
        cut = dat[dat['Participant'] == p]

        if type(p) != str:
            p = str(p)

        sd[p] = {}
    
        water = cut.loc[cut.DataType == "Water", \
            [date.strftime(r'%m/%d') for date in dates_]].\
                values.tolist()[0]

        produce = cut.loc[cut.DataType == "Produce ", \
            [date.strftime(r'%m/%d') for date in dates_]].\
                values.tolist()[0]

        # totals
        sd[p]['Total produce'] = np.nansum(produce)
        sd[p]['Total water'] = np.nansum(water)

        # averages
        sd[p]['Mean produce'] = np.mean(produce)
        sd[p]['Mean water'] = np.mean(water)

        # percent change over last weeks
        sd[p]['Dif produce'] = (produce[-1]-produce[-2])/\
            produce[-2]*100
        sd[p]['Dif water'] = (water[-1]-water[-2])/\
                                water[-2]*100

        # change over time using linear regression
        waterWeeks = np.arange(len(water))[:,None]
        waterReg = LR().fit(waterWeeks, water)
        sd[p]['dWater/dt'] = waterReg.coef_[0]

        # produce yilded per unit water input
        sd[p]['Yield per water'] = np.sum(produce)/\
                                   np.sum(water)

    return sd
        

