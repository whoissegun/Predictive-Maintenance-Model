# Predictive-Maintenance-Model


This project involves the creation and training of a deep learning model for predicting machine failures. It uses a synthetic dataset that reflects real-world predictive maintenance situations encountered in various industries.

Dataset
The dataset used in this project is a synthetic dataset which consists of 10,000 data points with 14 features. These features include unique identifiers, product IDs, various physical measures like air temperature, process temperature, rotational speed, torque, tool wear, etc., and two types of targets - a binary failure indicator and a failure type identifier.

Description
This project develops a predictive maintenance model using PyTorch and sklearn. The model is trained to predict whether a machine will fail (Target) and the type of failure it might experience (Failure Type). The model is designed with early stopping criteria to prevent overfitting and improve generalization.

The project consists of several steps:

Data loading and preprocessing
One-hot encoding of categorical data
Standardizing numerical data
Encoding of target variables
Splitting the dataset into training and test sets
Defining the model architecture
Training the model and saving the best model parameters
Early stopping to prevent overfitting
Dependencies
The project requires the following Python packages:

torch
pandas
sklearn
numpy
Usage
To run the predictive maintenance model, you need to execute the PredictiveMaintenanceModel.ipynb notebook. Make sure you have the necessary data file predictive_maintenance.csv in the same directory.
