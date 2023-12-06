# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 10:29:26 2023

This file is to create a pdr formatted to show the Dosimetry Values for the RS420Q+

#Last altered 10/26/2023 to create dosimetry report for Dustin's dosimetry on RS420Q+ China

@author: Jacob Garner
"""

#for creation of the PDF
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors
#just for some general stuffs
import datetime as dt
from datetime import date
#for heatmapping
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


#default variables to be used later
DosimetryTech = "Jacob Garner"
_day = dt.datetime.now().day
_month = dt.datetime.now().month
_year = dt.datetime.now().year
s_day = "0" + str(_day) if _day < 10  else str(_day)
s_month = "0" + str(_month) if _month < 10 else str(_month)
s_year = str(_year)
s_secondsOfDay = str((dt.datetime.now() - dt.datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0)).seconds)
unitSerial = "Prototype C" #China
#unitSerial = "Prototype B" #Engineering
#tubeSerial = "10880-7" #China
#tubeSerial = '10911-27' #Engineering
tubeSerial = '10911-1' #as of 11/27 for prototype
generatorSerial = "134908706-A00060" #China
#generatorSerial = "123132643-A00004" #Engineering
#lets create a unique ID for the report using the serial number and date/time
uID = unitSerial + s_year + s_month + s_day + s_secondsOfDay
#print("report uID: ", uID)
#Canister Dims
canisterHeight = 13
canisterRadius = 6

#print(_day, " | " , _month , " | ", _year)
#First, create a canvas with a name and size formatting
canvas = Canvas("Reports/DosimetryReport_RS420QPlus_"+unitSerial +"_" + uID + ".pdf", pagesize=(8.5*inch, 11*inch))

"""
All fonts available:
    Reportlab’s canvas.getAvailableFonts() seems to be aware of 
    ['Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique',
     'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', 'Symbol', 
     'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman', 'ZapfDingbats']

"""

def newLine(fontSize, current_y):
    fontSize_inch = fontSize * 0.013889
    return current_y - fontSize_inch

#some default x and y values for printing on the page
center_x = 8.5 * inch / 2
center_y = 11 * inch / 2
MainTitle_margin = center_x - 84
#set initial points for all writing
current_y = 10.2*inch
current_x = 0.5*inch
positionTableInside = [5 * inch, 5 * inch]


textobject = canvas.beginText(MainTitle_margin, current_y)
textobject.setTextOrigin(MainTitle_margin, current_y)
textobject.setFont("Times-Bold", 26)
textobject.textLine("Dosimetry Report")
textobject.setFont("Courier-Bold", 14)
#draw all text to the page
canvas.drawText(textobject)

#HEADER TABLES*********************************************************************************

#define y positions for the header tables
y_header_tables = 8.5*inch - 28
x_header_system_tables = 20
x_header_dosimeter_tables = 340
header_col_widths = (1.5* inch ,2 * inch)
#lets see if a table for the dosimeter information is adequate or if drawing text looks better
SystemData = [['Irradiator Model:', 'RS420Q+'],
              ['Irradiator Serial: ', unitSerial],
              ['Tube Model:' , 'Quastar DT-2105-OR'],
              ['Tube Serial: ', tubeSerial],
              ['Tube Power: ', '5 kW (225 kV, 22 mA)'],
              #['Tube Power: ', '4kW (225 kV, 17.7 mA)'],
              ['Generator Model:', 'Spellman X5826'],
              ['Generator Serial:', generatorSerial],
              ['Phantom Type: ', 'Cannabis Equivalent (0.096 g/cc)']]
tableFormat_Headers = TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                  ('INNERGRID', (0,0),(-1,-1), 0.25, colors.black),
                                  ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                                  ('BACKGROUND', (0,0),(0,-1), colors.ReportLabLightBlue),
                                  ('FACE', (1,0),(1,-1), 'Times-Bold')
                                  ])
SystemDataTab = Table(SystemData, header_col_widths, 14)

SystemDataTab.setStyle(tableFormat_Headers)
SystemDataTab.wrapOn(canvas,0,0)
SystemDataTab.drawOn(canvas, x_header_system_tables, y_header_tables)

DosimeterData = [['Dosimetry Tech: ', 'Dustin Baker'],
                 ['Procedure Date: ', date.today().strftime("%m/%d/%Y")],
                 ['Dosimetry Method: ', 'GAF EBT3-XD Film'],
                 ['Film Reader ID: ', 'DR4-009'],
                 ['Film Reader Serial: ', '12411'],
                 ['Film Reader Cal. Date: ', '11/8/2023'],
                 ['Film Lot Number: ', '01182201'],
                 ['Film Expiration Date: ', '7/18/2024']]

DosimeterDataTab = Table(DosimeterData, header_col_widths, 14)
DosimeterDataTab.setStyle((tableFormat_Headers))
DosimeterDataTab.wrapOn(canvas,0,0)
DosimeterDataTab.drawOn(canvas, x_header_dosimeter_tables, y_header_tables)

#DATA TABLES*************************************************************************************

#define Positions for the table starting positions
y_data_outside = 100
y_data_inside = 290
x_data_inside = 397
x_data_outside = 397
table_data_col_widths = (inch, 1.7* inch)

#lets test the data/table creation | We will need to create 2 tables, one for the inside line and one for the outside line
tableHeader_pos = 'Position'
tableHeader_values = 'Dose Rate (Gy/min)'
#Enginnering Data 5 kW - Original Data Commented out
#doseRateData_inside = [5.58,6.01,6.78,7.47,7.85,7.82,7.93,7.87,7.60,7.13,6.41]
#doseRateData_outside = [5.51,6.53,7.58,8.15,10.06,9.73,10.90,10.51,10.61,9.21,6.80]

#Most Recent Data goes here!
doseRateData_inside = [5.94,6.37,6.88,7.21,7.40,7.43,7.25,7.03,6.40,5.97,5.23]
doseRateData_outside = [6.22,7.15,8.07,9.04,9.85,9.93,9.90,8.97,7.94,6.49,5.58]

#used for extrapolating to 5 kW, comment out when looking at raw values
for i in range(len(doseRateData_inside)):
    doseRateData_inside[i] *= 1.25
    doseRateData_outside[i] *= 1.25


"""
#China Data 4 kW
doseRateData_inside = [4.619,5.007,5.585,5.984,5.995,5.998,5.998, 5.685,5.304,4.745,4.339]
doseRateData_outside = [4.918,5.793,6.676,7.529,7.96,8.158,8.018,7.391,6.44,5.408,4.394]
#China Data 5 kW
for i in range(len(doseRateData_inside)):
    doseRateData_inside[i] *= 1.25
    doseRateData_outside[i] *= 1.25
"""

doseRateData_total = doseRateData_inside + doseRateData_outside
numberTableVals = len(doseRateData_inside)
#now lets create a 2-D list
tableData_inside = [['Center Line', ''],[tableHeader_pos, tableHeader_values]]
tableData_outside = [['Outside Line', ''],[tableHeader_pos, tableHeader_values]]
for i in range(numberTableVals):
    tableData_inside.append([i+1,'%.2f' %doseRateData_inside[i]])
    tableData_outside.append([i+1,'%.2f' %doseRateData_outside[i]])
#now lets create a data table on our canvas/pdf
table_inside = Table(tableData_inside,
                     #column Width
                     table_data_col_widths,
                     #Row Height | use the font height for this?
                     14)
#set the formatting of the table
"""
table_inside.setStyle(TableStyle([('ALIGN', (1,1),(-2,-2), 'CENTER'),
                                  ('TEXTCOLOR',(1,1),(-2,-2),colors.red),
                                  ('VALIGN',(0,0),(0,-1),'TOP'),
                                  ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                                  ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                                  ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                  ('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
                                  ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                  ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                  ]))
"""
#playing with the setStyle
tableFormat_Data = TableStyle([('ALIGN', (0,0),(-1,-1),'CENTER'),
                                  ('FACE', (0,0), (-1,1), 'Courier-Bold'),
                                  ('FACE', (0,1),(-1,-1),'Courier'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                  ('BOX', (0,0), (-1,-1), 0.75, colors.black),
                                  ('SPAN', (0,0), (-1,0)),
                                  ('BACKGROUND', (0,1),(0,-1), colors.ReportLabLightBlue),
                                  ('BACKGROUND', (0,1),(-1,1), colors.ReportLabLightBlue),
                                  ('BACKGROUND', (0,0),(-1,0), colors.ReportLabLightGreen),])
#apply the table format
table_inside.setStyle(tableFormat_Data)
table_inside.wrapOn(canvas,0,72)

#Create the second table for the outside positions
table_outside = Table(tableData_outside, table_data_col_widths, 14)
table_outside.setStyle(tableFormat_Data)
table_outside.wrapOn(canvas, 0, 0)


#this method draws the table on the canvas
table_inside.drawOn(canvas, x_data_inside, y_data_inside)
table_outside.drawOn(canvas, x_data_outside, y_data_outside)

#now lets get a table showing the average, min and DUR for the dosimetry
#get the data first
minDoseRate = min(doseRateData_total)
averageDoseRate = round(sum(doseRateData_total)/len(doseRateData_total), 2)
DUR = round(max(doseRateData_total)/minDoseRate,2)
#print(minDoseRate, " |  ", averageDoseRate) #test to check the values for the max and average dose rates

tableData_summary = [['Dosimetry Summary', ''],
               ['Min. Dose Rate:', str('%.2f' %minDoseRate)],
               ['Average Dose Rate: ', str('%.2f' %averageDoseRate)],
               ['Dose Uniformity: ', str('%.2f' %DUR)]]

#format the table/data
tableFormat_Summary = TableStyle([('ALIGN', (0,0),(-1,-1),'CENTER'),
                                  ('FACE', (0,0), (-1,1), 'Courier-Bold'),
                                  ('FACE', (0,1),(-1,-1),'Courier'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                  ('BOX', (0,0), (-1,-1), 0.75, colors.black),
                                  ('SPAN', (0,0), (-1,0)),
                                  ('BACKGROUND', (0,1),(0,-1), colors.ReportLabLightBlue),
                                  ('BACKGROUND', (0,0),(-1,0), colors.ReportLabLightGreen)])
x_summary_pos = 354
y_summary_pos = 480
table_summary_col_widths = (1.8 * inch, 1.5 * inch)
table_summary = Table(tableData_summary, table_summary_col_widths, 14)
table_summary.setStyle(tableFormat_Summary)
table_summary.wrapOn(canvas,0,0)
table_summary.drawOn(canvas, x_summary_pos, y_summary_pos)

#lets add the "Results Filtered" Area
ResultsLine = [['Results: X-Ray specturm filtered through 3.1 mm of aluminum and 12.7 mm of water']]
table_ResultsLine = Table(ResultsLine,572, 14) #572 is due to having a 40 point margin on either side
tableFormat_Results = TableStyle([('ALIGN', (0,0), (-1,-1),'CENTER'),
                                  ('FACE', (0,0),(-1,-1), 'Times-Bold'),
                                  ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                  ('BACKGROUND', (0,0),(-1,-1),colors.lemonchiffon)])
table_ResultsLine.setStyle(tableFormat_Results)
table_ResultsLine.wrapOn(canvas,0,0)
table_ResultsLine.drawOn(canvas,20,550)

#PLOTS AND HEATMAP CREATION******************************************************************************
#first lets create the interploated lines for calculating all points along the outside and inside lines
InsideLineColor = 'darkcyan'
OutsideLineColor = 'deeppink'
x_both = np.array([0,1.62,3.01,4.41,6.80,6.5,7.20,8.59,9.98,11.38, 13]).reshape((-1,1)) # pulled directly from the film holders
y_inside = np.array(doseRateData_inside)
y_outside = np.array(doseRateData_outside)
#next lets plot the raw data on a graph
plt.plot(x_both, y_inside, label = 'Center Line', color = InsideLineColor)
plt.plot(x_both, y_outside, label = 'Outside Line', color = OutsideLineColor)
plt.xlabel('Position from Top of Canister (in.)')
plt.ylabel('Dose Rate (Gy/min)')
plt.legend(loc='upper left')
plt.title("Measured Dose Rate vs Position in Target Canister")
plt.xticks(np.arange(min(x_both), max(x_both)+1, 1.0))
plt.xlim(0,13)
#plt.savefig("Reports/DoseRateVsPosition.png")
#now lets create some heat maps!!

#We have the arrays all of length 11, lets create a polynomial regression to apporximate all values along the lines/axes
poly = PolynomialFeatures(degree=3, include_bias=False) #based on the graphs above, a 3rd degree polynomial should be more than adequate
#configure data to fit into the polyFeatures
polyFeatures = poly.fit_transform(x_both)
polyModel_inside = LinearRegression();
polyModel_outside = LinearRegression();
#now fit the models to their respective y values
polyModel_inside.fit(polyFeatures, y_inside)
polyModel_outside.fit(polyFeatures, y_outside)

numIterations = 100
x_pred_raw = np.arange(min(x_both), max(x_both), max(x_both)/numIterations)
x_pred = poly.fit_transform(x_pred_raw.reshape(-1,1))
y_pred_inside = polyModel_inside.predict(x_pred)
y_pred_outside = polyModel_outside.predict(x_pred)

plt.clf()
plt.scatter(x_pred_raw, y_pred_inside, label = 'Center Line', color = InsideLineColor)
plt.scatter(x_pred_raw, y_pred_outside, label = 'Outside Line', color = OutsideLineColor)
plt.title('Measured Dose Rate vs Position Target in Canister')
plt.xlabel('Position from Top of Canister (in.)')
plt.ylabel('Dose Rate (Gy/min)')
plt.xticks(np.arange(min(x_both), max(x_both)+1, 1.0))
plt.legend(loc = 'upper left')
InterpolatedDoseRateGraphFileName = 'Reports/'+unitSerial+'InterpolatedDoseRatesVsPosition.png'
plt.savefig(InterpolatedDoseRateGraphFileName)
plt.clf()

#now lets focus on making the interpolations accross each row; 100 interplated lines
stepSize = 2 * canisterRadius/numIterations
y_range = np.arange(-canisterRadius,canisterRadius+stepSize, stepSize)
#to simplify things, we will create a model that takes 2 variables (x,y) and returns the dose rate using multivariate polynomial regressions
#We need a dataframe first
train_x = []
train_y = []
train_doseRate = []

#first append x,y and DR for the outside line
for i in range(numIterations):
    train_x.append(x_pred_raw[i])
    train_y.append(-canisterRadius)
    train_doseRate.append(y_pred_outside[i])
#now append the center line
for i in range(numIterations):
    train_x.append(x_pred_raw[i])
    train_y.append(0)
    train_doseRate.append(y_pred_inside[i])
#now append the opposing outside line
for i in range(numIterations):
    train_x.append(x_pred_raw[i])
    train_y.append(canisterRadius)
    train_doseRate.append(y_pred_outside[i])
#turn our 3 lists into a pandas dataframe
heat_df = pd.DataFrame({'x': np.asarray(train_x).reshape(len(train_x),), 
                        'y': np.asarray(train_y).reshape(len(train_y),), 
                        'DoseRate': np.asarray(train_doseRate).reshape(len(train_doseRate),)})
#our data is set, lets start making our model!
X, y = heat_df[['x', 'y']], heat_df['DoseRate']
polyFullPredict = PolynomialFeatures(degree=3, include_bias = False)
polyFullPredictFeatures = polyFullPredict.fit_transform(X.values)
#we are not splitting the data as we will not be feed ing the model data it hasnt seen yet
polyFullPredict_model = LinearRegression()
polyFullPredict_model.fit(polyFullPredictFeatures, y)


sns.pairplot(heat_df)
plt.show()

#now we can predict every point using y range; lets create a set lists for 
heat_x = []
heat_y = []
heat_doseRate = []
for i in range(len(train_x)):
    for j in range(len(y_range)):
        heat_x.append(round(train_x[i], 4))
        heat_y.append(round(y_range[j], 4))
print(len(y_range))
#create our input dataframe for the prediction
X_predict = pd.DataFrame({'x': np.asarray(heat_x).reshape(len(heat_x)),
                           'y': np.asarray(heat_y).reshape(len(heat_y))})
#predict the values
poly = PolynomialFeatures(degree = 3, include_bias = False)
FullPredictFeatures = poly.fit_transform(X_predict.values)
heat_doseRate = polyFullPredict_model.predict(FullPredictFeatures)
FullPredict = pd.DataFrame({'x':heat_x, 'y':heat_y, 'DoseRate':heat_doseRate})
print(min(FullPredict['y'].values), " | ", max(FullPredict['y'].values))
print(min(y_range), " | ", max(y_range))
FullPredict = FullPredict.reset_index().pivot_table(index='x', columns = 'y', values ='DoseRate')
plt.clf()
plt.figure(figsize=(6,6))
ax = sns.heatmap(FullPredict)
ax.collections[0].colorbar.set_label('DoseRate (Gy/min)')
plt.title("Vertical Cross Sectional Dose Distribution")
plt.ylabel('Canister Height (in.)')
plt.xlabel('Canister Radius (in.)')
#the figure is a tad bit too small, lets adjust the figure size so that the axis (bottom) will show

crossSectionalHeatmapFileName = 'Reports/'+unitSerial+'CrossSectionalHeatmapCenterPlane_20231127.png'
plt.savefig(crossSectionalHeatmapFileName)

"""
#lets check our data via csvs
X_predict.to_csv("X_predict.csv")
FullPredict.to_csv("FullPredict.csv")
heat_df.to_csv("heat_df.csv")
"""
#right now our image h=288 pixels and w=432; lets keep this ratio as best as possible (ratio w:h = 1.5)
canvas.drawInlineImage(crossSectionalHeatmapFileName, 50, 50, width= 300, height = 300)
canvas.drawInlineImage(InterpolatedDoseRateGraphFileName, 30, 340,width = 300, height= 200)
#last thing is to add the rad source logo (we will add the email address and info if requested, but this is good enough for right now)
#canvas.drawInlineImage('Images/RadSourceLogo.png', 10, 10.5 * inch)
canvas.save()
