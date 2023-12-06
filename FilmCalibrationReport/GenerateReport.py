# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 11:16:22 2023

This is the report generator script for Rad Source Film Readers.

@author: JGarner
"""

import pandas as pd
import numpy as np
import csv
import math
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import os
import datetime as dt
from datetime import datetime
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors

#******************************************************************************
#
#   Controls
#
#******************************************************************************

savePlots = True
saveReport = True
saveData = False

#******************************************************************************
#
#   File Saving, Loading and UID
#
#******************************************************************************

#first, get the uid
_year = dt.datetime.now().year
_day = dt.datetime.now().day
_month = dt.datetime.now().month
sec = dt.datetime.now().second + dt.datetime.now().minute * 60 + dt.datetime.now().hour * 3600
year_s = str(_year)
day_s = '0' + str(_day) if _day < 10 else str(_day)
month_s = '0' + str(_month) if _month < 10 else str(_month)
uintSerialNumber = '12411'
uid = 'RS_' + year_s + month_s + day_s + str(sec).format(width = 5)

deviceType = 'FilmReader'

fileRootPrefix = 'Calibrations_' + deviceType + '/' + uintSerialNumber + '/'

filePrefix_Report = 'Reports/'
filePrefix_Plot = 'Plots/'
filePrefix_Data = 'Data/'

fileName_Report = 'RadSource_' + deviceType + '_SN' + uintSerialNumber + '_CalibrationReport_' + uid +'.pdf'
fileName_Plot = 'RadSource_' + deviceType + '_SN' + uintSerialNumber + '_CalibrationPlot_' + uid + '.png'
fileName_Data = 'RadSource_' + deviceType + '_SN' + uintSerialNumber + '_CalibrationData_' + uid + '.csv'

Revision = 'a'

filePath_RadSourceLogo = 'RadSourceLogo.png'

deviceID = 'DR4-009'
filmLotNumber = '01182201'
filmLotExpDate = '7/18/2024'
procedureDate = '7/7/2023'

tempCal = '21'
pressCal = '101.325'
relativeHum = '31'
calProc = 'BU-WI-0010'
filmType = 'EBT3-High'

#******************************************************************************
#
#   Report Information
#
#******************************************************************************

techName = "Jacob Garner, B.S."
infoRadCal = ['RAD-008', 'ADDM+', '47-1380', '10X6-0.6-3', '02-0815', '6/13/2024']
infoGenerator = ['Spellman X4119', '140690036-A01865']
infoTube = ['Quastar DT-1084', '9614-7R']
infoTubePower = ['4 kW', '155 kV', '25 mA']

#******************************************************************************
#
#   Methods
#
#******************************************************************************



#******************************************************************************
#
#   Data Import and Parsing
#
#******************************************************************************

dataFile = 'data.csv'
#first, pull in the csv file as a dataframe
df = pd.read_csv(dataFile)

#view the data to make sure it is proper
print(df)
#get our header for the file to ensure we are pulling the proper columns
header_data = list(df.columns.values)
print(header_data)

#extract all film positions for delta film ODs
filmDOD = []
filmDOD.append(df[header_data[2]].to_numpy())
filmDOD.append(df[header_data[5]].to_numpy())
filmDOD.append(df[header_data[8]].to_numpy())
filmDOD.append(df[header_data[11]].to_numpy())
filmDOD.append(df[header_data[14]].to_numpy())
filmDOD.append(df[header_data[17]].to_numpy())
#Extract the accumulated Doses for each step point | this will ALWAYS be the last column
accumDose = df[header_data[-1]].to_numpy()

filmAVG = []
filmSTD = []
#remember that we want to start from position 1, NOT 0 (which is the background)
for i in range(0,len(filmDOD[0])): 
    _sum = 0
    for j in range(len(filmDOD)):
        _sum += filmDOD[j][i]
    _avg = round(_sum/6, 4)
    _std = round(sum([((x - _avg) ** 2) for x in filmDOD[j]]) / 6 , 4)
    filmSTD.append(_std)
    filmAVG.append(_avg)
print(filmSTD)
#now turn the filmAVG into a numpy array to make it easier to work with!
filmAVG = np.array(filmAVG)

#******************************************************************************
#
#   Regression and Data Fitting
#
#******************************************************************************

#Lets start with the polynomial regression of the data; our x values are the film OD
poly = PolynomialFeatures(degree = 2, include_bias=False)
polyFeatures = poly.fit_transform(filmAVG[1:].reshape(-1,1))
polyReg = LinearRegression()
polyReg.fit(polyFeatures, accumDose[1:])


#Create or OD Range and our Dose Rate Range to match
polyPred = PolynomialFeatures(degree = 2, include_bias=False)
stepSize = (filmAVG[-1] - filmAVG[1])/100
polyPred_ODs = np.arange(filmAVG[1], filmAVG[-1] + stepSize, stepSize)
polyFeaturesPred = polyPred.fit_transform(polyPred_ODs.reshape(-1,1))
polyPred_accumDose = polyReg.predict(polyFeaturesPred)
polyA = polyReg.coef_[0]
polyB = polyReg.coef_[1]
polyC = polyReg.intercept_
polyPred_r2 = polyReg.predict(polyFeatures)
print('Coeffs:    ', polyReg.coef_)
print('Intercept: ', polyReg.intercept_)
print('Correlation: ', r2_score(accumDose[1:], polyPred_r2))
polyCorrelation = r2_score(accumDose[1:], polyPred_r2)

#now for the power regression
#first, lets get the log of our data | we will take the linear regression of our log10 data sets
log10_ODs = []
log10_AccumDose = []
for i in range(1, len(filmAVG)):
    log10_ODs.append(math.log10(filmAVG[i]))
    log10_AccumDose.append(math.log10(accumDose[i]))
#turn our lists into np.arrays
log10_ODs = np.array(log10_ODs)
log10_AccumDose = np.array(log10_AccumDose)
powerReg = LinearRegression()
powerReg.fit(log10_ODs.reshape(-1,1), log10_AccumDose)
#the tricky bit is that the Coeff IS the b Value (our exponent)
powerA = 10 ** powerReg.intercept_
powerB = powerReg.coef_[0]
#now lets get our preditions
powerPred_ODs = polyPred_ODs
powerPred_accumDose = powerA * (powerPred_ODs **powerB)
powerPred_r2 = powerA * (filmAVG[1:] **powerB)
powerCorrelation = r2_score(accumDose[1:], powerPred_r2)
print(powerCorrelation)

#******************************************************************************
#
#   Plotting the Data
#
#******************************************************************************

plotTitle = 'Film ' + '\u0394' + 'OD vs Accumulated Dose (Gy)'
plotYAxis = 'Accumulated Dose (Gy)'
plotXAxis = 'Film ' + '\u0394' + 'OD (using Green ' + '\u03BB' +')'
_colors = ['black', 'seagreen', 'magenta']
legend = ['data', 'Poly Fit', 'Power Fit']
#create Figure (this simplifies some stuffs)
fig = plt.figure(figsize=(8,5))
#plot our data (Scatter and our fits; we will want to show our fit values on the plot as text later)
plt.scatter(filmAVG[1:], accumDose[1:], color = _colors[0])
plt.plot(polyPred_ODs, polyPred_accumDose, color = _colors[1], label = legend[1])
plt.plot(powerPred_ODs, powerPred_accumDose, color = _colors[2], label = legend[2])
#now lets plot our error bars | they are a little small lol
for i in range(len(filmAVG[1:])):
    upper = accumDose[i + 1] + filmSTD[i]
    lower = accumDose[i + 1] - filmSTD[i]
    plt.plot([filmAVG[i+1], filmAVG[i+1]], [upper, lower], color = 'black')
    
    plt.plot()
#format our axes and other chart elements
plt.title(plotTitle, size = 16)
plt.ylabel(plotYAxis)
plt.xlabel(plotXAxis)
plt.xlim((0,1.2))
plt.ylim((0,60))
plt.grid(True)
plt.legend()
plt.text(0.005, 46, 'Poly Fit: ' + str(round(polyA,3)) + 'x\u00b2 + ' + str(round(polyB,3)) + ' + ' + str(round(polyC,3)), size = 11)
#we need to create a superscrip of the poly exponent
plt.text(0.003, 42, 'Power Fit: %s * x'%str(round(powerA,3)) + r'$^{%s} $' %str(round(powerB,3)), size = 11)

if(savePlots):
    if(not(os.path.exists(fileRootPrefix + filePrefix_Plot))):
        os.makedirs(fileRootPrefix + filePrefix_Plot)
    plt.savefig(fileRootPrefix + filePrefix_Plot + fileName_Plot, dpi=300)

#******************************************************************************
#
#   Making our Report!
#
#******************************************************************************

report = Canvas(fileRootPrefix + filePrefix_Report + fileName_Report, pagesize=(8.5 * inch, 11 * inch))
#Set a starting point
center_x = 8.5 * inch / 2
center_y = 11 * inch / 2
#Draw the Title
MainTitle_margin = center_x - 200
current_y = 10.2 * inch - 40
current_x = 0.5 * inch
textObject_Title = report.beginText(MainTitle_margin, current_y)
textObject_Title.setTextOrigin(MainTitle_margin, current_y)
textObject_Title.setFont('Times-Bold', 26)
textObject_Title.textLine("Film Reader Calibration SN" + uintSerialNumber)
report.drawText(textObject_Title)

#Draw our report ID in the upper right hand corner
position_OID = [center_x + 145, 10.2 * inch + 20]
textObject_OID = report.beginText(position_OID[0], position_OID[1])
textObject_OID.setTextOrigin(position_OID[0], position_OID[1])
textObject_OID.setFont('Courier-Bold', 9)
textObject_OID.textLine('Report ID: ' + uid)
report.drawText(textObject_OID)

#HEADER TABLES ****************************************************************
#System Data Table
y_header_tables = 8.5 * inch - 28 - 20
x_header_system_tables = 20
x_header_dosimeter_tables = 340
SystemData = [['System Information', ''],
              ['Calibration Tech:', techName],
              ['Procedure Date:', procedureDate],
              ['Tube Model:', infoTube[0]],
              ['Tube Serial:', infoTube[1]],
              ['Tube Power:', '4 kW Max @ 155 kV'],
              ['Generator Model:', infoGenerator[0]],
              ['Generator Serial:', infoGenerator[1]]]

tableFormat_Headers = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                  ("BOX",       (0,0), (-1,-1), 0.5,  colors.black),
                                  ('BACKGROUND',(0,0), (0, -1), colors.ReportLabLightBlue),
                                  ('BACKGROUND',(0,0), (-1, 0), colors.ReportLabLightBlue),
                                  ('FACE',      (0,0), (0,-1), 'Times-Bold'),
                                  ('FACE',      (1,0), (1,-1), 'Courier'),
                                  ('SPAN',      (0,0), (-1,-0))])
SystemDataTable = Table(SystemData, (1.5 * inch, 2 * inch), 14)
SystemDataTable.setStyle(tableFormat_Headers)
SystemDataTable.wrapOn(report, 0, 0)
SystemDataTable.drawOn(report, x_header_system_tables, y_header_tables)

#Dosimeter Data Table
DosimeterData = [['Reference Dosimeter Info', ''],
                 ['Reference Dosimeter:', 'RadCal Ion Chamber'],
                 ['Rad Cal ID #:', infoRadCal[0]],
                 ['Ion Chamber Model:', infoRadCal[3]],
                 ['Ion Chamber SN:', infoRadCal[4]],
                 ['Digitizer Model:', infoRadCal[1]],
                 ['Digitizer SN:', infoRadCal[2]],
                 ['Calibration Due Date:', infoRadCal[5]]]

DosimeterDataTable = Table(DosimeterData, (1.5 * inch, 2 * inch), 14)
DosimeterDataTable.setStyle(tableFormat_Headers)
DosimeterDataTable.wrapOn(report, 0, 0)
DosimeterDataTable.drawOn(report, x_header_dosimeter_tables, y_header_tables)

#Add the Plot
plotPosition = [center_x - 200, 300]
#plotPosition = [x_header_system_tables, 300]
plotSize = [400, 250] #based on the figsize that has been set above, this is 6x4 resolution
report.drawInlineImage(fileRootPrefix + filePrefix_Plot + fileName_Plot, plotPosition[0], plotPosition[1], width = plotSize[0], height = plotSize[1])

tableData_FilmReader = [['Film Reader Information',''],
                        ['Device ID:', deviceID],
                        ['Device SN:', uintSerialNumber],
                        ['Film Type:', filmType],
                        ['Film Lot:', filmLotNumber],
                        ['Film Exp. Date:', filmLotExpDate]]

tableFormat_FilmReader = TableStyle([('ALIGN',      (0,0), (-1,-1),'CENTER'),
                                     ('FACE',       (0,0), (-1,0), 'Times-Bold'),
                                     ('FACE',       (0,0), (0,-1), 'Times-Bold'),
                                     ('FACE',       (1,1), (-1,-1), 'Courier'),
                                     ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                     ('BOX',        (0,0), (-1,-1), 0.5, colors.black),
                                     ('BACKGROUND', (0,0), (-1,0), colors.ReportLabLightBlue),
                                     ('BACKGROUND', (0,0), (0,-1), colors.ReportLabLightBlue),
                                     ('SPAN',       (0,0), (-1,0))
                                     ])

table_FilmReader_col_widths = (1.5 * inch, 1.5 * inch)
FilmReaderTable = Table(tableData_FilmReader, table_FilmReader_col_widths, 14)
FilmReaderTable.setStyle(tableFormat_FilmReader)
FilmReaderTable.wrapOn(report,0,0)
FilmReaderTable.drawOn(report,x_header_system_tables, 210)

tableData_PolyFit = [['Polynomial Fit', ''],
                     ['A: ', str(round(polyA,3))],
                     ['B: ', str(round(polyB,3))],
                     ['C: ', str(round(polyC,3))],
                     ['r\u00b2:', str(round(polyCorrelation, 4))]]
tableFormat_PolyFit = TableStyle([('ALIGN',     (0,0), (-1,-1),'CENTER'),
                                  ('FACE',      (0,0), (-1,0), 'Times-Bold'),
                                  ('FACE',       (0,0), (0,-1), 'Times-Bold'),
                                  ('FACE',       (1,1), (-1,-1), 'Courier'),
                                  ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                  ('BOX',        (0,0), (-1,-1), 0.5, colors.black),
                                  ('BACKGROUND', (0,0), (-1,0), colors.ReportLabLightBlue),
                                  ('BACKGROUND', (0,0), (0,-1), colors.ReportLabLightBlue),
                                  ('SPAN',       (0,0), (-1,0))
                                  ])
table_PolyFit_col_widths = (inch, inch)
PolyFitTable = Table(tableData_PolyFit, table_PolyFit_col_widths, 14)
PolyFitTable.setStyle(tableFormat_PolyFit)
PolyFitTable.wrapOn(report,0,0)
PolyFitTable.drawOn(report,x_header_system_tables + 240, 224)

tableData_PowerFit = [['Power Fit', ''],
                      ['A: ', str(round(powerA,3))],
                      ['B: ', str(round(powerB, 3))],
                      ['r\u00b2: ', str(round(powerCorrelation,3))]]

tableFormat_PowerFit = TableStyle([('ALIGN',     (0,0), (-1,-1),'CENTER'),
                                  ('FACE',      (0,0), (-1,0), 'Times-Bold'),
                                  ('FACE',       (0,0), (0,-1), 'Times-Bold'),
                                  ('FACE',       (1,1), (-1,-1), 'Courier'),
                                  ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                  ('BOX',        (0,0), (-1,-1), 0.5, colors.black),
                                  ('BACKGROUND', (0,0), (-1,0), colors.ReportLabLightBlue),
                                  ('BACKGROUND', (0,0), (0,-1), colors.ReportLabLightBlue),
                                  ('SPAN',       (0,0), (-1,0))
                                  ])

PowerFitTable = Table(tableData_PowerFit, table_PolyFit_col_widths, 14)
PowerFitTable.setStyle(tableFormat_PowerFit)
PowerFitTable.wrapOn(report,0,0)
PowerFitTable.drawOn(report,x_header_system_tables + 410, 238)

#ADD LINES ABOUT ENVIRONMENTAL CONDITIONS
textObject_Comments = report.beginText(40, 180)
textObject_Comments.setTextOrigin(40, 180)
textObject_Comments.setFont('Times-Roman', 10)
textObject_Comments.textLine('Environmental Conditions: T=' + tempCal + ' \u00b0C, P=' + pressCal + ' kPa, RH=' + relativeHum + '%')
textObject_Comments.textLine('Calibration Procedure: ' + calProc)
report.drawText(textObject_Comments)

textObject_CalibratedBySig = report.beginText(40,100)
textObject_CalibratedBySig.setTextOrigin(40, 100) 
textObject_CalibratedBySig.setFont('Times-Roman', 12)
textObject_CalibratedBySig.textLine('__________________________________')
textObject_CalibratedBySig.textLine('Calibrated By:')
textObject_CalibratedBySig.textLine(techName)
textObject_CalibratedBySig.textLine('Calibration Technician')
report.drawText(textObject_CalibratedBySig)

textObject_VerifiedBySig = report.beginText(40,100)
textObject_VerifiedBySig.setTextOrigin(340, 100)
textObject_VerifiedBySig.setFont('Times-Roman', 12)
textObject_VerifiedBySig.textLine('__________________________________')
textObject_VerifiedBySig.textLine('Reviewed By:')
textObject_VerifiedBySig.textLine('Physicist or Calibration Lab')
textObject_VerifiedBySig.textLine('Committee Member or Dsignee')
report.drawText(textObject_VerifiedBySig)

#Add form and rev
textObject_FormNumberRev = report.beginText(40, 30)
textObject_FormNumberRev.setTextOrigin(180, 30)
textObject_FormNumberRev.setFont('Times-Italic', 10)
textObject_FormNumberRev.textLine('BU-F-### Film Reader Calibration Report Rev_' + Revision)
report.drawText(textObject_FormNumberRev)

#Add our logo!
logoPosition = [20, 72 * 10.2]
logoSize =  [104, 40] #130 x 50
report.drawInlineImage(filePath_RadSourceLogo, logoPosition[0], logoPosition[1], width = logoSize[0], height = logoSize[1])

#Save the report
print(inch)
if(saveReport):
    if(not(os.path.exists(fileRootPrefix + filePrefix_Report))):
        os.makedirs(fileRootPrefix + filePrefix_Report)
    report.save()
