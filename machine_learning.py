from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
import pandas as pd

df = pd.read_csv("dfFinal.csv")


y = df['WinOrLoss']


x = df[['HomeOrAway','Win_Percentage']] #you can select whichever variables you like from here

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)
svc_lin = SVC(kernel = 'linear', )
svc_lin_model = svc_lin.fit(x_train, y_train)
print('SVC Linear:', svc_lin_model.score(x_test, y_test))

