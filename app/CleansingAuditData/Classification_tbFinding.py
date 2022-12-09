# import Library
import csv
from deep_translator import GoogleTranslator
import pandas as pd
import pyodbc
from pythainlp import word_tokenize
from pythainlp.util import Trie     
# import .py   
# from CleansingAuditData.ScoredWord import *
# from CleansingAuditData.Cleansing_FindingDetails import *
# from connection_db import * 

from .ScoredWord import *
from .Cleansing_FindingDetails import Cleansing_FindingDetails
from ..connection_db import *


def StartCleansingtbFinding():
    # global Custom_Dict, DictCorrect, trie
    # global tbFindingArea, tbFindingSubArea, tbFindingContractor, tbFindingTof, tbFindingTopic, tbFindingDetail, tbFindingTranslateDetail, tbFindingAuditResult, tbFindingFinding, tbFindingTranslateFinding
    # global ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident
    # global Cluster_UnsafeAction, Cluster_UnsafeCondition, Cluster_NearMiss, Cluster_HNM, Cluster_Accident
    # global ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others
    # global ListWords_Lifting, ListWords_Housekeeping, ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding, ListWords_PaintCoatBlast
    # global ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil 
    # global ListWords_Insulation, ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security

    Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv', encoding='utf-8')
    DictCorrect = Custom_Dict['correct'].tolist()

    DictCorrect = list(set(DictCorrect))
    trie = Trie(DictCorrect)

    tbFindingArea = []
    tbFindingSubArea = []
    tbFindingContractor = []
    tbFindingTof = []
    tbFindingTopic = []
    tbFindingDetail = []
    tbFindingTranslateDetail = []
    tbFindingAuditResult = []
    tbFindingFinding = []
    tbFindingTranslateFinding = []

    ListWords_UnsafeAction = []
    ListWords_UnsafeCondition = []
    ListWords_NearMiss = []
    ListWords_HNM = []
    ListWords_Accident = []

    Cluster_UnsafeAction = []
    Cluster_UnsafeCondition = []
    Cluster_NearMiss = []
    Cluster_HNM = []
    Cluster_Accident = []

    ListWords_LOTO = []
    ListWords_WAH = []
    ListWords_Scaffolding = []
    ListWords_Transportation = []
    ListWords_PTW_JSA = []
    ListWords_ProcessOperation = []
    ListWords_Radiation = []
    ListWords_Others = []
    ListWords_Lifting = []
    ListWords_Housekeeping = []
    ListWords_ToolsEquipment = []
    ListWords_HotWork = []
    ListWords_Excavation = []
    ListWords_CSE = []
    ListWords_ElectricalGrounding = []
    ListWords_PaintCoatBlast = []
    ListWords_ChemicalWork = []
    ListWords_SafetyManagement = []
    ListWords_PPE = []
    ListWords_WaterJet = []
    ListWords_PressureTest = []
    ListWords_SLPerformance = []
    ListWords_WorkProcedure = []
    ListWords_Civil = []
    ListWords_Insulation = []
    ListWords_Environmental = []
    ListWords_InstallationAlignment = []
    ListWords_Security = []

    Cluster_LOTO = []
    Cluster_WAH = []
    Cluster_Scaffolding = []
    Cluster_Transportaion = []
    Cluster_PTWJSA = []
    Cluster_ProcessOperation = []
    Cluster_Radiation = []
    Cluster_Others = []
    Cluster_Lifting = []
    Cluster_Housekeeping = []
    Cluster_ToolsEquipment = []
    Cluster_HotWork = []
    Cluster_Excavation = []
    Cluster_CSE = []
    Cluster_ElectricalGrounding = []
    Cluster_PaintCoatBlast = []
    Cluster_ChemicalWork = []
    Cluster_SafetyManagement = []
    Cluster_PPE = []
    Cluster_WaterJet = []
    Cluster_PressureTest = []
    Cluster_SLPerformance = []
    Cluster_WorkProcedure = []
    Cluster_Civil = []
    Cluster_Insulation = []
    Cluster_Environmental = []
    Cluster_InstallationAlignment = []
    Cluster_Security = []
    TotalData = pd.read_csv('./SMIT_Data/TotalData.csv', encoding='utf-8')

    LatestDate = TotalData['LatestDate'].tolist()[0]
    # try:
    Query = '''
                SELECT (CAST([dbo].[LOG_Finding].[ID] AS int)),
                    [dbo].[LOG_Finding].[ID],
                    [dbo].[LOG_Finding].[Area],
                    [dbo].[LOG_Finding].[Finding],
                    [dbo].[LOG_Permit].[Detail],
                    [dbo].[LOG_Finding].[AuditResult]
                FROM [dbo].[LOG_Finding]
                JOIN [dbo].[LOG_Permit]
                ON   [dbo].[LOG_Finding].[Title] = [dbo].[LOG_Permit].[Title]
                WHERE [dbo].[LOG_Finding].ID > 113   AND [dbo].[LOG_Finding].ID != 131  AND [dbo].[LOG_Finding].ID != 5057 AND 
                    [dbo].[LOG_Finding].ID != 5058 AND [dbo].[LOG_Finding].ID != 190  AND [dbo].[LOG_Finding].ID != 1483 AND 
                    [dbo].[LOG_Finding].ID != 1486 AND [dbo].[LOG_Finding].ID != 1974 AND [dbo].[LOG_Finding].ID != 132  AND 
                    (AuditResult = 'Need to Improve' or AuditResult = 'Non-conform')  AND [dbo].[LOG_Permit].[Detail] != '' 
                    AND Corrective != '' AND [dbo].[LOG_Finding].[Created] > '''

    tbFinding = pd.read_sql(Query+"'"+str(LatestDate)+"'", connection_SafetyAudit)
    # tbFinding = pd.read_sql(Query, connection_SafetyAudit)
    if len(tbFinding) > 0:
        try:
            tbFindingArea = tbFinding['Area'].tolist()
            tbFindingSubArea = []
            tbFindingContractor = []
            tbFindingTof = []
            tbFindingTopic = []
            tbFindingDetail = tbFinding['Detail'].tolist()
            tbFindingTranslateDetail = []
            tbFindingAuditResult = tbFinding["AuditResult"].tolist()
            tbFindingFinding = tbFinding["Finding"].tolist()
            tbFindingTranslateFinding = []
                
            SafetyAudit = pd.read_csv("./SMIT_Data/AllRawSafetyAudit_New.csv", encoding='utf-8')
            IndexError = []

            for i in range(len(tbFindingFinding)):
                try:
                    tbFindingTranslateFinding.append(GoogleTranslator(source = 'auto', target = 'en').translate(tbFindingFinding[i]))
                except:
                    tbFindingArea.pop(i)
                    tbFindingDetail.pop(i)
                    tbFindingAuditResult.pop(i)
                    IndexError.append(i)

            for i in IndexError:
                tbFindingFinding.pop(i)

            IndexError = []

            for i in range(len(tbFindingDetail)):
                try:
                    tbFindingTranslateDetail.append(GoogleTranslator(source = 'auto', target = 'en').translate(tbFindingDetail[i]))
                except:
                    tbFindingArea.pop(i)
                    tbFindingFinding.pop(i)
                    tbFindingAuditResult.pop(i)
                    IndexError.append(i)

            for i in IndexError:
                tbFindingDetail.pop(i)

            # ------------------ Prepared Cluster : Unsafe Action ------------------
            ENData_UnsafeAction = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Unsafe Action", "TransCleansingDetails"]).tolist()
            THData_UnsafeAction = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Unsafe Action", "CleansingDetails"]).tolist()
            Data_UnsafeAction = ' '.join(ENData_UnsafeAction+THData_UnsafeAction)

            ListWords_UnsafeAction = list(set(word_tokenize(Data_UnsafeAction, custom_dict = trie, engine = 'newmm')))

            # ------------------ Prepared Cluster : Unsafe Condition ------------------

            ENData_UnsafeCondition = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Unsafe Condition", "TransCleansingDetails"]).tolist()
            THData_UnsafeCondition = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Unsafe Condition", "CleansingDetails"]).tolist()
            Data_UnsafeCondition = ' '.join(ENData_UnsafeCondition+THData_UnsafeCondition)

            ListWords_UnsafeCondition = list(set(word_tokenize(Data_UnsafeCondition, custom_dict = trie, engine = 'newmm')))

            # ------------------ Prepared Cluster : Near Miss ------------------

            ENData_NearMiss = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Near Miss", "TransCleansingDetails"]).tolist()
            THData_NearMiss = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Near Miss", "CleansingDetails"]).tolist()
            Data_NearMiss = ' '.join(ENData_NearMiss+THData_NearMiss)

            ListWords_NearMiss = list(set(word_tokenize(Data_NearMiss, custom_dict = trie, engine = 'newmm')))

            # ------------------ Prepared Cluster : HNM ------------------

            ENData_HNM = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "HNM", "TransCleansingDetails"]).tolist()
            THData_HNM = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "HNM", "CleansingDetails"]).tolist()
            Data_HNM = ' '.join(ENData_HNM+THData_HNM)

            ListWords_HNM = list(set(word_tokenize(Data_HNM, custom_dict = trie, engine='newmm')))

            # ------------------ Prepared Cluster : Accident ------------------
            ENData_Accident = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Accident", "TransCleansingDetails"]).tolist() 
            THData_Accident = (SafetyAudit.loc[SafetyAudit["TypeOfFinding"] == "Accident", "CleansingDetails"]).tolist() 
            Data_Accident = ' '.join(ENData_Accident+THData_Accident) 

            ListWords_Accident = list(set(word_tokenize(Data_Accident, custom_dict = trie, engine='newmm')))

            ENData_LOTO = (SafetyAudit.loc[SafetyAudit["Topic"] == "LOTO/ LB", "TransCleansingDetails"]).tolist()
            THData_LOTO = (SafetyAudit.loc[SafetyAudit["Topic"] == "LOTO/ LB", "CleansingDetails"]).tolist()
            Data_LOTO = ' '.join(ENData_LOTO+THData_LOTO)

            ListWords_LOTO = list(set(word_tokenize(Data_LOTO, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Work at height ------------------

            ENData_WAH = (SafetyAudit.loc[SafetyAudit["Topic"] == "Work at height", "TransCleansingDetails"]).tolist()
            THData_WAH = (SafetyAudit.loc[SafetyAudit["Topic"] == "Work at height", "CleansingDetails"]).tolist()
            Data_WAH = ' '.join(ENData_WAH+THData_WAH)

            ListWords_WAH = list(set(word_tokenize(Data_WAH, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Scaffolding ------------------

            ENData_Scaffolding = (SafetyAudit.loc[SafetyAudit["Topic"] == "Scaffolding", "TransCleansingDetails"]).tolist()
            THData_Scaffolding = (SafetyAudit.loc[SafetyAudit["Topic"] == "Scaffolding", "CleansingDetails"]).tolist()
            Data_Scaffolding = ' '.join(ENData_Scaffolding+THData_Scaffolding) 

            ListWords_Scaffolding = list(set(word_tokenize(Data_Scaffolding, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Transportation ------------------

            ENData_Transportation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Transportation", "TransCleansingDetails"]).tolist()
            THData_Transportation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Transportation", "CleansingDetails"]).tolist()
            Data_Transportation = ' '.join(ENData_Transportation+THData_Transportation)

            ListWords_Transportation = list(set(word_tokenize(Data_Transportation, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : PTW & JSA ------------------
            ENData_PTW_JSA = (SafetyAudit.loc[SafetyAudit["Topic"] == "PTW & JSA", "TransCleansingDetails"]).tolist() 
            THData_PTW_JSA = (SafetyAudit.loc[SafetyAudit["Topic"] == "PTW & JSA", "CleansingDetails"]).tolist() 
            Data_PTW_JSA = ' '.join(ENData_PTW_JSA+THData_PTW_JSA) 

            ListWords_PTW_JSA = list(set(word_tokenize(Data_PTW_JSA, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Process & Operation ------------------
            ENData_ProcessOperation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Process & Operation", "TransCleansingDetails"]).tolist() 
            THData_ProcessOperation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Process & Operation", "CleansingDetails"]).tolist() 
            Data_ProcessOperation = ' '.join(ENData_ProcessOperation+THData_ProcessOperation)    

            ListWords_ProcessOperation = list(set(word_tokenize(Data_ProcessOperation, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Radiation ------------------
            ENData_Radiation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Radiation", "TransCleansingDetails"]).tolist() 
            THData_Radiation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Radiation", "CleansingDetails"]).tolist() 
            Data_Radiation = ' '.join(ENData_Radiation+THData_Radiation)  

            ListWords_Radiation = list(set(word_tokenize(Data_Radiation, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Radiation ------------------
            ENData_Others = (SafetyAudit.loc[SafetyAudit["Topic"] == "Others", "TransCleansingDetails"]).tolist() 
            THData_Others = (SafetyAudit.loc[SafetyAudit["Topic"] == "Others", "CleansingDetails"]).tolist() 
            Data_Others = ' '.join(ENData_Others+THData_Others)  

            ListWords_Others = list(set(word_tokenize(Data_Others, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Lifting ------------------
            ENData_Lifting = (SafetyAudit.loc[SafetyAudit["Topic"] == "Lifting", "TransCleansingDetails"]).tolist() 
            THData_Lifting = (SafetyAudit.loc[SafetyAudit["Topic"] == "Lifting", "CleansingDetails"]).tolist() 
            Data_Lifting = ' '.join(ENData_Lifting+THData_Lifting) 

            ListWords_Lifting = list(set(word_tokenize(Data_Lifting, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Housekeeping ------------------
            ENData_Housekeeping = (SafetyAudit.loc[SafetyAudit["Topic"] == "Housekeeping", "TransCleansingDetails"]).tolist() 
            THData_Housekeeping = (SafetyAudit.loc[SafetyAudit["Topic"] == "Housekeeping", "CleansingDetails"]).tolist() 
            Data_Housekeeping = ' '.join(ENData_Housekeeping+THData_Housekeeping)  

            ListWords_Housekeeping = list(set(word_tokenize(Data_Housekeeping, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Tools & Equipment ------------------
            ENData_ToolsEquipment = (SafetyAudit.loc[SafetyAudit["Topic"] == "Tools & Equipment", "TransCleansingDetails"]).tolist() 
            THData_ToolsEquipment = (SafetyAudit.loc[SafetyAudit["Topic"] == "Tools & Equipment", "CleansingDetails"]).tolist() 
            Data_ToolsEquipment = ' '.join(ENData_ToolsEquipment+THData_ToolsEquipment)  

            ListWords_ToolsEquipment = list(set(word_tokenize(Data_ToolsEquipment, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Hot Work ------------------
            ENData_HotWork = (SafetyAudit.loc[SafetyAudit["Topic"] == "Hot Work", "TransCleansingDetails"]).tolist() 
            THData_HotWork = (SafetyAudit.loc[SafetyAudit["Topic"] == "Hot Work", "CleansingDetails"]).tolist() 
            Data_HotWork = ' '.join(ENData_HotWork+THData_HotWork) 

            ListWords_HotWork = list(set(word_tokenize(Data_HotWork, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Excavation ------------------
            ENData_Excavation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Excavation", "TransCleansingDetails"]).tolist() 
            THData_Excavation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Excavation", "CleansingDetails"]).tolist() 
            Data_Excavation = ' '.join(ENData_Excavation+THData_Excavation) 

            ListWords_Excavation = list(set(word_tokenize(Data_Excavation, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : CSE ------------------
            ENData_CSE = (SafetyAudit.loc[SafetyAudit["Topic"] == "CSE", "TransCleansingDetails"]).tolist() 
            THData_CSE = (SafetyAudit.loc[SafetyAudit["Topic"] == "CSE", "CleansingDetails"]).tolist() 
            Data_CSE = ' '.join(ENData_CSE+THData_CSE) 

            ListWords_CSE = list(set(word_tokenize(Data_CSE, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Electrical & Grounding ------------------
            ENData_ElectricalGrounding = (SafetyAudit.loc[SafetyAudit["Topic"] == "Electrical & Grounding", "TransCleansingDetails"]).tolist() 
            THData_ElectricalGrounding = (SafetyAudit.loc[SafetyAudit["Topic"] == "Electrical & Grounding", "CleansingDetails"]).tolist() 
            Data_ElectricalGrounding = ' '.join(ENData_ElectricalGrounding+THData_ElectricalGrounding) 

            ListWords_ElectricalGrounding = list(set(word_tokenize(Data_ElectricalGrounding, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Paint/ Coat/ Blast ------------------
            ENData_PaintCoatBlast = (SafetyAudit.loc[SafetyAudit["Topic"] == "Paint/ Coat/ Blast", "TransCleansingDetails"]).tolist() 
            THData_PaintCoatBlast = (SafetyAudit.loc[SafetyAudit["Topic"] == "Paint/ Coat/ Blast", "CleansingDetails"]).tolist() 
            Data_PaintCoatBlast = ' '.join(ENData_PaintCoatBlast+THData_PaintCoatBlast) 

            ListWords_PaintCoatBlast = list(set(word_tokenize(Data_PaintCoatBlast, custom_dict=trie, engine='newmm'))) 

            # ------------------ Prepared Cluster : Chemical Work ------------------
            ENData_ChemicalWork = (SafetyAudit.loc[SafetyAudit["Topic"] == "Chemical Work", "TransCleansingDetails"]).tolist() 
            THData_ChemicalWork = (SafetyAudit.loc[SafetyAudit["Topic"] == "Chemical Work", "CleansingDetails"]).tolist() 
            Data_ChemicalWork = ' '.join(ENData_ChemicalWork+THData_ChemicalWork) 

            ListWords_ChemicalWork = list(set(word_tokenize(Data_ChemicalWork, custom_dict=trie, engine='newmm'))) 

            # ------------------ Prepared Cluster : Safety Management ------------------
            ENData_SafetyManagement = (SafetyAudit.loc[SafetyAudit["Topic"] == "Safety Management", "TransCleansingDetails"]).tolist() 
            THData_SafetyManagement = (SafetyAudit.loc[SafetyAudit["Topic"] == "Safety Management", "CleansingDetails"]).tolist() 
            Data_SafetyManagement = ' '.join(ENData_SafetyManagement+THData_SafetyManagement) 

            ListWords_SafetyManagement = list(set(word_tokenize(Data_SafetyManagement, custom_dict=trie, engine='newmm'))) 

            # ------------------ Prepared Cluster : PPE ------------------
            ENData_PPE = (SafetyAudit.loc[SafetyAudit["Topic"] == "PPE", "TransCleansingDetails"]).tolist() 
            THData_PPE = (SafetyAudit.loc[SafetyAudit["Topic"] == "PPE", "CleansingDetails"]).tolist() 
            Data_PPE = ' '.join(ENData_PPE+THData_PPE) 

            ListWords_PPE = list(set(word_tokenize(Data_PPE, custom_dict = trie, engine='newmm'))) 

            # ------------------ Prepared Cluster : Water jet ------------------
            ENData_WaterJet = (SafetyAudit.loc[SafetyAudit["Topic"] == "Water jet", "TransCleansingDetails"]).tolist() 
            THData_WaterJet = (SafetyAudit.loc[SafetyAudit["Topic"] == "Water jet", "CleansingDetails"]).tolist() 
            Data_WaterJet = ' '.join(ENData_WaterJet+THData_WaterJet) 

            ListWords_WaterJet = list(set(word_tokenize(Data_WaterJet, custom_dict=trie, engine='newmm'))) 

            # ------------------ Prepared Cluster : Pressure test ------------------
            ENData_PressureTest = (SafetyAudit.loc[SafetyAudit["Topic"] == "Pressure test", "TransCleansingDetails"]).tolist() 
            THData_PressureTest = (SafetyAudit.loc[SafetyAudit["Topic"] == "Pressure test", "CleansingDetails"]).tolist() 
            Data_PressureTest = ' '.join(ENData_PressureTest+THData_PressureTest) 

            ListWords_PressureTest = list(set(word_tokenize(Data_PressureTest, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : SL Performance ------------------
            ENData_SLPerformance = (SafetyAudit.loc[SafetyAudit["Topic"] == "SL Performance", "TransCleansingDetails"]).tolist() 
            THData_SLPerformance = (SafetyAudit.loc[SafetyAudit["Topic"] == "SL Performance", "CleansingDetails"]).tolist() 
            Data_SLPerformance = ' '.join(ENData_SLPerformance+THData_SLPerformance) 

            ListWords_SLPerformance = list(set(word_tokenize(Data_SLPerformance, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Work Procedure ------------------
            ENData_WorkProcedure = (SafetyAudit.loc[SafetyAudit["Topic"] == "Work Procedure", "TransCleansingDetails"]).tolist() 
            THData_WorkProcedure = (SafetyAudit.loc[SafetyAudit["Topic"] == "Work Procedure", "CleansingDetails"]).tolist() 
            Data_WorkProcedure = ' '.join(ENData_WorkProcedure+THData_WorkProcedure) 

            ListWords_WorkProcedure = list(set(word_tokenize(Data_WorkProcedure, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Civil ------------------
            ENData_Civil = (SafetyAudit.loc[SafetyAudit["Topic"] == "Civil", "TransCleansingDetails"]).tolist() 
            THData_Civil = (SafetyAudit.loc[SafetyAudit["Topic"] == "Civil", "CleansingDetails"]).tolist() 
            Data_Civil = ' '.join(ENData_Civil+THData_Civil) 

            ListWords_Civil = list(set(word_tokenize(Data_Civil, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Insulation ------------------
            ENData_Insulation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Insulation", "TransCleansingDetails"]).tolist() 
            THData_Insulation = (SafetyAudit.loc[SafetyAudit["Topic"] == "Insulation", "CleansingDetails"]).tolist() 
            Data_Insulation = ' '.join(ENData_Insulation+THData_Insulation) 

            ListWords_Insulation = list(set(word_tokenize(Data_Insulation, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Environmental ------------------
            ENData_Environmental = (SafetyAudit.loc[SafetyAudit["Topic"] == "Environmental", "TransCleansingDetails"]).tolist() 
            THData_Environmental = (SafetyAudit.loc[SafetyAudit["Topic"] == "Environmental", "CleansingDetails"]).tolist() 
            Data_Environmental = ' '.join(ENData_Environmental+THData_Environmental) 

            ListWords_Environmental = list(set(word_tokenize(Data_Environmental, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Installation/ Alignment ------------------
            ENData_InstallationAlignment = (SafetyAudit.loc[SafetyAudit["Topic"] == "Installation/ Alignment", "TransCleansingDetails"]).tolist() 
            THData_InstallationAlignment = (SafetyAudit.loc[SafetyAudit["Topic"] == "Installation/ Alignment", "CleansingDetails"]).tolist() 
            Data_InstallationAlignment = ' '.join(ENData_InstallationAlignment+THData_InstallationAlignment) 

            ListWords_InstallationAlignment = list(set(word_tokenize(Data_InstallationAlignment, custom_dict=trie, engine='newmm')))

            # ------------------ Prepared Cluster : Installation/ Alignment ------------------
            ENData_Security = (SafetyAudit.loc[SafetyAudit["Topic"] == "Security", "TransCleansingDetails"]).tolist() 
            THData_Security = (SafetyAudit.loc[SafetyAudit["Topic"] == "Security", "CleansingDetails"]).tolist() 
            Data_Security = ' '.join(ENData_Security+THData_Security) 

            ListWords_Security = list(set(word_tokenize(Data_Security, custom_dict=trie, engine='newmm')))

            for word in ListWords_UnsafeAction:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTypeOfFinding(word, ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident))
                Cluster_UnsafeAction.append(temp)

            for word in ListWords_UnsafeCondition:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTypeOfFinding(word, ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident))
                Cluster_UnsafeCondition.append(temp)

            for word in ListWords_NearMiss:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTypeOfFinding(word, ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident))
                Cluster_NearMiss.append(temp)

            for word in ListWords_HNM:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTypeOfFinding(word, ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident))
                Cluster_HNM.append(temp)

            for word in ListWords_Accident:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTypeOfFinding(word, ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident))
                Cluster_Accident.append(temp)

            for word in ListWords_LOTO:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_LOTO.append(temp)

            for word in ListWords_WAH:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_WAH.append(temp)

            for word in ListWords_Scaffolding:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Scaffolding.append(temp)

            for word in ListWords_Transportation:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Transportaion.append(temp)

            for word in ListWords_PTW_JSA:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_PTWJSA.append(temp)

            for word in ListWords_ProcessOperation:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_ProcessOperation.append(temp)

            for word in ListWords_Others:
                temp = []
                temp.append(word)
                temp.append( CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Others.append(temp)

            for word in ListWords_Lifting:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Lifting.append(temp)

            for word in ListWords_Housekeeping:
                temp = []
                temp.append(word)
                temp.append( CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Housekeeping.append(temp)

            for word in ListWords_ToolsEquipment:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_ToolsEquipment.append(temp)

            for word in ListWords_HotWork:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_HotWork.append(temp)

            for word in ListWords_Excavation:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Excavation.append(temp)

            for word in ListWords_CSE:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_CSE.append(temp)

            for word in ListWords_ElectricalGrounding:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_ElectricalGrounding.append(temp)

            for word in ListWords_PaintCoatBlast:
                temp = []
                temp.append(word)
                temp.append( CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_PaintCoatBlast.append(temp)

            for word in ListWords_ChemicalWork:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_ChemicalWork.append(temp)

            for word in ListWords_SafetyManagement:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_SafetyManagement.append(temp)

            for word in ListWords_PPE:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_PPE.append(temp)

            for word in ListWords_WaterJet:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_WaterJet.append(temp)

            for word in ListWords_PressureTest:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_PressureTest.append(temp)

            for word in ListWords_SLPerformance:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_SLPerformance.append(temp)

            for word in ListWords_WorkProcedure:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_WorkProcedure.append(temp)

            for word in ListWords_Civil:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Civil.append(temp)

            for word in ListWords_Insulation:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Insulation.append(temp)

            for word in ListWords_Environmental:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Environmental.append(temp)

            for word in ListWords_InstallationAlignment:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_InstallationAlignment.append(temp)

            for word in ListWords_Security:
                temp = []
                temp.append(word)
                temp.append(CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                                    ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                                    ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                                    ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                                    ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                                    ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security))
                Cluster_Security.append(temp)
            
            TotalData = pd.read_csv('./SMIT_Data/TotalData.csv', encoding='utf-8')

            TotalOldClassification_Finding = TotalData['Old'].tolist()[0]
            TotalLatestClassification_Finding = TotalData['Latest'].tolist()[0]

            TotalOldAllRecord = TotalData['Old'].tolist()[1]

            ClassifyTopic = []

            tbFindingNo = []
            tbFindingArea = tbFinding['Area'].tolist()
            tbFindingSubArea = []
            tbFindingContractor = []
            tbFindingTof = []
            tbFindingTopic = []
            tbFindingFinding = tbFinding['Finding'].tolist()

            for index in range(len(tbFindingArea)):
                DataFinding = word_tokenize(tbFindingFinding[index], custom_dict=trie, engine='newmm')
                DataDetails = word_tokenize(tbFindingDetail[index], custom_dict=trie, engine='newmm')
                Finding = "-"
                Topic = "-"
                TempMostSimTOF = 0
                TempMostSimTopic = 0
                MostSimTopic = -1
                MostSimTOF = -1

                if len(set([x.lower() for x in DataFinding]) & set([i[0] for i in Cluster_UnsafeAction])) > 3:
                    for i in (set([x.lower() for x in DataFinding])):
                        if i in ([j[0] for j in Cluster_UnsafeAction]):
                            TempMostSimTOF += Cluster_UnsafeAction[ListWords_UnsafeAction.index(i)][1]
                    if TempMostSimTOF > MostSimTOF:
                        MostSimTOF = TempMostSimTOF
                        Finding = "Unsafe Action"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataFinding]) & set([i[0] for i in Cluster_UnsafeCondition])) > 3:
                    for i in (set([x.lower() for x in DataFinding])):
                        if i in ([j[0] for j in Cluster_UnsafeCondition]):
                            TempMostSimTOF += Cluster_UnsafeCondition[ListWords_UnsafeCondition.index(i)][1]
                    if TempMostSimTOF > MostSimTOF:
                        MostSimTOF = TempMostSimTOF
                        Finding = "Unsafe Condition"
                        TempMostSimTOF = 0

                if len(set([x.lower() for x in DataFinding]) & set([i[0] for i in Cluster_NearMiss])) > 3:
                    for i in (set([x.lower() for x in DataFinding])):
                        if i in ([j[0] for j in Cluster_NearMiss]):
                            TempMostSimTOF += Cluster_NearMiss[ListWords_NearMiss.index(i)][1]
                    if TempMostSimTOF > MostSimTOF:
                        MostSimTOF = TempMostSimTOF
                        Finding = "Near Miss"
                        TempMostSimTOF = 0

                if len(set([x.lower() for x in DataFinding]) & set([i[0] for i in Cluster_HNM])) > 3:
                    for i in set([x.lower() for x in DataFinding]):
                        if i in [j[0] for j in Cluster_HNM]:
                            TempMostSimTOF += Cluster_HNM[ListWords_HNM.index(i)][1]
                    if TempMostSimTOF > MostSimTOF:
                        MostSimTOF = TempMostSimTOF
                        Finding = "HNM"
                        TempMostSimTOF = 0

                if len(set([x.lower() for x in DataFinding]) & set([i[0] for i in Cluster_Accident])) > 3:
                    for i in (set([x.lower() for x in DataFinding])):
                        if i in ([j[0] for j in Cluster_Accident]):
                            TempMostSimTOF += Cluster_Accident[ListWords_Accident.index(i)][1]
                    if TempMostSimTOF > MostSimTOF:
                        MostSimTOF = TempMostSimTOF
                        Finding = "Accident"
                        TempMostSimTOF = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_LOTO])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_LOTO]):
                            TempMostSimTopic += Cluster_LOTO[ListWords_LOTO.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "LOTO/ LB"
                        TempMostSimTopic = 0  
                
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_WAH])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_WAH]):
                            TempMostSimTopic += Cluster_WAH[ListWords_WAH.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Work at height"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Scaffolding])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Scaffolding]):
                            TempMostSimTopic += Cluster_Scaffolding[ListWords_Scaffolding.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Scaffolding"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Transportaion])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Transportaion]):
                            TempMostSimTopic += Cluster_Transportaion[ListWords_Transportation.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Transportation"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_PTWJSA])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_PTWJSA]):
                            TempMostSimTopic += Cluster_PTWJSA[ListWords_PTW_JSA.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "PTW & JSA"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_ProcessOperation])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_ProcessOperation]):
                            TempMostSimTopic += Cluster_ProcessOperation[ListWords_ProcessOperation.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Process & Operation"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Radiation])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Radiation]):
                            TempMostSimTopic += Cluster_Radiation[ListWords_Radiation.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Radiation"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Others])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Others]):
                            TempMostSimTopic += Cluster_Others[ListWords_Others.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Others"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Lifting])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Lifting]):
                            TempMostSimTopic += Cluster_Lifting[ListWords_Lifting.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Lifting"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Housekeeping])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Housekeeping]):
                            TempMostSimTopic += Cluster_Housekeeping[ListWords_Housekeeping.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Housekeeping"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_ToolsEquipment])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_ToolsEquipment]):
                            TempMostSimTopic += Cluster_ToolsEquipment[ListWords_ToolsEquipment.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Tools & Equipment"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_HotWork])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_HotWork]):
                            TempMostSimTopic += Cluster_HotWork[ListWords_HotWork.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Hot Work"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Excavation])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Excavation]):
                            TempMostSimTopic += Cluster_Excavation[ListWords_Excavation.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Excavation"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_CSE])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_CSE]):
                            TempMostSimTopic += Cluster_CSE[ListWords_CSE.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "CSE"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_ElectricalGrounding])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_ElectricalGrounding]):
                            TempMostSimTopic += Cluster_ElectricalGrounding[ListWords_ElectricalGrounding.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Electrical & Grounding"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_PaintCoatBlast])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_PaintCoatBlast]):
                            TempMostSimTopic += Cluster_PaintCoatBlast[ListWords_PaintCoatBlast.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Paint/ Coat/ Blast"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_ChemicalWork])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_ChemicalWork]):
                            TempMostSimTopic += Cluster_ChemicalWork[ListWords_ChemicalWork.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Chemical Work"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_SafetyManagement])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_SafetyManagement]):
                            TempMostSimTopic += Cluster_SafetyManagement[ListWords_SafetyManagement.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Safety Management"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_PPE])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_PPE]):
                            TempMostSimTopic += Cluster_PPE[ListWords_PPE.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "PPE"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_WaterJet])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_WaterJet]):
                            TempMostSimTopic += Cluster_WaterJet[ListWords_WaterJet.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Water jet"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_PressureTest])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_PressureTest]):
                            TempMostSimTopic += Cluster_PressureTest[ListWords_PressureTest.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Pressure test"
                        TempMostSimTopic = 0

                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_SLPerformance])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_SLPerformance]):
                            TempMostSimTopic += Cluster_SLPerformance[ListWords_SLPerformance.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "SL Performance"
                        TempMostSimTopic = 0
                        
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_WorkProcedure])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_WorkProcedure]):
                            TempMostSimTopic += Cluster_WorkProcedure[ListWords_WorkProcedure.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Work Procedure"
                        TempMostSimTopic = 0
                        
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Civil])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Civil]):
                            TempMostSimTopic += Cluster_Civil[ListWords_Civil.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Civil"
                        TempMostSimTopic = 0
                        
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Insulation])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Insulation]):
                            TempMostSimTopic += Cluster_Insulation[ListWords_Insulation.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Insulation"
                        TempMostSimTopic = 0
                                    
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Environmental])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Environmental]):
                            TempMostSimTopic += Cluster_Environmental[ListWords_Environmental.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Environmental"
                        TempMostSimTopic = 0
                                    
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_InstallationAlignment])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_InstallationAlignment]):
                            TempMostSimTopic += Cluster_InstallationAlignment[ListWords_InstallationAlignment.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Installation/ Alignment"
                        TempMostSimTopic = 0
                                    
                if len(set([x.lower() for x in DataDetails]) & set([i[0] for i in Cluster_Security])) > 3:
                    for i in (set([x.lower() for x in DataDetails])):
                        if i in ([j[0] for j in Cluster_Security]):
                            TempMostSimTopic += Cluster_Security[ListWords_Security.index(i)][1]
                    if TempMostSimTopic > MostSimTopic:
                        MostSimTopic = TempMostSimTopic
                        Topic = "Security"
                        TempMostSimTopic = 0

                tbFindingNo.append(str(TotalOldClassification_Finding+index+1)) 
                # tbFindingNo.append(index+1)
                tbFindingSubArea.append('-')  
                tbFindingContractor.append('-')     
                tbFindingTof.append(Finding)
                tbFindingTopic.append(Topic)

            Classification_TbFinding = list(zip(tbFindingNo, tbFindingArea, tbFindingSubArea, 
                                                tbFindingContractor, tbFindingTof, tbFindingTopic, 
                                                tbFindingDetail, tbFindingTranslateDetail, tbFindingFinding, tbFindingTranslateFinding))

            cursor = connection_SMIT3.cursor()
            Query = "INSERT INTO [Classification_TbFinding] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

            cursor.executemany(Query, Classification_TbFinding)

            connection_SMIT3.commit()

            Query = 'SELECT MAX([dbo].[LOG_Finding].[Created]) FROM [dbo].[LOG_Finding]'

            GetLatestDate = pd.read_sql(Query, connection_SafetyAudit)

            GetLatestDate = GetLatestDate[""].tolist()[0]

            Head = ['Source', 'LatestDate', 'Old', 'Latest']

            Old_Size = len(tbFindingFinding)

            UpdateSize = [
                            ['Classfication_TbFinding', GetLatestDate, TotalOldClassification_Finding, int(TotalLatestClassification_Finding)+Old_Size],
                            ['All Record', '-', int(TotalOldAllRecord), '-']
                        ] 

            with open('./SMIT_Data/TotalData.csv', 'w', newline='', encoding="utf-8") as f:
                write = csv.writer(f)
                write.writerow(Head)
                write.writerows(UpdateSize)

            print("[Finished Classification tbFinding]...")

            return Cleansing_FindingDetails()
        except:
            return "There is an Error SQL Connection failure"
    else:
        return "Record is up to date", 200

