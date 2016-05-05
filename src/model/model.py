import pandas as pd
import numpy as np
import boto
import xgboost as xgb
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from boto.s3.key import Key

from sklearn.feature_extraction import DictVectorizer as DV
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import os
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import mean_squared_error

from get_data import write_to_s3

ACCESS_KEY = os.environ['AWS_ACCESS_KEY_ID']
SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

def dummies(df, col):
    """
    Create dummies for categorical variable
    """
    dummy = pd.get_dummies(df[col])
    # dummy.drop(drop_col, axis=1, inplace=True)
    df.drop(col, axis=1, inplace=True)
    return pd.concat([df, dummy], axis=1)

def cat_to_dummy(df, cat_cols, test=False, vectorizer=None):
    """
    Convert categorical variables to dummies for either train or test dataset
    """
    num_cols = list(set(df.columns) - set(cat_cols))

    cat = df[cat_cols].astype(str)
    num = df[num_cols]

    x_num = num.values

    cat.fillna( 'NA', inplace = True )

    x_cat = cat.T.to_dict().values()

    if test:
        vec_x_cat = vectorizer.transform(x_cat)
        x = np.hstack((x_num, vec_x_cat))
        return x

    else:
        vectorizer = DV(sparse=False)
        vec_x_cat = vectorizer.fit_transform(x_cat)
        x = np.hstack((x_num, vec_x_cat))
        return x, vectorizer

def plot_boxplot(X, y, ylabel):
    """
    Make boxplot for continuous variable X and output y (either 0 or 1)
    """

    fig, ax1 = plt.subplots(figsize=(10, 6))
    label = ['Hired', 'Not Hired']
    ax1.boxplot([X[y==1], X[y==0]], vert=1)
    ax1.set_xlabel('Whether hired by 180 days')
    ax1.set_ylabel(ylabel)
    ax1.set_xticklabels(label)
    plt.show()

def plot_countplot(x_col, y_col, df, title):
    sns.countplot(x=x_col, hue=y_col, data=admin_outcome)
    plt.title(title)
    plt.show()

def plot_scatterplot(x1, x2, y_col):
    fig, axes = plt.subplots(nrows=1, ncols=2)
    admin_assessment.plot(ax=axes[0], kind='scatter', x=x1, y=y_col)
    admin_assessment.plot(ax=axes[1], kind='scatter', x=x2, y=y_col)
    plt.show()

# feature importance
# https://github.com/zipfian/boosting/blob/master/pair.md

def plot_feature_importance(feature_importance, col_names, first_n):

    top_n = col_names[np.argsort(feature_importance)[-first_n:]]
    feature_import= feature_importance[np.argsort(feature_importance)][-first_n:]
    feat_import = feature_import/max(feature_import)

    fig = plt.figure(figsize=(8, 8))
    x_ind = np.arange(feat_import.shape[0])
    plt.barh(x_ind, feat_import, height=.3, align='center')
    plt.ylim(x_ind.min() + .5, x_ind.max() + .5)
    plt.yticks(x_ind, top_n, fontsize=14)
    plt.show()

def grid_search_helper(model, grid, x, y, scoring='mean_squared_error'):

    new_model_gridsearch = GridSearchCV(model,
                                 random_forest_grid,
                                 n_jobs=-1,
                                 verbose=False,
                                 cv=5,
                                 scoring='mean_squared_error')
    new_model_gridsearch.fit(x, y)

    print "best parameters:", new_model_gridsearch.best_params_

    best_model = new_model_gridsearch.best_estimator_

    best_model_pred = best_model.predict(x)
    best_model_MSE = mean_squared_error(y, best_model_pred)
    # print original_model.__class__.__name__
    # print "Original %f", original_model_MSE
    print "Optimized %f" % best_model_MSE
    return best_model

if __name__ == '__main__':
    this_year = 2016
    f = pd.read_csv("https://s3.amazonaws.com/cruntar_house/bayarea.csv")
    # X_cols = ['postalCode', 'bed', 'bath', 'sqft', 'lot_size', 'built', 'on_site', 'City', 'Region']
    all_cols = ['postalCode', 'bed', 'bath', 'sqft', 'lot_size', 'built', 'on_site', 'City', 'price', 'HOA', 'Latitude', 'Longitude', 'link', 'img', 'CND', 'Place Name']
    numeric_cols = ['bed', 'bath', 'sqft', 'lot_size', 'built', 'on_site', 'price', 'HOA', 'Latitude', 'Longitude']
    cat_cols = list(set(all_cols) - set(numeric_cols) - set(['link', 'img', 'postalCode', 'City', 'Place Name']))
    y_col = 'price'
    df_temp = f[all_cols]
    df_temp['lot_size'][df_temp['lot_size'].isnull()]=0
    df_temp.dropna(axis=0, inplace=True)
    df_temp['built'] = 2016 - df_temp['built']
    for col in ['City', 'CND']:
        df_temp = dummies(df_temp, col)
    df_temp = df_temp[(df_temp['price'] < 3000000)]
    y = df_temp[y_col].values
    X = df_temp.drop([y_col, 'link', 'img', 'postalCode', 'Place Name'], axis=1).values
    model = xgb.XGBRegressor(learning_rate=0.05,
                           n_estimators=200,
                           subsample=0.5,
                           max_depth=4,
                           silent=True)
    scores = cross_val_score(model, X, y, cv=5, scoring='mean_squared_error')
    rmse = ((-scores) ** 0.5).mean()
    print rmse


    df = f[all_cols]
    df['lot_size'][df['lot_size'].isnull()]=0
    df.dropna(axis=0, inplace=True)
    df['built'] = 2016 - df['built']

    # train_df = df[:200]
    # test_df = df[200:]

    # train_y = train_df.pop(y_col).values
    # test_y = test_df.pop(y_col).values
    # train_x, vectorizer = cat_to_dummy(train_df, cat_cols)
    # test_x = cat_to_dummy(test_df, cat_cols, test=True, vectorizer=vectorizer)
    #
    # ss = StandardScaler()
    # train_x_scaled = ss.fit_transform(train_x)
    # test_x_scaled = ss.transform(test_x)

    # df = dummies(df, 'postalCode')
    # df = dummies(df, 'City')
    df = dummies(df, 'CND')
    df = df[df['price'] < 3000000]
    y = df[y_col].values
    X_cols = list(set(df.columns) - set([y_col, 'link', 'img', 'postalCode', 'City', 'Place Name']))
    x = df[X_cols].values

    model = RandomForestRegressor()
    model.fit(x, y)
    feature_importance =  model.feature_importances_
    #print np.sum(gbc3.feature_importances_)
    col_names = np.array(X_cols)
    plot_feature_importance(feature_importance, col_names, 10)




    #Grid search
    random_forest_grid = {'max_depth': [3, None],
                      'max_features': ['sqrt', 'log2', None],
                      'min_samples_split': [1, 2, 4],
                      'min_samples_leaf': [1, 2, 4],
                      'bootstrap': [True, False],
                      'n_estimators': [10, 20, 40, 100],
                      'random_state': [1]}

    best_model_pram = grid_search_helper(model, random_forest_grid, x, y)
    df['estimate'] = best_model_pram.predict(x)
    df['estimate'] = df['estimate'].astype(int)
    df['percent_difference'] = (df['estimate'] - df['price']) / df['price']
    df = df[df['percent_difference']>0.1]


    print "Save dataframe as CSV"
    input_file = '../../data/df_prediction.csv'
    df.to_csv(input_file)
    print "Write CSV to S3"
    write_to_s3(input_file, 'prediction_bayarea.csv')
