from difflib import get_close_matches
import re
import pandas as pd
from pydantic import BaseModel
from pythainlp import word_tokenize
from pythainlp.util import Trie
from pythainlp.tag import pos_tag

class WPM_Details(BaseModel):
  WorkPermitDetails : str

def TokenizeInput(Data):

    Data = Data.lower()

    Corrected_input = ""

    Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary_Test.csv',encoding='utf-8')

    DictTokenize = Custom_Dict['words'].tolist()
    DictCorrect = Custom_Dict['correct'].tolist()

    Data = re.sub(',',' , ', Data)
    Data = re.sub(' +',' ', Data)

    ListUselessText = 'group|[a-z]+-[0-9]+[a-z]+|[a-z]+-[0-9]+| [0-9]+ | [a-z]v |[a-z]+-[0-9]+[a-z]+|[a-z]+-[a-z]+[0-9]+|[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+|[a-z]+[0-9]+[a-z-]+|[0-9]+ เมตร|[a-z]+[0-9]+|\#|\(|\)|\@|^[ ]|:|SYSTEM TEST|\"|M\.'

    FindUselessText = re.findall(ListUselessText, Data) 

    RemoveUnusedTypeofwords = Data
    
    trie = Trie(DictTokenize)

    if len(FindUselessText) != 0: 
        for words in FindUselessText:
            RemoveUnusedTypeofwords = RemoveUnusedTypeofwords.replace(words,' ')

    RemoveUnusedTypeofwords = ' '.join(RemoveUnusedTypeofwords.split())

    # print('RemoveUnusedTypeofwords', RemoveUnusedTypeofwords)
    
    TempListTokenize = word_tokenize(RemoveUnusedTypeofwords, custom_dict=trie, engine='newmm')

    # print('TempListTokenize', TempListTokenize)

    GetPos_TagListTokenize = pos_tag(TempListTokenize, corpus="orchid_ud")

    # print('GetPos_TagListTokenize', GetPos_TagListTokenize)

    # for index in range(len(GetPos_TagListTokenize)):
    #     if(GetPos_TagListTokenize[index][0] == '  '):
    #         TempGetPos_TagListTokenize = list(GetPos_TagListTokenize[index])
    #         TempGetPos_TagListTokenize[0] = ' '
    #         TempGetPos_TagListTokenize[1] = 'PUNCT'
    #         GetPos_TagListTokenize[index] = tuple(TempGetPos_TagListTokenize)
    #     elif((len(GetPos_TagListTokenize[index][0]) == 1 and GetPos_TagListTokenize[index][0] != " " and GetPos_TagListTokenize[index][0] != "/")or len(re.findall(' [A-Z][A-Z] ', GetPos_TagListTokenize[index][0])) == 2 ):
    #         IndexRemoveTupleTokenize.append(index)
        
    # for index in range(len(IndexRemoveTupleTokenize)):
    #     if(index == 0):
    #         GetPos_TagListTokenize = GetPos_TagListTokenize[:IndexRemoveTupleTokenize[index]] + GetPos_TagListTokenize[IndexRemoveTupleTokenize[index]+1:]
    #     else:
    #         IndexRemoveTupleTokenize[index] = IndexRemoveTupleTokenize[index]-1
    #         GetPos_TagListTokenize = GetPos_TagListTokenize[:IndexRemoveTupleTokenize[index]] + GetPos_TagListTokenize[IndexRemoveTupleTokenize[index]+1:]

    # print(GetPos_TagListTokenize)

    PROPNListTokenize = []
    ListTokenize = []

    for index in range(len(GetPos_TagListTokenize)):
        temp = []
        if (GetPos_TagListTokenize[index][1] == "SCONJ" or 
            GetPos_TagListTokenize[index][1] == "ADP" or 
            GetPos_TagListTokenize[index][1] == "CCONJ" or
            GetPos_TagListTokenize[index][1] == "PUNCT"):
            temp.append(GetPos_TagListTokenize[index][0])
            temp.append(index)
            PROPNListTokenize.append(temp)
        else: 
            ListTokenize.append(GetPos_TagListTokenize[index][0])

    print('ListTokenize', ListTokenize)

    TempResult = []
    CheckIfTempResultisAlready = []

    for i in range(len(ListTokenize)):
        # CheckIfTempResultisAlready = []
        print(CheckIfTempResultisAlready, ListTokenize[i])
        FinalJoinString = ''
        if(ListTokenize[i] in DictTokenize):
            IndexRepeatDictTokenize = []
            # Get all duplicate value in DictTokenize that match with ListTokenize[i]
            for idx, val in enumerate(DictTokenize):
                if ListTokenize[i] == val and idx not in IndexRepeatDictTokenize:
                    IndexRepeatDictTokenize.append(idx)
            if(len(IndexRepeatDictTokenize) > 1):   
                for index in IndexRepeatDictTokenize:
                    for j in range(i, len(ListTokenize)):
                        if ListTokenize[j] != ' ':
                            try:
                                TempJoinString = DictCorrect[index]+DictCorrect[DictTokenize.index(ListTokenize[j])]
                                if TempJoinString in DictCorrect:
                                    CheckIfTempResultisAlready.append(DictCorrect[index])
                                    CheckIfTempResultisAlready.append(DictCorrect[DictTokenize.index(ListTokenize[j])])
                                    CheckIfTempResultisAlready.append(TempJoinString)
                                    FinalJoinString = TempJoinString
                            except:   
                                FinalJoinString = ListTokenize[j]
                    if FinalJoinString not in CheckIfTempResultisAlready:
                        TempResult.append(FinalJoinString)       
                        CheckIfTempResultisAlready.append(FinalJoinString) 

            elif len(IndexRepeatDictTokenize) == 1:
                index = DictTokenize.index(ListTokenize[i])
                if DictCorrect[index] not in CheckIfTempResultisAlready:
                    TempResult.append(DictCorrect[index])
                    CheckIfTempResultisAlready.append(DictCorrect[index])
        else:
            try:
                if get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0] not in CheckIfTempResultisAlready:
                    TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
                    CheckIfTempResultisAlready.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
            except: 
                if ListTokenize[i] not in CheckIfTempResultisAlready:
                    TempResult.append(ListTokenize[i])
                    CheckIfTempResultisAlready.append(ListTokenize[i])

    print('CheckIfTempResultisAlready', CheckIfTempResultisAlready)                

    print('TempResult',TempResult)
    # print('CheckIfTempResultisAlready',CheckIfTempResultisAlready)

    for i in range(len(PROPNListTokenize)):
        TempResult.insert(PROPNListTokenize[i][1], PROPNListTokenize[i][0])
    # List of Result after cleansing : used to response list of words in api
    Result = []
    #### คิด Logic ใหม่ : ถ้า Index เป็น 0 จะ append หรือ ถ้า Index ไม่เท่ากับตัวสุดท้ายและ TempResult[index] มีค่าเท่ากับ TempResultตัวถัดไป จะ Insert ตัวแรก
    for index in range(len(TempResult)):
        if (index == 0):
           Result.append(TempResult[index]) 
        elif (index != len(TempResult)-1):
            if(TempResult[index] == TempResult[index+1]):
                Result.append(TempResult[index+1])
            else:
                Result.append(TempResult[index])
        elif (index == len(TempResult)-1) or (index == len(TempResult)):
            Result.append(TempResult[index])    

    # Result = ''.join(Result.split(" "))
    Corrected_input = "".join(Result)

    RemoveUnusedTypeofwords = Corrected_input
    ListSplitCharacter = "\/\/+|\/|\+|,|&|and|และ|กับ|เพื่อ|\n"
    FindSplitCharecter = re.findall(ListSplitCharacter, RemoveUnusedTypeofwords) 
    
    for word in FindSplitCharecter:
        RemoveUnusedTypeofwords = re.sub(' +',' ', RemoveUnusedTypeofwords)
        RemoveUnusedTypeofwords  = RemoveUnusedTypeofwords.replace(word, ', ')

    # Last Check 
    # print('RemoveUnusedTypeofwords', RemoveUnusedTypeofwords)

    if(RemoveUnusedTypeofwords not in DictCorrect):
        RemoveUnusedTypeofwords = word_tokenize(RemoveUnusedTypeofwords)
        
        if(len(RemoveUnusedTypeofwords) > 1):
            for i in range(len(RemoveUnusedTypeofwords)):
                try:
                    if RemoveUnusedTypeofwords[i] not in DictCorrect and RemoveUnusedTypeofwords[i] != ' ':
                        RemoveUnusedTypeofwords[i] = get_close_matches(RemoveUnusedTypeofwords[i], DictCorrect, 1, 0.4)[0]
                except:
                    continue

        RemoveUnusedTypeofwords = "".join(RemoveUnusedTypeofwords)
    
    # print('Correct Result', Result)

    # print('RemoveUnusedTypeofwords', RemoveUnusedTypeofwords)

    RawTokenizeInput = RemoveUnusedTypeofwords.split(',')

    TokenizeInput = []

    # print(len(RawTokenizeInput))

    for index in range(len(RawTokenizeInput)):
        if RawTokenizeInput[index] != ' ' and  RawTokenizeInput[index] != '':
            TokenizeInput.append(re.sub(' +',' ', RawTokenizeInput[index]))    

    print('TokenizeInput', TokenizeInput)

    # for i in range(len(PROPNListTokenize)):
    #     TokenizeInput.insert(i+1, PROPNListTokenize[i][0])

    # print('TokenizeInput', TokenizeInput)

    # Corrected_input = "".join(TokenizeInput)
    Corrected_input = re.sub(' +',' ', RemoveUnusedTypeofwords)

    print("Corrected_input", Corrected_input)
    return TokenizeInput

# @app.get('/') 
def TestSpellCheck(Data):
    # data = request.json()
    # data = json.loads(data)

    # Data = data['WorkPermitDetails']
    Data = Data.lower()

    Custom_Dict = pd.read_csv('./SMIT_Data/DataForModel/Raw_Dictionary.csv',encoding='utf-8')
    Unwanted_Dict = pd.read_csv('./SMIT_Data/DataForModel/UnwantedDict.csv',encoding='utf-8')

    DictTokenize = Custom_Dict['words'].tolist()
    DictCorrect = Custom_Dict['correct'].tolist()
    Unwanted_Dict = Unwanted_Dict['words'].tolist()

    Thai_Dict = pd.read_csv('./SMIT_Data/DataForModel/TH_Raw_Dictionary.csv',encoding='utf-8')
    THDictTokenize = Thai_Dict['words'].tolist()
    THDictTrie = Trie(THDictTokenize)

    Data = re.sub(' +',' ', Data)
    Data = re.sub('^ +','', Data)
    Data = re.sub('^ | $','', Data)

    Data = re.sub(',| ,|, | , ',' , ', Data)
    Data = re.sub(' +',' ', Data)
    
    # RemoveVowel = []
    # for word in Data:
    #     # if(re.findall(r'(^[\u0E30-\u0E3A\u0E47-\u0E4E]+)', "", Data[i]))
    #     # RemoveVowel.append(re.sub(r'(^[\u0E30-\u0E3A\u0E47-\u0E4E]+)', "", word))
    
    # Data = ''.join(RemoveVowel)
    
    ListUnwantedText = [
                        'no. [0-9-/]+',
                        '[a-z]+-[a-z]+[0-9]+[a-z0-9-/]+[a-z0-9]*',
                        '[0-9]+-[0-9]+/[0-9]+',
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|=',
                        '\?',
                        '\[|\]|\{|\}'
                        ]

    ListCutText = []
    for index in ListUnwantedText:
        Find_Text = re.findall(index, Data) 
        if len(Find_Text) != 0: 
            for words in Find_Text:
                if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
                    Data = Data.replace(words,' ')
                    ListCutText.append(words)
        else : 
            Data = Data

    ListSplitCharacter = "\/\/+|\/|\+|,|&|and|และ|กับ|เพื่อ|\n"
    FindSplitCharecter = re.findall(ListSplitCharacter, Data) 

    Tokenize_Input = Data
    Collected_Input = Data

    for words in FindSplitCharecter:
        Tokenize_Input = Tokenize_Input.replace(words, ' , ')

    ListUnwantedText = [
                        '[a-z]+-[0-9a-z]+-[a-z0-9]+',               #a-a0-a0     
                        '[a-z]+-[0-9]+[a-z]+[0-9]+[a-z]+',          #a-a0 
                        '[a-z]+-[0-9]+[a-z]+[a-z]+[0-9]+',          #
                        '[a-z]+-[a-z]+[0-9]+[0-9]+[a-z]+',          #
                        '[a-z]+-[a-z]+[0-9]+[a-z]+[0-9]+',          #
                        '[a-z]+[0-9]+[a-z-]+',                      #                          
                        '[a-z]+ [0-9]+ [a-z]+',                     # PIT 3060 ABC                         
                        '[a-z]+-[0-9]+-[a-z]+',                     #a-0-a                                               
                        '[a-z]+-[a-z]+-[0-9]+',                     #a-a-0
                        '[a-z]+-[0-9]+[a-z]+',                      # TT-8006BA
                        '[a-z]+-[0-9]+',                            #a-0
                        '[0-9]+[a-z]+',                             #0a
                        '[a-z]+[0-9]+',                             #a0                        
                        '[0-9]+ เมตร',                              #12 เมตร
                        '[0-9]+ ชม.',
                        '[0-9]+ ชั่วโมง',
                        '[0-9][0-9]+',                              #00 
                        ' [0-9] ',                                  # 0 
                        ' [a-z] ',                                  # a
                        '\#|\(|\)|\@|^[ ]|:|\"|M\.|-',              
                        'group',
                        'class',
                        'ฯ'
                        ]

    ListCutText = []
    for index in ListUnwantedText:
        Find_Text = re.findall(index, Tokenize_Input) 
        if len(Find_Text) != 0: 
            for words in Find_Text:
                if (words != ' ' and (words not in DictCorrect or words not in DictTokenize)):
                    Tokenize_Input = Tokenize_Input.replace(words,' ')
                    Collected_Input = Collected_Input.replace(words,' ')
                    ListCutText.append(words)
        else : 
            Tokenize_Input = Tokenize_Input
            Collected_Input = Collected_Input

    Tokenize_Input = Tokenize_Input.split(',')

    ResultTokenizeInput = []
    ResultCorrectedInput = ''

    trie = Trie(DictTokenize)

    for sentence in Tokenize_Input:
        TempListTokenize = word_tokenize(sentence, custom_dict=THDictTrie, engine='newmm')
        GetPos_TagListTokenize = pos_tag(TempListTokenize, corpus="orchid_ud")
        print(TempListTokenize)
        TempResult = []
        CheckIfTempResultisAlready = []
        PROPNListTokenize = []
        ListTokenize = []

        # print(TempListTokenize)

        for index in range(len(GetPos_TagListTokenize)):
            temp = []
            if (
                # GetPos_TagListTokenize[index][1] == "SCONJ" or 
                GetPos_TagListTokenize[index][1] == "ADP" or 
                GetPos_TagListTokenize[index][1] == "CCONJ" or
                GetPos_TagListTokenize[index][1] == "PUNCT"):
                temp.append(GetPos_TagListTokenize[index][0])
                temp.append(index)
                PROPNListTokenize.append(temp)
            else: 
                ListTokenize.append(GetPos_TagListTokenize[index][0])

        for i in range(len(ListTokenize)):    
            FinalJoinString = ''
            if(re.findall('(^[\u0E30-\u0E3A\u0E47-\u0E4E]+)', ListTokenize[i]) or len(re.findall('[\u0E01-\u0E4E]', ListTokenize[i])) == 1):
                continue
            elif(len(re.findall(' [a-z][a-z][a-z] | [a-z][a-z] ', ListTokenize[i])) > 1):
                TempResult.append(ListTokenize[i])     

            elif(len(re.findall('([A-Za-z])\w+', ListTokenize[i])) > 0):
                # print(re.findall('([A-Za-z])\w+', ListTokenize[i]))
                if ListTokenize[i] in DictTokenize:
                    TempResult.append(DictCorrect[DictTokenize.index(ListTokenize[i])])
                else:
                    try:
                        TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.4)[0])
                    except:
                        TempResult.append(ListTokenize[i])        
            else:    
                if(ListTokenize[i] in DictTokenize):
                    IndexRepeatDictTokenize = []
                    # Get all duplicate value in DictTokenize that match with ListTokenize[i]
                    for idx, val in enumerate(DictTokenize):
                        if ListTokenize[i] == val and idx not in IndexRepeatDictTokenize:
                            IndexRepeatDictTokenize.append(idx)
                    if (len(IndexRepeatDictTokenize) > 1):
                        for index in IndexRepeatDictTokenize:
                            for j in range(i, len(ListTokenize)):
                                if ListTokenize[j] != ' ':
                                    try:
                                        # TempJoinString = DictCorrect[DictTokenize.index(ListTokenize[j])]+DictCorrect[index]
                                        TempJoinString = TempResult[len(TempResult)-1]+DictCorrect[DictTokenize.index(ListTokenize[j])]
                                        if TempJoinString in DictCorrect:
                                            CheckIfTempResultisAlready.append(DictCorrect[index])
                                            CheckIfTempResultisAlready.append(TempResult[len(TempResult)-1])
                                            CheckIfTempResultisAlready.append(TempJoinString)
                                            FinalJoinString = TempJoinString
                                    except:     
                                        FinalJoinString = ListTokenize[j]
                            if FinalJoinString not in CheckIfTempResultisAlready:
                                TempResult.append(FinalJoinString)   
                                CheckIfTempResultisAlready.append(FinalJoinString)
                            elif FinalJoinString == '':
                                TempResult.append(ListTokenize[i])  

                    else:
                        index = DictTokenize.index(ListTokenize[i])
                        # if DictCorrect[index] not in CheckIfTempResultisAlready:
                        TempResult.append(DictCorrect[index])
                        CheckIfTempResultisAlready.append(DictCorrect[index])

                else:
                    if ListTokenize[i] != ' ':
                        try:
                            if get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0] not in CheckIfTempResultisAlready:
                                TempResult.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0])
                                CheckIfTempResultisAlready.append(get_close_matches(ListTokenize[i], DictCorrect, 1, 0.6)[0])
                        except: 
                            if ListTokenize[i] not in CheckIfTempResultisAlready:
                                TempResult.append(ListTokenize[i])
                                CheckIfTempResultisAlready.append(ListTokenize[i])
                    else:
                        TempResult.append(' ')
        
        for i in range(len(PROPNListTokenize)):
            TempResult.insert(PROPNListTokenize[i][1], PROPNListTokenize[i][0])

        Result = []
        TempResultTokenizeInput = ''
        # Remove first and last empty space in list
        for i in range(len(TempResult)):
            if(i == 0 and len(TempResult) > 1):
                ResultCorrectedInput = ' '+ResultCorrectedInput+TempResult[i]
            if (TempResult[i] == '') or (i == 0 and TempResult[i] == ' ') or (i == len(TempResult)-1 and TempResult[len(TempResult)-1] == ' ') or (TempResult[i] == ' ' and TempResult[i+1] == ' '):
                continue
            else:
                if(i == 0):
                    ResultCorrectedInput = ' '+ResultCorrectedInput
                Result.append(TempResult[i])
                TempResultTokenizeInput = TempResultTokenizeInput+TempResult[i]

        TempResultTokenizeInput = TempResultTokenizeInput+' '
        TempResultTokenizeInput = re.sub(' +', ' ',TempResultTokenizeInput)
        TempResultTokenizeInput = re.sub('^ ', '',TempResultTokenizeInput)

        if TempResultTokenizeInput not in ResultTokenizeInput and len(TempResultTokenizeInput) > 1: 
            ResultTokenizeInput.append(TempResultTokenizeInput)
            ResultCorrectedInput = ""+', '.join(ResultTokenizeInput)
    
    ResultCorrectedInput = re.sub(' +', ' ',ResultCorrectedInput)
    ResultCorrectedInput = re.sub('^ | $', '',ResultCorrectedInput)

    print("Tokenize Input :", ResultTokenizeInput)
    print("Corrected Input :", ResultCorrectedInput)

# test = "แก้ไข insul FT-8400,FT-8109" # ผ่าน
# test = 'ตัด เจียร ประกอบ เชือม Line 2"PR-A13049-B13A' # ผ่าน
# test = 'เปลี่ยนแบต DG-4003A,C,D' # ยังตัดตัวอักษรได้ไม่ครบ : เปลี่ยนแบต cm do : เหลือ c, d
# test = 'Check lighting ARU' # ผ่าน
# test = 'ตัด เชื่อม เจีย ประกอบ Pipe spool' # ผ่าน
# test = '''PM INSPT XV GROUP IN 890 AREA
# PM INSPT PDT GROUP IN LCB2 AREA PDT-201
# PM INSPT PV GROUP IN 880 AREA
# PM INSPT PV GROUP IN 890 AREA
# PM INSPT TV GROUP IN 880 AREA
# PM INSPT XV GROUP IN 880 AREA
# PM INSPT XV GROUP IN 960 AREA
# PM INSPT PDT GROUP IN FAR4 AREA''' # ผ่าน
# test = 'ชัดเจน' # ผ่าน
# test = 'PM for Safety Valve PSV-8706A, PSV-8706B On-Site Test' # ผ่าน
# test = 'PM O2 panamagnectic analyzer AT-9000,AT-9600' # ผ่าน 
# test = 'PM INSPTHV,XV,FV,TV,PCV GROUP IN Z-S401 , T-S420 AREA' # ผ่าน
# test = 'เปลี่ยน อะไหร่ air com' # แก้เป็น air com : air
# test = 'remove/install scaff' # คำนามไม่ครบประโยค ['remove', 'install scaffolding'] : ผ่าน
# test = '5ส Oiler+ Lifting Oil' # ผ่าน
test = 'ขนยายอุปกรนตังนังล้าน' # ผ่าน
# test = 'ขยายอุกรณ์อุปกรณ์นังล้านและอุกรณ์ติดตั้ง insul / velding' # ผ่าน
# test = 'ติดตั้งทุนรอยน้ำและแผงโซล่าเซลล์, ขยายอุกรณ์' # ผ่าน
# test = "ยก ขนย้ายอุปกรณ์เครื่องมือ, เครื่อง Gen, Pipe Spool เข้าหน้างาน" # ผ่าน
# test = ' งานตัด เจียร เชื่อม Support Conduit, งานติดตั้งท่อ Conduit, ลากสาย' # ผ่าน
# test = ' CALIBRATE TRANSMITTER PT-120R' # ผ่าน
# test = ' CALIBRATE TRANSMITTER TT-8006BA,8007BA,8017BA,8018BA' # ผ่าน    
# test = '5ส & Remove Scaffolding & ขนย้าย อุปกรณ์' # ผ่าน
# test = '6 WK PM SILICA ANALYZER AT-2003/AT-2201'  # ผ่าน
# test = 'ตั่งนังร๊าน ยกของง , ing' 
# test = ' CALIBRATE TRANSMITTER TT-127C-B, TT-127D-B,TT-127E-B, TT-127F-B' # ผ่าน
# test = ' Change EOL XV-165B Show Linefault' # ผ่าน
# test = 'BorScope H-100F + isual + ถ่ายรูปอุปกรณ์ H-100A,B + H-120R' # ผ่าน
# test = 'C/Swing blind support SC start up Area Cold = 6"=2 จุด / 2"=6 จุด' # ผ่าน
# test = 'check Steam trap passing+ ถ่ายรูป' # ผ่าน
# test = 'Calibrate TI2059A/B-A-B-C ( Ver. หน้างาน )' # calibrate -c verify. หน้างาน
# test = ' PM calibration Moisture Analyzer' # ผ่าน
# test = 'เจา เชือม เจีย' # ผ่าน
# test = 'PM INSP PV,TV,XV AREA T880,T890' # ผ่าน
# test = 'ตังนังรานสูง 13 และ 14 เมตร' # ผ่าน
# test = 'Remove And Install PSV-1227/1324' # ผ่าน
# test = 'รื้อหุ้มInsu ,ถ่ายรูปหลังซอมสีี' # ผ่าน
# test = 'Remove Temp.transmitter to calibration' # ผ่าน
# test = '''PM INSPT PV GROUP IN 870 AREA
# PM INSPT XV GROUP IN 850 AREA
# PM INSPT XV GROUP IN 860 AREA
# PM INSPT PDT GROUP IN FAR4 AREA
# PM INSPT PV GROUP IN 850 AREA
# PM INSPT PV GROUP IN 860 AREA
# PM INSPT TV GROUP IN 850 AREA
# PM INSPT TV GROUP IN 860 AREA
# A/เช็ค  Flow FIC-8604 Swing (เปลี่ยน Sensor)''' # ผ่าน
# test = 'รื้อหุ้ม Insulation+เช็คความหนา Pipe line HV,HL + ถ่ายรูป (ทำงานบนนั่งร้านสูง 6 เมตร)' # ผ่าน
# test = ' Confined  ขนย้ายอุปกรณ์นั่งร้านรื้อถอนติดตั้งนั่งร้านภายในและภายนอกบ่อ PIT 3060 ABC' # ผ่าน
# test = "ขยายอุปกร ด้วยรถเฮียบ" # ผ่าน
# test = "งานยกอุปกรณ์ Valve (FV-1611) โดยรถ HIAB" # ผ่าน
# test = '''A/LG-8901 และ LT-8901 อ่านค่าไม่เท่ากัน
# PV-8351 PG.Positioner Outlet leak *พันเกลียวขันอัดใหม่
# PV-8013 Regulator leak *Replace Oring  ใช้ Bypass''' # ผ่าน
# test = 'ตัด เชื่อม เจียร์ ประกอบ Pipe spool ของ Steam tracing สำหรับ Line No. 6" CKB 16028-A13A-ST Line No. 1-1/2" QOD 16040-A13A-ST Line No. 3" V 18001-A13A-ST บริเวณพื้นที่ TLS (LA-1830)' # ผ่าน
# test = ' LoadCKB-MX' # ผ่าน
# test = ' MEG PM-801B/PM-831B PM-850B/MEG PM-860B' # ผ่าน
# test = ' Replace new surge (Wire connect)and stroke test valve(Replace cable gland), Replace positioner FV-8610,FV-8611,FV-8612' # ผ่าน
# test = '03/12/21 งานถอดส่งCla Site 3' # ผ่าน
# test = 'claen flor' # ผ่าน
# test = '1WK PM PH Quench' # ผ่าน
# test = 'รื้อ-หุมInsu วัดความหนา ถ่ายรป' # ผ่าน
# test = 'ลากสายไฟ tempo ตุ้ คอนเทนเนอร์หน้า ข้าง MSS มาหน้า CCB' # ผ่าน
# test = 'สกัดปูน+เข้าแบบเทปูน' # ผ่าน
# test = 'สตารท เครื่องเจน' # ผ่าน
# test = 'ส่องกล้อง ฺBorscore Pipeline HV+ถ่ายรูป' # ผ่าน
# test = 'หุ้ม Insu.+รื้อถอนนั่งร้าน F-206A' # ผ่าน
# test = 'หู้มรื้อติดตั้ง Insulation / ติดตั้ง Scaffolding' # ผ่าน
# test = 'หู้ม Insulation' # ผ่าน
# test = 'อัดจารบี BV 10" (ทดสอบจุดDrain)' # ผ่าน
# test = 'อับอากาศขนย้ายอุปกรณ์เครื่องจักรติดตั้งปั้มนํ้าสูบนํ้าของเสียสกัดปูนดูดสารเคมีถ่ายของเสียถอดประกอบติดตั้งนั่งร้านทําความสะอาดบ่อ' # ผ่าน
# test = 'หุ้มฉนวน Air mss01/02/03/04' # ผ่าน
# test = 'หุ้มinsulation/ทาสีLine Regen/swingBlind' # ผ่าน
# test = 'หุ้มlnsu R-830' # แทนที่คำว่า stat แทนคำว่า at
# test = 'หุ้มเพิ่ม Insulation LT-S003 A,B,C at D-S002' # แทนที่คำว่า stat แทนคำว่า at
# test = 'หุ้มฉนวนแอร์ MSS/Confime  doring'
# test = 'ตังนังล้าน และ ยกของง, weding'
# test = 'ท่อร้อนบริเวณทางเดิน'
# test = 'พื้นที่รางระบายน้ำด้านข้าง high flare พบดิน slide ทรุดพังเป็นบริเวณกว้าง >> อยู่ระหว่างดำเนินการติดตั้ง hard barricade'
# test = 'Rigger สวมใส่เสื้อสะท้องแสงสีน้ำเงิน'
# test = 'Basket ใส่ Clamp ไม่มีแผ่น Plate รองน้ำหนัก'
# test = 'ตรวจสอบพบตู้เชื่อมมีการตรวจสอบเรียบร้อยแต่สภาพไม่พร้อมใช้งานโดยสายไฟหลังตู้มีการหลุดออกจากเต้าไฟ และ Regulator ยังไม่ผ่านการตรวจสอบและออกสติกเกอร์ของเดือนกรกฏาคม'
# test = '5 ส.  remove นั้งลาน,insu'
# test = 'งานนติดตั้งนั่งร้าน'
# test = 'ปูตัวหนอน,ตัดปูน,สกัดปูน'
# test = 'ตัดเชือม และ weding'
# test = 'ขนย้าน ผูกเหล็ก  ขุดดินปรับดิน'
# test = 'ตัด เจียร์ เชื่อม D-301 Project'
# test = 'Uninstall scaffolding '
# test = 'เข้าแบบ-เทปูน เกร้าปูน'
# test = ' จัดเก็บนี้งร้านเจ้าจุดกองเก็บ'
# test = 'D-3703B งานยกถังและอุปกรณ์ '
# test = 'E2 ติดตั้ง Dryer ชุด Under Water'
# test = 'Disassembly work and Water Jet D-630,E-637'
# test = 'Excavation Line Fire Water'
# test = 'ีื้รื้อนั่งร้าน '
# test = 'หุ้มinsulation'
# test = 'าน PM'
# test = 'หุ้ม ins'
# test = 'หุ้ทinsulation'
# test = 'ยัดเชื่อม line ls'
# test = 'ยกอุปกรณ์ด้วยรถเฮี้ยบ'
# test = 'รถเข้าชนอุปกร ฉาบปูน'
# test = 'ตัดเชื่อมเจียร'
# test = "เชือม เจีย / ตังนั่งล้าน"
# test = 'ขัดสนิมทาสี'
# test = 'install scafffolding'
# test = 'ตัด เชื่อ  เจียร ์์pipe support '
# test = 'ตัด เจียร์ รื้อรางTray'
# test = 'ตัดเชื่อม เจียระ ประกอบ Pipe support'
# test = 'จรวจสอบ CUS Pipe'
# test = 'งาานรื้อนั่งร้าน Project Unicat.'
# test = 'งานนั้งร้าน'
# test = 'งานยกติดตั้งเครื่อง Gen ฯ ,ห้องน้ำ และ ติดตั้งนั่งร้าน'
# test = 'งานสกัดปูน-่กออิฐ-ฉาบปูน-ทาสี'
# test = 'จาะติดตั้งsupport  ทาสี ลากสาย'
# test = 'งานหุ้ม Insuฯ'
# test = 'insaall insult'
# test = 'weddding, pant'
# test = 'ตัดเชือม และ weding'
# ---------------------------------------------- #

TestSpellCheck(test)