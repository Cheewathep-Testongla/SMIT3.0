/****** Script for SelectTopNRows command from SSMS  ******/
SELECT [v_Permit_WorkerList].ReqId, [v_Permit_WorkerList].Area, [v_Permit_WorkerList].Desire, [v_Permit_WorkerList].SafetyCompany
  FROM [e-Permit_MOC].[dbo].[v_Permit_WorkerList]
  JOIN [e-Permit_MOC].[dbo].[v_Permit_List]
  ON [e-Permit_MOC].[dbo].[v_Permit_WorkerList].PermitNo = [e-Permit_MOC].[dbo].[v_Permit_List].PermitNo
  WHERE [e-Permit_MOC].[dbo].[v_Permit_WorkerList].PermitNo != ''
  ORDER BY v_Permit_List.ReqId ASC;
