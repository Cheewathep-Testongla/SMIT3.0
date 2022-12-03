from deep_translator import GoogleTranslator
from difflib import get_close_matches
import re
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import pickle
from pythainlp import word_tokenize
from pythainlp.tag import pos_tag
from pythainlp.util import Trie

# from CleansingAuditData.getRiskScore import getRiskCount
# from ii_func.embed_text_ii import *
# from ii_func.ii import *
# from CleansingAuditData.Classification_tbFinding import *
# from connection_db import *

from .ii_func.embed_text_ii import *
from .ii_func.ii import *
from .CleansingAuditData.Classification_tbFinding import *
from .CleansingAuditData.Cleansing_FindingDetails import *
from .CleansingAuditData.Prepared_FindingDetails import *
from .CleansingAuditData.getRiskScore import getRiskCount
from .connection_db import *

modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

SafetyAudit = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')
SA_Details = SafetyAudit['Finding'].tolist()
SA_Area = SafetyAudit['Area'].tolist()
SA_Contractor = SafetyAudit['Contractor'].tolist()
SA_Tof = SafetyAudit['TypeOfFinding'].tolist()
SA_Topic = SafetyAudit['Topic'].tolist()
SA_Frequency = SafetyAudit['Frequency'].tolist()
SA_Details_Trans = SafetyAudit['TranslateFinding'].tolist()


with open('./SMIT_Data/Encode_SafeyAudit.pkl', "rb") as fIn:  # open pickle file (same as model_deployment\safety_equip_func\embed_text_safety_measure.py)
  Encode_Safey_Audit_Details = pickle.load(fIn)

def Cleansing_Input(Data, Case) :
  
  Data = Data.lower()

  Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv',encoding='utf-8')

  DictTokenize = Custom_Dict['words'].tolist()
  DictCorrect = Custom_Dict['correct'].tolist()
  AllDict = DictCorrect+DictTokenize

  
  Thai_Dict = pd.read_csv('./SMIT_Data/DataForModel/TH_Raw_Dictionary.csv',encoding='utf-8')
  THDictTokenize = Thai_Dict['words'].tolist()
  THDictTrie = Trie(THDictTokenize)

  Data = re.sub(' +',' ', Data)
  Data = re.sub('^ +','', Data)
  Data = re.sub('^ | $','', Data)
  
  Data = re.sub(',| ,|, | , ',' , ', Data)
  Data = re.sub(' +',' ', Data)

  if Case == 1:
    ListUnwantedText = [
                        'no. [0-9-/]+',
                        '[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+[a-z0-9]*',
                        '[0-9]+-[0-9]+/[0-9]+',
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|=',
                        '\?',
                        '\[|\]|\{|\}'
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

    ListSplitCharacter = "\/\/+|\/|\+|,|&|and|และ|กับ|เพื่อ|\n"
    FindSplitCharecter = re.findall(ListSplitCharacter, Data) 

    Tokenize_Input = Data
    Collected_Input = Data

    for words in FindSplitCharecter:
        Tokenize_Input = Tokenize_Input.replace(words, ' , ')

    ListUnwantedText = [
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
                        '[0-9]+ ชม.',
                        '[0-9]+ ชั่วโมง',
                        '[0-9][0-9]+',                              #00 
                        ' [0-9] ',                                  # 0 
                        ' [a-z] ',                                  # a
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|-',              
                        'group',
                        'class',
                        'ฯ'
                        ]

    ListCutText = []
    for index in ListUnwantedText:
        Find_Text = re.findall(index, Tokenize_Input) 
        if len(Find_Text) != 0: 
            for words in Find_Text:
                if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
                    Tokenize_Input = Tokenize_Input.replace(words,' ')
                    Collected_Input = Collected_Input.replace(words,' ')
                    ListCutText.append(words)
        else : 
            Tokenize_Input = Tokenize_Input
            Collected_Input = Collected_Input

    Tokenize_Input = Tokenize_Input.split(',')

    ResultTokenizeInput = []
    ResultCorrectedInput = ''

    # trie = Trie(AllDict)

    for sentence in Tokenize_Input:
        TempListTokenize = word_tokenize(sentence, custom_dict=THDictTrie, engine='newmm')
        GetPos_TagListTokenize = pos_tag(TempListTokenize, corpus="orchid_ud")
        
        TempResult = []
        CheckIfTempResultisAlready = []
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

        for i in range(len(ListTokenize)):    
            FinalJoinString = ''
            if(re.findall('(^[\u0E30-\u0E3A\u0E47-\u0E4E]+)', ListTokenize[i]) or len(re.findall('[\u0E01-\u0E4E]', ListTokenize[i])) == 1):
                continue
            elif(len(re.findall(' [a-z][a-z][a-z] | [a-z][a-z] ', ListTokenize[i])) > 1):
                TempResult.append(ListTokenize[i])     

            elif(len(re.findall('([A-Za-z])\w+', ListTokenize[i])) > 0):
                if ListTokenize[i] in DictTokenize:
                    TempResult.append(DictCorrect[DictTokenize.index(ListTokenize[i])])
                else:
                    try:
                        TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
                    except:
                        TempResult.append(ListTokenize[i])        
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
                                        # TempJoinString = DictCorrect[DictTokenize.index(ListTokenize[j])]+DictCorrect[index]
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
                        # if DictCorrect[index] not in CheckIfTempResultisAlready:
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
        # Remove first and last empty space in list
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
        TempResultTokenizeInput = re.sub('^ ', '',TempResultTokenizeInput)

        if TempResultTokenizeInput not in ResultTokenizeInput and len(TempResultTokenizeInput) > 1: 
            ResultTokenizeInput.append(TempResultTokenizeInput)
            ResultCorrectedInput = ""+', '.join(ResultTokenizeInput)
    
    ResultCorrectedInput = re.sub(' +', ' ',ResultCorrectedInput)
    ResultCorrectedInput = re.sub('^ | $', '',ResultCorrectedInput)


  elif Case == 2:
    ListUnwantedText =  [
                        'no. [0-9-/]+',
                        '[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+[a-z0-9]*',
                        '[0-9]+-[0-9]+/[0-9]+',
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|=',
                        '\?|\[|\]|\{|\}',
                        ]

    ListCutText = []
    for index in ListUnwantedText:
      Find_Text = re.findall(index, Data) 
      if len(Find_Text) != 0: 
        for words in Find_Text:
          if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
            Data = Data.replace(words,'')
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
            ResultTokenizeInput = Tokenize_Input.replace(words,' ')
            ResultCorrectedInput = Collected_Input.replace(words,' ')
      else : 
        ResultTokenizeInput = Tokenize_Input
        ResultCorrectedInput = Collected_Input

    ResultTokenizeInput = Tokenize_Input.split(',')

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

# def FindCA_PA(Data):
#   Translate_Input_Details = [Data]*len(corpus_embeddings)
#   Encode_Input_Details = model.encode(Translate_Input_Details)
        
#   Cosine_Sim = util.pytorch_cos_sim(corpus_embeddings, Encode_Input_Details) 
#   top_results = torch.topk(Cosine_Sim, k=5)
  
#   print(top_results)
# เพิ่มการคิด % ของแต่ละงานตามหมวดหมู่ Type of finding
# 
def Calculate_Risk_Score(Tof, Frequency):
  if(len(Tof) > 0 and len(Frequency) > 0):
    SumFrequencyFinding = {
        "Unsafe Action": 0,
        "Unsafe Condition": 0,
        "Near Miss": 0,
        "HNM": 0,
        "Accident": 0
    }
    
    for i in range(len(Tof)):
      if(Tof[i] != '-'):
        SumFrequencyFinding[Tof[i]] += Frequency[i]

    TotalRiskCount = {
        "Unsafe Action": getRiskCount("Unsafe Action"),
        "Unsafe Condition": getRiskCount("Unsafe Condition"),
        "Near Miss": getRiskCount("Near Miss"),
        "HNM": getRiskCount("HNM"),
        "Accident": getRiskCount("Accident")
    }

    print(SumFrequencyFinding, TotalRiskCount)
    RiskScore = {
      "Unsafe Action": round((SumFrequencyFinding["Unsafe Action"]*100)/TotalRiskCount["Unsafe Action"], 2),
      "Unsafe Condition": round((SumFrequencyFinding["Unsafe Condition"]*100)/TotalRiskCount["Unsafe Condition"], 2),
      "Near Miss": round((SumFrequencyFinding["Near Miss"]*100)/TotalRiskCount["Near Miss"], 2),
      "HNM": round((SumFrequencyFinding["HNM"]*100)/TotalRiskCount["HNM"], 2),
      "Accident": round((SumFrequencyFinding["Accident"]*100)/TotalRiskCount["Accident"], 2)
    }

    return RiskScore

  else:
    RiskScore = {
      "Unsafe Action": 0,
      "Unsafe Condition": 0,
      "Near Miss": 0,
      "HNM": 0,
      "Accident": 0
    }
    return RiskScore

def Compare_Cosine_Similarity(case, Safety_Audit_Details, Data_Details_Trans, Input_Details, List_Input_Details, Data_Frequency, Data_Contractor, Data_Tof, Data_Area, Data_Topic):
  global Encode_Safey_Audit_Details
  Suggestion_Safety_Audit_Detail = []
  Suggestion_Safety_Audit_Frequency = []
  Suggestion_Safety_Audit_Contractor = []
  Suggestion_Safety_Audit_Type_Of_Finding = []
  Suggestion_Safety_Audit_Area = []
  Suggestion_Safety_Audit_Topic = []
  Suggestion_Safety_Audit_CA = []
  Suggestion_Safety_Audit_PA = []

  Temp_Safety_Audit_Details = []
  Temp_Safety_Audit_Frequency = []
  Temp_Safety_Audit_Contractor = []
  Temp_Safety_Audit_Type_Of_Finding = []
  Temp_Safety_Audit_Area = []
  Temp_Safety_Audit_Topic = []

  if case == 1:
    for sentence in List_Input_Details:
      if len(Safety_Audit_Details) != 0:
        Translate_Input_Details = (GoogleTranslator(source='auto', target='en').translate(sentence))
        Translate_Input_Details = [Translate_Input_Details]*len(Safety_Audit_Details)

        Encode_Safey_Audit_Details = model.encode(Data_Details_Trans)
        Encode_Input_Details = model.encode(Translate_Input_Details)
        
        Cosine_Sim = util.pytorch_cos_sim(Encode_Safey_Audit_Details, Encode_Input_Details) 
        compare_work_with_Safety_Audit = []
        
        for i in range(len(Cosine_Sim)):
          j = 0
          compare_work_with_Safety_Audit.append([Cosine_Sim[i][j], i, j, Data_Frequency[i], Data_Contractor, Data_Tof[i], Data_Area, Data_Topic[i]])
        compare_work_with_Safety_Audit = sorted(compare_work_with_Safety_Audit, key=lambda x: x[0], reverse=True)

        run_Number = 1

        for score, i, j, k, l, m, n, o in compare_work_with_Safety_Audit[:5]:        
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
                    "Safety_Audit_CA": [["No Data"]],
                    "Safety_Audit_PA": [["No Data"]]
                  }
                  return Form_Response_SafetyAudit
                break

  elif case == 2:
    for sentence in List_Input_Details:
      if len(Safety_Audit_Details) != 0:
        Translate_Input_Details = (GoogleTranslator(source='auto', target='en').translate(sentence))
        Translate_Input_Details = [Translate_Input_Details]*len(Encode_Safey_Audit_Details)
        Encode_Input_Details = model.encode(Translate_Input_Details)
        
        Cosine_Sim = util.cos_sim(Encode_Safey_Audit_Details, Encode_Input_Details) 
        compare_work_with_Safety_Audit = []
        
        for i in range(len(Cosine_Sim)):
          j = 0
          compare_work_with_Safety_Audit.append([Cosine_Sim[i][j], i, j, Data_Frequency[i], Data_Contractor[i], Data_Tof[i], Data_Area[i], Data_Topic[i]])
        compare_work_with_Safety_Audit = sorted(compare_work_with_Safety_Audit, key=lambda x: x[0], reverse=True)

        run_Number = 1

        for score, i, j, k, l, m, n, o in compare_work_with_Safety_Audit[:5]:        
          if Cosine_Sim[i][0] > 0.6:
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
                  "Safety_Audit_CA": [["No Data"]],
                  "Safety_Audit_PA": [["No Data"]]
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
    Create_List_Safety_Audit_CA = []
    Create_List_Safety_Audit_PA = []

    Create_List_Safety_Audit_Details.append(Temp_Safety_Audit_Details[i])
    Create_List_Safety_Audit_Frequency.append(Temp_Safety_Audit_Frequency[i])
    Create_List_Safety_Audit_Contractor.append(Temp_Safety_Audit_Contractor[i])
    Create_List_Safety_Audit_Type_Of_Finding.append(Temp_Safety_Audit_Type_Of_Finding[i]) 
    Create_List_Safety_Audit_Area.append(Temp_Safety_Audit_Area[i]) 
    Create_List_Safety_Audit_Topic.append(Temp_Safety_Audit_Topic[i]) 

    if(Temp_Safety_Audit_Type_Of_Finding[i] == "Accident" or Temp_Safety_Audit_Type_Of_Finding[i] == "HNM" or Temp_Safety_Audit_Type_Of_Finding[i] == "Near Miss"):
      tempResultCAPA = {
          "name": Temp_Safety_Audit_Details[i],
          "tag_equip": "",
          "area": Temp_Safety_Audit_Area[i],
          "tool": "",
          "company": "",
          "correct": False
      }
      Response_CAPA = search_ii(tempResultCAPA, "Only CAPA")
      Create_List_Safety_Audit_CA.append(Response_CAPA['all_ca'])
      Create_List_Safety_Audit_PA.append(Response_CAPA['all_pa'])

    Suggestion_Safety_Audit_Detail.append(Create_List_Safety_Audit_Details)
    Suggestion_Safety_Audit_Frequency.append(Create_List_Safety_Audit_Frequency)
    Suggestion_Safety_Audit_Contractor.append(Create_List_Safety_Audit_Contractor)
    Suggestion_Safety_Audit_Type_Of_Finding.append(Create_List_Safety_Audit_Type_Of_Finding)
    Suggestion_Safety_Audit_Area.append(Create_List_Safety_Audit_Area)
    Suggestion_Safety_Audit_Topic.append(Create_List_Safety_Audit_Topic)
    Suggestion_Safety_Audit_CA.append(Create_List_Safety_Audit_CA)
    Suggestion_Safety_Audit_PA.append(Create_List_Safety_Audit_PA)
  
  RiskScore = Calculate_Risk_Score(Temp_Safety_Audit_Type_Of_Finding, Temp_Safety_Audit_Frequency)

  Form_Response_SafetyAudit = {
    "Safety_Audit_Details" : Suggestion_Safety_Audit_Detail,
    "Safety_Audit_Frequency" : Suggestion_Safety_Audit_Frequency,
    "Safety_Audit_Contractor" : Suggestion_Safety_Audit_Contractor,
    "Safety_Audit_Type_Of_Finding" : Suggestion_Safety_Audit_Type_Of_Finding,
    "Safety_Audit_Area" : Suggestion_Safety_Audit_Area,
    "Safety_Audit_Topic" : Suggestion_Safety_Audit_Topic,
    "Safety_Audit_CA": Suggestion_Safety_Audit_CA,
    "Safety_Audit_PA": Suggestion_Safety_Audit_PA,
    "RiskScore" : RiskScore
  }

  if len(Data_Details_Trans) == 0:
    Form_Response_SafetyAudit = {
      "Safety_Audit_Details": [["No Data about "+Input_Details+" was found"]],
      "Safety_Audit_Frequency": [[0]],
      "Safety_Audit_Contractor" : [["No Data"]],
      "Safety_Audit_Type_Of_Finding" : [["No Data"]],
      "Safety_Audit_Area" : [["No Data"]],
      "Safety_Audit_Topic" : [["No Data"]],
      "Safety_Audit_CA": [["No Data"]],
      "Safety_Audit_PA": [["No Data"]],
      "RiskScore" : RiskScore
    }
  return Form_Response_SafetyAudit

def CleansingAuditData():
  print("[Started Classification tbFinding]...")
  return StartCleansingtbFinding()









#----------Old Algorithm-----------#
# Cleansing_Input
# def Cleansing_Input(Data, Case) :

#   Data = Data.lower()

#   Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv',encoding='utf-8')

#   DictTokenize = Custom_Dict['words'].tolist()
#   DictCorrect = Custom_Dict['correct'].tolist()
#   AllDict = DictCorrect+DictTokenize

#   trie = Trie(AllDict)

#   Data = re.sub(' +',' ', Data)
#   Data = re.sub('^ +','', Data)
#   Data = re.sub('^ | $','', Data)
  
#   Data = re.sub(',| ,|, | , ',' , ', Data)
#   Data = re.sub(' +',' ', Data)
#   Data = re.sub('ชม|ชม.','ชั่วโมง', Data)

#   if Case == 1:
#     ListUnwantedText =  [
#                         '\/|\.|\#|\(|\)|\@|^[ ]|:|\"|M\.|-|\?|\[|\]|\{|\}',                   
#                         '[0-9]+ เมตร',                              #12 เมตร
#                         '[0-9]+ ชั่วโมง',
#                         'ชั่วโมง',
#                         'no. [0-9-/]+',
#                         '[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+[a-z0-9]*',
#                         '[0-9]+-[0-9]+/[0-9]+',
#                         '[a-z]+-[0-9a-z]+-[a-z0-9]+',               #a-a0-a0     
#                         '[a-z]+-[0-9]+[a-z]+[0-9]+[a-z]+',          #a-a0 
#                         '[a-z]+-[0-9]+[a-z]+[a-z]+[0-9]+',          #
#                         '[a-z]+-[a-z]+[0-9]+[0-9]+[a-z]+',          #
#                         '[a-z]+-[a-z]+[0-9]+[a-z]+[0-9]+',          #
#                         '[a-z]+[0-9]+[a-z-]+',                      #                          
#                         '[a-z]+ [0-9]+ [a-z]+',                     # PIT 3060 ABC                         
#                         '[a-z]+-[0-9]+-[a-z]+',                     #a-0-a                                               
#                         '[a-z]+-[a-z]+-[0-9]+',                     #a-a-0
#                         '[a-z]+-[0-9]+[a-z]+',                      # TT-8006BA
#                         '[a-z]+-[0-9]+',                            #a-0
#                         '[0-9]+[a-z]+',                             #0a
#                         '[a-z]+[0-9]+',                             #a0                        
#                         '[0-9][0-9]+',                              #00 
#                         ' [0-9] ',                                  # 0 
#                         ' [a-z] ',                                  # a
#                         'group',
#                         'class'
#                         ]

#     ListCutText = []

#     for index in ListUnwantedText:

#       Find_Text = re.findall(index, Data) 

#       if len(Find_Text) != 0: 
#         for words in Find_Text:
#           if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
#             Data = Data.replace(words,' ')
#             ListCutText.append(words)
#       else : 
#         Data = Data

#     ListSplitCharacter = "\/\/+|\/|\+|,|&| and | and|และ|กับ|เพื่อ|\n"
#     FindSplitCharecter = re.findall(ListSplitCharacter, Data) 

#     Tokenize_Input = Data

#     for words in FindSplitCharecter:
#       Tokenize_Input = Tokenize_Input.replace(words, ' , ')

#     Tokenize_Input = Tokenize_Input.split(',')

#     ResultTokenizeInput = []
#     ResultCorrectedInput = ''

#     for sentence in Tokenize_Input:
#       TempListTokenize = word_tokenize(sentence, custom_dict=trie, engine='newmm')
#       GetPos_TagListTokenize = pos_tag(TempListTokenize, corpus="orchid_ud")
#       ListTokenize = [GetPos_TagListTokenize[i][0] for i in range(len(GetPos_TagListTokenize))]
#       TempResult = []
#       for i in range(len(ListTokenize)):
#         if(len(re.findall(' [a-z][a-z][a-z] | [a-z][a-z] ', ListTokenize[i])) > 1):
#             TempResult.append(ListTokenize[i])     

#         elif(len(re.findall('([A-Za-z])\w+', ListTokenize[i])) > 0):
#             if ListTokenize[i] in DictTokenize:
#               TempResult.append(DictCorrect[DictTokenize.index(ListTokenize[i])])
#             else:
#               try:
#                 TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
#               except:
#                 TempResult.append(ListTokenize[i])            
#         else:
#           try:
#               TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
#           except: 
#               TempResult.append(ListTokenize[i])
    
#     Result = []
#     TempResultTokenizeInput = ''

#     for i in range(len(TempResult)):
#       if (i == 0 and len(TempResult) > 1):
#         ResultCorrectedInput = ' '+ResultCorrectedInput+TempResult[i]
#       if (TempResult[i] == '') or (i == 0 and TempResult[i] == ' ') or (i == len(TempResult)-1 and TempResult[len(TempResult)-1] == ' ') or (TempResult[i] == ' ' and TempResult[i+1] == ' '):
#         continue
#       else:
#         if(i == 0):
#           ResultCorrectedInput = ' '+ResultCorrectedInput
#         Result.append(TempResult[i])
#         TempResultTokenizeInput = TempResultTokenizeInput+TempResult[i]

#     TempResultTokenizeInput = TempResultTokenizeInput+' '
#     TempResultTokenizeInput = re.sub(' +', ' ',TempResultTokenizeInput)
#     TempResultTokenizeInput = re.sub('^ | $', '',TempResultTokenizeInput)

#     if TempResultTokenizeInput not in ResultTokenizeInput and len(TempResultTokenizeInput) > 1: 
#       ResultTokenizeInput.append(TempResultTokenizeInput)
#       ResultCorrectedInput = ""+', '.join(ResultTokenizeInput)
    
#     ResultCorrectedInput = re.sub(' +', ' ',ResultCorrectedInput)
#     ResultCorrectedInput = re.sub('^ | $', '',ResultCorrectedInput)

#   elif Case == 2:
#     ListUnwantedText =  [
#                         'no. [0-9-/]+',
#                         '[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+[a-z0-9]*',
#                         '[0-9]+-[0-9]+/[0-9]+',
#                         '\#|\(|\)|\@|^[ ]|:|\"|M\.|=',
#                         '\?|\[|\]|\{|\}',
#                         ]

#     ListCutText = []
#     for index in ListUnwantedText:
#       Find_Text = re.findall(index, Data) 
#       if len(Find_Text) != 0: 
#         for words in Find_Text:
#           if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
#             Data = Data.replace(words,'')
#             ListCutText.append(words)
#       else : 
#         Data = Data

#     ListSplitCharacter = "\/\/+|\/|\+|,|&| and | and|และ|กับ|เพื่อ|\n"
#     FindSplitCharecter = re.findall(ListSplitCharacter, Data) 

#     Tokenize_Input = Data
#     Collected_Input = Data

#     for words in FindSplitCharecter:
#       Tokenize_Input = Tokenize_Input.replace(words, ' , ')

#     ListUnwantedText =  [
#                         '[a-z]+-[0-9a-z]+-[a-z0-9]+',               #a-a0-a0     
#                         '[a-z]+-[0-9]+[a-z]+[0-9]+[a-z]+',          #a-a0 
#                         '[a-z]+-[0-9]+[a-z]+[a-z]+[0-9]+',          #
#                         '[a-z]+-[a-z]+[0-9]+[0-9]+[a-z]+',          #
#                         '[a-z]+-[a-z]+[0-9]+[a-z]+[0-9]+',          #
#                         '[a-z]+[0-9]+[a-z-]+',                      #                          
#                         '[a-z]+ [0-9]+ [a-z]+',                     # PIT 3060 ABC                         
#                         '[a-z]+-[0-9]+-[a-z]+',                     #a-0-a                                               
#                         '[a-z]+-[a-z]+-[0-9]+',                     #a-a-0
#                         '[a-z]+-[0-9]+[a-z]+',                      # TT-8006BA
#                         '[a-z]+-[0-9]+',                            #a-0
#                         '[0-9]+[a-z]+',                             #0a
#                         '[a-z]+[0-9]+',                             #a0                        
#                         '[0-9]+ เมตร',                              #12 เมตร
#                         '[0-9][0-9]+',                              #00 
#                         ' [0-9] ',                                  # 0 
#                         ' [a-z] ',                                  # a
#                         '\#|\(|\)|\@|^[ ]|:|\"|M\.|-',              
#                         'group'
#                         ]

#     for index in ListUnwantedText:
#       Find_Text = re.findall(index, Tokenize_Input) 
#       if len(Find_Text) != 0: 
#         for words in Find_Text:
#           if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
#             ResultTokenizeInput = Tokenize_Input.replace(words,' ')
#             ResultCorrectedInput = Collected_Input.replace(words,' ')
#       else : 
#         ResultTokenizeInput = Tokenize_Input
#         ResultCorrectedInput = Collected_Input

#     ResultTokenizeInput = Tokenize_Input.split(',')

#     for index in range(len(ResultTokenizeInput)):
#       ResultTokenizeInput[index] = re.sub('^ ', '', ResultTokenizeInput[index])
      
#   Response_SpellChecker = {
#     "Collected_Input" : ResultCorrectedInput,
#     "Result" : ResultTokenizeInput
#   }
#   return Response_SpellChecker

# UploadFinding
# def UploadFinding(FindingData):
#   # connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#   #             Server = "smitazure.database.windows.net",
#   #             Database = "Smit1",
#   #             uid = 'smitadmin',
#   #             pwd = 'Abc12345',
#   #             Trusted_Connection = 'no')
  
#   connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#                             Server = "TONY",
#                             Database = "SMIT3",
#                             uid = 'Local_SMIT3.0',
#                             pwd = 'Tony123456',
#                             Trusted_Connection = 'yes')  
#   cursor = connect_db.cursor()

#   Query = "INSERT INTO [FindingDetails] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
  
#   if len(FindingData) == 0:
#     return "All Finding Detail is existed!", 200
#   else:
#     cursor.executemany(Query, FindingData)
#     connect_db.commit()
#     return "Upload Data Success", 200

# GetFindingDetail
# def GetFindingDetail(Orderby):
#   # connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#   #             Server = "smitazure.database.windows.net",
#   #             Database = "Smit1",
#   #             uid = 'smitadmin',
#   #             pwd = 'Abc12345',
#   #             Trusted_Connection = 'no') 
  
#   connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
#                           Server = "TONY",
#                           Database = "SMIT3",
#                           uid = 'Local_SMIT3.0',
#                           pwd = 'Tony123456',
#                           Trusted_Connection = 'yes')  

#   ResponseFindingDetail = pd.read_sql("SELECT * FROM FindingDetails ORDER BY FindingNo "+Orderby, connect_db)

#   return ResponseFindingDetail

# Upload_Audit_To_Database
# def Upload_Audit_To_Database(Data):
#   with open('./SMIT_Data/Audit_Result/SMIT3_Audit_Result.csv', 'a', newline='', encoding="utf-8") as f:
#     write = csv.writer(f)
#     write.writerow(Data)
#   return "Success"