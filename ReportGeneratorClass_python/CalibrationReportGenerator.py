# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 10:28:58 2023

This file contains the class required to create a report for the Ion Chamber
Calibration for the Portable Phantom!

@author: JGarner
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import math

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors

import os

filePrefixLocalStorage = 'data/'
filrPrefixReports = 'reports/'
filePrefixPlots = 'plots/'
radSourceLogoLoc = 'Resources/RadSourceLogo.png'

class tubeInfo():
    def __init__(self, TubeModel, TubeSN, TubekV, TubemA):
        self.tubeModel = TubeModel
        self.tubeSN = TubeSN
        self.tubekV = TubekV
        self.tubemA = TubemA
        

class PortablePhantomReportGenerator:
    #default constructor
    def __init__(self, _unitSerialNumber,
                 _calData_x, _calData_y, _calTechName,
                 _procedureDate):
                 #_tubeModel, _tubeSN, _tubekV, _tubemA, 
                # _generatorModel, _generatorSN):
        self.x = _calData_x
        self.y = _calData_y
        self.unitSerialNumber = _unitSerialNumber
        self.techName = _calTechName
        self.generateUID()
        self.procedureDate = _procedureDate
        self.reportGenerationDate = dt.datetime.now()
        self.tubeInfoInput = False
        self.generatorInfoInput = False
        self.environMentalInfoInput = False
        self.plotGenerated = False
        self.referenceDosimeterInfoInput = False
        self.calIonChamberInfoInput = False
        self.FormNumber = "BU-F-### "
        self.FormName = "Ion Chamber Calibration Form Rev_"
        self.FormRevision = "0.a"
        return
    
    #setter for the environmental conditions
    def setEnvironmentConditions(self, _temp, _pres, _hum):
        self.temp = _temp
        self.pres = _pres
        self.hum = _hum
        self.environMentalInfoInput = True
        return
        
    #Call to generate plot and save it to local location
    def generateCalPlot(self):
        #first we need the predicti
        self.fitCoeffs = self.generateFitCurves()
        x_pred = np.arange(min(self.x), max(self.x)+1, 1)
        y_pred = self.regModel.predict(x_pred.reshape(-1,1))
        self.fig = plt.figure(figsize=(8,5))
        plt.title("Calibration Curve for Ion Chamber " + str(self.unitSerialNumber))
        plt.xlabel('Counts (~Volt)')
        plt.ylabel('Dose rate (Gy/min')
        plt.scatter(self.x, self.y, color = 'teal')
        plt.plot(x_pred, y_pred, color = 'magenta')
        plt.grid(True)
        #plt.legend(loc='Upeer Left')
        plt.text(min(self.x), 0.98 * max(self.y), 'Calibration Coeffs: ' + str(round(self.fitCoeffs[0],4)).format(width = 4) + ' x + ' + str(round(self.fitCoeffs[1], 4)).format(width = 4))
        if(not(os.path.exists(filePrefixLocalStorage + filePrefixPlots))):
            os.makedirs(filePrefixLocalStorage + filePrefixPlots)
        self.plotName = filePrefixLocalStorage + filePrefixPlots + 'CalibrationPlot_' + self.uid + '.png'
        plt.savefig(self.plotName, dpi = 300)
        self.plotGenerated = True
        return
    
    def setTubeInfo(self, tubeModel, tubeSN, tubekV, beamQuality):
        self.tubeSN = tubeSN
        self.tubeModel = tubeModel
        self.tubekV = tubekV
        self.beamQulaity = beamQuality
        self.tubeInfoInput = True
    
    def setGeneratorInfo(self, genModel, genSN):
        self.genSN = genSN
        self.genModel = genModel
        self.generatorInfoInput = True
    
    def setReferenceDosimeterInfo(self, ICIDNumber, ICManu, ICModel, ICSN, ElectroManu, ElectroModel, ElectroSN, CalDate):
        self.ICIDNumber = ICIDNumber
        self.ICManu = ICManu
        self.ICModel = ICModel
        self.ICSN = ICSN
        self.ElectroManu = ElectroManu
        self.ElectroModel = ElectroModel
        self.ElectroSN = ElectroSN
        self.refDosimeterCalDate = CalDate
        self.referenceDosimeterInfoInput = True
    
    def setCalIonChamberInfo(self, ICModel, ICSN, DigiModel, DigiSN):
        self.unitICSN = ICSN
        self.unitICModel = ICModel
        self.unitDigiSN = DigiSN
        self.unitDigiModel = DigiModel
        self.calIonChamberInfoInput = True
    
    def generateFitCurves(self):
        X = self.x.reshape(-1,1)
        y = self.y
        self.regModel = LinearRegression()
        self.regModel.fit(X,y)
        return list((self.regModel.coef_[0], self.regModel.intercept_))
        
    def generateUID(self):
        _now = dt.datetime.now()
        _day = _now.day
        _month = _now.month
        _year = _now.year
        s_day = '0' + str(_day) if _day < 10 else str(_day)
        s_month = '0' + str(_month) if _month < 10 else str(_month)
        s_year = str(_year)
        sec = dt.datetime.now().second + dt.datetime.now().minute * 60 + dt.datetime.now().hour * 3600
        self.uid = 'RS_' + s_year + s_month + s_day + str(sec).format(width = 5)
    
    #this will return the canvas that we create as an object, we will have to call the save externally to this, same as with the plots generated above
    def generateReport(self):
        #ensure that a calibration plot has been generated | this will 
        if not(self.plotGenerated):
            self.generateCalPlot()
        if not(self.environMentalInfoInput):
            print("Environmental information not input, please call PortablePhantomReportGenerator.setEnvironmentConditions(_temp, _pres, _hum) to set these parameters.")
            return
        if not(self.tubeInfoInput):
            print("Tube information not input, please call PortablePhantomReportGenerator.setTubeInfo(tubeSN, tubeModel, tubekV) to set these parameters.")
            return
        if not(self.generatorInfoInput):
            print("Generator information not input, please call PortablePhantomReportGenerator.setGeneratorInfo(genSN, genModel) to set these parameters.")
            return
        if not(self.referenceDosimeterInfoInput):
            print("Reference Ion Chamber information not input, please call PortablePhantomReportGenerator.setReferenceDosimeterInfo(ICManu, ICModel, ICSN, ElectroManu, ElectroModel, ElectroSN, CalDate) to set these parameters.")
            return
        if not(self.calIonChamberInfoInput):
            print("Data for the unit being calibrated has not been input, plese call PortablePhantomReportGenerator.setCalIonChamberInfo(ICSN, DigiSN)")
            return
        
        #now we can start creating our Calibration Report
        if(not(os.path.exists(filePrefixLocalStorage + filrPrefixReports))):
            os.makedirs(filePrefixLocalStorage + filrPrefixReports)
        self.currentReportFileName = filePrefixLocalStorage + filrPrefixReports + "PortablePhantomIonChamberCalibrationReport_" + self.uid + '.pdf'
        self.report = Canvas(self.currentReportFileName, pagesize=(8.5 * inch, 11 * inch))
        center_x = 8.5 * inch / 2
        center_y = 11 * inch / 2
        
        #lets draw our title first
        MainTitle_margin = center_x - 200
        current_y = 10.2 * inch - 40
        current_x = 0.5 * inch
        
        #PAGE TITLE FIRST
        textObject_Title = self.report.beginText(MainTitle_margin, current_y)
        textObject_Title.setTextOrigin(MainTitle_margin, current_y)
        textObject_Title.setFont('Times-Bold', 26)
        textObject_Title.textLine("Ion Chamber Measurement Data")   #we have removed the serial number here as we need to specify elsewhere what serial number we are measureing
        self.report.drawText(textObject_Title)
        
        #REPORT ID NUMBER
        position_RID = [center_x + 145, 10.2 * inch + 20]
        textObject_RID = self.report.beginText(position_RID[0], position_RID[1])
        textObject_RID.setTextOrigin(position_RID[0], position_RID[1])
        textObject_RID.setFont('Courier-Bold', 9)
        textObject_RID.textLine("Report ID: " + self.uid)
        self.report.drawText(textObject_RID)
        
        #DRAW THE RAD SOURCE LOGO IN THE UPPER LEFT HAND CORNER
        logoPosition = [20, inch * 10.2]
        logoSize = [104, 40]
        self.report.drawInlineImage(radSourceLogoLoc, logoPosition[0], logoPosition[1], width = logoSize[0], height = logoSize[1])
        
        #DRAW THE HEADER TABLES FOR OUR SYSTEM AND REFERENCE ION CHAMBER DATA
        y_header_tables = 8.5 * inch - 28 - 20
        x_header_system_tables = 20
        x_header_dosimeter_tables = 340
        tableSystemInfo_Data = [['System Information', ''],
                                ['Procedure Date: ', self.procedureDate],
                                ['Tube Model: ', self.tubeModel],
                                ['Tube Serial:', self.tubeSN],
                                ['Tube kV: ', self.tubekV + ' kV'],
                                ['Beam Quality: ', self.beamQulaity],
                                ['Generator Model: ', self.genModel],
                                ['Generator Serial: ', self.genSN]]
        
        #We will use this formatting for a few things, we can leave it generically as the Headers format
        tableFormat_Headers = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                          ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                          ("BOX",       (0,0), (-1,-1), 0.5,  colors.black),
                                          ('BACKGROUND',(0,0), (0, -1), colors.ReportLabLightBlue),
                                          ('BACKGROUND',(0,0), (-1, 0), colors.ReportLabLightBlue),
                                          ('FACE',      (0,0), (0,-1), 'Times-Bold'),
                                          ('FACE',      (1,0), (1,-1), 'Courier'),
                                          ('SPAN',      (0,0), (-1,-0))]) 
        
        SystemDataTable = Table(tableSystemInfo_Data, (1.5 * inch, 2 * inch), 14)
        SystemDataTable.setStyle(tableFormat_Headers)
        SystemDataTable.wrapOn(self.report, 0, 0)
        SystemDataTable.drawOn(self.report, x_header_system_tables, y_header_tables)
        
        tableDosimeterInfo_Data = [['Reference Dosimeter Information', ''],
                                   ['Ion Chamber ID: ', self.ICIDNumber],
                                   ['Manufacture: ', self.ICManu],
                                   ['Ion Chamber Model: ', self.ICModel],
                                   ['Ion Chamber Serial: ', self.ICSN],
                                   ['Digitizer Model: ', self.ElectroModel],
                                   ['Digitizer Serial: ', self.ElectroSN],
                                   ['Calibration Due Date: ', self.refDosimeterCalDate]]
        
        ReferenceDosiTable = Table(tableDosimeterInfo_Data,(1.5 * inch, 2 * inch), 14)
        ReferenceDosiTable.setStyle(tableFormat_Headers)
        ReferenceDosiTable.wrapOn(self.report, 0, 0)
        ReferenceDosiTable.drawOn(self.report, x_header_dosimeter_tables, y_header_tables)
        
        #ADD OUR PLOT TO OUR CALIBRATION SHEET
        plotPosition = [center_x - 200, 300]
        #plotPosition = [x_header_system_tables, 300]
        plotSize = [400, 250] #based on the figsize that has been set above, this is 6x4 resolution
        self.report.drawInlineImage(self.plotName, plotPosition[0], plotPosition[1], width = plotSize[0], height = plotSize[1])
        
        #TABLE FOR CALIBRATED UNIT
        """
        tableCalibratedUnit_Data = [['Ionization Chamber Information', '', '','','',''],
                                    ['Digitizer Model', 'Digitizer Serial', 'Ion Chamber Model', 'Ion Chamber SN', 'System Coeff(Gy/Rdg)', 'System Offset (Gy)'],
                                    ['PP_DaughterCard', self.unitDigiSN, 'RS_IonChamber', self.unitICSN, '{:.3f}'.format(self.fitCoeffs[0]), '{:.3f}'.format(self.fitCoeffs[1])]]
        
        tableCalibratedUnit_Format = TableStyle([('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                                                 ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                                 ("BOX",        (0,0), (-1,-1), 0.5,  colors.black),
                                                 ('BACKGROUND', (0,0), (-1, 0), colors.ReportLabGreen),
                                                 ('BACKGROUND', (0,1), (-1, 1), colors.ReportLabLightBlue),
                                                 ('SPAN',       (0,0), (-1, 0))
                                                 ])
        
        colWidth_CalibratedUnitTable = (1.3 * inch, 1.3 * inch,1.3 * inch,1.3 * inch,1.3 * inch,1.3 * inch)
        tablewidth_CalibratedUnitTable = sum(colWidth_CalibratedUnitTable)
        CalibratedUnitTable = Table(tableCalibratedUnit_Data, colWidth_CalibratedUnitTable, 14)
        CalibratedUnitTable.setStyle(tableCalibratedUnit_Format)
        CalibratedUnitTable.wrapOn(self.report, 0,0)
        CalibratedUnitTable.drawOn(self.report, center_x - tablewidth_CalibratedUnitTable/2, 220)
        """
        
        #COMMENT/TEXT LINES FOR DIGITIZER INFORMATION
        textObject_CalIonChamber = self.report.beginText(40, 270)
        textObject_CalIonChamber.setTextOrigin(40, 270)
        textObject_CalIonChamber.setFont('Times-Bold', 10)
        textObject_CalIonChamber.textLine("Ionization Chamber Information:")
        textObject_CalIonChamber.setFont('Courier', 10)
        textObject_CalIonChamber.textLine('Model:  ' + self.unitICModel)
        textObject_CalIonChamber.textLine('Serial: ' + self.unitICSN)
        self.report.drawText(textObject_CalIonChamber)
        #COMMENT/TEXT LINES FOR DIGITIZER INFORMATION
        textObject_CalDigitizer = self.report.beginText(40, 225)
        textObject_CalDigitizer.setTextOrigin(40,225)
        textObject_CalDigitizer.setFont('Times-Bold', 10)
        textObject_CalDigitizer.textLine('Digitizer/Electrometer Information:')
        textObject_CalDigitizer.setFont('Courier', 10)
        textObject_CalDigitizer.textLine('Model:  ' + self.unitDigiModel)
        textObject_CalDigitizer.textLine('Serial: ' + self.unitDigiSN)
        textObject_CalDigitizer.textLine('Scale:  ' + 'Dose Rate')
        textObject_CalDigitizer.textLine('Range:  ' + 'Gy/min')
        self.report.drawText(textObject_CalDigitizer)
        
        #now lets create a table to show the Calibration Coeffs
        tableCalibration_Data = [['Calibration Coeffs', ''],
                                 ['System Coeff (Gy/min/Rdg):', '{:.3f}'.format(self.fitCoeffs[0])],
                                 ['System Offset (Gy/min):',    '{:.3f}'.format(self.fitCoeffs[1])],
                                 ['System Uncertanty:', 'N/A']]
        tableCalibration_Format = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                              ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                              ("BOX",        (0,0), (-1,-1), 0.5,  colors.black),
                                              ('BACKGROUND', (0,0), (-1,0), colors.ReportLabLightBlue),
                                              ('SPAN',       (0,0), (-1, 0)),
                                              ('FACE',       (0,0), (-1,-1), 'Times-Bold'),
                                              ('FACE',       (1,1), (1, -1), 'Courier')
                                              ])
        
        colWidths_CalibrationDataTable = (1.75 * inch, 1 * inch)
        tableWidth_CalibrationDataTable = sum(colWidths_CalibrationDataTable)
        CalibrationDataTable = Table(tableCalibration_Data, colWidths_CalibrationDataTable, 14)
        CalibrationDataTable.setStyle(tableCalibration_Format)
        CalibrationDataTable.wrapOn(self.report, 0, 0)
        CalibrationDataTable.drawOn(self.report, center_x + tableWidth_CalibrationDataTable/2 - 40 , 210)
        
        #LINES ABOUT CALIBRATION PROCEDURE
        #textObject_CalComments = self.report.beginText()
        
        #LINES ABOUT ENVIRONMENTAL CONDITIONS
        textObject_Comments = self.report.beginText(40, 140)
        textObject_Comments.setTextOrigin(40, 140)
        textObject_Comments.setFont('Times-Roman', 10)
        textObject_Comments.textLine('Environmental Conditions: T=' + str(self.temp).format(width = 3) + ' \u00b0C, P=' + str(self.pres).format(width = 6) + ' kPa, RH=' + str(self.hum).format(width = 2) + '%')
        #textObject_Comments.textLine('Calibration Procedure: ' + calProc)
        self.report.drawText(textObject_Comments)
        
        #SIGNATURE LINES
        textObject_CalibratedBySig = self.report.beginText(40,100)
        textObject_CalibratedBySig.setTextOrigin(40, 100) 
        textObject_CalibratedBySig.setFont('Times-Roman', 12)
        textObject_CalibratedBySig.textLine('__________________________________')
        textObject_CalibratedBySig.textLine('Calibrated By:')
        textObject_CalibratedBySig.textLine(self.techName)
        textObject_CalibratedBySig.textLine('Calibration Technician')
        self.report.drawText(textObject_CalibratedBySig)

        textObject_VerifiedBySig = self.report.beginText(40,100)
        textObject_VerifiedBySig.setTextOrigin(340, 100)
        textObject_VerifiedBySig.setFont('Times-Roman', 12)
        textObject_VerifiedBySig.textLine('__________________________________')
        textObject_VerifiedBySig.textLine('Reviewed By:')
        textObject_VerifiedBySig.textLine('Physicist or Calibration Lab')
        textObject_VerifiedBySig.textLine('Committee Member or Dsignee')
        self.report.drawText(textObject_VerifiedBySig)
        
        #ADD FORM AND REV NUMBER
        textObject_FormNumberRev = self.report.beginText(40, 30)
        textObject_FormNumberRev.setTextOrigin(180, 30)
        textObject_FormNumberRev.setFont('Times-Italic', 10)
        textObject_FormNumberRev.textLine(self.FormNumber + self.FormName + self.FormRevision)
        self.report.drawText(textObject_FormNumberRev)
        
        return self.report
        
    
class FilmReaderCalibrationReportGenerator:
    def __init__(self, unitIDNumber, _unitSerialNumber, 
                 _calTechName, _procedureDate,
                 _calData_x = [], _calData_y = []):
        self.x = _calData_x
        self.y = _calData_y
        self.unitIDNumber = unitIDNumber
        self.x_dev = 0 #used for error bars for the plotting; only used when dataframe data is uploaded
        self.unitSerialNumber = _unitSerialNumber
        self.techName = _calTechName
        self.generateUID()
        self.procedureDate = _procedureDate
        self.reportGenerationDate = dt.datetime.now()
        self.tubeInfoInput = False
        self.generatorInfoInput = False
        self.environMentalInfoInput = False
        self.plotGenerated = False
        self.referenceDosimeterInfoInput = False
        self.calIonChamberInfoInput = False
        self.FormNumber = "BU-F-### "
        self.FormName = "Ion Chamber Calibration Form Rev_"
        self.FormRevision = "0.a"
        
    def setEnvironmentConditions(self, _temp, _pres, _hum):
        self.temp = _temp
        self.pres = _pres
        self.hum = _hum
        self.environMentalInfoInput = True
        return
        
    #Call to generate plot and save it to local location
    def generateCalPlot(self):
        #first we need the predicti
        self.fitCoeffsPower = self.generatePowerFit()
        self.fitCoeffsPoly = self.generatePolyFit()
        #Get predicted lines, we will avoid using the predict method to have more control over the output on the plot
        #we use the stepsize to ensure that we get a smooth plot
        stepsize = max(self.x)/100
        x_pred = np.arange(min(self.x), max(self.x)+stepsize, stepsize)
        y_pred_poly = []
        y_pred_power = []
        for x in x_pred:
            y_pred_power.append(self.fitCoeffsPower[0] * x ** self.fitCoeffsPower[1])
            y_pred_poly.append(self.fitCoeffsPoly[0] * (x **2) + self.fitCoeffsPoly[1] * x + self.fitCoeffsPoly[2])
        #lets create our figure and plot our data and fit lines
        self.fig = plt.figure(figsize=(8,5))
        colors_p = ['teal', 'magenta', 'cyan']
        labels = ['Data', 
                  'Polynomial Fit: ' + str(round(self.fitCoeffsPoly[0], 3)) + 'x\u00b2 +' + str(round(self.fitCoeffsPoly[1], 3)) + 'x + ' + str(round(self.fitCoeffsPoly[2],3)), 
                  'Power Fit: ' + str(round(self.fitCoeffsPower[0], 3)) + 'x' + r'$^{%s}$' %str(round(self.fitCoeffsPower[1],3))]
        plt.title(str(self.unitIDNumber) + ' Gaf-Chromic Film \u0394OD vs Dose (Gy)')
        plt.xlabel('\u0394' + 'OD (for Green ' + '\u03BB)')
        plt.ylabel('Dose (Gy)')
        plt.scatter(self.x, self.y, color = colors_p[0])
        plt.plot(x_pred, y_pred_poly, color = colors_p[1], label = labels[1])
        plt.plot(x_pred, y_pred_power, color = colors_p[2], label = labels[2])
        plt.grid(True)
        plt.legend(loc='upper left')
        #plt.text(min(self.x), 0.98 * max(self.y), 'Calibration Coeffs (Power): ' + str(round(self.fitCoeffs[0],4)).format(width = 4) + ' x + ' + str(round(self.fitCoeffs[1], 4)).format(width = 4))
        print()
        if(not(os.path.exists(filePrefixLocalStorage + filePrefixPlots))):
            os.makedirs(filePrefixLocalStorage + filePrefixPlots)
        self.plotName = filePrefixLocalStorage + filePrefixPlots + 'CalibrationPlot_' + self.uid + '.png'
        plt.savefig(self.plotName, dpi = 300)
        self.plotGenerated = True
        return
    
    def setDataFromDataFrame(self, _dataFrame):
        colHeaders = list(_dataFrame.columns.values)
        filmDOD = []
        filmDOD.append(_dataFrame[colHeaders[2]].to_numpy()[1:])
        filmDOD.append(_dataFrame[colHeaders[5]].to_numpy()[1:])
        filmDOD.append(_dataFrame[colHeaders[8]].to_numpy()[1:])
        filmDOD.append( _dataFrame[colHeaders[11]].to_numpy()[1:])
        filmDOD.append(_dataFrame[colHeaders[14]].to_numpy()[1:])
        filmDOD.append(_dataFrame[colHeaders[17]].to_numpy()[1:])
        accumDose = _dataFrame[colHeaders[-1]].to_numpy()[1:]
        filmAVG = []
        filmSTD = []
        for i in range(len(filmDOD[0])):
            _sum = 0
            for j in range(6):
                _sum += filmDOD[j][i] 
            _avg = round(_sum/6, 4)
            std = round(sum([((x - _avg) ** 2) for x in filmDOD[j]])/ 6 , 4)
            filmAVG.append(_avg)
            filmSTD.append(std)
        self.x = np.array(filmAVG)
        self.x_dev = np.array(filmSTD)
        self.y = np.array(accumDose)

    
    def setTubeInfo(self, tubeModel, tubeSN, tubekV, beamQuality):
        self.tubeSN = tubeSN
        self.tubeModel = tubeModel
        self.tubekV = tubekV
        self.beamQulaity = beamQuality
        self.tubeInfoInput = True
    
    def setGeneratorInfo(self, genModel, genSN,):
        self.genSN = genSN
        self.genModel = genModel
        self.generatorInfoInput = True
    
    def setReferenceDosimeterInfo(self, ICIDNumber, ICManu, ICModel, ICSN, ElectroManu, ElectroModel, ElectroSN, CalDate):
        self.ICIDNumber = ICIDNumber
        self.ICManu = ICManu
        self.ICModel = ICModel
        self.ICSN = ICSN
        self.ElectroManu = ElectroManu
        self.ElectroModel = ElectroModel
        self.ElectroSN = ElectroSN
        self.refDosimeterCalDate = CalDate
        self.referenceDosimeterInfoInput = True
    
    def setCalFilmReaderInfo(self, IDNO, Manu, Model, SN):
        self.unitSN = SN
        self.unitIDNumber = IDNO
        self.unitManu = Manu
        self.unitModel = Model
        self.calIonChamberInfoInput = True
    
    def generatePolyFit(self):
        X = self.x.reshape(-1,1)
        y = self.y
        poly = PolynomialFeatures(degree = 2, include_bias = False)
        polyFeatures = poly.fit_transform(X)
        
        self.regModel = LinearRegression()
        self.regModel.fit(polyFeatures,y)
        #Remember, the coeffs start from x^1 at index 0
        return list([self.regModel.coef_[1], self.regModel.coef_[0], self.regModel.intercept_])
        
    
    def generatePowerFit(self):
        #for a power fit, we have to log10 our data and then de log the fit values
        log10_x = []
        log10_y = []
        for i in range(len(self.x)):
            log10_x.append(math.log10(self.x[i]))
            log10_y.append(math.log10(self.y[i]))
        log10_x = np.array(log10_x)
        log10_y = np.array(log10_y)
        self.powerReg = LinearRegression()
        self.powerReg.fit(log10_x.reshape(-1,1), log10_y)
        powerA = 10 ** self.powerReg.intercept_
        powerB = self.powerReg.coef_[0]
        return (powerA, powerB)
    
    def generateUID(self):
        _now = dt.datetime.now()
        _day = _now.day
        _month = _now.month
        _year = _now.year
        s_day = '0' + str(_day) if _day < 10 else str(_day)
        s_month = '0' + str(_month) if _month < 10 else str(_month)
        s_year = str(_year)
        sec = dt.datetime.now().second + dt.datetime.now().minute * 60 + dt.datetime.now().hour * 3600
        self.uid = 'RS_' + s_year + s_month + s_day + str(sec).format(width = 5)
    
    def generateReport(self):
        #ensure that a calibration plot has been generated | this will 
        if not(self.plotGenerated):
            self.generateCalPlot()
        if not(self.environMentalInfoInput):
            print("Environmental information not input, please call PortablePhantomReportGenerator.setEnvironmentConditions(_temp, _pres, _hum) to set these parameters.")
            return
        if not(self.tubeInfoInput):
            print("Tube information not input, please call PortablePhantomReportGenerator.setTubeInfo(tubeSN, tubeModel, tubekV) to set these parameters.")
            return
        if not(self.generatorInfoInput):
            print("Generator information not input, please call PortablePhantomReportGenerator.setGeneratorInfo(genSN, genModel) to set these parameters.")
            return
        if not(self.referenceDosimeterInfoInput):
            print("Reference Ion Chamber information not input, please call PortablePhantomReportGenerator.setReferenceDosimeterInfo(ICManu, ICModel, ICSN, ElectroManu, ElectroModel, ElectroSN, CalDate) to set these parameters.")
            return
        if not(self.calIonChamberInfoInput):
            print("Data for the unit being calibrated has not been input, plese call PortablePhantomReportGenerator.setCalIonChamberInfo(ICSN, DigiSN)")
            return
        
        #now we can start creating our Calibration Report
        if(not(os.path.exists(filePrefixLocalStorage + filrPrefixReports))):
            os.makedirs(filePrefixLocalStorage + filrPrefixReports)
        self.currentReportFileName = filePrefixLocalStorage + filrPrefixReports + "PortablePhantomIonChamberCalibrationReport_" + self.uid + '.pdf'
        self.report = Canvas(self.currentReportFileName, pagesize=(8.5 * inch, 11 * inch))
        center_x = 8.5 * inch / 2
        center_y = 11 * inch / 2
        
        #lets draw our title first
        MainTitle_margin = center_x - 200
        current_y = 10.2 * inch - 40
        current_x = 0.5 * inch
        
        #PAGE TITLE FIRST
        textObject_Title = self.report.beginText(MainTitle_margin, current_y)
        textObject_Title.setTextOrigin(MainTitle_margin, current_y)
        textObject_Title.setFont('Times-Bold', 26)
        textObject_Title.textLine("Ion Chamber Measurement Data")   #we have removed the serial number here as we need to specify elsewhere what serial number we are measureing
        self.report.drawText(textObject_Title)
        
        #REPORT ID NUMBER
        position_RID = [center_x + 145, 10.2 * inch + 20]
        textObject_RID = self.report.beginText(position_RID[0], position_RID[1])
        textObject_RID.setTextOrigin(position_RID[0], position_RID[1])
        textObject_RID.setFont('Courier-Bold', 9)
        textObject_RID.textLine("Report ID: " + self.uid)
        self.report.drawText(textObject_RID)
        
        #DRAW THE RAD SOURCE LOGO IN THE UPPER LEFT HAND CORNER
        logoPosition = [20, inch * 10.2]
        logoSize = [104, 40]
        self.report.drawInlineImage(radSourceLogoLoc, logoPosition[0], logoPosition[1], width = logoSize[0], height = logoSize[1])
        
        #DRAW THE HEADER TABLES FOR OUR SYSTEM AND REFERENCE ION CHAMBER DATA
        y_header_tables = 8.5 * inch - 28 - 20
        x_header_system_tables = 20
        x_header_dosimeter_tables = 340
        tableSystemInfo_Data = [['System Information', ''],
                                ['Procedure Date: ', self.procedureDate],
                                ['Tube Model: ', self.tubeModel],
                                ['Tube Serial:', self.tubeSN],
                                ['Tube kV: ', self.tubekV + ' kV'],
                                ['Beam Quality: ', self.beamQulaity],
                                ['Generator Model: ', self.genModel],
                                ['Generator Serial: ', self.genSN]]
        
        #We will use this formatting for a few things, we can leave it generically as the Headers format
        tableFormat_Headers = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                          ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                          ("BOX",       (0,0), (-1,-1), 0.5,  colors.black),
                                          ('BACKGROUND',(0,0), (0, -1), colors.ReportLabLightBlue),
                                          ('BACKGROUND',(0,0), (-1, 0), colors.ReportLabLightBlue),
                                          ('FACE',      (0,0), (0,-1), 'Times-Bold'),
                                          ('FACE',      (1,0), (1,-1), 'Courier'),
                                          ('SPAN',      (0,0), (-1,-0))]) 
        
        SystemDataTable = Table(tableSystemInfo_Data, (1.5 * inch, 2 * inch), 14)
        SystemDataTable.setStyle(tableFormat_Headers)
        SystemDataTable.wrapOn(self.report, 0, 0)
        SystemDataTable.drawOn(self.report, x_header_system_tables, y_header_tables)
        
        tableDosimeterInfo_Data = [['Reference Dosimeter Information', ''],
                                   ['Ion Chamber ID: ', self.ICIDNumber],
                                   ['Manufacture: ', self.ICManu],
                                   ['Ion Chamber Model: ', self.ICModel],
                                   ['Ion Chamber Serial: ', self.ICSN],
                                   ['Digitizer Model: ', self.ElectroModel],
                                   ['Digitizer Serial: ', self.ElectroSN],
                                   ['Calibration Due Date: ', self.refDosimeterCalDate]]
        
        ReferenceDosiTable = Table(tableDosimeterInfo_Data,(1.5 * inch, 2 * inch), 14)
        ReferenceDosiTable.setStyle(tableFormat_Headers)
        ReferenceDosiTable.wrapOn(self.report, 0, 0)
        ReferenceDosiTable.drawOn(self.report, x_header_dosimeter_tables, y_header_tables)
        
        #ADD OUR PLOT TO OUR CALIBRATION SHEET
        plotPosition = [center_x - 200, 300]
        #plotPosition = [x_header_system_tables, 300]
        plotSize = [400, 250] #based on the figsize that has been set above, this is 6x4 resolution
        self.report.drawInlineImage(self.plotName, plotPosition[0], plotPosition[1], width = plotSize[0], height = plotSize[1])
        
        #TABLE FOR CALIBRATED UNIT
        """
        tableCalibratedUnit_Data = [['Ionization Chamber Information', '', '','','',''],
                                    ['Digitizer Model', 'Digitizer Serial', 'Ion Chamber Model', 'Ion Chamber SN', 'System Coeff(Gy/Rdg)', 'System Offset (Gy)'],
                                    ['PP_DaughterCard', self.unitDigiSN, 'RS_IonChamber', self.unitICSN, '{:.3f}'.format(self.fitCoeffs[0]), '{:.3f}'.format(self.fitCoeffs[1])]]
        
        tableCalibratedUnit_Format = TableStyle([('ALIGN',      (0,0), (-1,-1), 'CENTER'),
                                                 ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                                 ("BOX",        (0,0), (-1,-1), 0.5,  colors.black),
                                                 ('BACKGROUND', (0,0), (-1, 0), colors.ReportLabGreen),
                                                 ('BACKGROUND', (0,1), (-1, 1), colors.ReportLabLightBlue),
                                                 ('SPAN',       (0,0), (-1, 0))
                                                 ])
        
        colWidth_CalibratedUnitTable = (1.3 * inch, 1.3 * inch,1.3 * inch,1.3 * inch,1.3 * inch,1.3 * inch)
        tablewidth_CalibratedUnitTable = sum(colWidth_CalibratedUnitTable)
        CalibratedUnitTable = Table(tableCalibratedUnit_Data, colWidth_CalibratedUnitTable, 14)
        CalibratedUnitTable.setStyle(tableCalibratedUnit_Format)
        CalibratedUnitTable.wrapOn(self.report, 0,0)
        CalibratedUnitTable.drawOn(self.report, center_x - tablewidth_CalibratedUnitTable/2, 220)
        """
        
        #COMMENT/TEXT LINES FOR DIGITIZER INFORMATION
        textObject_CalIonChamber = self.report.beginText(40, 270)
        textObject_CalIonChamber.setTextOrigin(40, 270)
        textObject_CalIonChamber.setFont('Times-Bold', 10)
        textObject_CalIonChamber.textLine("Ionization Chamber Information:")
        textObject_CalIonChamber.setFont('Courier', 10)
        textObject_CalIonChamber.textLine('Model:  ' + self.unitICModel)
        textObject_CalIonChamber.textLine('Serial: ' + self.unitICSN)
        self.report.drawText(textObject_CalIonChamber)
        #COMMENT/TEXT LINES FOR DIGITIZER INFORMATION
        textObject_CalDigitizer = self.report.beginText(40, 225)
        textObject_CalDigitizer.setTextOrigin(40,225)
        textObject_CalDigitizer.setFont('Times-Bold', 10)
        textObject_CalDigitizer.textLine('Digitizer/Electrometer Information:')
        textObject_CalDigitizer.setFont('Courier', 10)
        textObject_CalDigitizer.textLine('Model:  ' + self.unitDigiModel)
        textObject_CalDigitizer.textLine('Serial: ' + self.unitDigiSN)
        textObject_CalDigitizer.textLine('Scale:  ' + 'Dose Rate')
        textObject_CalDigitizer.textLine('Range:  ' + 'Gy/min')
        self.report.drawText(textObject_CalDigitizer)
        
        #now lets create a table to show the Calibration Coeffs
        tableCalibration_Data = [['Calibration Coeffs', ''],
                                 ['System Coeff (Gy/min/Rdg):', '{:.3f}'.format(self.fitCoeffs[0])],
                                 ['System Offset (Gy/min):',    '{:.3f}'.format(self.fitCoeffs[1])],
                                 ['System Uncertanty:', 'N/A']]
        tableCalibration_Format = TableStyle([('ALIGN',     (0,0), (-1,-1), 'CENTER'),
                                              ('INNERGRID',  (0,0), (-1,-1), 0.25, colors.black),
                                              ("BOX",        (0,0), (-1,-1), 0.5,  colors.black),
                                              ('BACKGROUND', (0,0), (-1,0), colors.ReportLabLightBlue),
                                              ('SPAN',       (0,0), (-1, 0)),
                                              ('FACE',       (0,0), (-1,-1), 'Times-Bold'),
                                              ('FACE',       (1,1), (1, -1), 'Courier')
                                              ])
        
        colWidths_CalibrationDataTable = (1.75 * inch, 1 * inch)
        tableWidth_CalibrationDataTable = sum(colWidths_CalibrationDataTable)
        CalibrationDataTable = Table(tableCalibration_Data, colWidths_CalibrationDataTable, 14)
        CalibrationDataTable.setStyle(tableCalibration_Format)
        CalibrationDataTable.wrapOn(self.report, 0, 0)
        CalibrationDataTable.drawOn(self.report, center_x + tableWidth_CalibrationDataTable/2 - 40 , 210)
        
        #LINES ABOUT CALIBRATION PROCEDURE
        #textObject_CalComments = self.report.beginText()
        
        #LINES ABOUT ENVIRONMENTAL CONDITIONS
        textObject_Comments = self.report.beginText(40, 140)
        textObject_Comments.setTextOrigin(40, 140)
        textObject_Comments.setFont('Times-Roman', 10)
        textObject_Comments.textLine('Environmental Conditions: T=' + str(self.temp).format(width = 3) + ' \u00b0C, P=' + str(self.pres).format(width = 6) + ' kPa, RH=' + str(self.hum).format(width = 2) + '%')
        #textObject_Comments.textLine('Calibration Procedure: ' + calProc)
        self.report.drawText(textObject_Comments)
        
        #SIGNATURE LINES
        textObject_CalibratedBySig = self.report.beginText(40,100)
        textObject_CalibratedBySig.setTextOrigin(40, 100) 
        textObject_CalibratedBySig.setFont('Times-Roman', 12)
        textObject_CalibratedBySig.textLine('__________________________________')
        textObject_CalibratedBySig.textLine('Calibrated By:')
        textObject_CalibratedBySig.textLine(self.techName)
        textObject_CalibratedBySig.textLine('Calibration Technician')
        self.report.drawText(textObject_CalibratedBySig)

        textObject_VerifiedBySig = self.report.beginText(40,100)
        textObject_VerifiedBySig.setTextOrigin(340, 100)
        textObject_VerifiedBySig.setFont('Times-Roman', 12)
        textObject_VerifiedBySig.textLine('__________________________________')
        textObject_VerifiedBySig.textLine('Reviewed By:')
        textObject_VerifiedBySig.textLine('Physicist or Calibration Lab')
        textObject_VerifiedBySig.textLine('Committee Member or Dsignee')
        self.report.drawText(textObject_VerifiedBySig)
        
        #ADD FORM AND REV NUMBER
        textObject_FormNumberRev = self.report.beginText(40, 30)
        textObject_FormNumberRev.setTextOrigin(180, 30)
        textObject_FormNumberRev.setFont('Times-Italic', 10)
        textObject_FormNumberRev.textLine(self.FormNumber + self.FormName + self.FormRevision)
        self.report.drawText(textObject_FormNumberRev)
        
        return self.report 