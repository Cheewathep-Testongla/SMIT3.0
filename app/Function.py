from deep_translator import GoogleTranslator
from difflib import get_close_matches
import re
from sentence_transformers import SentenceTransformer, util
import pandas as pd
from pythainlp import sent_tokenize, word_tokenize, correct, spell
from pythainlp.tag import pos_tag, pos_tag_sents
from pythainlp.util import Trie

import torch
import tensorflow as tf
import time
import csv
import pyodbc

modelPath = "./Model/SentenceTransformer"
# Test
model = SentenceTransformer(modelPath)

SafetyAudit = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')
SA_Details = SafetyAudit['Details'].tolist()
SA_Area = SafetyAudit['Area'].tolist()
SA_Contractor = SafetyAudit['Contractor'].tolist()
SA_Tof = SafetyAudit['TypeOfFinding'].tolist()
SA_Topic = SafetyAudit['Topic'].tolist()
SA_Frequency = SafetyAudit['Frequency'].tolist()
SA_Details_Trans = SafetyAudit['TranslateDetails'].tolist()

def Cleansing_Input(Data, Case) :

  Data = Data.lower()

  Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv',encoding='utf-8')

  DictTokenize = Custom_Dict['words'].tolist()
  DictCorrect = Custom_Dict['correct'].tolist()

  Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Thai_Dictionary.csv',encoding='utf-8')
  THDictTokenize = Custom_Dict['words'].tolist()
  THDictCorrect = Custom_Dict['correct'].tolist()

  Data = re.sub(' +',' ', Data)
  Data = re.sub('^ +','', Data)
  Data = re.sub('^ | $','', Data)
  
  Data = re.sub(',| ,|, | , ',' , ', Data)
  Data = re.sub(' +',' ', Data)

  if Case == 1:
    ListUnwantedText =  [
                        'no. [0-9-/]+',
                        '[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+[a-z0-9]*',
                        '[0-9]+-[0-9]+/[0-9]+',
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|='
                        ]

    ListCutText = []
    for index in ListUnwantedText:
      Find_Text = re.findall(index, Data) 
      if len(Find_Text) != 0: 
        for words in Find_Text:
          if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
            Data = Data.replace(words,' ')
            ListCutText.append(words)
      else : 
        Data = Data

    ListSplitCharacter = "\/\/+|\/|\+|,|&| and | and|และ|กับ|เพื่อ|\n"
    FindSplitCharecter = re.findall(ListSplitCharacter, Data) 

    Tokenize_Input = Data
    Collected_Input = Data

    for words in FindSplitCharecter:
      Tokenize_Input = Tokenize_Input.replace(words, ' , ')

    ListUnwantedText =  [
                        '[a-z]+-[0-9a-z]+-[a-z0-9]+',               #a-a0-a0     
                        '[a-z]+-[0-9]+[a-z]+[0-9]+[a-z]+',          #a-a0 
                        '[a-z]+-[0-9]+[a-z]+[a-z]+[0-9]+',          #
                        '[a-z]+-[a-z]+[0-9]+[0-9]+[a-z]+',          #
                        '[a-z]+-[a-z]+[0-9]+[a-z]+[0-9]+',          #
                        '[a-z]+[0-9]+[a-z-]+',                      #                          
                        '[a-z]+ [0-9]+ [a-z]+',                     # PIT 3060 ABC                         
                        '[a-z]+-[0-9]+-[a-z]+',                     #a-0-a                                               
                        '[a-z]+-[a-z]+-[0-9]+',                     #a-a-0
                        '[a-z]+-[0-9]+[a-z]+',                      # TT-8006BA
                        '[a-z]+-[0-9]+',                            #a-0
                        '[0-9]+[a-z]+',                             #0a
                        '[a-z]+[0-9]+',                             #a0                        
                        '[0-9]+ เมตร',                              #12 เมตร
                        '[0-9][0-9]+',                              #00 
                        ' [0-9] ',                                  # 0 
                        ' [a-z] ',                                  # a
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|-',              
                        'group'
                        ]

    for index in ListUnwantedText:
      Find_Text = re.findall(index, Tokenize_Input) 
      if len(Find_Text) != 0: 
        for words in Find_Text:
          if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
            Tokenize_Input = Tokenize_Input.replace(words,' ')
            Collected_Input = Collected_Input.replace(words,' ')
      else : 
        Tokenize_Input = Tokenize_Input
        Collected_Input = Collected_Input

    Tokenize_Input = Tokenize_Input.split(',')

    ResultTokenizeInput = []
    ResultCorrectedInput = ''

    trie = Trie(THDictTokenize)

    for sentence in Tokenize_Input:
      TempListTokenize = word_tokenize(sentence, custom_dict=trie, engine='newmm')
      GetPos_TagListTokenize = pos_tag(TempListTokenize, corpus="orchid_ud")

      PROPNListTokenize = []
      ListTokenize = []

      for index in range(len(GetPos_TagListTokenize)):
        temp = []
        if (
          # GetPos_TagListTokenize[index][1] == "SCONJ" or 
          GetPos_TagListTokenize[index][1] == "ADP" or 
          GetPos_TagListTokenize[index][1] == "CCONJ" or
          GetPos_TagListTokenize[index][1] == "PUNCT"):
          temp.append(GetPos_TagListTokenize[index][0])
          temp.append(index)
          PROPNListTokenize.append(temp)
        else: 
          ListTokenize.append(GetPos_TagListTokenize[index][0])

        TempResult = []
        CheckIfTempResultisAlready = []

        for i in range(len(ListTokenize)):    
          FinalJoinString = ''
          if(len(re.findall(' [a-z][a-z][a-z] | [a-z][a-z] ', ListTokenize[i])) > 1):
              TempResult.append(ListTokenize[i])     

          elif(len(re.findall('([A-Za-z])\w+', ListTokenize[i])) > 0):
              if ListTokenize[i] in DictTokenize:
                TempResult.append(DictCorrect[DictTokenize.index(ListTokenize[i])])
              else:
                try:
                  TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
                  # CheckIfTempResultisAlready.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0])
                except:
                  TempResult.append(ListTokenize[i])            
          # print('ListTokenize', ListTokenize[i])
          else:
            if(ListTokenize[i] in DictTokenize):
              IndexRepeatDictTokenize = []
              # Get all duplicate value in DictTokenize that match with ListTokenize[i]
              for idx, val in enumerate(DictTokenize):
                if ListTokenize[i] == val and idx not in IndexRepeatDictTokenize:
                  IndexRepeatDictTokenize.append(idx)
              if (len(IndexRepeatDictTokenize) > 1):
                for index in IndexRepeatDictTokenize:
                  for j in range(i, len(ListTokenize)):
                    if ListTokenize[j] != ' ':
                      try:
                        TempJoinString = TempResult[len(TempResult)-1]+DictCorrect[DictTokenize.index(ListTokenize[j])]
                        if TempJoinString in DictCorrect:
                          CheckIfTempResultisAlready.append(DictCorrect[index])
                          CheckIfTempResultisAlready.append(TempResult[len(TempResult)-1])
                          CheckIfTempResultisAlready.append(TempJoinString)
                          FinalJoinString = TempJoinString
                      except:     
                        FinalJoinString = ListTokenize[j]
                  if FinalJoinString not in CheckIfTempResultisAlready:
                    TempResult.append(FinalJoinString)   
                    CheckIfTempResultisAlready.append(FinalJoinString)
                  elif FinalJoinString == '':
                    TempResult.append(ListTokenize[i])  
              else:
                  index = DictTokenize.index(ListTokenize[i])
                  if DictCorrect[index] not in CheckIfTempResultisAlready:
                    TempResult.append(DictCorrect[index])
                    CheckIfTempResultisAlready.append(DictCorrect[index])
            else:
              if ListTokenize[i] != ' ':
                try:
                  if get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0] not in CheckIfTempResultisAlready:
                    TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0])
                    CheckIfTempResultisAlready.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0])
                except: 
                  if ListTokenize[i] not in CheckIfTempResultisAlready:
                    TempResult.append(ListTokenize[i])
                    CheckIfTempResultisAlready.append(ListTokenize[i])
              else:
                TempResult.append(' ')

        for i in range(len(PROPNListTokenize)):
          TempResult.insert(PROPNListTokenize[i][1], PROPNListTokenize[i][0])

        Result = []
        TempResultTokenizeInput = ''
        for i in range(len(TempResult)):
          if(i == 0 and len(TempResult) > 1):
            ResultCorrectedInput = ' '+ResultCorrectedInput+TempResult[i]
          if (TempResult[i] == '') or (i == 0 and TempResult[i] == ' ') or (i == len(TempResult)-1 and TempResult[len(TempResult)-1] == ' ') or (TempResult[i] == ' ' and TempResult[i+1] == ' '):
            continue
          else:
            if(i == 0):
              ResultCorrectedInput = ' '+ResultCorrectedInput
            Result.append(TempResult[i])
            TempResultTokenizeInput = TempResultTokenizeInput+TempResult[i]

      TempResultTokenizeInput = TempResultTokenizeInput+' '
      TempResultTokenizeInput = re.sub(' +', ' ',TempResultTokenizeInput)
      TempResultTokenizeInput = re.sub('^ | $', '',TempResultTokenizeInput)

      if TempResultTokenizeInput not in ResultTokenizeInput and len(TempResultTokenizeInput) > 1: 
        ResultTokenizeInput.append(TempResultTokenizeInput)
        ResultCorrectedInput = ""+', '.join(ResultTokenizeInput)
      
    ResultCorrectedInput = re.sub(' +', ' ',ResultCorrectedInput)
    ResultCorrectedInput = re.sub('^ | $', '',ResultCorrectedInput)

  elif Case == 2:
    ListSplitCharacter = "\/\/+|\/|\+|,|&| and | and|และ|กับ|เพื่อ|\n"
    FindSplitCharecter = re.findall(ListSplitCharacter, Data) 

    Data = re.sub(' +', ' ', Data)
    Data = re.sub('^ | $', '', Data)

    ResultTokenizeInput = Data
    ResultCorrectedInput = Data

    for words in FindSplitCharecter:
      ResultTokenizeInput = ResultTokenizeInput.replace(words, ', ')

    ResultTokenizeInput = re.sub(' +', ' ', ResultTokenizeInput)
    ResultTokenizeInput = re.sub('^ | $', '', ResultTokenizeInput)

    ResultCorrectedInput = ResultTokenizeInput
    ResultTokenizeInput = ResultTokenizeInput.split(',')
    
    for index in range(len(ResultTokenizeInput)):
      ResultTokenizeInput[index] = re.sub('^ ', '', ResultTokenizeInput[index])

  Response_SpellChecker = {
    "Collected_Input" : ResultCorrectedInput,
    "Result" : ResultTokenizeInput
  }
  return Response_SpellChecker

def RemoveText(words, sentence):
  for i in words:
    sentence = sentence.replace(i, '')
  return sentence

def Search_Safety_Audit(case, Input_Location, Input_Coworker):
  Data_Contractor_1 = ''
  Data_Area_1 = ''
  Data_Contractor_2 = []
  Data_Area_2 = []
  Data_Tof = []
  Data_Details = []
  Data_Details_Trans = []
  Data_Topic = []
  Data_Frequency = []

  if case == 1:
    for i in range(len(SA_Details)):
      if Input_Location == SA_Area[i]:
        Data_Area_1 = SA_Area[i]
        if Input_Coworker == SA_Contractor[i]:
          Data_Topic.append(SA_Topic[i])
          Data_Contractor_1 = SA_Contractor[i]
          Data_Details.append(RemoveText(re.findall('[A-Z-]+[0-9]+[A-Z]*|เวลา[ 0-9:]+น.|>>.*|   |[A-Z]+-[A-Z][0-9]+ ของ [A-Z]+-[A-Z][0-9]+| [0-9]* เมตร |"|^ ', SA_Details[i]),SA_Details[i]))
          Data_Details_Trans.append(SA_Details_Trans[i])
          Data_Tof.append(SA_Tof[i])
          Data_Frequency.append(SA_Frequency[i])
      
    if len(Data_Details) == 0:
      return '', '', [], [], [], [], []
    else:
      return Data_Contractor_1, Data_Area_1, Data_Tof, Data_Details, Data_Details_Trans, Data_Topic, Data_Frequency

  elif case == 2:
    for i in range(len(SA_Details)):
      Data_Area_2.append(SA_Area[i])
      Data_Topic.append(SA_Topic[i])
      Data_Contractor_2.append(SA_Contractor[i])
      Data_Details.append(RemoveText(re.findall('[A-Z-]+[0-9]+[A-Z]*|เวลา[ 0-9:]+น.|>>.*|   |[A-Z]+-[A-Z][0-9]+ ของ [A-Z]+-[A-Z][0-9]+| [0-9]* เมตร |"|^ ', SA_Details[i]),SA_Details[i]))
      Data_Details_Trans.append(SA_Details_Trans[i])
      Data_Tof.append(SA_Tof[i])
      Data_Frequency.append(SA_Frequency[i])

    if len(Data_Details) == 0:
      return [], [], [], [], [], [], []
    else:
      return Data_Contractor_2, Data_Area_2, Data_Tof, Data_Details, Data_Details_Trans, Data_Topic, Data_Frequency
    
def Compare_Cosine_Similarity(case, Safety_Audit_Details, Data_Details_Trans, Input_Details, List_Input_Details, Data_Frequency, Data_Contractor, Data_Tof, Data_Area, Data_Topic):
  Suggestion_Safety_Audit_Detail = []
  Suggestion_Safety_Audit_Frequency = []
  Suggestion_Safety_Audit_Contractor = []
  Suggestion_Safety_Audit_Type_Of_Finding = []
  Suggestion_Safety_Audit_Area = []
  Suggestion_Safety_Audit_Topic = []

  Temp_Safety_Audit_Details = []
  Temp_Safety_Audit_Frequency = []
  Temp_Safety_Audit_Contractor = []
  Temp_Safety_Audit_Type_Of_Finding = []
  Temp_Safety_Audit_Area = []
  Temp_Safety_Audit_Topic = []

  if case == 1:
    # start_time = time.time()
    for sentence in List_Input_Details:
      if len(Safety_Audit_Details) != 0:
        Translate_Input_Details = (GoogleTranslator(source='auto', target='en').translate(sentence))
        Translate_Input_Details = [Translate_Input_Details]*len(Safety_Audit_Details)
        Encode_Safey_Audit_Details = model.encode(Data_Details_Trans)
        Encode_Input_Details = model.encode(Translate_Input_Details)
        
        # print("Old Algorithm : --- %s seconds ---" % (time.time() - start_time))

        Cosine_Sim = util.pytorch_cos_sim(Encode_Safey_Audit_Details, Encode_Input_Details) 
        compare_work_with_Safety_Audit = []
        
        for i in range(len(Cosine_Sim)):
          j = 0
          compare_work_with_Safety_Audit.append([Cosine_Sim[i][j], i, j, Data_Frequency[i], Data_Contractor, Data_Tof[i], Data_Area, Data_Topic[i]])
        compare_work_with_Safety_Audit = sorted(compare_work_with_Safety_Audit, key=lambda x: x[0], reverse=True)

        run_Number = 1

        for score, i, j, k, l, m, n, o in compare_work_with_Safety_Audit[:2]:        
            if Cosine_Sim[i][0] > 0.4:
              Temp_Safety_Audit_Details.append(Safety_Audit_Details[i])
              Temp_Safety_Audit_Frequency.append(Data_Frequency[i])
              Temp_Safety_Audit_Contractor.append(Data_Contractor)
              Temp_Safety_Audit_Type_Of_Finding.append(Data_Tof[i])
              Temp_Safety_Audit_Area.append(Data_Area)
              Temp_Safety_Audit_Topic.append(Data_Topic[i])
              run_Number += 1
            elif (len(Temp_Safety_Audit_Details) == 0):
              if(sentence != List_Input_Details[len(List_Input_Details)-1] and run_Number == 1):
                break
              else:
                if run_Number == 1:
                  Form_Response_SafetyAudit = {
                    "Safety_Audit_Details": [["No Data about "+Input_Details+" was found"]],
                    "Safety_Audit_Frequency": [[0]],
                    "Safety_Audit_Contractor" : [["No Data"]],
                    "Safety_Audit_Type_Of_Finding" : [["No Data"]],
                    "Safety_Audit_Area" : [["No Data"]],
                    "Safety_Audit_Topic" : [["No Data"]],
                  }
                  return Form_Response_SafetyAudit
                break
  elif case == 2:
    for sentence in List_Input_Details:
      if len(Safety_Audit_Details) != 0:
        Translate_Input_Details = (GoogleTranslator(source='auto', target='en').translate(sentence))
        Translate_Input_Details = [Translate_Input_Details]*len(Safety_Audit_Details)
        Encode_Safey_Audit_Details = model.encode(Data_Details_Trans)
        Encode_Input_Details = model.encode(Translate_Input_Details)
        
        Cosine_Sim = util.cos_sim(Encode_Safey_Audit_Details, Encode_Input_Details) 
        compare_work_with_Safety_Audit = []
        
        for i in range(len(Cosine_Sim)):
          j = 0
          compare_work_with_Safety_Audit.append([Cosine_Sim[i][j], i, j, Data_Frequency[i], Data_Contractor[i], Data_Tof[i], Data_Area[i], Data_Topic[i]])
        compare_work_with_Safety_Audit = sorted(compare_work_with_Safety_Audit, key=lambda x: x[0], reverse=True)

        run_Number = 1

        for score, i, j, k, l, m, n, o in compare_work_with_Safety_Audit[:3]:        
          if Cosine_Sim[i][0] > 0.4:
            Temp_Safety_Audit_Details.append(Safety_Audit_Details[i])
            Temp_Safety_Audit_Frequency.append(Data_Frequency[i])
            Temp_Safety_Audit_Contractor.append(Data_Contractor[i])
            Temp_Safety_Audit_Type_Of_Finding.append(Data_Tof[i])
            Temp_Safety_Audit_Area.append(Data_Area[i])
            Temp_Safety_Audit_Topic.append(Data_Topic[i])
            run_Number += 1
          elif (len(Temp_Safety_Audit_Details) == 0):
            if(sentence != List_Input_Details[len(List_Input_Details)-1] and run_Number == 1):
              break
            else:
              if run_Number == 1:
                Form_Response_SafetyAudit = {
                  "Safety_Audit_Details": [["No Data about "+Input_Details+" was found"]],
                  "Safety_Audit_Frequency": [[0]],
                  "Safety_Audit_Contractor" : [["No Data"]],
                  "Safety_Audit_Type_Of_Finding" : [["No Data"]],
                  "Safety_Audit_Area" : [["No Data"]],
                  "Safety_Audit_Topic" : [["No Data"]],
                }
                return Form_Response_SafetyAudit
              break

  Temp_Safety_Audit_Details = [frequency for _, frequency in sorted(zip(Temp_Safety_Audit_Frequency, Temp_Safety_Audit_Details), reverse=True)]
  Temp_Safety_Audit_Contractor = [frequency for _, frequency in sorted(zip(Temp_Safety_Audit_Frequency, Temp_Safety_Audit_Contractor), reverse=True)]
  Temp_Safety_Audit_Type_Of_Finding = [frequency for _, frequency in sorted(zip(Temp_Safety_Audit_Frequency, Temp_Safety_Audit_Type_Of_Finding), reverse=True)]
  Temp_Safety_Audit_Area = [frequency for _, frequency in sorted(zip(Temp_Safety_Audit_Frequency, Temp_Safety_Audit_Area), reverse=True)]
  Temp_Safety_Audit_Topic = [frequency for _, frequency in sorted(zip(Temp_Safety_Audit_Frequency, Temp_Safety_Audit_Topic), reverse=True)]
  Temp_Safety_Audit_Frequency = sorted(Temp_Safety_Audit_Frequency, reverse=True)

  for i in range(len(Temp_Safety_Audit_Details)):
    Create_List_Safety_Audit_Details = []
    Create_List_Safety_Audit_Frequency = []
    Create_List_Safety_Audit_Contractor = []
    Create_List_Safety_Audit_Type_Of_Finding = []
    Create_List_Safety_Audit_Area = []
    Create_List_Safety_Audit_Topic = []

    Create_List_Safety_Audit_Details.append(Temp_Safety_Audit_Details[i])
    Create_List_Safety_Audit_Frequency.append(Temp_Safety_Audit_Frequency[i])
    Create_List_Safety_Audit_Contractor.append(Temp_Safety_Audit_Contractor[i])
    Create_List_Safety_Audit_Type_Of_Finding.append(Temp_Safety_Audit_Type_Of_Finding[i]) 
    Create_List_Safety_Audit_Area.append(Temp_Safety_Audit_Area[i]) 
    Create_List_Safety_Audit_Topic.append(Temp_Safety_Audit_Topic[i]) 
    
    Suggestion_Safety_Audit_Detail.append(Create_List_Safety_Audit_Details)
    Suggestion_Safety_Audit_Frequency.append(Create_List_Safety_Audit_Frequency)
    Suggestion_Safety_Audit_Contractor.append(Create_List_Safety_Audit_Contractor)
    Suggestion_Safety_Audit_Type_Of_Finding.append(Create_List_Safety_Audit_Type_Of_Finding)
    Suggestion_Safety_Audit_Area.append(Create_List_Safety_Audit_Area)
    Suggestion_Safety_Audit_Topic.append(Create_List_Safety_Audit_Topic)

  Form_Response_SafetyAudit = {
    "Safety_Audit_Details" : Suggestion_Safety_Audit_Detail,
    "Safety_Audit_Frequency" : Suggestion_Safety_Audit_Frequency,
    "Safety_Audit_Contractor" : Suggestion_Safety_Audit_Contractor,
    "Safety_Audit_Type_Of_Finding" : Suggestion_Safety_Audit_Type_Of_Finding,
    "Safety_Audit_Area" : Suggestion_Safety_Audit_Area,
    "Safety_Audit_Topic" : Suggestion_Safety_Audit_Topic,
  }
  if len(Data_Details_Trans) == 0:
    Form_Response_SafetyAudit = {
      "Safety_Audit_Details": [["No Data about "+Input_Details+" was found"]],
      "Safety_Audit_Frequency": [[0]],
      "Safety_Audit_Contractor" : [["No Data"]],
      "Safety_Audit_Type_Of_Finding" : [["No Data"]],
      "Safety_Audit_Area" : [["No Data"]],
      "Safety_Audit_Topic" : [["No Data"]],
    }
  return Form_Response_SafetyAudit

def Upload_Audit_To_Database(Data):
  with open('./SMIT_Data/Audit_Result/SMIT3_Audit_Result.csv', 'a', newline='', encoding="utf-8") as f:
    write = csv.writer(f)
    write.writerow(Data)
  return "Success"

# def Response_WPM_Detail(Primary_Key):
  
#   connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#             Server = "smitazure.database.windows.net",
#             Database = "Smit1",
#             uid = 'smitadmin',
#             pwd = 'Abc12345',
#             Trusted_Connection = 'no') 

#   WorkPermit = pd.read_sql("SELECT [RequestLocation], [Cocompany], [WorkName] FROM [WPR_OneDoc] WHERE DocID = '"+Primary_Key+"';", connect_db)
#   Detail = WorkPermit.sort_values('WorkName')
#   Area = WorkPermit.sort_values('RequestLocation')
#   Coworker = WorkPermit.sort_values('Cocompany')

#   return Detail, Area, Coworker

def GetFindingDetail(Orderby):
  # connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
  #             Server = "smitazure.database.windows.net",
  #             Database = "Smit1",
  #             uid = 'smitadmin',
  #             pwd = 'Abc12345',
  #             Trusted_Connection = 'no') 
  
  connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
                          Server = "TONY",
                          Database = "SMIT3",
                          uid = 'Local_SMIT3.0',
                          pwd = 'Tony123456',
                          Trusted_Connection = 'yes')  

  ResponseFindingDetail = pd.read_sql("SELECT * FROM FindingDetails ORDER BY FindingNo "+Orderby, connect_db)

  return ResponseFindingDetail

def UploadFinding(FindingData):
  # connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
  #             Server = "smitazure.database.windows.net",
  #             Database = "Smit1",
  #             uid = 'smitadmin',
  #             pwd = 'Abc12345',
  #             Trusted_Connection = 'no')
  
  connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
                            Server = "TONY",
                            Database = "SMIT3",
                            uid = 'Local_SMIT3.0',
                            pwd = 'Tony123456',
                            Trusted_Connection = 'yes')  
  cursor = connect_db.cursor()

  Query = "INSERT INTO [FindingDetails] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
  
  if len(FindingData) == 0:
    return "All Finding Detail is existed!", 200
  else:
    cursor.executemany(Query, FindingData)
    connect_db.commit()
    return "Upload Data Success", 200
