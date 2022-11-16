from sqlite3 import Row
from cryptography.fernet import Fernet
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from .Function import *
import json
import uvicorn
from pydantic import BaseModel
import secrets
from typing import List, Tuple

# from smit_create_dict import Start_API

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app = FastAPI(title="SMIT API",
                debug=True,
                version="0.0.1")

class Input_WPM_Details(BaseModel):
  Detail : List[str]
  Area : str
  Coworker : str
  Collected_Input: str

class Form_Response_SafetyAudit(BaseModel):
  Safety_Audit_Details : List[str]
  Safety_Audit_Frequency : List[int]
  Safety_Audit_Contractor : List[str]
  Safety_Audit_Type_Of_Finding : List[str]
  Safety_Audit_Area : List[str]
  Safety_Audit_Topic : List[str]

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

def time_in_range(current):
    if current >= "00:00" and current <= "04:00":
      return False
    else:
      return True

@app.get('/') 
def Hello(auth: str = Depends(BasicAuth)):
  # now = datetime.now().time()
  # current_time = now.strftime("%H:%M")
  # if time_in_range(current_time) == False:
  #   return "API In maintenance!!!", 400
  # else:
    if auth == True:
      return "Welcome to SMIT3.0 API"

@app.post('/WPMDetails', status_code=status.HTTP_200_OK, response_model=Form_Response_SafetyAudit)
async def Suggest_Safety_Audit(request: Input_WPM_Details, auth: str = Depends(BasicAuth)):
  if auth == True:
    # now = datetime.now().time()
    # current_time = now.strftime("%H:%M")
    # if time_in_range(current_time) == False:
    #   return "API In maintenance", 400
    # else:
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
    # now = datetime.now().time()
    # current_time = now.strftime("%H:%M")
    # if time_in_range(current_time) == False:
    #   return "API In maintenance", 400
    # else:
      data = request.json()
      data = json.loads(data)
      Input_Details = data['WorkPermitDetails']
      Cleansing_Case = data['Case']
      ResponseSpellCheck = Cleansing_Input(Input_Details, Cleansing_Case)
      return JSONResponse(ResponseSpellCheck)

@app.post('/InsertAuditToDatabase', status_code=status.HTTP_200_OK)
async def UploadDataToDatabase(request: All_Audit, auth: str = Depends(BasicAuth)):
  if auth == True:
    # now = datetime.now().time()
    # current_time = now.strftime("%H:%M")
    # if time_in_range(current_time) == False:
    #   return "API In maintenance", 300
    # else:
      data = request.json()
      data = json.loads(data)

      ResponseFindingDetail = GetFindingDetail("DESC")
      Index = ResponseFindingDetail['FindingNo'].tolist()
      Index = Index[0]

      Index = data['Index']
      Safety_Audit_Details = data['Safety_Audit_Details']
      Count = data['Count']
      Area = data['Area']
      Contractor = data['Contractor']
      Type_Of_Finding = data['Type_Of_Finding']
      Topic = data['Topic']
      Answer = data['Result']
      Problems = data['Problems']
      Solution = data['Solution']
      Date = data['Date']
      
      Result = [Index]
      Result.extend([Safety_Audit_Details])
      Result.extend([Count])
      Result.extend([Area])
      Result.extend([Contractor])
      Result.extend([Type_Of_Finding])
      Result.extend([Topic])
      Result.extend([Answer])
      Result.extend([Problems])
      Result.extend([Solution])
      Result.extend([Date])

      return Upload_Audit_To_Database(Result)

# @app.get('/Request_WPM_Detail', status_code=status.HTTP_200_OK)
# async def Request_WPM_Detail(request: Get_WPM_Detail, auth: str = Depends(BasicAuth)):
#   if auth == True:
#     now = datetime.now().time()
#     current_time = now.strftime("%H:%M")
#     if time_in_range(current_time) == False:
#       return "API In maintenance", 300
#     else:
#       data = request.json()
#       data = json.loads(data)

#       Primary_Key = data['DocID']
#       return Response_WPM_Detail(Primary_Key)

@app.post('/UploadNewFindingDetails', status_code=status.HTTP_200_OK)
async def UploadNewFindingDetails(request: NewFindingDetails, auth: str = Depends(BasicAuth)):
  if auth == True:
    # now = datetime.now().time()
    # current_time = now.strftime("%H:%M")
    # if time_in_range(current_time) == False:
    #   return "API In maintenance", 400
    # else:
      data = request.json()
      data = json.loads(data)
      
      FindingNo = data['No']
      FindingCompany = data['Company']
      FindingArea = data['Area']
      FindingSubArea = data['SubArea']
      FindingReportor = data['Reportor']
      FindingContractor = data['Contractor']
      FindingTypeOfFinding = data['TypeOfFinding']
      FindingTopic = data['Topic']
      FindingDetails = data['Details']
      FindingCorrectiveAction = data['CorrectiveAction']
      FindingIssueDate = data['IssueDate']
      FindingDueDate = data['DueDate']
      FindingStatus = data['Status']

      ResponseFindingDetail = GetFindingDetail("DESC")

      ResponseFindingDetail = list(ResponseFindingDetail.itertuples(index=False, name=None))

      FindingData = list(zip(FindingNo, FindingCompany, FindingArea, FindingSubArea, 
                            FindingReportor, FindingContractor, FindingTypeOfFinding, 
                            FindingTopic, FindingDetails, FindingCorrectiveAction,
                            FindingIssueDate, FindingDueDate, FindingStatus))

      ResultFindingData = list(set(FindingData) - set(ResponseFindingDetail))

      return UploadFinding(ResultFindingData)

# if __name__ == '__main__':
#   uvicorn.run("main:app", host='0.0.0.0', port=80, reload=True, debug=True)