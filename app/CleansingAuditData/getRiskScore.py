# from connection_db import *   
from ..connection_db import *   
import pyodbc
import pandas as pd

def getRiskCount(Type):
    if Type != '-':
        try:
            print("Used Data source from SQL Server")
            RiskCount = pd.read_sql("SELECT COUNT([TypeOfFinding])FROM [dbo].[Cleansing_FindingDetails] WHERE TypeOfFinding = '"+Type+"' GROUP BY TypeOfFinding ;", 
                                    connection_SMIT3)
            RiskCount = RiskCount[''].tolist()[0]
            return RiskCount
        except:
            print("Used Data source from CSV")
            RiskCount = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')
            RiskCount = (RiskCount.loc[RiskCount["TypeOfFinding"] == type, "TypeOfFinding"]).tolist() 
            return len(RiskCount)