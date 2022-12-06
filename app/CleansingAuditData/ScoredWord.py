def CreateFrequencyTypeOfFinding(word, ListWords_UnsafeAction, ListWords_UnsafeCondition, ListWords_NearMiss, ListWords_HNM, ListWords_Accident):
    Value = 6
    if word in ListWords_UnsafeAction:
        Value -= 1
    if word in ListWords_UnsafeCondition:
        Value -= 1
    if word in ListWords_NearMiss:
        Value -= 1
    if word in ListWords_HNM:
        Value -= 1
    if word in ListWords_Accident:
        Value -= 1
    if Value == 6:
        return 0
    else:
        return Value

def CreateFrequencyTopic(word, ListWords_LOTO, ListWords_WAH, ListWords_Scaffolding, ListWords_Transportation, ListWords_PTW_JSA, 
                               ListWords_ProcessOperation, ListWords_Radiation, ListWords_Others, ListWords_Lifting, ListWords_Housekeeping,
                               ListWords_ToolsEquipment, ListWords_HotWork, ListWords_Excavation, ListWords_CSE, ListWords_ElectricalGrounding,
                               ListWords_PaintCoatBlast, ListWords_ChemicalWork, ListWords_SafetyManagement, ListWords_PPE, ListWords_WaterJet, 
                               ListWords_PressureTest, ListWords_SLPerformance, ListWords_WorkProcedure, ListWords_Civil, ListWords_Insulation,
                               ListWords_Environmental, ListWords_InstallationAlignment, ListWords_Security):
    Value = 29
    if word in ListWords_LOTO:
        Value -= 1
    if word in ListWords_WAH:
        Value -= 1
    if word in ListWords_Scaffolding:
        Value -= 1
    if word in ListWords_Transportation:
        Value -= 1
    if word in ListWords_PTW_JSA:
        Value -= 1
    if word in ListWords_ProcessOperation:
        Value -= 1
    if word in ListWords_Radiation:
        Value -= 1
    if word in ListWords_Others:
        Value -= 1
    if word in ListWords_Lifting:
        Value -= 1
    if word in ListWords_Housekeeping:
        Value -= 1
    if word in ListWords_ToolsEquipment:
        Value -= 1
    if word in ListWords_HotWork:
        Value -= 1
    if word in ListWords_Excavation:
        Value -= 1
    if word in ListWords_CSE:
        Value -= 1
    if word in ListWords_ElectricalGrounding:
        Value -= 1
    if word in ListWords_PaintCoatBlast:
        Value -= 1
    if word in ListWords_ChemicalWork:
        Value -= 1
    if word in ListWords_SafetyManagement:
        Value -= 1
    if word in ListWords_PPE:
        Value -= 1
    if word in ListWords_WaterJet:
        Value -= 1
    if word in ListWords_PressureTest:
        Value -= 1
    if word in ListWords_SLPerformance:
        Value -= 1
    if word in ListWords_WorkProcedure:
        Value -= 1
    if word in ListWords_Civil:
        Value -= 1
    if word in ListWords_Insulation:
        Value -= 1
    if word in ListWords_Environmental:
        Value -= 1
    if word in ListWords_InstallationAlignment:
        Value -= 1
    if word in ListWords_Security:
        Value -= 1
    if Value == 28:
        return 0
    else:
        return Value