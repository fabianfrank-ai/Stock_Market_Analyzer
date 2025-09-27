from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

def sklearn_prediction(data):
    
    # split the dataset into training and testing data
    dataframe_sk = pd.DataFrame({'Close' : data['Close']} ,
                                 index = data.index)

    y = dataframe_sk['Close'].values

    dataframe_sk['Days'] = np.arange(len(dataframe_sk))

    X = (dataframe_sk.index - dataframe_sk.index[0]).days.values.reshape(-1,1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    

    # scale the data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)


    # create the model
    model = LinearRegression()

    model.fit(X_train_scaled, y_train)


    # predict the model
    y_pred = model.predict(X_test_scaled)


    X_flattened = X_test.flatten()


    return y_pred, X_flattened

