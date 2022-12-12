# import Library
import csv    
from deep_translator import GoogleTranslator   
import pandas as pd                                        
import pyodbc                                          
from sentence_transformers import SentenceTransformer, util
from difflib import get_close_matches
import re
import pandas as pd
import pickle
from pythainlp import word_tokenize
from pythainlp.tag import pos_tag
from pythainlp.util import Trie

# import .py
# from CleansingAuditData.Prepared_FindingDetails import *           
# from CleansingAuditData.Prepared_FindingDetails import Prepared_FindingDetails
# from connection_db import *                      

# from ..connection_db import *   
from .Prepared_FindingDetails import *

modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer(modelPath)

def Cleansing_Input(Data, Case) :
  
  Data = Data.lower()

  Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv',encoding='utf-8')

  DictTokenize = Custom_Dict['words'].tolist()
  DictCorrect = Custom_Dict['correct'].tolist()
  AllDict = DictCorrect+DictTokenize

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

    trie = Trie(AllDict)

    for sentence in Tokenize_Input:
        TempListTokenize = word_tokenize(sentence, custom_dict=trie, engine='newmm')
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
          
    Response_SpellChecker = {
        "Collected_Input" : ResultCorrectedInput,
        "Result" : ResultTokenizeInput
    }

    return Response_SpellChecker

def Cleansing_FindingDetails():
    print("[Started Cleansing FindingDetails]...")
    
    # connection_SMIT3 = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
    #                                   Server = "smitazure.database.windows.net",
    #                                   Database = "SMIT3",
    #                                   uid = 'smitadmin',
    #                                   pwd = 'Abc12345',
    #                                   Trusted_Connection = 'no')

    TotalData = pd.read_csv('./SMIT_Data/TotalData.csv', encoding='utf-8')

    TotalOldClassification_Finding = TotalData['Old'].tolist()[0]

    TotalOldAllRecord = TotalData['Old'].tolist()[1]

    # FindingDetails = pd.read_csv("./SMIT_Data/AllRawSafetyAudit.csv", encoding='utf-8')

    # SA_FindingNo = FindingDetails['FindingNo'].tolist()
    # SA_FindingNo = ["-" if pd.isnull(x) else x for x in SA_FindingNo]

    # SA_Area = FindingDetails['Area'].tolist()
    # SA_Area = ["-" if pd.isnull(x) else x for x in SA_Area]

    # SA_SubArea = FindingDetails['SubArea'].tolist()
    # SA_SubArea = ["-" if pd.isnull(x) else x for x in SA_SubArea]

    # SA_Contractor = FindingDetails['Contractor'].tolist()
    # SA_Contractor = ["-" if pd.isnull(x) else x for x in SA_Contractor]

    # SA_Tof = FindingDetails['TypeOfFinding'].tolist()
    # SA_Tof = ["-" if pd.isnull(x) else x for x in SA_Tof]

    # SA_Topic = FindingDetails['Topic'].tolist()
    # SA_Topic = ["-" if pd.isnull(x) else x for x in SA_Topic]

    # SA_Details = FindingDetails['Details'].tolist()
    # SA_Details = ["-" if pd.isnull(x) else x for x in SA_Details]

    # SA_CleansingDetails = FindingDetails['CleansingDetails'].tolist()
    # SA_CleansingDetails = ["-" if pd.isnull(x) else x for x in SA_CleansingDetails]

    # SA_TranslateDetails = FindingDetails['TransCleansingDetails'].tolist()
    # SA_TranslateDetails = ["-" if pd.isnull(x) else x for x in SA_TranslateDetails]
    # ------------------------------------------------------------------- #

    connection_SMIT3 = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
                                Server = "smitazure.database.windows.net",
                                Database = "SMIT3",
                                uid = 'smitadmin',
                                pwd = 'Abc12345',
                                Trusted_Connection = 'no') 

    Classification_TbFinding = pd.read_sql("SELECT * FROM [Classification_TbFinding] WHERE FindingNo > "+str(TotalOldClassification_Finding), connection_SMIT3)

    CTB_Area = Classification_TbFinding['Area'].tolist()
    CTB_Area = ["-" if pd.isnull(x) else x for x in CTB_Area]

    CTB_SubArea = Classification_TbFinding['SubArea'].tolist()
    CTB_SubArea = ["-" if pd.isnull(x) else x for x in CTB_SubArea]

    CTB_Contractor = Classification_TbFinding['Contractor'].tolist()
    CTB_Contractor = ["-" if pd.isnull(x) else x for x in CTB_Contractor]

    CTB_Tof = Classification_TbFinding['TypeOfFinding'].tolist()
    CTB_Tof = ["-" if pd.isnull(x) else x for x in CTB_Tof]

    CTB_Topic = Classification_TbFinding['Topic'].tolist()
    CTB_Topic = ["-" if pd.isnull(x) else x for x in CTB_Topic]

    CTB_Details = Classification_TbFinding['Details'].tolist()
    CTB_Details = ["-" if pd.isnull(x) else x for x in CTB_Details]

    CTB_Finding = Classification_TbFinding['Finding'].tolist()
    CTB_Finding = ["-" if pd.isnull(x) else x for x in CTB_Finding]

    CTB_TranslateFinding = Classification_TbFinding['TranslateFinding'].tolist()
    CTB_TranslateFinding = ["-" if pd.isnull(x) else x for x in CTB_TranslateFinding]

    # DataSize = len(CTB_Details)+len(SA_Details)

    # Data_FindingNo = [i for i in range(TotalOldAllRecord+1, 
    #                                     TotalOldAllRecord+DataSize+1)]

    # Data_Area = CTB_Area+SA_Area

    # Data_SubArea = CTB_SubArea+SA_SubArea

    # Data_Contractor = CTB_Contractor+SA_Contractor

    # Data_Tof = CTB_Tof+SA_Tof

    # Data_Topic = CTB_Topic+SA_Topic

    # Data_Details = CTB_Finding+SA_Details

    DataSize = len(CTB_Details)

    Data_FindingNo = [i for i in range(TotalOldAllRecord+1, 
                                        TotalOldAllRecord+DataSize+1)]
    Data_Area = CTB_Area

    Data_SubArea = CTB_SubArea

    Data_Contractor = CTB_Contractor

    Data_Tof = CTB_Tof

    Data_Topic = CTB_Topic

    Data_Details = CTB_Finding

    Data_TransDetails = []
    Data_CleansingDetails = []

    for i in range(len(Data_Details)):
        ResponseSpellCheck = Cleansing_Input(Data_Details[i], 1)
        Data_CleansingDetails.append(ResponseSpellCheck['Collected_Input'])
        Data_TransDetails.append(GoogleTranslator(source='auto', target='en').translate(ResponseSpellCheck['Collected_Input']))
    
    Data_FindingNo = sorted(Data_FindingNo, reverse=False)
    Data_Area = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_Area), reverse=False)]
    Data_SubArea = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_SubArea), reverse=False)]
    Data_Contractor = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_Contractor), reverse=False)]
    Data_Tof = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_Tof), reverse=False)]
    Data_Topic = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_Topic), reverse=False)]
    Data_Details = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_Details), reverse=False)]
    Data_CleansingDetails = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_CleansingDetails), reverse=False)]
    Data_TransDetails = [frequency for _, frequency in sorted(zip(Data_FindingNo, Data_TransDetails), reverse=False)]  

    NewSafetyAuditData = list(zip(Data_FindingNo, Data_Area, Data_SubArea, 
                                    Data_Contractor, Data_Tof, Data_Topic,
                                    Data_Details, Data_CleansingDetails, Data_TransDetails))

    if len(NewSafetyAuditData) > 0:  

        cursor = connection_SMIT3.cursor()
        Query = "INSERT INTO [Cleansing_FindingDetails] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.executemany(Query, NewSafetyAuditData)
        connection_SMIT3.commit()
        
        cursor.close()
        connection_SMIT3.close()

        TotalData = (pd.read_csv('./SMIT_Data/TotalData.csv', encoding='utf-8'))
        Classfication_TbFindingLatestDate = TotalData['LatestDate'].tolist()[0]
        TotalOldClassification_Finding = TotalData['Latest'].tolist()[0]
        TotalOldAllRecord = DataSize

        Head = ['Source', 'LatestDate', 'Old', 'Latest']

        UpdateSize = [
                    ['Classfication_TbFinding', Classfication_TbFindingLatestDate, TotalOldClassification_Finding, TotalOldClassification_Finding],
                    ['All Record', '-', TotalOldAllRecord+DataSize, '-']
                    ] 
        
        with open('./SMIT_Data/TotalData.csv', 'w', newline='', encoding="utf-8") as f:
            write = csv.writer(f)
            write.writerow(Head)
            write.writerows(UpdateSize)

        print("[Finished Cleansing FindingDetails]...")

        return Prepared_FindingDetails()