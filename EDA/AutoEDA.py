# -*- coding: utf-8 -*-

# Report:
# The pandas-profiling library generates a report having:
# - An overview of the dataset
# - Variable properties
# - Interaction of variables
# - Correlation of variables
# - Missing values
# - Remove duplicated data
# - Sample data

import timeit
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
import time

# settings to display all columns
pd.get_option("display.max_columns")
warnings.filterwarnings("ignore")

def time_counter_decorator (func) :
    def measure_time (*args,**kwargs) :
        start_time = time.time()
        result = func(*args,**kwargs)
        elapsed = time.time() - start_time
        print(func.__name__ , 'spend', elapsed , 'sec(s)')
        
        return result        

    return measure_time
@time_counter_decorator
# Print All Data Information
def dataInformation(df):
    print('========================================================================\n')
    print('\nThe data looks like this: \n',df.head())
    print('\nThe shape of data is: ',df.shape)
    print('\nSome useful data information: \n')
    print(df.info())
    print('\nThe columns in data are: \n',df.columns.values)
    print('\nThe number of duplicate rows : ',df.duplicated().sum())
    print('\nThe summary of data is: \n',df.describe().T)	
    print('========================================================================\n')
@time_counter_decorator
# select 
# 1.numerical_features  --> datatype : int64  ,float64
# 2.categorical_data_df --> datatype : object
def numericalCategoricalSplit(df):
    numerical_features=df.select_dtypes(exclude=['object']).columns
    categorical_features=df.select_dtypes(include=['object']).columns
    numerical_data_df=df[numerical_features]
    categorical_data_df=df[categorical_features]
    return(numerical_data_df,categorical_data_df)

@time_counter_decorator
def nullFind(df):
    null_numerical=pd.isnull(df).sum().sort_values(ascending=False)
    null_categorical=pd.isnull(df).sum().sort_values(ascending=False)
    return(null_numerical,null_categorical)

@time_counter_decorator
# removing null rows in Pandas DataFrame
def removeNullRows(df,few_null_col_list):
    for col in few_null_col_list:
        df=df[df[col].notnull()]
    return(df)

@time_counter_decorator
# Finding and removing duplicate rows in Pandas DataFrame
def removeDuplicateRows(df):
    df.drop_duplicates(keep='last',inplace=True)
    print('\nAfter The number of duplicate rows : ',df.duplicated().sum())
    return(df)

@time_counter_decorator
def CheckDuplicateRows(df):
    cnt_duplicate = df.duplicated().sum()
    print('\nThe number of duplicate rows : ',cnt_duplicate)
    if cnt_duplicate > 0:
        df=removeDuplicateRows(df)
        print('\nafter removing duplicates')
        print('\nThe number of duplicate rows : ',cnt_duplicate)
        print('\nThe number of rows Data : ',len(df))		

    return(df)

@time_counter_decorator
def ChangeDataType(df,list_col):
    for index, tuple in enumerate(list_col):
        col_name  = tuple[0]
        cdatatype = tuple[1]
        if cdatatype == 'DATE':
            format_date = tuple[2]
            df[col_name] = pd.to_datetime(df[col_name],format=format_date)
        elif  cdatatype == 'STRING':
            df[col_name] = df[col_name].astype(str)
        elif  cdatatype == 'INT':
            df[col_name] = df[col_name].astype(int)
        else: null

    return(df)

@time_counter_decorator
def EDA(df):
 
    df_orig=df

    dataInformation(df_orig)

    null_cutoff=0.8
    numerical_df=numericalCategoricalSplit(df_orig)[0]
    categorical_df=numericalCategoricalSplit(df_orig)[1]
    null_numerical=nullFind(numerical_df)[0]
    null_categorical=nullFind(categorical_df)[1]
    null_all=pd.concat([null_numerical,null_categorical])
    null_colname_df=pd.DataFrame({'Null_in_Data':null_all}).sort_values(by=['Null_in_Data'],ascending=False)
    null_df_many=(null_colname_df.loc[(null_colname_df.Null_in_Data>null_cutoff*len(df_orig))])
    null_df_few=(null_colname_df.loc[(null_colname_df.Null_in_Data!=0)&(null_colname_df.Null_in_Data<null_cutoff*len(df_orig))])

    many_null_col_list=null_df_many.index
    few_null_col_list=null_df_few.index
    
    #remove many null columns
    df_orig.drop(many_null_col_list,axis=1,inplace=True)
    #remove some rows
    df_without_null=removeNullRows(df_orig,few_null_col_list)
	#remove duplicate rows
    df_cleaning=CheckDuplicateRows(df_without_null)

    print('================================================== Final Data After EDA ==================================================')
    print('\nThe numerical features are: \n',df_cleaning.select_dtypes(exclude=['object']).columns.tolist())
    print('\nThe categorical features are: \n',df_cleaning.select_dtypes(include=['object']).columns.tolist())
    dataInformation(df_cleaning)
    print('================================================== Final EDA ==================================================')

    return df_cleaning,df_cleaning.select_dtypes(exclude=['object']).columns.tolist(),df_cleaning.select_dtypes(include=['object']).columns.tolist()