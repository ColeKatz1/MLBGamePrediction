from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
import pandas as pd

df = pd.read_csv("dfFinal.csv") #this is the csv file outputted by the create_dataset.py file


y = df['WinOrLoss']


x = df[['HomeOrAway','Win_Percentage','Pit_Moving_Average_3','SLG_Moving_Average_10','Win_Percentage_Moving_Average_10','OPS_Season_Long_Average','SO_Moving_Average_3']]


#this outputs the accuracy score over 100 separate training and testings 
totalScore = 0
count = 0
for i in range(100):
    print(i)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)
    svc_lin = SVC(kernel = 'linear', )
    svc_lin_model = svc_lin.fit(x_train, y_train)
    y_pred = svc_lin_model.predict(x_test)
    score = accuracy_score(y_test, y_pred)
    totalScore = totalScore + score
    count = count + 1
    print(totalScore/count)

