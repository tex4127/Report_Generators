# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 12:13:58 2023

this file is just to test the library for various data sets 

@author: JGarner
"""
import pandas as pd
import numpy as np
from CalibrationReportGenerator import PortablePhantomReportGenerator
from CalibrationReportGenerator import FilmReaderCalibrationReportGenerator

#For Testing the Ion Chamber Calibration Report
"""
df = pd.read_csv('data/Data_IonChamber.csv')
colHeaders = list(df.columns.values)
x = df[colHeaders[1]].to_numpy()
y = df[colHeaders[0]].to_numpy()

rg = PortablePhantomReportGenerator('1006','Jacob Garner, B.S.', "12/8/2023",x,y)
rg.setEnvironmentConditions(22.1, 99.58, 34)
rg.setTubeInfo("DT-1084", "10277-01", "120", "120-M")
rg.setGeneratorInfo("X-4119", "A013468")
rg.setReferenceDosimeterInfo("RAD-008","RadCal", "10x0.6-6", "02-1964", "RadCal", "ADDM+", "47-1995", "1/24/2024")
rg.setCalIonChamberInfo("Type J","1006", "Phantom C Daughter Card","1014")

report = rg.generateReport()

report.save()
"""

#For Testing the Film Reader Calibration Report Generation

df = pd.read_csv('data/Data_Film.csv')

rg = FilmReaderCalibrationReportGenerator('DR4-009', '12411', 'Jacob Garner', '12/8/2023')
rg.setDataFromDataFrame(df)
rg.setTubeInfo("DT-1084", "10277-01", "120", "120-M")
rg.setGeneratorInfo("X-4119", "A013468")
rg.setReferenceDosimeterInfo("RAD-008","RadCal", "10x0.6-6", "02-1964", "RadCal", "ADDM+", "47-1995", "1/24/2024")
rg.setEnvironmentConditions(22.1, 99.58, 34)

rg.generateCalPlot()