import csv
from deep_translator import GoogleTranslator         
# from Function import * 
# from connection_db import *     
# from CleansingAuditData.embedding_SafetyAudit import embedding_SafetyAudit   

from ..Function import * 
# from ..connection_db import *     
from .embedding_SafetyAudit import embedding_SafetyAudit       
 
import pandas as pd                                        
                                            
import re                                                  
from sentence_transformers import SentenceTransformer, util

RiskCount = {
    "UnsafeAction": 0,
    "UnsafeCondition": 0,
    "NearMiss": 0,
    "HNM": 0,
    "Accident": 0
}

modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer(modelPath)

# def ResetRiskCount():

#     global RiskCount

#     RiskCount = {
#         "UnsafeAction": 0,
#         "UnsafeCondition": 0,
#         "NearMiss": 0,
#         "HNM": 0,
#         "Accident": 0
#     }

def Prepared_FindingDetails():
    print("[Start Prepared FindingDetails]...")

    global RiskCount

    # ResetRiskCount()
    connection_SMIT3 = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
                                Server = "smitazure.database.windows.net",
                                Database = "SMIT3",
                                uid = 'smitadmin',
                                pwd = 'Abc12345',
                                Trusted_Connection = 'no')
    
    Cleansing_FindingDetails = pd.read_sql("SELECT * FROM [Cleansing_FindingDetails]", connection_SMIT3)

    FindingNo = Cleansing_FindingDetails['FindingNo'].tolist()
    FindingNo = ["-" if pd.isnull(x) else x for x in FindingNo]

    Area = Cleansing_FindingDetails['Area'].tolist()
    Area = ["-" if pd.isnull(x) else x for x in Area]

    SubArea = Cleansing_FindingDetails['SubArea'].tolist()
    SubArea = ["-" if pd.isnull(x) else x for x in SubArea]

    Contractor = Cleansing_FindingDetails['Contractor'].tolist()
    Contractor = ["-" if pd.isnull(x) else x for x in Contractor]

    Tof = Cleansing_FindingDetails['TypeOfFinding'].tolist()
    Tof = ["-" if pd.isnull(x) else x for x in Tof]

    Topic = Cleansing_FindingDetails['Topic'].tolist()
    Topic = ["-" if pd.isnull(x) else x for x in Topic]

    Details = Cleansing_FindingDetails['Finding'].tolist()
    Details = ["-" if pd.isnull(x) else x for x in Details]

    CleansingDetails = Cleansing_FindingDetails['CleansingFinding'].tolist()
    CleansingDetails = ["-" if pd.isnull(x) else x for x in CleansingDetails]

    TranslateDetails = Cleansing_FindingDetails['TranslateFinding'].tolist()
    TranslateDetails = ["-" if pd.isnull(x) else x for x in TranslateDetails]

    Prepared_FindingNo = []
    Prepared_Area = []
    Prepared_SubArea = []
    Prepared_Contractor = []
    Prepared_Tof = []
    Prepared_Topic = []
    Prepared_Details = []
    Prepared_Frequency = []
    Prepared_CleansingDetails = []
    Prepared_Translate_Details = []
    Prepared_ListFindingNo = []
    MostMatch = []

    Encode_Translate_Cleansing_Safety_Audit = model.encode(TranslateDetails)

    Cosine_Sim = util.cos_sim(Encode_Translate_Cleansing_Safety_Audit, Encode_Translate_Cleansing_Safety_Audit)


    Size = len(Encode_Translate_Cleansing_Safety_Audit)

    for i in range(0, Size):
        Index_Most_Frequency = 0
        Count_Frequency = 0
        Max_Cosine = 0
        Index_Frequency = []
        if i not in MostMatch:
            if (Tof[i] == "Unsafe Condition"):
                for j in range(0, Size):
                    if i != j:
                        if Cosine_Sim[i][j] > 0.6 and Tof[j] == "Unsafe Condition":
                            Count_Frequency += 1 
                            Index_Frequency.append(j) 
                            if Cosine_Sim[i][j] > Max_Cosine:
                                Max_Cosine = Cosine_Sim[i][j]
                                Index_Most_Frequency = j
                    
            elif (Tof[i] == "Unsafe Action"):
                for j in range(0, Size):
                    if i != j:
                        if Cosine_Sim[i][j] > 0.6 and Tof[j] == "Unsafe Action": 
                            Count_Frequency += 1 
                            Index_Frequency.append(j) 
                            if Cosine_Sim[i][j] > Max_Cosine:
                                Max_Cosine = Cosine_Sim[i][j]
                                Index_Most_Frequency = j

            elif (Tof[i] == "HNM"):
                for j in range(0, Size):
                    if i != j:
                        if Cosine_Sim[i][j] > 0.7 and Tof[j] == "HNM": 
                            Count_Frequency += 1 
                            Index_Frequency.append(j) 
                        if Cosine_Sim[i][j] > Max_Cosine: 
                            Max_Cosine = Cosine_Sim[i][j]
                            Index_Most_Frequency = j

            elif (Tof[i] == "Near Miss"):
                for j in range(0, Size):
                    if i != j:
                        if Cosine_Sim[i][j] > 0.7 and Tof[j] == "Near Miss": 
                            Count_Frequency += 1 
                            Index_Frequency.append(j) 
                            if Cosine_Sim[i][j] > Max_Cosine:
                                Max_Cosine = Cosine_Sim[i][j]
                                Index_Most_Frequency = j

            elif (Tof[i] == "Accident"):
                for j in range(0, Size):
                    if i != j:
                        if Cosine_Sim[i][j] > 0.7 and Tof[j] == "Accident": 
                            Count_Frequency += 1 
                            Index_Frequency.append(j) 
                            if Cosine_Sim[i][j] > Max_Cosine:   
                                Max_Cosine = Cosine_Sim[i][j]
                                Index_Most_Frequency = j
                            
            if Count_Frequency == 0:
                Index_Frequency.append(i)
                Count_Frequency = 1 
                Index_Most_Frequency = i  

            if (Index_Most_Frequency not in MostMatch) and Details[Index_Most_Frequency] not in Prepared_Details:
                Prepared_FindingNo.append(int(FindingNo[Index_Most_Frequency]))
                Prepared_Area.append(Area[Index_Most_Frequency])
                Prepared_SubArea.append(SubArea[Index_Most_Frequency])
                Prepared_Contractor.append(Contractor[Index_Most_Frequency])
                Prepared_Tof.append(Tof[Index_Most_Frequency])
                Prepared_Topic.append(Topic[Index_Most_Frequency])
                Prepared_Details.append(Details[Index_Most_Frequency])
                Prepared_Frequency.append(Count_Frequency)
                Prepared_CleansingDetails.append(CleansingDetails[Index_Most_Frequency])
                Prepared_Translate_Details.append(TranslateDetails[Index_Most_Frequency])
                Prepared_ListFindingNo.append(Index_Frequency)
                MostMatch.append(Index_Most_Frequency)

            if Index_Most_Frequency in MostMatch and (Details[Index_Most_Frequency] in Prepared_Details and Area[Index_Most_Frequency] in Prepared_Area):
                Index = MostMatch.index(Index_Most_Frequency)
                Temp_Prepared_ListFindingNo = Prepared_ListFindingNo[Index]+Index_Frequency
                Temp_Prepared_ListFindingNo = list(set(Temp_Prepared_ListFindingNo))
                Prepared_ListFindingNo[Index] = Temp_Prepared_ListFindingNo
                Prepared_Frequency[Index] = len(Temp_Prepared_ListFindingNo)

    Prepared_Safety_Audit = list(zip(Prepared_FindingNo, Prepared_Area, Prepared_SubArea, 
                                Prepared_Contractor, Prepared_Tof, Prepared_Topic, Prepared_Details, 
                                Prepared_Frequency, Prepared_CleansingDetails, Prepared_Translate_Details))

    cursor = connection_SMIT3.cursor()
    Query = "DELETE FROM [Prepared_FindingDetails];"
    cursor.execute(Query)
    connection_SMIT3.commit()

    Query = "INSERT INTO [Prepared_FindingDetails] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
    cursor.executemany(Query, Prepared_Safety_Audit)
    connection_SMIT3.commit()

    Head = ['FindingNo', 'Area', 'SubArea', 'Contractor', 'TypeOfFinding', 'Topic', 'Finding', 'Frequency', 'CleansingFinding', 'TranslateFinding']

    with open('./SMIT_Data/Prepared_Safety_Audit.csv', 'w', newline='', encoding="utf-8") as f:
        write = csv.writer(f)
        write.writerow(Head)
        write.writerows(Prepared_Safety_Audit)

    cursor.close()
    connection_SMIT3.close()

    print("[Finished Prepared FindingDetails]...")
    
    return embedding_SafetyAudit()
