# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 09:51:13 2023

This is generates the calibration curves for a Smart Ion Chamber unit.

@author: JGarner
"""

#DEPENDANCIES *****************************************************************
import numpy as np
import pandas as pd
import os
#Curve Fitting libs
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
#from sklearn.model_selection import train_test_split #Not used for this iteration
#plotting libs
import matplotlib.pyplot as plt
import seaborn as sns
#Date time libs
import datetime as dt
from datetime import datetime
#report generating libs
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors

#CALIBRATION INFORMATION ******************************************************
Tech_name = "Hart Horton, B.S."
#               Rad ID, Dig Model, Dig SN, IC Model, IC SN, Calibration Due Date
RadCal_Info = ['RAD-008', 'ADDM+', '47-1380', '10X6-0.6-3', '02-0815', '6/13/2024']
#               Generator Model, SN
Generator_Info = ['Spellman X4119', '140690036-A01865']
#               Tube Model, Tube Serial
Tube_Info = ['Quastar DT-1084', '9614-7R']
Tube_Power = ['4 kW', '155 kV', '25 mA']


#CONTROLS *********************************************************************
saveFigs = True
saveCoeffCSV = True
savePDF = True
digitizerSN = 'R6008'

#TIME AND OID STUFF
_day = dt.datetime.now().day
_month = dt.datetime.now().month
_year = dt.datetime.now().year
s_day = '0' + str(_day) if _day < 10 else str(_day)
s_month = '0' + str(_month) if _month < 10 else str(_month)
s_year = str(_year)
ReportOID = s_year + s_month + s_day + digitizerSN
Revision = 'a'

#SAVE AND LOAD FILE NAMES *****************************************************
filePathPrefix_Data = os.pardir + '/20231003/' #os.pardir is essentially a cross platform '../'
file_CalibrationData = filePathPrefix_Data + 'SiC_Calibrations.csv'
filePathPrefix_Reports = filePathPrefix_Data + 'Reports/'
filePathPrefix_Images = filePathPrefix_Reports + 'images/'
filePathPrefix_Tables = filePathPrefix_Reports + 'tables/'
fileName_CalibrationPlot = 'CalibrationCurves_' + digitizerSN + s_year + s_month + s_day + '.png'
fileName_CalibrationCoeffsTable = 'SiC_' + digitizerSN + '_Calibration_Coeffs_Table' + s_year + s_month + s_day + '.csv'
fileName_CalibrationReport = 'SiC_CalibrationReport_' + digitizerSN + '_' + s_year + s_month + s_day + '.pdf'
filePath_RadSourceLogo = 'RadSourceLogo.png'
 
#READ THE DATA FROM CSV FILE **************************************************
df_CalData = pd.read_csv(file_CalibrationData)
#based on the formatted data, [0] = index, [1] = Dose Rate Pos1, [2] Dose Rate Pos2, [3] Ion1 Voltage, [4] Ion 2 Voltage
pos1_Gy = df_CalData.iloc[:, [1]].to_numpy()
pos2_Gy = df_CalData.iloc[:, [2]].to_numpy()
pos1_V = df_CalData.iloc[:, [3]].to_numpy()
pos2_V = df_CalData.iloc[:, [4]].to_numpy()
#pos1_XThresh = str("{:.4f}").format(df_CalData.iloc[:,[5]].to_numpy()[0][0])
#pos2_XThresh = str("{:.4f}").format(df_CalData.iloc[:,[6]].to_numpy()[0][0])
pos1_XThresh = df_CalData.iloc[:,[5]].to_numpy()[0][0]
pos2_XThresh = df_CalData.iloc[:,[6]].to_numpy()[0][0]
pos1_DRCoeff = df_CalData.iloc[:,[7]].to_numpy()[0][0]
pos2_DRCoeff = df_CalData.iloc[:,[8]].to_numpy()[0][0]

col_names = list(df_CalData.columns)

#LETS GENERATE SOME COEFFS BIATCHES *******************************************
poly_degrees = 2
poly = PolynomialFeatures(degree = poly_degrees)
polyFeatures_pos1 = poly.fit_transform(pos1_V)
polyFeatures_pos2 = poly.fit_transform(pos2_V)
#lets create some models
model_pos1 = LinearRegression()
model_pos2 = LinearRegression()
model_pos1.fit(polyFeatures_pos1, pos1_Gy)
model_pos2.fit(polyFeatures_pos2, pos2_Gy)

#LETS MAKE SOME PLOTS YALL ****************************************************
step_size = 0.0001
pos1_x_p_raw = np.arange(min(pos1_V), max(pos1_V), step_size).reshape(-1,1)
pos2_x_p_raw = np.arange(min(pos2_V), max(pos2_V), step_size).reshape(-1,1)
pos1_x_p = poly.fit_transform(pos1_x_p_raw)
pos2_x_p = poly.fit_transform(pos2_x_p_raw)
pos1_y_p = model_pos1.predict(pos1_x_p)
pos2_y_p = model_pos2.predict(pos2_x_p)
colors_p = ['magenta', 'cyan']
labels_p = [col_names[3], col_names[4]]
plt.figure(figsize=(8,5))
plt.title('Calibration Curves for SiC ' + digitizerSN, weight='bold', size = 18)
plt.grid = True
plt.xlabel('Ion Chamber Voltage delta (V)', weight = 'bold')
plt.ylabel('Dose Rate (mGy/min)', weight = 'bold')
plt.xlim(0.95 * min(min(pos1_x_p_raw),min(pos2_x_p_raw)), 1.05 * max(max(pos1_x_p_raw),max(pos2_x_p_raw)))
plt.ylim(0.95 * min(min(pos1_y_p),min(pos2_y_p)), 1.05 * max(max(pos1_y_p), max(pos2_y_p)))
plt.plot(pos1_x_p_raw, pos1_y_p, color = colors_p[0], label = labels_p[0])
plt.plot(pos2_x_p_raw, pos2_y_p, color = colors_p[1], label = labels_p[1])
#Add Opperational Range
y_max_operRange = 1450
y_min_operRange = 1000   #determined from calibration between 9 mA and 13 mA
plt.plot([min(min(pos1_x_p_raw),min(pos2_x_p_raw)), max(max(pos1_x_p_raw),max(pos2_x_p_raw))], [y_max_operRange, y_max_operRange], color = 'black', linestyle = 'dashed')
plt.plot([min(min(pos1_x_p_raw),min(pos2_x_p_raw)), max(max(pos1_x_p_raw),max(pos2_x_p_raw))], [y_min_operRange, y_min_operRange], color = 'black', linestyle = 'dashed')
#Draw range of target values
y_textTarget = ((y_max_operRange + y_min_operRange)// 2) - 40
x_textTartet = 0.9 * max(max(pos1_x_p_raw),max(pos2_x_p_raw))
plt.text(x_textTartet, y_textTarget ,' Target Range (2kW)')
min_x_val = min(min(pos1_x_p_raw),min(pos2_x_p_raw)) * 1.03
x_offset_DashedLines = 0.05
plt.plot([x_textTartet + x_offset_DashedLines, x_textTartet + x_offset_DashedLines], [y_max_operRange, y_textTarget + 60], color = 'black', linestyle = 'dashed')
plt.plot([x_textTartet + x_offset_DashedLines, x_textTartet + x_offset_DashedLines], [y_textTarget-20, y_min_operRange], color = 'black', linestyle = 'dashed')
plt.legend(loc='best')

if(saveFigs):
    if(not(os.path.exists(filePathPrefix_Images))):
        os.makedirs(filePathPrefix_Images)
    plt.savefig(filePathPrefix_Images+fileName_CalibrationPlot)

#EXTRACT THE COEFFS
#wea re only using a degree 2 poly for the coeffs
round_perc = 6
Ion1_modelCoeffs = model_pos1.coef_[0]
Ion1_modelCoeffs = np.append(Ion1_modelCoeffs,model_pos1.intercept_)
Ion2_modelCoeffs = model_pos2.coef_[0]
Ion2_modelCoeffs = np.append(Ion2_modelCoeffs,model_pos2.intercept_)
#create a dataframe from these values
df_Coeffs = pd.DataFrame({'Ion Chamber SN' : np.array([col_names[3], col_names[4]]),
                          'x2' : np.array([round(Ion1_modelCoeffs[2], round_perc), round(Ion2_modelCoeffs[2],round_perc)]),
                          'x'  : np.array([round(Ion1_modelCoeffs[1], round_perc), round(Ion2_modelCoeffs[1], round_perc)]),
                          'c'  : np.array([round(Ion1_modelCoeffs[-1], round_perc), round(Ion2_modelCoeffs[-1], round_perc)]),
                          'Voltage Threshold' : np.array([round(pos1_XThresh, round_perc), round(pos2_XThresh, round_perc)]),
                          'Dose Rate Coeff' : np.array([round(pos1_DRCoeff, round_perc),round(pos2_DRCoeff, round_perc)])
                          })

if(saveCoeffCSV):
    if(not(os.path.exists(filePathPrefix_Tables))):
        os.makedirs(filePathPrefix_Tables)
    df_Coeffs.to_csv(filePathPrefix_Tables + fileName_CalibrationCoeffsTable)
    
#******************************************************************************    
#GENERATE A REPORT ************************************************************
#******************************************************************************
canvas = Canvas(filePathPrefix_Reports + fileName_CalibrationReport, pagesize=(8.5 * inch, 11 * inch))
#PDF HEADER TITLE
center_x = 8.5 * inch / 2
center_y = 11 * inch / 2
MainTitle_margin = center_x - 200
current_y = 10.2 * inch - 40
current_x = 0.5 * inch
textObject_Title = canvas.beginText(MainTitle_margin, current_y)
textObject_Title.setTextOrigin(MainTitle_margin, current_y)
textObject_Title.setFont("Times-Bold", 26)
textObject_Title.textLine("Calibration Report for SiC " + digitizerSN)
canvas.drawText(textObject_Title)

position_OID = [center_x + 145, 10.2 * inch + 20]
textObject_OID = canvas.beginText(position_OID[0], position_OID[1])
textObject_OID.setTextOrigin(position_OID[0], position_OID[1])
textObject_OID.setFont('Courier-Bold', 9)
textObject_OID.textLine('Report ID: ' + ReportOID)
canvas.drawText(textObject_OID)

#HEADER TABLES ****************************************************************
#System Data Table
y_header_tables = 8.5 * inch - 28 - 20
x_header_system_tables = 20
x_header_dosimeter_tables = 340
SystemData = [['Calibration Tech:', Tech_name],
              ['Procedure Date:', s_month+'/' + s_day + '/' + s_year],
              ['Tube Model:', Tube_Info[0]],
              ['Tube Serial:', Tube_Info[1]],
              ['Tube Power:', '4 kW Max @ 155 kV'],
              ['Generator Model:', Generator_Info[0]],
              ['Generator Serial:', Generator_Info[1]]]

tableFormat_Headers = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                  ("BOX",       (0,0), (-1,-1), 0.5,  colors.black),
                                  ('BACKGROUND',(0,0), (0, -1), colors.ReportLabLightBlue),
                                  ('FACE',      (0,0), (0,-1), 'Times-Bold'),
                                  ('FACE',      (1,0), (1,-1), 'Courier')])
SystemDataTable = Table(SystemData, (1.5 * inch, 2 * inch), 14)
SystemDataTable.setStyle(tableFormat_Headers)
SystemDataTable.wrapOn(canvas, 0, 0)
SystemDataTable.drawOn(canvas, x_header_system_tables, y_header_tables)

#Dosimeter Data Table
DosimeterData = [['Reference Dosimeter:', 'RadCal Ion Chamber'],
                 ['Rad Cal ID #:', RadCal_Info[0]],
                 ['Ion Chamber Model:', RadCal_Info[3]],
                 ['Ion Chamber SN:', RadCal_Info[4]],
                 ['Digitizer Model:', RadCal_Info[1]],
                 ['Digitizer SN:', RadCal_Info[2]],
                 ['Calibration Due Date:', RadCal_Info[5]]]

DosimeterDataTable = Table(DosimeterData, (1.5 * inch, 2 * inch), 14)
DosimeterDataTable.setStyle(tableFormat_Headers)
DosimeterDataTable.wrapOn(canvas, 0, 0)
DosimeterDataTable.drawOn(canvas, x_header_dosimeter_tables, y_header_tables)

#Coeffs Data Table NEED TO WORK ON BACKGROUND COLORS, DATA IS GOOD THOUGH
table_Coeffs_widths = (1.25 * inch, 1 * inch, 1 * inch, 1 * inch, 1 *inch, 1 * inch)
tableFormat_Coeffs = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                  ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                  ("BOX",       (0,0), (-1,-1), 0.5,  colors.black),
                                  ('BACKGROUND',(0,0), (-1, 0), colors.lightgreen),
                                  ('BACKGROUND',(0,1), (0, -1), colors.ReportLabLightBlue),
                                  ('BACKGROUND',(0,1), (-1, 1), colors.ReportLabLightBlue),
                                  ('FACE',      (0,0), (-1,0), 'Times-Bold'),
                                  ('SIZE',      (0,0), (-1,0), 13),
                                  ('FACE',      (0,1), (-1,1), 'Times-Bold'),
                                  ('FACE',      (0,0), (0,-1), 'Times-Bold'),
                                  ('FACE',      (1,2), (-1,-1), 'Courier'),
                                  ('SPAN',      (0,0), (-1, 0))
                                  ])

#manip data to make it easier to work with
Ion1_data = df_Coeffs.iloc[[0], :].to_numpy().tolist()
#Ion1_data[0].append(pos1_XThresh)
#Ion1_data[0].append(pos1_DRCoeff)
Ion2_data = df_Coeffs.iloc[[1], :].to_numpy().tolist()
#Ion2_data[0].append(pos2_XThresh)
#Ion2_data[0].append(pos2_DRCoeff)
CoeffsData = [['Ion Chamber Coefficients', '', '', ''],
              ['Ion Chamber SN', 'A (x^2)', 'B (x)', 'C', 'X Threshold', 'Dose Rate Coeff'],
              [Ion1_data[0][0], str("{:.4f}").format(Ion1_data[0][1]), str("{:.4f}").format(Ion1_data[0][2]), str("{:.4f}").format(Ion1_data[0][3]), str("{:.4f}").format(Ion1_data[0][4]), str("{:.4f}").format(Ion1_data[0][5])],
              [Ion2_data[0][0], str("{:.4f}").format(Ion2_data[0][1]), str("{:.4f}").format(Ion2_data[0][2]), str("{:.4f}").format(Ion2_data[0][3]), str("{:.4f}").format(Ion2_data[0][4]), str("{:.4f}").format(Ion2_data[0][5])]]
print(Ion1_data[0][0])
print(Ion1_data[0][1])
CoeffsDataTable = Table(CoeffsData, (table_Coeffs_widths), 14)
CoeffsDataTable.setStyle(tableFormat_Coeffs)
CoeffsDataTable.wrapOn(canvas, 0, 0)
CoeffsDataTable.drawOn(canvas, x_header_system_tables + 55, 230)#shifted up by 10

#Add the Plot
plotPosition = [center_x - 200, 300]
plotSize = [400, 250] #based on the figsize that has been set above, this is 6x4 resolution
canvas.drawInlineImage(filePathPrefix_Images+fileName_CalibrationPlot, plotPosition[0], plotPosition[1], width = plotSize[0], height = plotSize[1])
logoPosition = [20, 72 * 10.2]
logoSize =  [104, 40] #130 x 50
canvas.drawInlineImage(filePath_RadSourceLogo, logoPosition[0], logoPosition[1], width = logoSize[0], height = logoSize[1])

#ADD SIGNITURE LINES AND ADDITIONAL TEXT
textObject_Comments = canvas.beginText(40, 100)
textObject_Comments.setTextOrigin(40, 200) #shifted up by 10
textObject_Comments.setFont('Times-Bold', 11)
textObject_Comments.textLine('Comments regarding Calibrration')
textObject_Comments.setFont('Times-Italic', 11)
textObject_Comments.textLine('Ion Chamber oriented such that the plates are perpindicular to tangent of tube flange; Serial Numbers facing inward.')
textObject_Comments.textLine('Center of chamber volume used as the reference point.')
textObject_Comments.textLine('Quastart DT-1084 at static 155 kV with varied current to ensure proper beam quality.')
textObject_Comments.textLine('Ion Chamber calibration only valid when using Digitizer ' + digitizerSN + ' with Ion Chamber ' + Ion1_data[0][0] + ' connected to')
textObject_Comments.textLine('channel 1 and Ion Chamber ' + Ion2_data[0][0] + ' connected to channel 2.')
#textObject_Comments.textLine('Target Air Kerma Rate: Between 700 mGy/min and 1200 mGy/min.')
canvas.drawText(textObject_Comments)

textObject_CalibratedBySig = canvas.beginText(40,100)
textObject_CalibratedBySig.setTextOrigin(40, 100) 
textObject_CalibratedBySig.setFont('Times-Roman', 12)
textObject_CalibratedBySig.textLine('__________________________________')
textObject_CalibratedBySig.textLine('Calibrated By:')
textObject_CalibratedBySig.textLine(Tech_name)
textObject_CalibratedBySig.textLine('Calibration Technician')
canvas.drawText(textObject_CalibratedBySig)

textObject_VerifiedBySig = canvas.beginText(40,100)
textObject_VerifiedBySig.setTextOrigin(340, 100)
textObject_VerifiedBySig.setFont('Times-Roman', 12)
textObject_VerifiedBySig.textLine('__________________________________')
textObject_VerifiedBySig.textLine('Reviewed By:')
textObject_VerifiedBySig.textLine('Physicist or Calibration Lab')
textObject_VerifiedBySig.textLine('Committee Member or Dsignee')
canvas.drawText(textObject_VerifiedBySig)

#Add form and rev
textObject_FormNumberRev = canvas.beginText(40, 30)
textObject_FormNumberRev.setTextOrigin(180, 30)
textObject_FormNumberRev.setFont('Times-Italic', 10)
textObject_FormNumberRev.textLine('BU-F-### Smart Ion Chamber Calibration Report Rev_' + Revision)
canvas.drawText(textObject_FormNumberRev)

if(savePDF):
    if(not(os.path.exists(filePathPrefix_Reports))):
        os.makedirs(filePathPrefix_Reports)
    canvas.save()