/****** Script for SelectTopNRows command from SSMS  ******/
SELECT (CAST([dbo].[LOG_Finding].[ID] AS int))
	ID,
	Finding,
	AuditResult
FROM [dbo].[LOG_Finding]
JOIN [dbo].[LOG_Permit]
ON [dbo].[LOG_Finding].[Title] = [dbo].[LOG_Permit].[Title]
WHERE [dbo].[LOG_Finding].ID > 113 AND [dbo].[LOG_Finding].ID != 131 AND [dbo].[LOG_Finding].ID != 5057 AND 
[dbo].[LOG_Finding].ID != 5058 AND [dbo].[LOG_Finding].ID != 190 AND [dbo].[LOG_Finding].ID != 1483 AND 
[dbo].[LOG_Finding].ID != 1486 AND [dbo].[LOG_Finding].ID != 1974 AND [dbo].[LOG_Finding].ID != 132 AND 
 (AuditResult = 'Need to Improve' or AuditResult = 'Non-conform') 
 AND Corrective != '' AND [dbo].[LOG_Finding].Created > '2022-01-01 10:02:00.000'