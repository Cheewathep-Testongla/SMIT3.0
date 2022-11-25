import deepcut
from deep_translator import GoogleTranslator
from difflib import get_close_matches
# from flask import Flask, request, json
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import json
# from flask_restful import Resource, Api, reqparse
import re
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import uvicorn
from pythainlp import sent_tokenize, word_tokenize, correct, spell
from pythainlp.spell import NorvigSpellChecker
from pydantic import BaseModel
import torch
import tensorflow as tf
import pyodbc

# import warnings
app = FastAPI(title="SMIT3.0 API",
                debug=True,
                version="0.0.1")
modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer(modelPath)

class Input_WPM_Details(BaseModel):
  Detail : str
  Area : str
  Coworker : str

class WPM_Details(BaseModel):
  Detail : str
# def fxn():
#     warnings.warn("deprecated", DeprecationWarning)

# with warnings.catch_warnings():
#     warnings.simplefilter("ignore")
#     fxn()
#     # from keytotext import pipeline
#     def f():
#         print('before')
#         warnings.warn("deprecated", DeprecationWarning)
#         print('after')

# connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#             Server = "smitazure.database.windows.net",
#             Database = "Smit1",
#             uid = 'smitadmin',
#             pwd = 'Abc12345',
#             Trusted_Connection = 'no') 

SafetyAudit = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')
SA_Details = SafetyAudit['Details'].tolist()
SA_Area = SafetyAudit['Area'].tolist()
SA_Contractor = SafetyAudit['Contractor'].tolist()
SA_Tof = SafetyAudit['Type of finding'].tolist()
SA_Topic = SafetyAudit['Topic'].tolist()
SA_Frequency = SafetyAudit['Frequency'].tolist()
SA_Details_Trans = SafetyAudit['Translate Details'].tolist()
TH_Dict_For_DeepCut = pd.read_csv('./SMIT_Data/Dict/Raw_Dictionary/TH_Raw_Dictionary.csv' ,encoding='utf-8')
EN_Dict_For_DeepCut = pd.read_csv('./SMIT_Data/Dict/Raw_Dictionary/EN_Raw_Dictionary.csv' ,encoding='utf-8')
TH_Dict_For_DeepCut = TH_Dict_For_DeepCut['words'].tolist()
EN_Dict_For_DeepCut = EN_Dict_For_DeepCut['words'].tolist()
Dict_For_DeepCut = TH_Dict_For_DeepCut
Dict_For_DeepCut.extend(EN_Dict_For_DeepCut)

# Chosen_Test = pd.read_csv('../SMIT_Data/Dict/Raw_Dictionary/WPM/TH_Error_WPM_Freq_Dictionary.csv' ,encoding='utf-8')
# Chosen_Test = Chosen_Test['words'].tolist()
TH_Custom_Dict = pd.read_csv('./SMIT_Data/Dict/TH_Correction_Dictionary.csv' ,encoding='utf-8')
EN_Custom_Dict = pd.read_csv('./SMIT_Data/Dict/EN_Correction_Dictionary.csv' ,encoding='utf-8')
TH_Custom_Dict = TH_Custom_Dict['words'].tolist()
EN_Custom_Dict = EN_Custom_Dict['words'].tolist()
Custom_Dict = TH_Custom_Dict
Custom_Dict.extend(EN_Custom_Dict)

def Check_Coworker(Coworker):
  if Coworker == "Nalco":
    Coworker = "NALCO"
  # elif                                 
  return Coworker
  
def Check_Area(Area):
  if Area == "OLE2":
    return 'Olefins2'
  else :
    return Area

def Cleansing_Input(case, Data) :
  Tokenize_Input = ''
  if case == 1:
    Find_Text = re.findall("[A-Z]+-[A-Z]*[0-9]+[A-Z,0-9-/]+|[A-Z]+[0-9]+[A-Z]| ,[0-9A-Z,-]+|[0-9][0-9]|[A-Z]+[0-9]+|\#|\(|\)|\@|\+", Data) 
    if len(Find_Text) != 0: 
      for words in Find_Text:
        Tokenize_Input = Tokenize_Input.replace(words,'')
    else : 
      Tokenize_Input = Data
  elif case == 2:
    Find_Text = re.findall("\#|\(|\)|\@|\+|\%|\'", Data)
    if len(Find_Text) != 0: 
      for words in Find_Text:
        Tokenize_Input = Tokenize_Input.replace(words,'')
    else : 
      Tokenize_Input = Data
  Split_Input_Details = deepcut.tokenize(Tokenize_Input) 
  for i in range(len(Split_Input_Details)):
    if Split_Input_Details[i] != ' ':
      if Split_Input_Details[i].isnumeric():
        # check_test.append(Split_Input_Details[i])
        Split_Input_Details[i] = Split_Input_Details[i]
      else:
        Split_Input_Details[i] = get_close_matches(Split_Input_Details[i], Custom_Dict, 1, 0.4)[0]
        # check_test.append(check.correct(Split_Input_Details[i]))
  Cleansing_Input = ''.join(Split_Input_Details)
  return Cleansing_Input

def RemoveText(words, sentence):
  for i in words:
    sentence = sentence.replace(i, '')
  return sentence

def Search_Safety_Audit(case, Input_Details, Input_Location, Input_Coworker):
  Data_Contractor = ''
  Data_Area = ''
  Data_Tof = []
  Data_Details = []
  Data_Details_Trans = []
  Data_Topic = []
  Data_Frequency = []

  if case == 1:
    for i in range(len(SA_Details)):
      if Input_Location == SA_Area[i]:
        Data_Area = SA_Area[i]
        if Input_Coworker == SA_Contractor[i]:
          Data_Topic.append(SA_Topic[i])
          Data_Contractor = SA_Contractor[i]
          Data_Details.append(RemoveText(re.findall('[A-Z-]+[0-9]+[A-Z]*|เวลา[ 0-9:]+น.|>>.*|   |[A-Z]+-[A-Z][0-9]+ ของ [A-Z]+-[A-Z][0-9]+| [0-9]* เมตร |"', SA_Details[i]),SA_Details[i]))
          Data_Details_Trans.append(SA_Details_Trans[i])
          Data_Tof.append(SA_Tof[i])
          Data_Frequency.append(SA_Frequency[i])
    if len(Data_Details) == 0:
      return '', '', [], [], [], [], []
    else:
      return Data_Contractor, Data_Area, Data_Tof, Data_Details, Data_Details_Trans, Data_Topic, Data_Frequency

  elif case == 2:
    for i in range(len(SA_Details)):
      Data_Area = SA_Area[i]
      Data_Topic.append(SA_Topic[i])
      Data_Contractor = SA_Contractor[i]
      Data_Details.append(RemoveText(re.findall('[A-Z-]+[0-9]+[A-Z]*|เวลา[ 0-9:]+น.|>>.*|   |[A-Z]+-[A-Z][0-9]+ ของ [A-Z]+-[A-Z][0-9]+| [0-9]* เมตร |"', SA_Details[i]),SA_Details[i]))
      Data_Details_Trans.append(SA_Details_Trans[i])
      Data_Tof.append(SA_Tof[i])
      Data_Frequency.append(SA_Frequency[i])
    if len(Data_Details) == 0:
      return '', '', [], [], [], [], []
    else:
      return Data_Contractor, Data_Area, Data_Tof, Data_Details, Data_Details_Trans, Data_Topic, Data_Frequency
    
def Compare_Cosine_Similarity(case, Safety_Audit_Details, Data_Details_Trans, Input_Details, Data_Frequency):
  
  if len(Safety_Audit_Details) != 0:
    Translate_Input_Details = (GoogleTranslator(source='auto', target='en').translate(Input_Details))
    Translate_Input_Details = [Translate_Input_Details]*len(Safety_Audit_Details)
    Encode_Safey_Audit_Details = model.encode(Data_Details_Trans)
    Encode_Input_Details = model.encode(Translate_Input_Details)
    
    Cosine_Sim = util.cos_sim(Encode_Safey_Audit_Details, Encode_Input_Details) 
    compare_work_with_Safety_Audit = []
    for i in range(len(Cosine_Sim)):
      j = 0
      compare_work_with_Safety_Audit.append([Cosine_Sim[i][j], i, j, Data_Frequency[i]])
    compare_work_with_Safety_Audit = sorted(compare_work_with_Safety_Audit, key=lambda x: x[0], reverse=True)
    
    Suggestion_Safety_Audit = []
    run_Number = 1
    if case == 1:
      Result = sorted(compare_work_with_Safety_Audit, key=lambda x: x[3], reverse=True)
      for score, i, j, k in Result:
        temp = []
        if Cosine_Sim[i][0] > 0.4:
          temp.append(Safety_Audit_Details[i])
          temp.append(Data_Frequency[i])
          run_Number += 1
          Suggestion_Safety_Audit.append(temp)
        else:
          if run_Number == 1:
            return "Safety Audit of "+Input_Details+" not found"
          break
      return Suggestion_Safety_Audit
    elif case == 2:
      for score, i, j, k in compare_work_with_Safety_Audit[:10]:
        temp = []
        if Cosine_Sim[i][0] > 0.4:
          temp.append(Safety_Audit_Details[i])
          temp.append(Data_Frequency[i])
          run_Number += 1
          Suggestion_Safety_Audit.append(temp)
        else:
          if run_Number == 1:
            return "Safety Audit of "+Input_Details+" not found"
          break
      Suggestion_Safety_Audit = sorted(Suggestion_Safety_Audit, key=lambda x: x[1], reverse=True)
      return Suggestion_Safety_Audit
  else:
    return "Safety Audit of "+Input_Details+" not found"
        
@app.get('/main') 
def Hello():
  return "Hello"   

@app.get('/WPMDetails', status_code=status.HTTP_200_OK)
async def Suggest_Safety_Audit(request: Input_WPM_Details):
  data = request.json()
  data = json.loads(data)

  Input_Details = data['Detail']
  Input_Location = data['Area']
  Input_Coworker = data['Coworker']

  Corrected_input = Cleansing_Input(1, Input_Details)
  Data_Contractor_1, Data_Area_1, Data_Tof_1, Data_Details_1, Data_Details_Trans_1, Data_Topic_1, Data_Frequency_1 = Search_Safety_Audit(1, Corrected_input, Input_Location, Input_Coworker)
  Suggestion_Safety_Audit_1 = Compare_Cosine_Similarity(1, Data_Details_1, Data_Details_Trans_1, Corrected_input, Data_Frequency_1)
  
  Corrected_input = Cleansing_Input(2, Input_Details)
  Data_Contractor_2, Data_Area_2, Data_Tof_2, Data_Details_2, Data_Details_Trans_2, Data_Topic_2, Data_Frequency_2 = Search_Safety_Audit(2, Corrected_input, Input_Location, Input_Coworker)
  Suggestion_Safety_Audit_2 = Compare_Cosine_Similarity(2, Data_Details_2, Data_Details_Trans_2, Corrected_input, Data_Frequency_2)
  
  result = {'case 1': Suggestion_Safety_Audit_1, 'case 2': Suggestion_Safety_Audit_2}
  return result

@app.get('/SpellCheck', status_code=status.HTTP_200_OK)
async def Corrected_input(request: WPM_Details):
  data = request.json()
  data = json.loads(data)

  Input_Details = data['Detail']
  
  result = {'Result': Cleansing_Input(1, Input_Details)}
  return result

if __name__ == '__main__':
  uvicorn.run("smit_sbert0_4:app", host='0.0.0.0', port=5000, reload=True, debug=True)