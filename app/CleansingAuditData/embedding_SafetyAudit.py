import pickle
import numpy as np
from sentence_transformers import SentenceTransformer, util
import pandas as pd

modelPath = "./Model/SentenceTransformer"

model = SentenceTransformer(modelPath)

def embedding_SafetyAudit():
    try:
        SafetyAudit = pd.read_csv('./SMIT_Data/Prepared_Safety_Audit.csv', encoding='utf-8')
        SA_Finding = SafetyAudit['Finding'].tolist()
        SA_Area = SafetyAudit['Area'].tolist()
        SA_Contractor = SafetyAudit['Contractor'].tolist()
        SA_Tof = SafetyAudit['TypeOfFinding'].tolist()
        SA_Topic = SafetyAudit['Topic'].tolist()
        SA_Frequency = SafetyAudit['Frequency'].tolist()
        SA_Finding_Trans = SafetyAudit['TranslateFinding'].tolist()
        # SA_Details_Trans = SafetyAudit['TranslateDetails'].tolist()

        # Encode_Safey_Audit_Details = model.encode(SA_Details_Trans)
        # Encode_Safey_Audit_Details = np.array(Encode_Safey_Audit_Details)

        Encode_Safety_Audit_Finding = model.encode(SA_Finding_Trans)
        Encode_Safety_Audit_Finding = np.array(Encode_Safety_Audit_Finding)
        
        # with open('./SMIT_Data/Encode_Details.pkl', 'wb') as files:
        #     pickle.dump(Encode_Safey_Audit_Details, files)
        
        with open('./SMIT_Data/Encode_SafeyAudit.pkl', 'wb') as files:
            pickle.dump(Encode_Safety_Audit_Finding, files)

        return "Prepared audit data success!", 200
    except:
        return "Don't have newer data or There is an error", 400

# embedding_SafetyAudit()
