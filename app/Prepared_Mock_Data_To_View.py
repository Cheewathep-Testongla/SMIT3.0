import deepcut
from deep_translator import GoogleTranslator
from difflib import get_close_matches
from Function import Compare_Cosine_Similarity, Search_Safety_Audit, Cleansing_Input
import json
import re
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import pyodbc
from itertools import chain
from pythainlp import sent_tokenize, word_tokenize, correct, spell, Tokenizer
from pythainlp.tag import pos_tag, pos_tag_sents
from pythainlp.spell import NorvigSpellChecker
from pythainlp.corpus.common import thai_words
from pythainlp.util import dict_trie, Trie

import torch
import tensorflow as tf
import csv

from sklearn.model_selection import train_test_split

modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer(modelPath)
# Get All SafetyCompany
Permit_Data = pd.read_csv('./SMIT_Data/Work_Permit_New.csv', encoding='utf-8')

SafetyCompany = Permit_Data["SafetyCompany"]
InitialCompany = Permit_Data["InitialCompany"]

# Get All Safety Audit
SafetyAudit = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')

SA_Details = SafetyAudit['Details'].tolist()
SA_Area = SafetyAudit['Area'].tolist()
SA_Contractor = SafetyAudit['Contractor'].tolist()
SA_Tof = SafetyAudit['Type of finding'].tolist()
SA_Topic = SafetyAudit['Topic'].tolist()
SA_Frequency = SafetyAudit['Frequency'].tolist()
SA_Details_Trans = SafetyAudit['Translate Details'].tolist()

# Get Work Permit Data from Database
connect_db = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
                            Server = "TONY",
                            Database = "e-Permit_MOC",
                            uid = 'Local_SMIT3.0',
                            pwd = 'Tony123456',
                            Trusted_Connection = 'Yes') 

QueryFromDB = pd.read_sql('''SELECT [v_Permit_WorkerList].[ReqID], [v_Permit_WorkerList].[Desire], [v_Permit_WorkerList].[Area], [SafetyCompany] 
                            FROM [v_Permit_List] 
                            JOIN [v_Permit_WorkerList] 
                            ON [v_Permit_List].[PermitNo] = [v_Permit_WorkerList].[PermitNo] 
                            WHERE [v_Permit_List].[Desire] != '' 
                            and [v_Permit_WorkerList].[Desire] != '' 
                            and [v_Permit_WorkerList].[PermitNo] != '' 
                            and [v_Permit_WorkerList].[Area] != ''
                            and [v_Permit_WorkerList].[SafetyCompany] != ''
                            ORDER BY [v_Permit_List].[ReqId] ,[v_Permit_WorkerList].[SafetyCompany] ASC;'''
                        , connect_db)

ReqID = QueryFromDB['ReqID'].to_list()
Cocompany = QueryFromDB['SafetyCompany'].to_list()
WPMDetail = QueryFromDB['Desire'].to_list()
Area = QueryFromDB['Area'].to_list()

cursor = connect_db.cursor()

ResponseSpellCheck = {
    "Collected_Input" : "",
    "Result" : []
}

CheckGetResponse_1 = True
CheckGetResponse_2 = True

Error_Words = []
def AllChecklistAuditOfWPMDetail():
    global CheckGetResponse_1
    global CheckGetResponse_2

    for index in range(len(WPMDetail)):
        if index != len(Cocompany) - 1:
            if (ReqID[index] == ReqID[index + 1] and Cocompany[index] == Cocompany[index + 1] and CheckGetResponse_1 == True) or (ReqID[index] != ReqID[index + 1] and ReqID[index] != ReqID[index - 1] and CheckGetResponse_1 == True):
                
                CheckGetResponse_1 = False
                
                tempCocompany = Cocompany[index]
                tempWPMDetail = WPMDetail[index]
                tempArea = Area[index]

                for SafetyCompanyIndex in range(len(SafetyCompany)):
                    if tempCocompany == SafetyCompany[SafetyCompanyIndex] and InitialCompany[SafetyCompanyIndex] != "-":
                        tempCocompany = InitialCompany[SafetyCompanyIndex]
                        break

                ResponseSpellCheck = Cleansing_Input(tempWPMDetail, 1)

                Data_Contractor_1, Data_Area_1, Data_Tof_1, Data_Details_1, Data_Details_Trans_1, Data_Topic_1, Data_Frequency_1 = Search_Safety_Audit(1, tempArea, tempCocompany)
                Suggestion_Safety_Audit_1 = Compare_Cosine_Similarity(1, Data_Details_1, Data_Details_Trans_1, ResponseSpellCheck['Collected_Input'], ResponseSpellCheck['Result'], Data_Frequency_1, Data_Contractor_1, Data_Tof_1, Data_Area_1, Data_Topic_1)

                Data_Contractor_2, Data_Area_2, Data_Tof_2, Data_Details_2, Data_Details_Trans_2, Data_Topic_2, Data_Frequency_2 = Search_Safety_Audit(2, tempArea, tempCocompany)
                Suggestion_Safety_Audit_2 = Compare_Cosine_Similarity(2, Data_Details_2, Data_Details_Trans_2, ResponseSpellCheck['Collected_Input'], ResponseSpellCheck['Result'], Data_Frequency_2, Data_Contractor_2, Data_Tof_2, Data_Area_2, Data_Topic_2)
                
                cursor.execute("INSERT INTO [v_Response_SafetyAudit] VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                (ReqID[index], 
                                tempWPMDetail, 
                                tempArea, 
                                tempCocompany, 
                                ResponseSpellCheck['Collected_Input'], 
                                json.dumps(ResponseSpellCheck['Result'], ensure_ascii=False), 
                                json.dumps(Suggestion_Safety_Audit_1, ensure_ascii=False),
                                json.dumps(Suggestion_Safety_Audit_2, ensure_ascii=False)))

                connect_db.commit()

            elif ReqID[index] == ReqID[index + 1] and Cocompany[index] != Cocompany[index + 1] and CheckGetResponse_2 == True:

                CheckGetResponse_2 = False

                tempCocompany = Cocompany[index+1]
                tempWPMDetail = WPMDetail[index+1]
                tempArea = Area[index+1]

                for SafetyCompanyIndex in range(len(SafetyCompany)):
                    if tempCocompany == SafetyCompany[SafetyCompanyIndex] and InitialCompany[SafetyCompanyIndex] != "-":
                        tempCocompany = InitialCompany[SafetyCompanyIndex]
                        break

                ResponseSpellCheck = Cleansing_Input(tempWPMDetail, 1)

                Data_Contractor_1, Data_Area_1, Data_Tof_1, Data_Details_1, Data_Details_Trans_1, Data_Topic_1, Data_Frequency_1 = Search_Safety_Audit(1, tempArea, tempCocompany)
                Suggestion_Safety_Audit_1 = Compare_Cosine_Similarity(1, Data_Details_1, Data_Details_Trans_1, ResponseSpellCheck['Collected_Input'], ResponseSpellCheck['Result'], Data_Frequency_1, Data_Contractor_1, Data_Tof_1, Data_Area_1, Data_Topic_1)

                Data_Contractor_2, Data_Area_2, Data_Tof_2, Data_Details_2, Data_Details_Trans_2, Data_Topic_2, Data_Frequency_2 = Search_Safety_Audit(2, tempArea, tempCocompany)
                Suggestion_Safety_Audit_2 = Compare_Cosine_Similarity(2, Data_Details_2, Data_Details_Trans_2, ResponseSpellCheck['Collected_Input'], ResponseSpellCheck['Result'], Data_Frequency_2, Data_Contractor_2, Data_Tof_2, Data_Area_2, Data_Topic_2)

                cursor.execute("INSERT INTO [v_Response_SafetyAudit] VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                (ReqID[index+1], 
                                tempWPMDetail, 
                                tempArea, 
                                tempCocompany, 
                                ResponseSpellCheck['Collected_Input'], 
                                json.dumps(ResponseSpellCheck['Result'], ensure_ascii=False), 
                                json.dumps(Suggestion_Safety_Audit_1, ensure_ascii=False),
                                json.dumps(Suggestion_Safety_Audit_2, ensure_ascii=False)))

                connect_db.commit()
        
            if ReqID[index] != ReqID[index + 1] and Cocompany[index] != Cocompany[index + 1]: 
                CheckGetResponse_1 = True
                CheckGetResponse_2 = True

# Classification Topic from tbFinding
# def ClassificationTopic():
#     tbFinding = pd.read_csv('./SMIT_Data/Classification_tbFinding/tbFinding.csv', encoding='utf-8')
#     SafetyAudit = pd.read_csv('./SMIT_Data/All_Prepared_Safety_Audit.csv', encoding='utf-8')

#     Finding = tbFinding['Finding'].tolist()
#     Translate_Finding = []

#     Topic = SafetyAudit['Topic'].tolist()
#     Cleansing_Translate_Details = SafetyAudit['Clean_Translate_Details'].tolist()

#     # for sentence in Finding:
#     #     Translate_Finding.append(GoogleTranslator(source = 'auto', target = 'en').translate(sentence))
    
#     count_vector = CountVectorizer()  
#     count_vector = CountVectorizer(stop_words = 'english')     

#     count_vector.fit(Cleansing_Translate_Details)                        

#     doc_array = count_vector.transform(Cleansing_Translate_Details).toarray() 

#     X_train, X_test, Y_train, Y_test = train_test_split(doc_array, Topic, test_size=0.1)

#     gnb = GaussianNB()
#     bnb = BernoulliNB()
#     cnb = CategoricalNB()

#     bnb.fit(X_train, Y_train)

#     newVec = CountVectorizer(vocabulary = count_vector.vocabulary_)   
    
#     new_doc = [GoogleTranslator(source = 'auto', target = 'en').translate(Finding[169])]

#     doc_array = newVec.transform(new_doc).toarray()     
    
#     y_label = bnb.predict(doc_array)    
#     print(Finding[169])                
#     print(bnb.predict_proba(doc_array), y_label[0])              

def ManualClassificationTopic():
    tbFinding = pd.read_csv('./SMIT_Data/Classification_tbFinding/tbFindingResult.csv', encoding='utf-8')

    tbFindingID = tbFinding['ID'].tolist()
    tbFindingTitle = tbFinding['Title'].tolist()
    tbFindingFinding = tbFinding['Finding'].tolist()
    tbFindingArea = tbFinding['Area'].tolist()
    tbFindingCategory = tbFinding['Category'].tolist()
    tbFindingCheckListNo = tbFinding['CheckListNo'].tolist()
    tbFindingAuditResult = tbFinding['AuditResult'].tolist()   
    tbFindingCorrective = tbFinding['Corrective'].tolist()
    tbFindingAuthorizePerson = tbFinding['AuthorizePerson'].tolist()
    tbFindingCauseDeviation = tbFinding['CauseDeviation'].tolist()
    tbFindingFindingBy = tbFinding['FindingBy'].tolist()
    tbFindingFindingDate = tbFinding['FindingDate'].tolist()
    tbFindingCreated = tbFinding['Created'].tolist()
    tbFindingCreatedBy = tbFinding['CreatedBy'].tolist()
    tbFindingModified = tbFinding['Modified'].tolist()
    tbFindingModifiedBy = tbFinding['ModifiedBy'].tolist()
    tbFindingimgURL = tbFinding['imgURL'].tolist()
    tbFindingTranslate = tbFinding['TranslateFinding'].tolist()

    SafetyAudit = pd.read_csv('./SMIT_Data/AllRawSafetyAudit.csv', encoding='utf-8')
    
    SafetyAuditCleansingDetails = SafetyAudit['CleansingDetails'].tolist()
    SafetyAuditTranslateDetails = SafetyAudit['TransCleansingDetails'].tolist()
    SafetyAuditTopic = SafetyAudit['Topic'].tolist()
    SafetyAuditTof = SafetyAudit['Type of finding'].tolist()

    Cluster_UnsafeCondition = []
    Cluster_UnsafeAction = []
    Cluster_NearMiss = []
    Cluster_HNM = []
    Cluster_Accident = []
    
    Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv',encoding='utf-8')
    DictCorrect = Custom_Dict['correct'].tolist()

    trie = Trie(DictCorrect)

    for index in range(len(SafetyAuditCleansingDetails)):
        temp = []
        Tokenize = word_tokenize(SafetyAuditCleansingDetails[index], custom_dict=trie, engine='newmm')
        if(SafetyAuditTof[index] == 'Unsafe Condition'):
            if(len(Cluster_UnsafeCondition) == 0):
                Cluster_UnsafeCondition = Tokenize
            else:
                for words in Tokenize:
                    if words not in Cluster_UnsafeCondition:
                        Cluster_UnsafeCondition.append(words)

        elif(SafetyAuditTof[index] == 'Unsafe Action'):
            if(len(Cluster_UnsafeAction) == 0):
                Cluster_UnsafeAction = Tokenize
            else:
                for words in Tokenize:
                    if words not in Cluster_UnsafeAction:
                        Cluster_UnsafeAction.append(words)

        elif(SafetyAuditTof[index] == 'Near Miss'):
            if(len(Cluster_NearMiss) == 0):
                Cluster_NearMiss = Tokenize
            else:
                for words in Tokenize:
                    if words not in Cluster_NearMiss:
                        Cluster_NearMiss.append(words)

        elif(SafetyAuditTof[index] == 'HNM'):
            if(len(Cluster_HNM) == 0):
                Cluster_HNM = Tokenize
            else:
                for words in Tokenize:
                    if words not in Cluster_HNM:
                        Cluster_HNM.append(words)

        elif(SafetyAuditTof[index] == 'Accident'):
            if(len(Cluster_Accident) == 0):
                Cluster_Accident = Tokenize
            else:
                for words in Tokenize:
                    if words not in Cluster_Accident:
                        Cluster_Accident.append(words)            

    Cluster_UnsafeCondition = list(set(Cluster_UnsafeCondition) - set(Cluster_UnsafeAction) - set(Cluster_NearMiss) - set(Cluster_HNM) - set(Cluster_Accident))
    
    Cluster_UnsafeAction = list(set(Cluster_UnsafeAction) - set(Cluster_UnsafeCondition) - set(Cluster_NearMiss) - set(Cluster_HNM) - set(Cluster_Accident))

    Cluster_NearMiss = list(set(Cluster_NearMiss) - set(Cluster_UnsafeAction) - set(Cluster_UnsafeCondition) - set(Cluster_HNM) - set(Cluster_Accident))

    Cluster_HNM = list(set(Cluster_HNM) - set(Cluster_NearMiss) - set(Cluster_UnsafeAction) - set(Cluster_UnsafeCondition) - set(Cluster_Accident))

    Cluster_Accident = list(set(Cluster_Accident) - set(Cluster_HNM) - set(Cluster_NearMiss) - set(Cluster_UnsafeAction) - set(Cluster_UnsafeCondition))

    GetPos_TagTokenize = pos_tag(Cluster_UnsafeCondition, corpus="orchid_ud")
    
    # print(GetPos_TagTokenize)

    print("Cluster_UnsafeCondition :",len(Cluster_UnsafeCondition))
    print("Cluster_UnsafeAction :",len(Cluster_UnsafeAction))
    print("Cluster_NearMiss :",len(Cluster_NearMiss))
    print("Cluster_HNM :",len(Cluster_HNM))
    print("Cluster_Accident :",len(Cluster_Accident))

    print(Cluster_Accident)

    ClassifyTopic = []
    for index in range(len(tbFindingID)):
        Data = word_tokenize(tbFindingFinding[index], custom_dict=trie, engine='newmm')
        Finding = ""
        temp = []
        MaxCount = 0
        if len(set(Data) & set(Cluster_UnsafeCondition)) > MaxCount:
            Finding = "Unsafe Condition"
            MaxCount = len(set(Data) & set(Cluster_UnsafeCondition))

        if len(set(Data) & set(Cluster_UnsafeAction)) > MaxCount:
            Finding = "Unsafe Action"
            MaxCount = len(set(Data) & set(Cluster_UnsafeAction))

        if len(set(Data) & set(Cluster_NearMiss)) > MaxCount:
            Finding = "Near Miss"
            MaxCount = len(set(Data) & set(Cluster_NearMiss))

        if len(set(Data) & set(Cluster_HNM)) > MaxCount:
            Finding = "HNM"
            MaxCount = len(set(Data) & set(Cluster_HNM))

        if len(set(Data) & set(Cluster_Accident)) > MaxCount:
            Finding = "Accident"
            MaxCount = len(set(Data) & set(Cluster_Accident))

        temp.append(tbFindingFinding[index]) 
        temp.append(Finding)
        ClassifyTopic.append(temp)

    # print(ClassifyTopic)

    Head = ['Details', 'Type of finding', 'Topic']
    with open('./SMIT_Data/ClassifyAudit.csv', 'w', newline='', encoding="utf-8") as f:
        write = csv.writer(f)
        write.writerow(Head)
        write.writerows(ClassifyTopic)
        
    # for index in range(len(tbFinding)):
    #     TempFinding = [SafetyAuditTranslate[index]]*len(SafetyAuditTranslate)

    #     Encode_Safey_Audit_Details = model.encode(TempFinding)
    #     Encode_Input_Details = model.encode(tbFindingTranslate[index])
        
    #     Cosine_Sim = util.cos_sim(Encode_Safey_Audit_Details, Encode_Input_Details) 
    #     compare_work_with_Safety_Audit = []
        
    #     for i in range(len(Cosine_Sim)):
    #       j = 0
    #       compare_work_with_Safety_Audit.append([Cosine_Sim[i][j], i, j, SafetyAuditTopic[i], SafetyAuditTof[i]])
        
    #     compare_work_with_Safety_Audit = sorted(compare_work_with_Safety_Audit, key=lambda x: x[0], reverse=True)
        
    #     print(compare_work_with_Safety_Audit[0])

    # return Form_Response_SafetyAudit

ManualClassificationTopic()
