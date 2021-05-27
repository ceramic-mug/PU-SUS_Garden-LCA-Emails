############################################################
# Title: generatePlots.py
# Author: Joshua Eastman
#
# Description:
#   This script takes in a .csv of garden LCA water and
#   produce data and outputs a directory in the current
#   working directory containing a set of figures for 
#   each participant.
#
# Input args:
#   [1] name of data file (e.g. gardenData.csv)
#
# Input directory structure:
#   root
#   |-  generatePlots.py
#   |-  gardenData.csv (or your datafile)
#   ...
#
# Output directory structure:
#   root
#   |-  generatePlots.py
#   |-  gardenData.csv (or your datafile)
#   |-  yyyy-mm-dd_out
#       |-1_fig.png
#       |-2_fig.png
#       ...
#   ...
#
#   where 1_fig.png and 2_fig.png refer to output figures
#   for participants 1 and 2, respectively
############################################################

# (1) Import packages

import pandas as pd # for handling tabular data
import matplotlib.pyplot as plt # for plotting
import matplotlib # for changing plotting params
import matplotlib.dates as mdates # for formatting dates
from datetime import datetime # for date handling
import sys # for reading command-line args
import os # for creating a directory to hold output
import LCAutils

############################################################

# (2) Get name of datafile and read data

inFile = input('Data file name: ')
dat = pd.read_csv(inFile)

############################################################

# (3) Build output folder

# get rid of columns without data
dat = LCAutils.removeUnwantedColumns(dat)

# get dates from column names
dates = LCAutils.dates(dat)
lastDate = dates[-1]

# check to see if output folder is created

outDir = datetime.strftime(lastDate, r'%Y-%m-%d_out')

if not os.path.exists(outDir):
    os.makedirs(outDir)

############################################################

# (4) Construct line plot for each participant

water_color = 'cornflowerblue'
produce_color = 'limegreen'
myFmt = mdates.DateFormatter('%b-%d')

for participant in dat.Participant.unique():

    # create the figure
    fig, (ax1, ax2) = plt.subplots(2,1, dpi=300, \
        figsize=(10,4), sharex=True)

    # select the subset of the dataframe corresponding to
    # the participant in question
    cut = dat[dat['Participant'] == participant]

    # create lists with values from the cut for water
    # and produce
    water = cut.loc[cut.DataType == "Water", \
        [date.strftime(r'%m/%d') for date in dates]].\
            values.tolist()[0]

    produce = cut.loc[cut.DataType == "Produce ", \
        [date.strftime(r'%m/%d') for date in dates]].\
            values.tolist()[0]

    # create the plots
    ax1.set_axisbelow(True)
    ax1.grid(axis='y',color='k',linewidth=0.5)

    ax1.fill_between(dates, water, y2=0, \
        color=water_color, alpha=1)
    ax1.yaxis.label.set_color(water_color)
    ax1.set_ylabel('')
    ax1.set_xticks([])
    ax1.set_xticklabels('')
    ax1.tick_params(axis=u'both', which=u'both',length=0)

    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_title('Water Input (Gallon)',color=water_color,\
        weight='bold',style='italic')

    ax2.set_axisbelow(True)
    ax2.grid(axis='y',color='k',linewidth=0.5)


    ax2.fill_between(dates, produce, y2=0, \
        color=produce_color, alpha=1)
    ax2.yaxis.label.set_color(produce_color)
    ax2.set_ylabel('')

    ax2.set_xticks(dates)
    ax2.set_xticklabels([date.strftime('%b-%d') for date \
        in dates])
    ax2.xaxis.set_major_formatter(myFmt)
    ax2.tick_params(axis=u'both', which=u'both',length=0)

    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.set_title('Produce Yield (kg)',color=produce_color,\
        weight='bold',style='italic')

    fig.suptitle('Garden Statistics for '+str(participant),\
        weight='bold',
        y=1.05)

    # save the plots
    fig.savefig(outDir+'/'+str(participant)+'_line.png', \
        bbox_inches='tight')

############################################################

# (5) Construct
