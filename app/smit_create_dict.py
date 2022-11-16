from collections import Counter
import csv
from datetime import datetime
import deepcut
from deep_translator import GoogleTranslator
from difflib import get_close_matches
# from Function import Compare_Cosine_Similarity, Search_Safety_Audit, Cleansing_Input, Upload_Audit_To_Database, Response_WPM_Detail, RemoveCustomPosTag
from IPython.display import clear_output
from itertools import chain
import json
import numpy as np
import pandas as pd
import pyodbc 
from pythainlp import sent_tokenize, word_tokenize, correct, spell
from pythainlp.spell import NorvigSpellChecker
from pythainlp.util import Trie
import re
from sentence_transformers import SentenceTransformer, util
import tensorflow as tf
from textblob import TextBlob
import time

model = SentenceTransformer('all-MiniLM-L6-v2')

# connect_SMITdb = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#             Server = "smitazure.database.windows.net",
#             Database = "Smit1",
#             uid = 'smitadmin',
#             pwd = 'Abc12345',
#             Trusted_Connection = 'no') 

# connect_Localdb = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#                             Server = "TONY",
#                             Database = "e-Permit_MOC",
#                             uid = 'Local_SMIT3.0',
#                             pwd = 'Tony123456',
#                             Trusted_Connection = 'Yes') 

# QueryFromDB = pd.read_sql('''SELECT [v_Permit_WorkerList].[ReqID], [v_Permit_WorkerList].[Desire]
#                             FROM [v_Permit_WorkerList] 
#                             ORDER BY [v_Permit_WorkerList].[ReqId] ASC;'''
#                         , connect_Localdb)
# Dict_For_DeepCut = pd.read_csv('C:\SMIT\SMIT_Data\Dict\Raw_Dictionary\WPM\TH_WPM_Freq_Dictionary.csv' ,encoding='utf8')
# Dict_For_DeepCut = Dict_For_DeepCut['words'].tolist()

# Older_Amount_Data = pd.read_csv('C:\SMIT\SMIT_Data\Count_Latest_Data.csv' ,encoding='utf8')
# Old_Size_WPM = Older_Amount_Data['WPM'].tolist()
# Old_Size_Safety_Audit = Older_Amount_Data['Safety Audit'].tolist()

# WorkPermit = pd.read_sql('SELECT * FROM WPR_OneDoc', connect_SMITdb)
# WorkPermit = QueryFromDB.sort_values('ID')

# Raw_Desire_Details = QueryFromDB['Desire'].tolist()
# AllData = WorkPermit['WorkName'].tolist()

# AllData.extend(Raw_Desire_Details)


# Raw_PTW_Location = QueryFromDB['DocID'].tolist()
# Raw_PTW_Cocompany = QueryFromDB['Cocompany'].tolist()

# SafetyAudit = pd.read_csv('./SMIT_Data/Raw_Safety_Audit.csv', encoding='utf-8')
# AllData.extend(SafetyAudit['Details'].tolist())

# Dict_For_DeepCut_Thai = []
# Dict_For_DeepCut_Eng = []

# Dict_For_Correct_Thai = []
# Dict_For_Correct_Eng = []

# Dict_For_Spell_Thai = []
# Dict_For_Spell_Eng = []

def RemoveText(words, sentence):
  for i in words:
    sentence = sentence.replace(i, '')
  return sentence

def CreateDict(Cleansing_Input):
  TempThaiDictionary = []
  for i in Cleansing_Input:
    TempThaiDictionary.append(word_tokenize(i, engine="newmm"))

#   Flatten_SMIT_Dict = list(chain.from_iterable(TempThaiDictionary))

#   Custom_Dict = list(dict.fromkeys(Flatten_SMIT_Dict))

#   return Custom_Dict

Thai_Vowels = ['ะ', 'ั', '็', 'า', 'ิ', '่', 'ํ', '“', 'ุ', 'ู', 'เ', 'ใ', 'ไ', 'โ', 'ฤ', 'ๅ', 'ฦ', 'ำ', ' ', '  ', '์']

def RemoveVowels(word):
  for check in Thai_Vowels:
    if word == check:
      return False
  return True

# CheckThaiAppendDict = pd.read_csv('./SMIT_Data/DataForModel/TH_Raw_Dictionary.csv',encoding='utf-8')
# CheckThaiDict = CheckThaiAppendDict['words'].tolist()
# CheckThaiCorrect = CheckThaiAppendDict['correct'].tolist()

# CheckEngAppendDict = pd.read_csv('./SMIT_Data/DataForModel/EN_Raw_Dictionary.csv', encoding='utf-8')
# CheckEngDict = CheckEngAppendDict['words'].tolist()
# CheckEngCorrect = CheckEngAppendDict['correct'].tolist()

# CheckRawAppendDict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv', encoding='utf-8')
# CheckRawDict = CheckRawAppendDict['words'].tolist()
# CheckRawCorrect = CheckRawAppendDict['correct'].tolist()

# if 'aru ' in CheckEngDict:
#   print("yes")
# else:
#   print("no")

# eng = re.findall("[A-Za-z]+", "install scaffolding in aru")

# print(eng)

# for word in eng:
#   if word not in CheckEngDict:
#     print(word)
#   else:
#     print(word, CheckEngDict.index(word))

# for sentence in AllData:
#   if sentence != None:
#     # Remove Tools code name & Remove Special Character
#     words = re.findall("\#|\(|\)|\@|\+|\%|\+|\0xa2|[0-9]", sentence)
#     sentence = RemoveText(words, sentence)
    
#     thai = re.findall("[\u0E00-\u0E7F]+", sentence)
#     eng = re.findall("[A-Za-z]+", sentence)

#     if len(thai) != 0:
#       for i in thai:
#         Split_words = word_tokenize(i, engine="newmm")
#         if(len(Split_words)) > 1:
#           for j in Split_words:
#             if RemoveVowels(j) == True:
#               if(j not in CheckThaiDict):
#                 Dict_For_DeepCut_Thai.append(j)
#         else:
#           if(i not in CheckThaiDict):
#             Dict_For_DeepCut_Thai.append(j)

#     if len(eng) != 0:
#       for i in eng:
#         Split_words = word_tokenize(i, engine="newmm")
#         if(len(Split_words)) > 1:
#           for j in Split_words:
#             if(j not in CheckRawDict and len(j) > 1):
#             # if len(j) > 1:
#               Dict_For_DeepCut_Eng.append(j.lower())
#         else:
#           if(i not in CheckRawDict and len(i) > 1):
#           # if len(i) > 1:
#             Dict_For_DeepCut_Eng.append(i.lower())

# print(len(Dict_For_DeepCut_Thai), len(Dict_For_DeepCut_Eng))

# Dict_For_DeepCut_Thai = Counter(Dict_For_DeepCut_Thai)
# Dict_For_DeepCut_Eng = Counter(Dict_For_DeepCut_Eng)

# List_Deepcut_Thai = [[words, frequency] for words,frequency in Dict_For_DeepCut_Thai.items()]
# List_Deepcut_Eng = [[words, frequency] for words,frequency in Dict_For_DeepCut_Eng.items()]

# ThaiDictionary = []

# for i in range(len(List_Deepcut_Thai)):
#   temp = []
#   if (List_Deepcut_Thai[i][1] > 1):
#     temp.append(List_Deepcut_Thai[i][0])
#     try:
#       if (len(get_close_matches(List_Deepcut_Thai[i][0], CheckThaiDict, 1, 0.5)[0]) > 0):
#         temp.append(CheckThaiCorrect.index(get_close_matches(List_Deepcut_Thai[i][0], CheckThaiCorrect, 1, 0.5)))
#         temp.append(CheckThaiCorrect.index(get_close_matches(List_Deepcut_Thai[i][0], CheckThaiCorrect, 1, 0.5)[0]))
#     except:
#       temp.append(spell(List_Deepcut_Thai[i][0]))
#       temp.append(correct(List_Deepcut_Thai[i][0]))
#     temp.append(List_Deepcut_Thai[i][1])
#     ThaiDictionary.append(temp)

# print(ThaiDictionary)

# EngDictionary = []

# for i in range(len(List_Deepcut_Eng)):
#   temp = []
#   if(List_Deepcut_Eng[i][0] not in CheckRawDict):
#     if (List_Deepcut_Eng[i][1] > 1):
#       temp.append(List_Deepcut_Eng[i][0])
#       try:
#         temp.append(get_close_matches(List_Deepcut_Eng[i][0], CheckEngCorrect))
#       except:
#         CorrectedByTextBlob = TextBlob(List_Deepcut_Eng[i][0])
#         temp.append(str(CorrectedByTextBlob.correct()))
#       try:
#         temp.append(get_close_matches(List_Deepcut_Eng[i][0], CheckEngCorrect)[0])
#       except:
#         CorrectedByTextBlob = TextBlob(List_Deepcut_Eng[i][0])
#         temp.append(str(CorrectedByTextBlob.correct()))
#       temp.append(List_Deepcut_Eng[i][1])
#       EngDictionary.append(temp)

# print(EngDictionary)
# Head = ['words','spell','correct','frequency']


# with open('C:\SMIT3.0\SMIT_Data\DataForModel\TH_Raw_Dictionary.csv', 'a', newline='', encoding="utf-8") as f:
#   write = csv.writer(f)
#   write.writerows(ThaiDictionary)

# with open('C:\SMIT3.0\SMIT_Data\DataForModel\EN_Raw_Dictionary_1.csv', 'a', newline='', encoding="utf-8") as f:
#   write = csv.writer(f)
#   Head = ['words','spell','correct','frequency']
#   write.writerows(EngDictionary)

# AllDictionary = ThaiDictionary
# AllDictionary.extend(EngDictionary)

# with open('C:\SMIT3.0\SMIT_Data\DataForModel\Raw_Dictionary.csv', 'a', newline='', encoding="utf-8") as f:
#   write = csv.writer(f)
#   write.writerows(AllDictionary)

# # # รอเปลี่ยนเป็นดึงข้อมูลจาก Database ที่เก็บข้อมูล Safety Audit โดยจะเลือกข้อมูลที่จะเพิ่มจากจำนวนข้อมูลที่มีอยู่

SafetyAudit = pd.read_csv('C:\SMIT\SMIT_Data\Raw_Safety_Audit.csv', encoding='utf-8')

SA_Details = SafetyAudit['Details'].tolist()
SA_Area = SafetyAudit['Area'].tolist()
SA_Contractor = SafetyAudit['Contractor'].tolist()
SA_Tof = SafetyAudit['Type of finding'].tolist()
SA_Topic = SafetyAudit['Topic'].tolist()

Cleansing_All_Safety_Audit = []
Cleansing_Safety_Audit = []

for sentence in SA_Details:
  words = re.findall("\([A-Z-]+[0-9]+[A-Z]*|เวลา[ 0-9:]+น.\)|>>.*|   |  |[A-Z]+-[A-Z][0-9]+ ของ [A-Z]+-[A-Z][0-9]+|, [0-9]+ |ชั้น [0-9,]+|\(|\)|\n*", sentence)
  Cleansing_All_Safety_Audit.append(RemoveText(words, sentence))
  # Cleansing_Safety_Audit.append(RemoveCustomPosTag(sentence))

Translate_All_Cleansing_Safety_Audit = []
Translate_Cleansing_Safety_Audit = []

for sentence in range(len(Cleansing_All_Safety_Audit)):
  Translate_All_Cleansing_Safety_Audit.append(GoogleTranslator(source='auto', target='en').translate(Cleansing_All_Safety_Audit[sentence]))
  Translate_Cleansing_Safety_Audit.append(GoogleTranslator(source='auto', target='en').translate(Cleansing_Safety_Audit[sentence]))

# All_Prepared_Safety_Audit = []

# for i in range(len(Cleansing_All_Safety_Audit)):
#   temp = []
#   temp.append(Cleansing_Safety_Audit[i])
#   temp.append(Translate_Cleansing_Safety_Audit[i])
#   temp.append(SA_Area[i])
#   temp.append(SA_Contractor[i])
#   temp.append(SA_Tof[i])
#   temp.append(SA_Topic[i])
#   temp.append(Cleansing_Safety_Audit[i])
#   temp.append(Translate_Cleansing_Safety_Audit[i])
#   All_Prepared_Safety_Audit.append(temp)

# Head = ['Details', 'Translate_Details', 'Area', 'Contractor', 'Type_of_finding', 'Topic', 'Clean_Details', 'Clean_Translate_Details']
# with open('C:\SMIT3.0\SMIT_Data\DataForModel\All_Prepared_Safety_Audit.csv', 'w', newline='', encoding="utf-8") as f:
#   write = csv.writer(f)
#   write.writerow(Head)
#   write.writerows(All_Prepared_Safety_Audit)

# --------------------------------------------------------------- #
Prepared_SA_Details = []
Prepared_SA_Area = []
Prepared_SA_Contractor = []
Prepared_SA_Tof = []
Prepared_SA_Topic = []
Prepared_SA_Frequency = []
Prepared_SA_Translate_Details = []

Encode_Translate_Cleansing_Safety_Audit = model.encode(Translate_All_Cleansing_Safety_Audit)

Cosine_Sim = util.cos_sim(Encode_Translate_Cleansing_Safety_Audit, Encode_Translate_Cleansing_Safety_Audit)

# Case 1 :
# for i in range(Encode_Translate_Cleansing_Safety_Audit):
#   Max_Cosine = 0
#   Count_Frequency = 0
#   Index_Frequency = 0
#   for j in range(Encode_Translate_Cleansing_Safety_Audit):
#     if Cosine_Sim < 0.8: 
#       Prepared_SA_Details.append(Cleansing_Safety_Audit[j])
#       Prepared_SA_Area.append(SA_Area[j])
#       Prepared_SA_Contractor.append(SA_Contractor[j])
#       Prepared_SA_Tof.append(SA_Tof[j])
#       Prepared_SA_Topic.append(SA_Topic[j])
#       Prepared_SA_Frequency.append(1)
#     else:
#       Max_Cosine = Cosine_Sim[i][j]
#       Count_Frequency += 1
#       Index_Frequency = j
#   Prepared_SA_Details.append(Cleansing_Safety_Audit[i])
#   Prepared_SA_Area.append(SA_Area[i])
#   Prepared_SA_Contractor.append(SA_Contractor[i])
#   Prepared_SA_Tof.append(SA_Tof[i])
#   Prepared_SA_Topic.append(SA_Topic[i])
#   Prepared_SA_Frequency.append(Count_Frequency)

# Case 2
Index_Frequency = []

for i in range(len(Encode_Translate_Cleansing_Safety_Audit)):
  Index_Most_Frequency = 0
  Count_Frequency = 1
  Max_Cosine = Cosine_Sim[i][0]
  if i not in Index_Frequency:
    for j in range(len(Encode_Translate_Cleansing_Safety_Audit)):
      if i != j:
        if Cosine_Sim[i][j] > 0.8: 
          Index_Frequency.append(j)
          Count_Frequency += 1  
          if Cosine_Sim[i][j] > Max_Cosine:
            Max_Cosine = Cosine_Sim[i][j]
            Index_Most_Frequency = j
    if Cleansing_Safety_Audit[Index_Most_Frequency] not in Prepared_SA_Details:
        Prepared_SA_Details.append(Cleansing_Safety_Audit[Index_Most_Frequency])
        Prepared_SA_Translate_Details.append(Translate_Cleansing_Safety_Audit[Index_Most_Frequency])
        Prepared_SA_Area.append(SA_Area[Index_Most_Frequency])
        Prepared_SA_Contractor.append(SA_Contractor[Index_Most_Frequency])
        Prepared_SA_Tof.append(SA_Tof[Index_Most_Frequency])
        Prepared_SA_Topic.append(SA_Topic[Index_Most_Frequency])
        Prepared_SA_Frequency.append(Count_Frequency)

Prepared_Safety_Audit = []
for i in range(len(Prepared_SA_Details)):
  temp = []
  temp.append(Prepared_SA_Details[i])
  temp.append(Prepared_SA_Translate_Details[i])
  temp.append(Prepared_SA_Area[i])
  temp.append(Prepared_SA_Contractor[i])
  temp.append(Prepared_SA_Tof[i])
  temp.append(Prepared_SA_Topic[i])
  temp.append(Prepared_SA_Frequency[i])
  Prepared_Safety_Audit.append(temp)

Head = ['Details', 'Translate Details', 'Area', 'Contractor', 'Type of finding', 'Topic', 'Frequency']
with open('C:\SMIT\SMIT_Data\Prepared_Safety_Audit_Test.csv', 'w', newline='', encoding="utf-8") as f:
  write = csv.writer(f)
  write.writerow(Head)
  write.writerows(Prepared_Safety_Audit)

# Update latest data #

# count_wpm = len(Raw_PTW_Details)
# count_safety_audit = len(Raw_PTW_Details)

# count_all_data = []
# count_all_data.append(count_wpm)
# count_all_data.append(count_safety_audit)

# Head = ['WPM', 'Safety Audit']
# with open('C:\SMIT\SMIT_Data\Count_Latest_Data.csv', 'w', newline='', encoding="utf-8") as f:
#   write = csv.writer(f)
#   write.writerow(Head)
#   write.writerows(len(count_all_data))


##### Prepared tbFinding to be Classified #####
# tbFinding = pd.read_csv('./SMIT_Data/Classification_tbFinding/tbFinding.csv', encoding='utf-8')
# # SafetyAudit = pd.read_csv('./SMIT_Data/All_Prepared_Safety_Audit.csv', encoding='utf-8')

# tbFindingID = tbFinding['ID'].tolist()
# tbFindingTitle = tbFinding['Title'].tolist()
# tbFindingFinding = tbFinding['Finding'].tolist()
# tbFindingArea = tbFinding['Area'].tolist()
# tbFindingCategory = tbFinding['Category'].tolist()
# tbFindingCheckListNo = tbFinding['CheckListNo'].tolist()
# tbFindingAuditResult = tbFinding['AuditResult'].tolist()   
# tbFindingCorrective = tbFinding['Corrective'].tolist()
# tbFindingAuthorizePerson = tbFinding['AuthorizePerson'].tolist()
# tbFindingCauseDeviation = tbFinding['CauseDeviation'].tolist()
# tbFindingFindingBy = tbFinding['FindingBy'].tolist()
# tbFindingFindingDate = tbFinding['FindingDate'].tolist()
# tbFindingCreated = tbFinding['Created'].tolist()
# tbFindingCreatedBy = tbFinding['CreatedBy'].tolist()
# tbFindingModified = tbFinding['Modified'].tolist()
# tbFindingModifiedBy = tbFinding['ModifiedBy'].tolist()
# tbFindingimgURL = tbFinding['imgURL'].tolist()

# tbFindingResult = []

# for index in range(len(tbFindingFinding)):
#   temp = []
#   temp.append(tbFindingID[index])
#   temp.append(tbFindingTitle[index])
#   temp.append(tbFindingFinding[index])
#   temp.append(tbFindingArea[index])
#   temp.append(tbFindingCategory[index])
#   temp.append(tbFindingCheckListNo[index])
#   temp.append(tbFindingAuditResult[index])
#   temp.append(tbFindingCorrective[index])
#   temp.append(tbFindingAuthorizePerson[index])
#   temp.append(tbFindingCauseDeviation[index])
#   temp.append(tbFindingFindingBy[index])
#   temp.append(tbFindingFindingDate[index])
#   temp.append(tbFindingCreated[index])
#   temp.append(tbFindingCreatedBy[index])
#   temp.append(tbFindingModified[index])
#   temp.append(tbFindingModifiedBy[index])
#   temp.append(tbFindingimgURL[index])
#   temp.append(GoogleTranslator(source='auto', target='en').translate(tbFindingFinding[index]))

#   tbFindingResult.append(temp)

# header = ['ID',	'Title', 'Area',	'Category',	'CheckListNo',	
#           'AuditResult', 'Finding',	'Corrective',	'AuthorizePerson',	
#           'CauseDeviation',	'FindingBy',	'FindingDate',	'Created',	
#           'CreatedBy',	'Modified',	'ModifiedBy',	'imgURL', 'TranslateFinding']

# with open('./SMIT_Data/Classification_tbFinding/tbFindingResult.csv', 'w', newline='', encoding="utf-8") as f:
#   write = csv.writer(f)
#   write.writerow(header)
#   write.writerows(tbFindingResult) 

print("Finish")