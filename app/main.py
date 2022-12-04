from sqlite3 import Row
from cryptography.fernet import Fernet
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel
import secrets
from typing import List
import uvicorn
# from ii_func.ii import *
# from Function import *

from .ii_func.ii import *
from .Function import *

app = FastAPI(title="SMIT API",
                debug=True,
                version="0.0.1")

class Input_WPM_Details(BaseModel):
  Detail : List[str]
  Area : str
  Coworker : str
  Collected_Input: str

class input_api(BaseModel):
  name : str
  tag_equip : str
  area : str
  tool : str
  company : str
  correct : bool

class FindingScore(BaseModel):
  UnsafeAction: float
  UnsafeCondition: float
  NearMiss: float
  HNM: float
  Accident: float

class Form_Response_SafetyAudit(BaseModel):
  Safety_Audit_Details : List[str]
  Safety_Audit_Frequency : List[int]
  Safety_Audit_Contractor : List[str]
  Safety_Audit_Type_Of_Finding : List[str]
  Safety_Audit_Area : List[str]
  Safety_Audit_Topic : List[str]
  CA : List[str]
  PA : List[str]
  Risk_Score : FindingScore

class Response_SafetyAudit(BaseModel):
  case_1 : Form_Response_SafetyAudit
  case_2 : Form_Response_SafetyAudit

class Response_SpellChecker(BaseModel):
  Collected_Input : str
  Result : List[str]

class WPM_Details(BaseModel):
  WorkPermitDetails : str
  Case : int

class Template_Audit(BaseModel):
  Index : List[int]
  Safety_Audit_Details : List[str]
  Count : List[int]
  Area : List[str]
  Contractor : List[str]
  Type_Of_Finding : List[str]
  Topic : List[str]
  Result : List[str]
  Problems : List[str]
  Solution : List[str]

class All_Audit(BaseModel):
  Index : int
  Safety_Audit_Details : str
  Count : int
  Area : str
  Contractor : str
  Type_Of_Finding : str
  Topic : str
  Result : str
  Problems : str
  Solution : str
  Date : str

class Get_WPM_Detail(BaseModel):
  DocID : str

class NewFindingDetails(BaseModel):
  No : List[int]
  Company : List[str]
  Area : List[str]
  SubArea : List[str]
  Reportor : List[str]
  Contractor : List[str]
  TypeOfFinding : List[str]
  Topic : List[str]
  Details : List[str]
  CorrectiveAction : List[str]
  IssueDate : List[str]
  DueDate : List[str]
  Status : List[str] 

class case_Prop_search_engine_ii(BaseModel):
  id : int
  ii_incidentName : List[str]
  ii_incidentDetail : List[str]
  ii_incidentCause : List[str]
  ii_capa_incidentCauseType : List[List[str]]
  ii_capa_incidentCauseName : List[List[str]]
  ii_ca : List[str]
  ii_pa : List[str]
  ii_humanImpact : List[str]
  ii_propertyImpact : List[str]
  ii_environmentImpact : List[str]
  ii_classification : List[str]
  ii_incidentType : List[str]
  sim_score : List[float]

class Prop_search_engine_ii(BaseModel):
  ii_count : List[float]
  ii_count_real : List[int]
  case : List[case_Prop_search_engine_ii]
  relate : case_Prop_search_engine_ii

class relate_Prop_search_engine_ii(BaseModel):
  case : List[case_Prop_search_engine_ii]

class most_similar_ii(BaseModel):
  type_acc : str
  case : List[case_Prop_search_engine_ii] 

class search_engine_ii(BaseModel):
  find_count : List[float]
  risk_score : List[float]
  most_similar : most_similar_ii
  nm : Prop_search_engine_ii
  hnm : Prop_search_engine_ii
  lv1 : Prop_search_engine_ii
  lv2 : Prop_search_engine_ii
  lv3 : Prop_search_engine_ii

# Get BasicAuth Username & Password
f = open('./Authentication/userAuthen.json')
data = json.load(f)

def API_Status():
  return "API is still maintenance", 400  

security = HTTPBasic()

def BasicAuth(credentials: HTTPBasicCredentials = Depends(security)):
    key = Fernet.generate_key()
    fernet = Fernet(key)

    current_username_bytes = credentials.username.encode("utf8")
    current_password_bytes = credentials.password.encode("utf8")

    encrypt_username_bytes = fernet.encrypt(current_username_bytes)
    encrypt_password_bytes = fernet.encrypt(current_password_bytes)

    decrypt_username_bytes = fernet.decrypt(encrypt_username_bytes).decode()
    decrypt_password_bytes = fernet.decrypt(encrypt_password_bytes).decode()

    is_correct_username = secrets.compare_digest(
        decrypt_username_bytes, data['Username']
    )

    is_correct_password = secrets.compare_digest(
        decrypt_password_bytes, data['Password']
    )

    if not (is_correct_username and is_correct_password):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Basic Auth can't Authorize",
        headers={"WWW-Authenticate": "Basic"},
      )
    return True

@app.get('/') 
def Hello(auth: str = Depends(BasicAuth)):
    if auth == True:
      return "Welcome to SMIT3.0 API"

@app.post('/WPMDetails', status_code=status.HTTP_200_OK, response_model=Form_Response_SafetyAudit)
async def Suggest_Safety_Audit(request: Input_WPM_Details, auth: str = Depends(BasicAuth)):
  if auth == True:
    data = request.json()
    data = json.loads(data)

    Input_Details = data['Detail']
    Input_Location = data['Area']
    Input_Coworker = data['Coworker']
    Collected_Input = data['Collected_Input']

    Data_Contractor_1, Data_Area_1, Data_Tof_1, Data_Details_1, Data_Details_Trans_1, Data_Topic_1, Data_Frequency_1 = Search_Safety_Audit(1, Input_Location, Input_Coworker)
    Suggestion_Safety_Audit_1 = Compare_Cosine_Similarity(1, Data_Details_1, Data_Details_Trans_1, Collected_Input, Input_Details, Data_Frequency_1, Data_Contractor_1, Data_Tof_1, Data_Area_1, Data_Topic_1)

    Data_Contractor_2, Data_Area_2, Data_Tof_2, Data_Details_2, Data_Details_Trans_2, Data_Topic_2, Data_Frequency_2 = Search_Safety_Audit(2, Input_Location, Input_Coworker)
    Suggestion_Safety_Audit_2 = Compare_Cosine_Similarity(2, Data_Details_2, Data_Details_Trans_2, Collected_Input, Input_Details, Data_Frequency_2, Data_Contractor_2, Data_Tof_2, Data_Area_2, Data_Topic_2)
    result = {'case_1': Suggestion_Safety_Audit_1, 'case_2': Suggestion_Safety_Audit_2}
    return JSONResponse(result)

@app.post('/SpellCheck', status_code=status.HTTP_200_OK, response_model=Response_SpellChecker)
async def Corrected_input(request: WPM_Details, auth: str = Depends(BasicAuth)):
  if auth == True:
      data = request.json()
      data = json.loads(data)
      Input_Details = data['WorkPermitDetails']
      Cleansing_Case = data['Case']
      ResponseSpellCheck = Cleansing_Input(Input_Details, Cleansing_Case)
      return JSONResponse(ResponseSpellCheck)

@app.post("/ii", status_code=status.HTTP_200_OK ,response_model= search_engine_ii)
async def ii_api(request: input_api, auth: str = Depends(BasicAuth)):
  if auth == True:
    data = request.json() # change input(request model) to Json
    data = json.loads(data) # change Json to Dict
    if data is not None:
        form_ii = search_ii(data, "All ii")  # call function search_ii
        return JSONResponse(form_ii) # change Dict to Json in response
    else:
        return {
             "Please pass a properly formatted JSON object to the API"
        }  

@app.get('/PreparedAuditData', status_code=status.HTTP_200_OK)
async def Corrected_input(auth: str = Depends(BasicAuth)):
  if auth == True:
    return CleansingAuditData()

# if __name__ == '__main__':
#   uvicorn.run("main:app", host='0.0.0.0', port=443, reload=True, debug=True)