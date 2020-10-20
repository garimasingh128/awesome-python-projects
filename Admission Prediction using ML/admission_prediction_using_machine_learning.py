# Admission_Prediction_using_Machine_Learning By Zahra Shahid


"""# **Import libraries**"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


"""# **Upload and Read file**"""

from google.colab import files
files.upload()

df = pd.read_csv("Admission_Predict_Ver1.1.csv")

df.head(8)


"""# **Cleaning the data**"""

df.columns

df.drop('Serial No.',axis=1,inplace=True)

df.head()


"""#**Exploratory Data Aanalysis**"""

df.describe()

df.corr()

sns.heatmap(df.corr(), annot=True)

sns.distplot(df.CGPA)

sns.pairplot(df,x_vars=['SOP','GRE Score','TOEFL Score','CGPA'],y_vars=['Chance of Admit '],height=5, aspect=0.8, kind='reg')


"""# **Creating Model**"""

df.columns

x=df[['GRE Score', 'TOEFL Score', 'CGPA']]

y=df[['Chance of Admit ']]

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import random

x_train, x_test, y_train, y_test =train_test_split(x,y,test_size=0.20,random_state=0)

x_train.shape

y_train.shape

linreg = LinearRegression()
linreg.fit(x_train,y_train)


"""# **Testing and Evaluating the Model**"""

y_pred=linreg.predict(x_test)

y_pred[:7]

y_test.head(7)

from sklearn import metrics
print(metrics.mean_absolute_error(y_test,y_pred))   #96% prediction

