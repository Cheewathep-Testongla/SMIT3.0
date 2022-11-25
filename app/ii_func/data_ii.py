from sentence_transformers import SentenceTransformer
import pandas as pd

from ..connect_db import con

model_url = 'sentence-transformers_msmarco-distilbert-base-dot-prod-v3' # folder model
model_ii = SentenceTransformer(model_url) # load model
# --- SQL query command ---------------------
query = "SELECT * FROM [dbo].[II_cleanData];"
df_case = pd.read_sql(query, con)
# ---------------stored data in numpy ----------------------------
case_DocNo = df_case['DocNo'].to_numpy()
case_capa_IINO = df_case['IINo'].to_numpy()
case_IncidentCat = df_case['IncidentCategory'].to_numpy()
case_Incidentlevel = df_case['Severity'].to_numpy()
case_name = df_case['IncidentName'].to_numpy()
case_detail = df_case['IncidentDetail'].to_numpy()
case_cause = df_case['Cause'].to_numpy()
case_human = df_case['HumanImpact'].to_numpy()
case_prop = df_case['PropertyImpact'].to_numpy()
case_env = df_case['EnvironmentImpact'].to_numpy()
case_date_Y = df_case['Y'].to_numpy()
# change Y data to int [user to detect error in excel file when Y = null (present: in database don't found this problem)]
for i in range(len(case_date_Y)):
    case_date_Y[i] = int(float(case_date_Y[i]))
case_classification = df_case['IncidentClassification'].to_numpy()
case_companyLo = df_case['LocationCompanyName'].to_numpy()
case_IncidentType = df_case['IncidentType'].to_numpy()
# removing duplicate IncidentClassification (count to calculate statistic in weight of classification type (fire/explotion = 1))
count_unique_classification = list(set(case_classification))
# removing duplicate Y (count to calculate statistic (find all accident in each year))
count_unique_Y = list(set(case_date_Y))
# sort smallest to maximum (eg. 2543,...,2564)
count_unique_Y.sort()

from ..connect_db import con # connecting to db
# ------- SQL query command (CAPA data)--------------
query = "SELECT * FROM capa_Data"
df_capa = pd.read_sql(query, con)
# -----------------------------------------
capa_IINO = df_capa['IINo'].to_numpy()
capa_LLNO = df_capa['LLNo'].to_numpy()
capa_CauseName = df_capa['CauseName'].to_numpy()
capa_CauseType = df_capa['CauseType'].to_numpy()
capa_CAPAName = df_capa['CAPAName'].to_numpy()
capa_CAPAType = df_capa['CAPAType'].to_numpy()

# --------- ii data --------------------------
case_name_en = df_case['IncidentName_en'].to_numpy()
case_detail_en = df_case['IncidentDetail_en'].to_numpy()
case_cause_en = df_case['Cause_en'].to_numpy()

case_name_display = df_case['IncidentName_display'].to_numpy()
case_detail_display = df_case['IncidentDetail_display'].to_numpy()
case_cause_display = df_case['Cause_display'].to_numpy()
