from sklearn.impute import SimpleImputer
import logging, time
import numpy as np
import pandas as pd

class _DefaultNone:
    Default = None

class CleanerBase(object):
    #initialize DataCleanerฺฺBase with a string
    def __init__(self,
                 df
                 ):
        self.df = df

    def getNulls(self):
        return self.df.isnull().sum()

    def getNullsColsInfo(self):
            mis_val = self.df.isnull().sum()
            mis_val_percent = 100 * mis_val / len(self.df)
            mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
            mis_val_table_ren_columns = mis_val_table.rename(
            columns = {0 : 'Missing Values', 1 : '% of Total Values'})
            mis_val_table_ren_columns = mis_val_table_ren_columns[
                mis_val_table_ren_columns.iloc[:,1] != 0].sort_values('% of Total Values', ascending=False).round(1)
            #print ("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"      
            #       "There are " + str(mis_val_table_ren_columns.shape[0]) +
            #       " columns that have missing values.")
            return mis_val_table_ren_columns

    def getInfo(self):
        return self.df.info()

    def getRowDup(self):
        return self.df.duplicated().sum()

    def getShape(self):
        # Shape (dimensions) of the DataFrame
        return self.df.shape

    def getCateFeat(self):
        #Summary statistics of the categorical features
        return self.df.describe(include='object')


    def getDataFrame(self):
        return self.df

class DataCleanerฺฺ(CleanerBase):
    def __init__(self,
                 df,
                 cols_to_drop = _DefaultNone, 
                 index_col    = _DefaultNone, 
                 automate     = False
                 ):
        self.df = df
        self.cols_to_drop = cols_to_drop
        self.index_col = index_col
        self.automate  = automate

        if(index_col != _DefaultNone):
            self.df.set_index(index_col, inplace = True)
        if(self.cols_to_drop != _DefaultNone):
            self.dropColumns()

        #Automatically clean the data if desired
        if(automate):
            self.transformColTypes()
            self.handleNulls()
            self.handleRowDups()

    def valueToNan(self,value,columns):
        """
        This function converts values within columns to NaN and is used
        for invalid values which have been marked as 0, null, etc
        Parameters
        ----------
        data is a dataframe containing data
        value is the invalid value
        columns are the columns where the invalid value is located
        """
        self.df[[columns]] = self.df[[columns]].replace(value,np.NaN)


    def dropColumns(self):
        """
        This function tries to drop any column
        """
        try:
              for columns in self.cols_to_drop :
                self.df.drop(columns, inplace = True, axis = 1)
        except Exception as e:
              print('An exception Drop column : {} - {}'.format(self.cols_to_drop,e))
              

    def handleNulls(self):
        """
        This function tries to fill null values, or drops columns with
        more than 90% missing values. Drops rows with more than 90% 
        missing values
        """
        #Drop columns which have 90% NaN
        self.df.dropna(thresh=int(self.df.shape[0] * .9), axis=1, inplace = True)
        #Drop rows which have 90% NaN
        self.df.dropna(thresh=int(self.df.shape[0] * .9), axis=0, inplace = True)
        #use imputer to impute the rest of the null values with column mean
        try:
          imputer = SimpleImputer(missing_values = "NaN", strategy = "mean")
          imputer = imputer.fit(self.df)
          self.df = imputer.transform(self.df)
        except Exception as e:
              print('Error in handleNulls :{}'.format(e))
              
    def handleRowDups(self):
        """
        This function tries to remove duplicate rows
        """
        self.df = self.df.drop_duplicates()

    def transformColTypes(self):
        """
        This function tries to impute column types from default dtypes
        Parameters and gets 
        ---------
        data is a dataframe containing data
        """
        #First, try to infer data types to convert object type columns
        self.df = self.df.infer_objects()
        for column in self.df.columns:
            #Test for conversion to categorical type, then get dummies
            if(self.df[column].nunique() < 5):
                try:
                    self.df[column].astype('category')
                except:
                    continue
                pd.get_dummies(self.df, prefix = column, drop_first = True)

 
