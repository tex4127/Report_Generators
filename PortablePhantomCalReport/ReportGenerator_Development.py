# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 10:30:02 2023

@author: JGarner
"""

import pandas as pd
import numpy as np
import csv
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


df = pd.read_csv("Data.csv")
#get header data
headerData = list(df.columns.values)

#extract data into numpy arrays
x = df[headerData[1]].to_numpy()
y = df[headerData[0]].to_numpy()

#lts do some magic with the fit curves
reg = LinearRegression()
reg.fit(x.reshape(-1,1), y)
#now create some arbitrary data for our fit line
x_pred = np.arange(min(x), max(x), 1).reshape(-1,1)
y_pred = reg.predict(x_pred)
coeffA = "{:.4f}".format(reg.coef_[0])
coeffB = "{:.4f}".format(reg.intercept_)
print(coeffA)
print(coeffB)

IonChamberSN = "1003"

#lets generate some plots using this information first
fig = plt.figure(figsize=(8,5))
plt.title("Portable Phantom Calibration Curve for %s" %IonChamberSN)
plt.ylabel("%s" %headerData[0])
plt.xlabel("%s" %headerData[1])
plt.scatter(x,y)
plt.plot(x_pred, y_pred, color = 'magenta', label = "Predicted Fit Curve")
plt.legend()
plt.grid(True)
plt.text(min(x), 0.9 * max(y), "Fit Coeffs: " + coeffA + " x + " + coeffB)

plt.savefig("TesingFig.png", dpi = 300)

