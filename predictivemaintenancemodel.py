from torch import nn
import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

df = pd.read_csv("predictive_maintenance.csv") 

df = df.dropna() #dropping any rows in the csv with an empty cell 

#extracting our target values
y_target = df["Target"] 
y_failure_type = df["Failure Type"]  

df = pd.get_dummies(df,columns=["Type"]) 
# Applying one-hot encoding to the "Type" column of the DataFrame, because it is a feature with categorical data. This will create new binary (0 or 1) columns
# in the DataFrame for each unique value in the "Type" column. Rows will have a 1 in the column for their 
# original "Type" value and 0 in all other new "Type" columns.

X = df.drop(["Target","Failure Type","UDI","Product ID"] , axis=1) #dropping the columns that have no correlation to output and also target columns

#Splitting train and test data. 60% train, 40% test

X_train,X_test,y_target_train,y_target_test = train_test_split(X,y_target,test_size=0.40,random_state=42)
y_failure_type_train,y_failure_type_test = train_test_split(y_failure_type,test_size=0.40,random_state=42)



scaler = StandardScaler() #standardizing the numerical data 
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

encoder = LabelEncoder() #this is used to map numerical values to non-numerical data
y_failure_type_train = encoder.fit_transform(y_failure_type_train)
y_failure_type_test = encoder.transform(y_failure_type_test)


X_train

#converting data to tensors

X_train = torch.tensor(X_train,dtype=torch.float)
X_test = torch.tensor(X_test,dtype=torch.float)
y_target_train = torch.tensor(y_target_train.values,dtype=torch.float)
y_target_test = torch.tensor(y_target_test.values,dtype=torch.float)
y_failure_type_train = torch.tensor(y_failure_type_train,dtype=torch.long)
y_failure_type_test = torch.tensor(y_failure_type_test,dtype=torch.long)

class TargetPredictionModel(nn.Module): #binary classification model
  def __init__(self):
    super().__init__()
    self.layers = nn.Sequential(
        nn.Linear(in_features=8,out_features=16),
        nn.BatchNorm1d(16),
        nn.ReLU(),
        nn.Linear(in_features=16,out_features =30),
        nn.BatchNorm1d(30),
        nn.ReLU(),
        nn.Linear(in_features=30,out_features =15),
        nn.BatchNorm1d(15),
        nn.ReLU(),
        nn.Linear(in_features=15,out_features =13),
        nn.BatchNorm1d(13),
        nn.ReLU(),
        nn.Linear(in_features=13,out_features =10),
        nn.BatchNorm1d(10),
        nn.ReLU(),
        nn.Linear(in_features=10,out_features=1)
    )

  def forward(self,X):
     return self.layers(X).squeeze(dim=1)

model0 = TargetPredictionModel()

NUM_CLASSES = len(y_failure_type.unique()) #gets the total number of unique faiilure types

class FailureTypePredictionModel(nn.Module): #multiclass classification  model
  def __init__(self):
    super().__init__()
    self.layers = nn.Sequential(
          nn.Linear(in_features=8,out_features=16),
          nn.BatchNorm1d(16),
          nn.ReLU(),
          nn.Linear(in_features=16,out_features =24),
          nn.BatchNorm1d(24),
          nn.ReLU(),
          nn.Linear(in_features=24,out_features =32),
          nn.BatchNorm1d(32),
          nn.ReLU(),
          nn.Linear(in_features=32,out_features =36),
          nn.BatchNorm1d(36),
          nn.ReLU(),
          nn.Linear(in_features=36,out_features=NUM_CLASSES)
      )

  def forward(self,X):
     X =self.layers(X)
     return X.squeeze(dim=1)

model1 = FailureTypePredictionModel()

target_loss_fn = nn.BCEWithLogitsLoss()
failure_type_loss_fn = nn.CrossEntropyLoss()
target_optimizer = torch.optim.Adam(params=model0.parameters(),lr=0.0008)
failure_type_optimizer = torch.optim.Adam(params=model1.parameters(),lr=0.005)

epochs = 5000
target_min_val_loss = float('inf')
# Define patience and counter for early stopping
target_patience = 2
target_patience_counter = 0

for epoch in range(epochs):
  model0.train()
  y_target_preds = model0(X_train)
  loss = target_loss_fn(y_target_preds,y_target_train)
  target_optimizer.zero_grad()
  loss.backward()
  target_optimizer.step()

  if epoch % 200 == 0:
    with torch.inference_mode():
      model0.eval()
      y_target_test_preds = model0(X_test)
      test_loss = target_loss_fn(y_target_test_preds,y_target_test)

      if test_loss < target_min_val_loss:
        # Save the model state
        print(test_loss)
        torch.save(model0.state_dict(), 'PredictTarget.pt')
        target_min_val_loss = test_loss
        target_patience_counter = 0
      else:
        target_patience_counter += 1
        if target_patience_counter >= target_patience:
          print("Early stopping: Stop training")
          # Load the last saved weights
          model0.load_state_dict(torch.load('PredictTarget.pt'))
          break

epochs = 4000
failure_type_min_val_loss = float('inf')
# Define patience and counter for early stopping
failure_type_patience = 2
failure_type_patience_counter = 0
for epoch in range(epochs):
  model0.train()
  y_failure_type_preds = model1(X_train)
  loss = failure_type_loss_fn(y_failure_type_preds,y_failure_type_train)
  failure_type_optimizer.zero_grad()
  loss.backward()
  failure_type_optimizer.step()

  if epoch % 10 == 0:
    with torch.inference_mode():
      model0.eval()
      y_failure_type_test_preds = model1(X_test)
      test_loss = failure_type_loss_fn(y_failure_type_test_preds,y_failure_type_test)

      if test_loss < failure_type_min_val_loss:
        # Save the model state
        print(test_loss)
        torch.save(model0.state_dict(), 'PredictFailureType.pt')
        failure_type_min_val_loss = test_loss
        failure_type_patience_counter = 0
      else:
        failure_type_patience_counter += 1
        if failure_type_patience_counter >= failure_type_patience:
          print("Early stopping: Stop training")
          # Load the last saved weights
          model0.load_state_dict(torch.load('PredictFailureType.pt'))
          break

      print(test_loss)
