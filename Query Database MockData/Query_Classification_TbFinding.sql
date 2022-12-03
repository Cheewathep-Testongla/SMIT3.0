CREATE TABLE Classification_tbFinding 
(
	FindingNo INT NOT NULL PRIMARY KEY,
	Area VARCHAR(max),
	SubArea VARCHAR(max),
	Contractor VARCHAR(max),
	TypeOfFinding VARCHAR(max),
	Topic VARCHAR(max),
	Details VARCHAR(max) COLLATE SQL_Latin1_General_CP1_CI_AS,
	TranslateDetails VARCHAR(max),
	Finding VARCHAR(max) COLLATE SQL_Latin1_General_CP1_CI_AS,
	TranslateFinding VARCHAR(max)
);