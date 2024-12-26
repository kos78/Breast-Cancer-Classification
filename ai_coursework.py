# -*- coding: utf-8 -*-
"""AI Coursework

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XDerfUTqBgIseMVV-Ho-c0rMoFXs7uUe

Importing libraries and loading dataset
"""

import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
# allows the file to be uploaded
from google.colab import files
uploaded = files.upload()

# read the the dataset
df = pd.read_csv('data.csv')

"""**Data Preprocessing**"""

# shows the sum of all the missing values in each feature
print(df.isnull().sum())

"""**Feature Selection**"""

from sklearn.feature_selection import SelectKBest, chi2
# remove the target variable and the id as the id has no bearings on the prediction
X = df.drop(['id', 'diagnosis'], axis=1)
y = df['diagnosis']
selector = SelectKBest(chi2, k=10)
selector.fit(X, y)
# get selected feature names
feature_mask = selector.get_support()
selected_features = X.columns[feature_mask]
print(selected_features)

# print out the first five values of each feature just to see
print(df.head())

"""Exploratory Data Analysis"""

import seaborn as sns
import matplotlib.pyplot as plt
# find the column that contains non-numeric values
non_numeric_columns = df.select_dtypes(exclude=['number']).columns
# drop the column that contains no numeric values
df_encoded = pd.get_dummies(df, columns=non_numeric_columns, drop_first=True)
# drop the id since it's not data of the breast mass
df_no_id = df_encoded.drop(['id',], axis=1)
plt.figure(figsize=(24, 24))
# plot the heat map where the more red it is the high the correlation and the more blue it is the lower the correlation
sns.heatmap(df_no_id.corr(), annot=True, cmap='coolwarm')
plt.show()

# Using box plots
import matplotlib.pyplot as plt
df_no_id = df.drop('id', axis=1)
df_no_id.plot(kind='box', figsize=(20,20))
plt.show()

# include only the numeric values inside the dataset
df_no_id_numeric = df_no_id.select_dtypes(include=[float, int])
# define the lower and upper quartile
Q1 = df_no_id_numeric.quantile(0.25)
Q3 = df_no_id_numeric.quantile(0.75)
# interquartile range formula
IQR = Q3 - Q1

# define the lower and upper bounds
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# define what an outlier is
outliers = ((df_no_id_numeric < lower_bound) | (df_no_id_numeric > upper_bound))
outlier_row = df_no_id_numeric[outliers.any(axis=1)]
# print out the rows that contain outliers
print(outlier_row)

"""Define X and Y."""

# X is all the features except for the id which has no affect on the diagnosis
# and the diagnosis itself
X = pd.get_dummies(df.drop(['id','diagnosis'] + selected_features.tolist(), axis=1), dtype=float)
# y is the diagnosis since that's what we're trying to predict.
# a function is applied that assigns 1 to the column if the diagnosis is malignant
# and 0 for anything else i.e., Benign
y = df['diagnosis'].apply(lambda x: 1 if x =='M' else 0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# checking just for confirmation
y_test.shape

"""Importing necessary libraries"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.metrics import accuracy_score

"""**Model 1: Sequential**"""

model = Sequential() # uses a sequential model good for classification
# add two layers to the network one first one has 32 neurons, second has 64
model.add(Dense(units=32, activation='relu', input_dim=len(X.columns)))
model.add(Dense(units=64, activation='relu'))
model.add(Dense(units=1, activation='sigmoid')) # produces a binary output which is ideal for classification

model.compile(optimizer='sgd', loss='binary_crossentropy',metrics=['accuracy'])

"""Training the model"""

model.fit(X_train, y_train, epochs = 300, batch_size=32)

y_hat_sq = model.predict(X_test)
y_hat_sq

"""**Evaluating the model**"""

test_loss, test_acc = model.evaluate(X_test, y_test)
print('Test accuracy:', test_acc, 'Test loss:', test_loss)

# using a confusion matrix
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
# uses a heatmap to show accuracy
cm = confusion_matrix(y_test, y_hat_sq.round())
sns.heatmap(cm, annot=True, fmt='d')
plt.xlabel('Predicted')
plt.ylabel('Truth')
# recall shows how many of the actual positives (True Negatives + True positives) were correctly predicted
# precision measures how many of the predicted postives were correct

# shows the precision, recall and f1-score
print(classification_report(y_test, y_hat_sq.round()))

"""Evaluating the model using ROC-AUC"""

#Evaluating model using ROC-AUC
from sklearn.metrics import roc_curve, roc_auc_score
# calculate to ROC score
roc_auc_score(y_test, y_hat_sq)

# Plot the ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_hat_sq)
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc_score(y_test, y_hat_sq))
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')

print(y_test)
accuracy_score(y_test, y_hat_sq.round())

"""**Model 2: DecisionTreeClassifier**"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree
X = pd.get_dummies(df.drop(['id', 'diagnosis'], axis=1), dtype=float)
y = df['diagnosis'].apply(lambda x: 1 if x =='M' else 0)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf = DecisionTreeClassifier(criterion='entropy')
clf.fit(X_train, y_train)
y_hat_dtc = clf.predict(X_test)

tree.plot_tree(clf)

"""Feature Importance"""

# to see which features have the most affect on the result of achieving a maligant diagnosis
# for loop goes through all the columns and prints out each features feature importance
feature_importance = clf.feature_importances_
for i in range(len(X.columns)):
  print(X.columns[i], feature_importance[i])

# better graph that includes colour

import graphviz
from graphviz import Source

dot_data = tree.export_graphviz(clf, out_file=None,
                                feature_names=X.columns,
                                class_names=['B', 'M'],
                                filled=True, proportion=True)


dot_data = dot_data.replace('digraph Tree {', 'digraph Tree {\nsize="8,9";')

# Create the Source object with the modified DOT data
graph = Source(dot_data, format="png")

# Render and view the graph
graph


# coloured_graph = graphviz.Source(dot_data, format="png")
# coloured_graph.graph_attr.update(size='10,10')
# coloured_graph

"""**Evaluating the model**"""

# using a confusion matrix
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
# uses a heatmap to show accuracy
cm = confusion_matrix(y_test, y_hat_dtc)
sns.heatmap(cm, annot=True, fmt='d')
plt.xlabel('Predicted')
plt.ylabel('Truth')
# recall shows how many of the actual positives (True Negatives + True positives) were correctly predicted
# precision measures how many of the predicted postives were correct

# shows the precision, recall and f1-score
print(classification_report(y_test, y_hat_dtc.round()))

#Evaluating model using ROC-AUC
from sklearn.metrics import roc_curve, roc_auc_score
# calculate to ROC score
roc_auc_score(y_test, y_hat_dtc)

# Plot the ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_hat_dtc)
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc_score(y_test, y_hat_dtc))
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

# performance metrics for sequential model
accuracy_sq = accuracy_score(y_test, y_hat_sq.round())
precision_sq = precision_score(y_test, y_hat_sq.round())
recall_sq = recall_score(y_test, y_hat_sq.round())
f1_sq = f1_score(y_test, y_hat_sq.round())

# performance metrics for decision tree classifier
accuracy_dtc = accuracy_score(y_test, y_hat_dtc)
precision_dtc = precision_score(y_test, y_hat_dtc)
recall_dtc = recall_score(y_test, y_hat_dtc)
f1_dtc = f1_score(y_test, y_hat_dtc)

comparison_data = {
    'Model': ['Sequential', 'Decision Tree Classifier'],
    'Accuracy': [accuracy_sq, accuracy_dtc],
    'Precision': [precision_sq, precision_dtc],
    'Recall': [recall_sq, recall_dtc],
    'F1-Score': [f1_sq, f1_dtc]
}

comparison_df = pd.DataFrame(comparison_data)
comparison_df