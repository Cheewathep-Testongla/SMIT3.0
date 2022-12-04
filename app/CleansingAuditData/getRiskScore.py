# from connection_db import *   
from ..connection_db import *   
import pyodbc
import pandas as pd

def getRiskCount(Type):
    if Type != '-':
        RiskCount = pd.read_sql("SELECT COUNT([TypeOfFinding])FROM [dbo].[Cleansing_FindingDetails] WHERE TypeOfFinding = '"+Type+"' GROUP BY TypeOfFinding ;", 
                                connection_SMIT3)
        RiskCount = RiskCount[''].tolist()[0]
        return RiskCount