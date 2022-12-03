/****** Script for SelectTopNRows command from SSMS  ******/
SELECT CAST([dbo].[LOG_Finding].[ID] AS int)
	  ,[dbo].[LOG_Permit].[Title]
      ,[dbo].[LOG_Finding].[Area]
      ,[dbo].[LOG_Permit].[Detail]
	  ,[dbo].[LOG_Finding].[AuditResult]
	  ,[dbo].[LOG_Finding].[Finding]
  FROM [dbo].[LOG_Permit]
  JOIN [dbo].[LOG_Finding]
  ON [dbo].[LOG_Permit].[Title] = [dbo].[LOG_Finding].[Title]
  WHERE [dbo].[LOG_Finding].[AuditResult] = 'Need to Improve' or 
  [dbo].[LOG_Finding].[AuditResult] = 'Non-conform';