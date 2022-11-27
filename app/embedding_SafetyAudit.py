import pickle # to load pickle from embed all ii file 
import numpy as np
from sentence_transformers import SentenceTransformer, util
import pandas as pd

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

Encode_Safey_Audit_Details = model.encode(SA_Details_Trans)
Encode_Safey_Audit_Details = np.array(Encode_Safey_Audit_Details)

with open('./SMIT_Data/Encode_SafeyAudit.pkl', 'wb') as files:
    pickle.dump(Encode_Safey_Audit_Details, files)
