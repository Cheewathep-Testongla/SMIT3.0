
# @app.post('/InsertAuditToDatabase', status_code=status.HTTP_200_OK)
# async def UploadDataToDatabase(request: All_Audit, auth: str = Depends(BasicAuth)):
#   if auth == True:
#     # now = datetime.now().time()
#     # current_time = now.strftime("%H:%M")
#     # if time_in_range(current_time) == False:
#     #   return "API In maintenance", 300
#     # else:
#       data = request.json()
#       data = json.loads(data)

#       ResponseFindingDetail = GetFindingDetail("DESC")
#       Index = ResponseFindingDetail['FindingNo'].tolist()
#       Index = Index[0]

#       Index = data['Index']
#       Safety_Audit_Details = data['Safety_Audit_Details']
#       Count = data['Count']
#       Area = data['Area']
#       Contractor = data['Contractor']
#       Type_Of_Finding = data['Type_Of_Finding']
#       Topic = data['Topic']
#       Answer = data['Result']
#       Problems = data['Problems']
#       Solution = data['Solution']
#       Date = data['Date']
      
#       Result = [Index]
#       Result.extend([Safety_Audit_Details])
#       Result.extend([Count])
#       Result.extend([Area])
#       Result.extend([Contractor])
#       Result.extend([Type_Of_Finding])
#       Result.extend([Topic])
#       Result.extend([Answer])
#       Result.extend([Problems])
#       Result.extend([Solution])
#       Result.extend([Date])

#       return Upload_Audit_To_Database(Result)

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

# @app.post('/UploadNewFindingDetails', status_code=status.HTTP_200_OK)
# async def UploadNewFindingDetails(request: NewFindingDetails, auth: str = Depends(BasicAuth)):
#   if auth == True:
#     # now = datetime.now().time()
#     # current_time = now.strftime("%H:%M")
#     # if time_in_range(current_time) == False:
#     #   return "API In maintenance", 400
#     # else:
#       data = request.json()
#       data = json.loads(data)
      
#       FindingNo = data['No']
#       FindingCompany = data['Company']
#       FindingArea = data['Area']
#       FindingSubArea = data['SubArea']
#       FindingReportor = data['Reportor']
#       FindingContractor = data['Contractor']
#       FindingTypeOfFinding = data['TypeOfFinding']
#       FindingTopic = data['Topic']
#       FindingDetails = data['Details']
#       FindingCorrectiveAction = data['CorrectiveAction']
#       FindingIssueDate = data['IssueDate']
#       FindingDueDate = data['DueDate']
#       FindingStatus = data['Status']

#       ResponseFindingDetail = GetFindingDetail("DESC")

#       ResponseFindingDetail = list(ResponseFindingDetail.itertuples(index=False, name=None))

#       FindingData = list(zip(FindingNo, FindingCompany, FindingArea, FindingSubArea, 
#                             FindingReportor, FindingContractor, FindingTypeOfFinding, 
#                             FindingTopic, FindingDetails, FindingCorrectiveAction,
#                             FindingIssueDate, FindingDueDate, FindingStatus))

#       ResultFindingData = list(set(FindingData) - set(ResponseFindingDetail))

#       return UploadFinding(ResultFindingData)