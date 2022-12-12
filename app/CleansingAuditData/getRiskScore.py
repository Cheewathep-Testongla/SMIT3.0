# from connection_db import *   
from ..connection_db import *   
import pyodbc
import pandas as pd

connection = connection_SMIT3

def getRiskCount():
    # connection_SMIT3 = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
    #                                 Server = "smitazure.database.windows.net",
    #                                 Database = "SMIT3",
    #                                 uid = 'smitadmin',
    #                                 pwd = 'Abc12345',
    #                                 Trusted_Connection = 'no') 
    # try:
    #     RiskCount = pd.read_sql("SELECT TypeOfFinding, SUM([Frequency]) as [Frequency] FROM [dbo].[Prepared_FindingDetails] WHERE TypeOfFinding != '-' GROUP BY TypeOfFinding;", 
    #                             connection_SMIT3)

    #     TotalUnsafeAction = RiskCount.loc[RiskCount['TypeOfFinding'] == "Unsafe Action", "Frequency"].tolist()[0]
    #     TotalUnsafeCondition = RiskCount.loc[RiskCount['TypeOfFinding'] == "Unsafe Condition", "Frequency"].tolist()[0]
    #     TotalNearMiss = RiskCount.loc[RiskCount['TypeOfFinding'] == "Near Miss", "Frequency"].tolist()[0]
    #     TotalHNM = RiskCount.loc[RiskCount['TypeOfFinding'] == "HNM", "Frequency"].tolist()[0]
    #     TotalAccident = RiskCount.loc[RiskCount['TypeOfFinding'] == "Accident", "Frequency"].tolist()[0]

    #     connection_SMIT3.close()

    #     print("Used Data source from SQL Server")

    #     return TotalUnsafeAction, TotalUnsafeCondition, TotalNearMiss, TotalHNM, TotalAccident
    # except:
        RiskCount = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')

        TotalUnsafeAction = (RiskCount.loc[RiskCount["TypeOfFinding"] == "Unsafe Action", "Frequency"]).sum() 
        TotalUnsafeCondition = (RiskCount.loc[RiskCount["TypeOfFinding"] == "Unsafe Condition", "Frequency"]).sum() 
        TotalNearMiss = (RiskCount.loc[RiskCount["TypeOfFinding"] == "Near Miss", "Frequency"]).sum() 
        TotalHNM = (RiskCount.loc[RiskCount["TypeOfFinding"] == "HNM", "Frequency"]).sum() 
        TotalAccident = (RiskCount.loc[RiskCount["TypeOfFinding"] == "Accident", "Frequency"]).sum() 

        print("Used Data source from CSV")

        return TotalUnsafeAction, TotalUnsafeCondition, TotalNearMiss, TotalHNM, TotalAccident