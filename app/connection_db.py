import pyodbc

connection_SafetyAudit = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
            Server = "smitazure.database.windows.net",
            Database = "SafetyAudit",
            uid = 'smitadmin',
            pwd = 'Abc12345',
            Trusted_Connection = 'no') 

connection_SMIT3 = pyodbc.connect(Driver = "ODBC Driver 17 for SQL Server",
            Server = "smitazure.database.windows.net",
            Database = "SMIT3",
            uid = 'smitadmin',
            pwd = 'Abc12345',
            Trusted_Connection = 'no') 