CREATE TABLE v_Response_SafetyAudit (
	ReqID INT,
	Desire VARCHAR(max),
	Area VARCHAR(max) ,
	SafetyCompany VARCHAR(max),
	CollectedDesire VARCHAR(max),
	ResultCollectedDesire NVARCHAR(max),
	Case1_SafetyAuditResult NVARCHAR(max),
	Case2_SafetyAuditResult NVARCHAR(max)
);