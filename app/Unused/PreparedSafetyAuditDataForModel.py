from deep_translator import GoogleTranslator
from Function import Cleansing_Input
import pandas as pd
import pyodbc 
import re
from sentence_transformers import SentenceTransformer, util

modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer(modelPath)

Thai_Vowels = ['ะ', 'ั', '็', 'า', 'ิ', '่', 'ํ', '“', 'ุ', 'ู', 'เ', 'ใ', 'ไ', 'โ', 'ฤ', 'ๅ', 'ฦ', 'ำ', ' ', '  ', '์']

# def RemoveVowels(word):
#   for check in Thai_Vowels:
#     if word == check:
#       return False
#   return True

# def RemoveText(words, sentence):
#   for i in words:
#     sentence = sentence.replace(i, '')
#   return sentence

SafetyAudit = pd.read_csv('./SMIT_Data/Raw_Safety_Audit.csv', encoding='utf-8')

SA_FindingNo = SafetyAudit['No.'].tolist()
SA_FindingNo = ["-" if pd.isnull(x) else x for x in SA_FindingNo]

SA_Company = SafetyAudit['Company'].tolist()
SA_Company = ["-" if pd.isnull(x) else x for x in SA_Company]

SA_Area = SafetyAudit['Area'].tolist()
SA_Area = ["-" if pd.isnull(x) else x for x in SA_Area]

SA_SubArea = SafetyAudit['Sub Area'].tolist()
SA_SubArea = ["-" if pd.isnull(x) else x for x in SA_SubArea]

SA_Reportor = SafetyAudit['Reportor'].tolist()
SA_Reportor = ["-" if pd.isnull(x) else x for x in SA_Reportor]

SA_Contractor = SafetyAudit['Contractor'].tolist()
SA_Contractor = ["-" if pd.isnull(x) else x for x in SA_Contractor]

SA_Tof = SafetyAudit['Type of finding'].tolist()
SA_Tof = ["-" if pd.isnull(x) else x for x in SA_Tof]

SA_Topic = SafetyAudit['Topic'].tolist()
SA_Topic = ["-" if pd.isnull(x) else x for x in SA_Topic]

SA_Details = SafetyAudit['Details'].tolist()
SA_Details = ["-" if pd.isnull(x) else x for x in SA_Details]

SA_CorrectiveAction = SafetyAudit['Corrective Action'].tolist()
SA_CorrectiveAction = ["-" if pd.isnull(x) else x for x in SA_CorrectiveAction]

SA_IssueDate = SafetyAudit['Issue Date'].tolist()
SA_IssueDate = ["-" if pd.isnull(x) else x for x in SA_IssueDate]

SA_DueDate = SafetyAudit['Due Date'].tolist()
SA_DueDate = ["-" if pd.isnull(x) else x for x in SA_DueDate]

SA_Status = SafetyAudit['Status'].tolist()
SA_Status = ["-" if pd.isnull(x) else x for x in SA_Status]

SA_TransDetails = []
SA_CleansingDetails = []
NewSafetyAuditData = []

Cleansing_Safety_Audit = []

for index in range(len(SA_Details)):
  temp = []
  ResponseSpellCheck = Cleansing_Input(SA_Details[index], 2)
  
  temp.append(SA_FindingNo[index])
  temp.append(SA_Company[index])
  temp.append(SA_Area[index])
  temp.append(SA_SubArea[index])
  temp.append(SA_Reportor[index])
  temp.append(SA_Contractor[index])
  temp.append(SA_Tof[index])
  temp.append(SA_Topic[index])
  temp.append(SA_Details[index])
  temp.append(SA_CorrectiveAction[index])
  temp.append(SA_IssueDate[index])
  temp.append(SA_DueDate[index])
  temp.append(SA_Status[index])
  temp.append(ResponseSpellCheck['Collected_Input'])

  SA_CleansingDetails.append(ResponseSpellCheck['Collected_Input'])
  TransDetails = GoogleTranslator(source='auto', target='en').translate(ResponseSpellCheck['Collected_Input'])
  SA_TransDetails.append(TransDetails)
  temp.append(TransDetails)
  NewSafetyAuditData.append(temp)

connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
                            Server = "TONY",
                            Database = "SMIT3",
                            uid = 'Local_SMIT3.0',
                            pwd = 'Tony123456',
                            Trusted_Connection = 'yes')      

ResponseFindingDetail = pd.read_sql("SELECT * FROM FindingDetails;", connect_db)

NewSafetyAuditData = list(set(NewSafetyAuditData) - set(ResponseFindingDetail))

cursor = connect_db.cursor()

Query = "INSERT INTO [Cleansing_FindingDetails] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

# if len(NewSafetyAuditData) != 0:
cursor.executemany(Query, NewSafetyAuditData)
connect_db.commit()

# ---------------------------------------- #
Translate_Cleansing_Safety_Audit = []

Prepared_SA_FindingNo = []
Prepared_SA_Area = []
Prepared_SA_SubArea = []
Prepared_SA_Contractor = []
Prepared_SA_Tof = []
Prepared_SA_Topic = []
Prepared_SA_Details = []
Prepared_SA_Frequency = []
Prepared_SA_CleansingDetails = []
Prepared_SA_Translate_Details = []
Prepared_SA_ListFindingNo = []

Encode_Translate_Cleansing_Safety_Audit = model.encode(SA_TransDetails)

Cosine_Sim = util.cos_sim(Encode_Translate_Cleansing_Safety_Audit, Encode_Translate_Cleansing_Safety_Audit)

Index_Frequency = []

for i in range(len(Encode_Translate_Cleansing_Safety_Audit)):
  Index_Most_Frequency = 0
  Count_Frequency = 1
  Max_Cosine = Cosine_Sim[i][0]
  temp_ListFindingNo = []
  if i not in Index_Frequency:
    for j in range(len(Encode_Translate_Cleansing_Safety_Audit)):
      if i != j:
        if Cosine_Sim[i][j] > 0.6: 
          Index_Frequency.append(j)
          Count_Frequency += 1  
          if Cosine_Sim[i][j] > Max_Cosine:
            Max_Cosine = Cosine_Sim[i][j]
            Index_Most_Frequency = j
            temp_ListFindingNo.append(Index_Most_Frequency)
    if SA_Details[Index_Most_Frequency] not in Prepared_SA_Details:
      Prepared_SA_FindingNo.append(SA_FindingNo[Index_Most_Frequency])
      Prepared_SA_Area.append(SA_Area[Index_Most_Frequency])
      Prepared_SA_SubArea.append(SA_SubArea[Index_Most_Frequency])
      Prepared_SA_Contractor.append(SA_Contractor[Index_Most_Frequency])
      Prepared_SA_Tof.append(SA_Tof[Index_Most_Frequency])
      Prepared_SA_Topic.append(SA_Topic[Index_Most_Frequency])
      Prepared_SA_Details.append(SA_Details[Index_Most_Frequency])
      Prepared_SA_Frequency.append(Count_Frequency)
      Prepared_SA_CleansingDetails.append(SA_CleansingDetails[Index_Most_Frequency])
      Prepared_SA_Translate_Details.append(SA_TransDetails[Index_Most_Frequency])
      Prepared_SA_ListFindingNo.append(temp_ListFindingNo)

Prepared_Safety_Audit = []
for i in range(len(Prepared_SA_Details)):
  temp = []
  temp.append(Prepared_SA_FindingNo[i])
  temp.append(Prepared_SA_Area[i])
  temp.append(Prepared_SA_SubArea[i])
  temp.append(Prepared_SA_Contractor[i])
  temp.append(Prepared_SA_Tof[i])
  temp.append(Prepared_SA_Topic[i])
  temp.append(Prepared_SA_Details[i])
  temp.append(Prepared_SA_Frequency[i])
  temp.append(Prepared_SA_CleansingDetails[i])
  temp.append(Prepared_SA_Translate_Details[i])
  temp.append(Prepared_SA_ListFindingNo[i])
  Prepared_Safety_Audit.append(temp)

cursor = connect_db.cursor()
Query = "INSERT INTO [Prepared_FindindDetails] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

# if len(NewSafetyAuditData) != 0:
cursor.executemany(Query, Prepared_Safety_Audit)
connect_db.commit()

# ---------------------------------------- #