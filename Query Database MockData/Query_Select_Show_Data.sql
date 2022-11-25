SELECT [v_Permit_WorkerList].[ReqID], [v_Permit_WorkerList].[Desire], [v_Permit_WorkerList].[Area], [SafetyCompany] 
                            FROM [v_Permit_List] 
                            JOIN [v_Permit_WorkerList] 
                            ON [v_Permit_List].[PermitNo] = [v_Permit_WorkerList].[PermitNo] 
                            WHERE [v_Permit_List].[Desire] != '' and [v_Permit_WorkerList].[Desire] != ''
                            ORDER BY [v_Permit_List].[ReqId] ,[v_Permit_WorkerList].[SafetyCompany] ASC;