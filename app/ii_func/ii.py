# import data and function
# from ii_func.data_ii import *
# from ii_func.embed_text_ii import *
# from clean import *

from .data_ii import *
from .embed_text_ii import *
from ..clean_func import clean

#import library
import re # regex
from deep_translator import GoogleTranslator # translate th -> en
import torch # compare between embed text
import pandas as pd # Dataframe
import numpy as np # use with number
from sentence_transformers import SentenceTransformer, util # embed file

import pickle # load pickle file

from typing import List # define input/output

model_url = './Model/sentence-transformers_msmarco-distilbert-base-dot-prod-v3' # folder model
model_ii = SentenceTransformer(model_url) # load model

# Dict to stored accident classification
store_classification = {
    'case_classification': []
}

# Dict to stored in store_classification['case_classification']
case_classification_to_store = {
    'name': "",
    'count': 0
}
# loop get all accident classification from ii data
for i in range(len(count_unique_classification)):
    case_classification_to_store['name'] = count_unique_classification[i]
    case_classification_to_store['count'] = 0
    store_classification['case_classification'].append(
        case_classification_to_store)
    case_classification_to_store = {
        'name': "",
        'count': 0
    }
# Dict stored statistic of accident (count year)
store_stat_acc = {
    'data': []
}
# Dict to stored in store_stat_acc['data]
data_count_acc = {
    'year_th': 0,
    'year_en': 0,
    'all_count': 0,
    'nm': 0,
    'hnm': 0,
    'lv1': 0,
    'lv2': 0,
    'lv3': 0,
}
# loop get all year into 'store_stat_acc'
for i in range(len(count_unique_Y)):
    data_count_acc['year_th'] = count_unique_Y[i]
    data_count_acc['year_en'] = count_unique_Y[i]-543
    store_stat_acc['data'].append(data_count_acc)
    data_count_acc = {
        'year_th': 0,
        'year_en': 0,
        'all_count': 0,
        'nm': 0,
        'hnm': 0,
        'lv1': 0,
        'lv2': 0,
        'lv3': 0,
    }
# ------------ response model equal to search_engine_ii -----------------------
ca_pa = {
    'all_ca': [],
    'all_pa': []
}

form_ii = {
    'find_count': [],
    'risk_score': [],
    'all_ca': [],
    'all_pa': [],
    'most_similar': {
        "type_acc": "",
        "case": []
    },
    'nm': {
        'ii_count': [],
        'ii_count_real': [],
        'case': [],
        'relate': {
            'case': []
        }
    },
    'hnm': {
        'ii_count': [],
        'ii_count_real': [],
        'case': [],
        'relate': {
            'case': []
        }
    },
    'lv1': {
        'ii_count': [],
        'ii_count_real': [],
        'case': [],
        'relate': {
            'case': []
        }
    },
    'lv2': {
        'ii_count': [],
        'ii_count_real': [],
        'case': [],
        'relate': {
            'case': []
        }
    },
    'lv3': {
        'ii_count': [],
        'ii_count_real': [],
        'case': [],
        'relate': {
            'case': []
        }
    }
}
# -------------------------------------------------------

def update_ii() -> None:
    """
    use to update ii data
    (this method is the same as restart app service)
    """
    # ------------ set variable to use global ----------------------------------
    # -------------------ii data ------------------------------
    global df_case # Dataframe ii
    global case_DocNo # DocNo
    global case_capa_IINO # IINO
    global case_IncidentCat # IncidentCategory
    global case_Incidentlevel # Severity
    global case_name # IncidentName
    global case_detail # IncidentDetail
    global case_cause # Cause
    global case_human # HumanImpact
    global case_name_en  # IncidentName_en
    global case_detail_en # IncidentDetail_en
    global case_cause_en # Cause_en
    global case_name_display # IncidentName_display
    global case_detail_display # IncidentDetail_display
    global case_cause_display # Cause_display
    global case_prop # PropertyImpact
    global case_env # EnvironmentImpact
    global case_date_Y # Y
    global case_classification # IncidentClassification
    global case_companyLo # LocationCompanyName
    global case_IncidentType  # IncidentType
    global count_unique_Y # stored unique Y
    global count_unique_classification  # stored unique IncidentClassification
    # --------------- capa data -----------------------------------
    global df_capa # Dataframe capa
    global capa_IINO  # IINO
    global capa_LLNO # LLNO
    global capa_CauseName  # CauseName
    global capa_CauseType  # CauseType
    global capa_CAPAName  # CAPAName
    global capa_CAPAType  # CAPAType
    # ---------- embedding -------------------------------------------
    global corpus_embeddings
    # ----------------------------------------------------------------------------------------
    # from ..connect_db import con # import data for connecting to database

    # SQL query command (ii data) 
    df_case = pd.read_csv("./SMIT_Data/SMIT2_Data/ii/ii_split_column_translate_all_display.csv", encoding='utf-8')

    # stored data in variabled
    case_DocNo = df_case['DocNo'].to_numpy()
    case_capa_IINO = df_case['IINo'].to_numpy()
    case_IncidentCat = df_case['IncidentCategory'].to_numpy()
    case_Incidentlevel = df_case['Severity'].to_numpy()
    case_name = df_case['IncidentName'].to_numpy()
    case_detail = df_case['IncidentDetail'].to_numpy()
    case_cause = df_case['Cause'].to_numpy()
    case_human = df_case['HumanImpact'].to_numpy()
    case_prop = df_case['PropertyImpact'].to_numpy()
    case_env = df_case['EnvironmentImpact'].to_numpy()
    case_date_Y = df_case['Y'].to_numpy()
    # change Y data to int [user to detect error in excel file when Y = null (present: in database don't found this problem)]
    for i in range(len(case_date_Y)):
        case_date_Y[i] = int(float(case_date_Y[i]))
    case_classification = df_case['IncidentClassification'].to_numpy()
    case_companyLo = df_case['LocationCompanyName'].to_numpy()
    case_IncidentType = df_case['IncidentType'].to_numpy()
    # removing duplicate IncidentClassification (count to calculate statistic in weight of classification type (fire/explotion = 1))
    count_unique_classification = list(set(case_classification))
    # removing duplicate Y (count to calculate statistic (find all accident in each year))
    count_unique_Y = list(set(case_date_Y))
    # sort smallest to maximum (eg. 2543,...,2564)
    count_unique_Y.sort()

    # from ..connect_db import con # connecting to db
    # ------- SQL query command (CAPA data)--------------
    # query = "SELECT * FROM capa_Data"
    df_capa =  pd.read_csv("./SMIT_Data/SMIT2_Data/ii/capa.csv", encoding='utf-8')
    # -----------------------------------------
    capa_IINO = df_capa['IINo'].to_numpy()
    capa_LLNO = df_capa['LLNo'].to_numpy()
    capa_CauseName = df_capa['CauseName'].to_numpy()
    capa_CauseType = df_capa['CauseType'].to_numpy()
    capa_CAPAName = df_capa['CAPAName'].to_numpy()
    capa_CAPAType = df_capa['CAPAType'].to_numpy()

    # --------- ii data --------------------------
    case_name_en = df_case['IncidentName_en'].to_numpy()
    case_detail_en = df_case['IncidentDetail_en'].to_numpy()
    case_cause_en = df_case['Cause_en'].to_numpy()

    case_name_display = df_case['IncidentName_display'].to_numpy()
    case_detail_display = df_case['IncidentDetail_display'].to_numpy()
    case_cause_display = df_case['Cause_display'].to_numpy()

    with open('./SMIT_Data/SMIT2_Data/embeddings_ii_new_all.pkl', "rb") as fIn:  # open pickle file (same as model_deployment\safety_equip_func\embed_text_safety_measure.py)
        stored_data = pickle.load(fIn)
        corpus_embeddings = stored_data['embeddings']
    
    return {"message":"Completely update embedding file"}


def terminate_ii_json() -> None:
    """
    reset variable to initial state
    """
    global store_classification  # Dict to stored accident classification
    global case_classification_to_store # Dict to stored in store_classification['case_classification']
    global store_stat_acc  # Dict stored statistic of accident (count year)
    global data_count_acc  # Dict to stored in store_stat_acc['data]
    global form_ii  # response model equal to search_engine_ii
    global ca_pa
    # -------------- same as line 22 -121 ---------------------------
    store_classification = {
        'case_classification': []
    }

    case_classification_to_store = {
        'name': "",
        'count': 0
    }

    for i in range(len(count_unique_classification)):
        case_classification_to_store['name'] = count_unique_classification[i]
        case_classification_to_store['count'] = 0
        store_classification['case_classification'].append(
            case_classification_to_store)
        case_classification_to_store = {
            'name': "",
            'count': 0
        }

    store_stat_acc = {
        'data': []
    }

    data_count_acc = {
        'year_th': 0,
        'year_en': 0,
        'all_count': 0,
        'nm': 0,
        'hnm': 0,
        'lv1': 0,
        'lv2': 0,
        'lv3': 0,
    }

    for i in range(len(count_unique_Y)):
        #     print(count_unique_Y[i])
        data_count_acc['year_th'] = count_unique_Y[i]
        data_count_acc['year_en'] = count_unique_Y[i]-543
        store_stat_acc['data'].append(data_count_acc)
        data_count_acc = {
            'year_th': 0,
            'year_en': 0,
            'all_count': 0,
            'nm': 0,
            'hnm': 0,
            'lv1': 0,
            'lv2': 0,
            'lv3': 0,
        }

    ca_pa = {
    'all_ca': [],
    'all_pa': []
    }

    form_ii = {
        'find_count': [],
        'risk_score': [],
        'all_ca': [],
        'all_pa': [],
        'most_similar': {
            "type_acc": "",
            "case": []
        },
        'nm': {
            'ii_count': [],
            'ii_count_real': [],
            'case': [],
            'relate': {
                'case': []
            }
        },
        'hnm': {
            'ii_count': [],
            'ii_count_real': [],
            'case': [],
            'relate': {
                'case': []
            }
        },
        'lv1': {
            'ii_count': [],
            'ii_count_real': [],
            'case': [],
            'relate': {
                'case': []
            }
        },
        'lv2': {
            'ii_count': [],
            'ii_count_real': [],
            'case': [],
            'relate': {
                'case': []
            }
        },
        'lv3': {
            'ii_count': [],
            'ii_count_real': [],
            'case': [],
            'relate': {
                'case': []
            }
        }
    }
    # --------------------------------------------------------------------


def update_ii_json(work: List[int], work_relate: List[int], sim_work: List[float], capa: List[List[int]], group_type: str):
    """
    update variable for response form_ii[(type of accident())]
    """
    global store_classification  # Dict to stored accident classification
    global case_classification_to_store # Dict to stored in store_classification['case_classification']
    global store_stat_acc  # Dict stored statistic of accident (count year)
    global data_count_acc  # Dict to stored in store_stat_acc['data]
    global form_ii  # response model equal to search_engine_ii
    # response model equal to case_Prop_search_engine_ii
    case = {
        'id': 0,
        'ii_incidentName': [],
        'ii_incidentDetail': [],
        'ii_incidentCause': [],
        'ii_capa_incidentCauseType': [],
        'ii_capa_incidentCauseName': [],
        'ii_ca': [],
        'ii_pa': [],
        'ii_humanImpact': [],
        'ii_propertyImpact': [],
        'ii_environmentImpact': [],
        'ii_classification': [],
        'ii_incidentType': [],
        'sim_score': []
    }
    # ----------------------------------------------
    capa_cause_name = []  # list to store CauseName (CAPA)
    capa_cause_type = []  # list to store CauseType (CAPA)
    capa_detail = []  # list to store CAPAName (CAPA)
    ca_pa_type = []  # list to store CAPAType (CAPA)

    for i in range(len(work)):
        # try to find capa from IINO
        try: 
            # loop store in list from line 365-368
            for list_capa in capa[i]:
                capa_cause_type.append(capa_CauseType[list_capa]) 
                capa_detail.append(capa_CAPAName[list_capa])
                capa_cause_name.append(capa_CauseName[list_capa])
                ca_pa_type.append(capa_CAPAType[list_capa])
            # replace NaN with '-'
            capa_cause_type = ['-' if x is np.nan else x for x in list(capa_cause_type[0])]
            capa_detail = ['-' if x is np.nan else x for x in list(capa_detail[0])]
            capa_cause_name = ['-' if x is np.nan else x for x in list(capa_cause_name[0])]
        except:
            # if not found use initial value
            capa_cause_type = []
            capa_detail = []
            capa_cause_name = []
        # store data in Dict 'case' by index
        case["id"] = i+1
        case["ii_incidentName"].append(case_name_display[work[i]])
        case["ii_incidentDetail"].append(case_detail_display[work[i]])
        case["ii_incidentCause"].append(case_cause_display[work[i]])
        case["ii_humanImpact"].append(case_human[work[i]])
        case["ii_propertyImpact"].append(case_prop[work[i]])
        case["ii_environmentImpact"].append(case_env[work[i]])
        case["ii_incidentType"].append(case_IncidentType[work[i]])
        case["ii_classification"].append(case_classification[work[i]])
        case["sim_score"].append(sim_work[i])
        # if find CAPA
        if(len(capa_cause_type) > 0):
            # stored unique CauseType(CAPA) , CauseName(CAPA)
            case["ii_capa_incidentCauseType"].append(list(dict.fromkeys(capa_cause_type)))
            case["ii_capa_incidentCauseName"].append(list(dict.fromkeys(capa_cause_name)))
            # loop in CAPAType
            for num in range(len(ca_pa_type[0])):
                # stored CA (corrective action) of accident that pass search criteria
                if(ca_pa_type[0][num] == 'CA'):
                    case["ii_ca"].append(capa_detail[num]) # of each case
                    if(not(work_relate[i])): # check if match case (pass criteria and have word matching)
                        form_ii['all_ca'].append(capa_detail[num]) # stored all CA case

                # stored PA (preventive action) of accident that pass search criteria
                elif(ca_pa_type[0][num] == 'PA'):
                    case["ii_pa"].append(capa_detail[num])  # of each case
                    # check if match case (pass criteria and have word matching)
                    if(not(work_relate[i])):
                        form_ii['all_pa'].append(capa_detail[num]) # stored all PA case

        # reset to initial
        capa_cause_type = []
        capa_detail = []
        capa_cause_name = []
        ca_pa_type = []

        if(len(case['ii_pa']) == 0):
            case['ii_pa'].append("-")
        if(len(case['ii_ca']) == 0):
            case['ii_ca'].append("-")

        if(not work_relate[i]):  # check if match case (pass criteria and have word matching)
            form_ii[group_type]["case"].append(case) # stored in main case (show in 'match case')
        else:
            # stored in relate case (show in 'relate case')
            form_ii[group_type]['relate']["case"].append(case)
        # reset to initial
        case = {
            'id': 0,
            'ii_incidentName': [],
            'ii_incidentDetail': [],
            'ii_incidentCause': [],
            'ii_capa_incidentCauseType': [],
            'ii_capa_incidentCauseName': [],
            'ii_ca': [],
            'ii_pa': [],
            'ii_humanImpact': [],
            'ii_propertyImpact': [],
            'ii_environmentImpact': [],
            'ii_classification': [],
            'ii_incidentType': [],
            'sim_score': []
        }
    # sort match case by similarity score
    if(len(form_ii[group_type]['case']) > 0):
        for i in range(len(form_ii[group_type]['case'])-1):
            for j in range(i+1, len(form_ii[group_type]['case'])):
                if(form_ii[group_type]['case'][i]['sim_score'] < form_ii[group_type]['case'][j]['sim_score']):
                    temp = form_ii[group_type]['case'][i]
                    form_ii[group_type]['case'][i] = form_ii[group_type]['case'][j]
                    form_ii[group_type]['case'][j] = temp
            form_ii[group_type]['case'][i]['id'] = i+1 # change id to range (use to ranging top 3)
        form_ii[group_type]['case'][len(form_ii[group_type]['case'])-1]['id'] = len(form_ii[group_type]['case'])
    else:
        form_ii[group_type]['case'] = [
            {
            'id': -1,
            'ii_incidentName': ["-"],
            'ii_incidentDetail': ["-"],
            'ii_incidentCause': ["-"],
            'ii_capa_incidentCauseType': ["-"],
            'ii_capa_incidentCauseName': ["-"],
            'ii_ca': ["-"],
            'ii_pa': ["-"],
            'ii_humanImpact': ["-"],
            'ii_propertyImpact': ["-"],
            'ii_environmentImpact': ["-"],
            'ii_classification': ["-"],
            'ii_incidentType': ["-"],
            'sim_score': [0]
            }
        ]
    # sort relate case by similarity score
    if(len(form_ii[group_type]['relate']['case']) > 0):
        for i in range(len(form_ii[group_type]['relate']['case'])-1):
            for j in range(i+1, len(form_ii[group_type]['relate']['case'])):
                if(form_ii[group_type]['relate']['case'][i]['sim_score'] < form_ii[group_type]['relate']['case'][j]['sim_score']):
                    temp = form_ii[group_type]['relate']['case'][i]
                    form_ii[group_type]['relate']['case'][i] = form_ii[group_type]['relate']['case'][j]
                    form_ii[group_type]['relate']['case'][j] = temp
            form_ii[group_type]['relate']['case'][i]['id'] = i+1 # change id to range (use to ranging top 3)
        form_ii[group_type]['relate']['case'][len(form_ii[group_type]['relate']['case'])-1]['id'] = len(form_ii[group_type]['relate']['case'])
    else:
        form_ii[group_type]['relate']['case'] = [
            {
            'id': -1,
            'ii_incidentName': ["-"],
            'ii_incidentDetail': ["-"],
            'ii_incidentCause': ["-"],
            'ii_capa_incidentCauseType': ["-"],
            'ii_capa_incidentCauseName': ["-"],
            'ii_ca': ["-"],
            'ii_pa': ["-"],
            'ii_humanImpact': ["-"],
            'ii_propertyImpact': ["-"],
            'ii_environmentImpact': ["-"],
            'ii_classification': ["-"],
            'ii_incidentType': ["-"],
            'sim_score': [0]
            }
        ]

def prepare_data_search_ii(data):
    # remove quantity from text (eg. เมตร, กิโลมตร etc.)
    remove_quan = clean.remove_quantity(data["name"])
    # replace connect word with comma(,)
    regex_replaceSW = re.compile(r"\s(and)\s|(และ)")
    clean_SW = regex_replaceSW.sub(",", remove_quan.strip())

    # if user confirm function correct is correct use it
    if(data['correct']):
        clean_text = clean.cleaning([clean_SW])
    else:
        clean_text = [clean_SW]
    # remove tag equipment from text
    clean_text = clean.remove_tag(clean_text[0])
    # remove symbol
    clean_text = clean.remove_data_parentheses(clean_text)
    # split work
    split_task = re.split(r'\,|\/', clean_text)
    temp_split_task = []
    # remove space or empty element from list of work
    for i in range(len(split_task)):
        split_task[i] = split_task[i].strip()
        if(split_task[i] != ""):
            temp_split_task.append(split_task[i])
    split_task = temp_split_task

    queries = [] # list stored Work name (English)
    tag_all = [] # list stored tag equipment
    token = [] # list stored token(คำที่ถูกตัดแบ่ง) (Thai)
    # translate list of work to english if error (limit of library) use same text as before
    for split_word in split_task:
        try:
            queries.append(GoogleTranslator(source='auto', target='en').translate(split_word))
            tag = clean.find_tag(split_word)
            tag_all = tag_all + tag
        except:
            queries = queries
    tag_all = list(set(tag_all))
    token_eng = [] # token (English)
    # loop check part-of-speech (English)
    for sentences in queries:
        token_eng.append(clean.check_pos_en(sentences))
    # loop tokenize thai Work name
    for split_word in split_task:
        token.append(clean.tokenize_deepcut(split_word, tag_all))
    # remove token that only have number/symbol
    token_remove_num = []
    for i in range(len(token)):
        token_remove_num.append(clean.remove_num(token[i]))
    token = token_remove_num
    # loop check part-of-speech (Thai)
    pos_token = []
    for i in range(len(token)):
        pos_token.append(clean.check_pos_th([token[i]]))
    token = pos_token
    # return
    return queries, token, split_task, token_eng


def search_ii(data, ResponseCase):
    global form_ii # use global variable
    terminate_ii_json() # reset to initial value
    queries, token, split_task, token_eng = prepare_data_search_ii(data) #preprocess data

    # company = data["company"].upper()
    top_k = min(len(case_name), len(case_name)) # get top (in this case want to find all accident)
    # accident level 1
    work_lv_1 = [] # index of case
    work_lv_1_is_relate = [] # boolean separate match case, relate case
    capa_lv_1 = [] # stored index of capa
    sim_work_lv_1 = [] # stored similarity score
    # accident level 2
    work_lv_2 = []
    work_lv_2_is_relate = []
    capa_lv_2 = []
    sim_work_lv_2 = []
    # accident level 3
    work_lv_3 = []
    work_lv_3_is_relate = []
    capa_lv_3 = []
    sim_work_lv_3 = []
    # Near miss
    work_lv_NM = []
    work_lv_NM_is_relate = []
    capa_lv_NM = []
    sim_work_lv_NM = []
    # High potential near miss
    work_lv_hNM = []
    work_lv_hNM_is_relate = []
    capa_lv_hNM = []
    sim_work_lv_hNM = []
    # stored all word that pass search criteria
    work_all = []

    temp_most_sim = [] # temporary find most similar case (have greatest similarity score)
    # stored count of accident
    num_1 = 0 
    num_2 = 0
    num_3 = 0
    num_NM = 0
    num_hNM = 0
    num_all = 0

    # queries = (GoogleTranslator(source='auto', target='en').translate(data['name'].tolist()))

    # loop in list of Work name
    for query in range(len(queries)):

        query_embedding = model_ii.encode(queries[query], convert_to_tensor=True) # encode Work name

        # use cosine-similarity and torch.topk (find top ...(in this project use all of data)....)
        cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k)
        # initial flag to separate case that pass criteria (True)
        pass_flag = False

        num_word = 0 # word matching score in each round
        all_num_word = 0 # stored word matching
        # loop in length of data
        for i in range(len(top_results[0])):
            index_ii_DocNo = int(top_results[1][i]) # get index of case
            # print(len(top_results[1]), index_ii_DocNo, index_ii_DocNo, len(case_capa_IINO), len(corpus_embeddings))
            index_capa = list(np.where(capa_IINO == case_capa_IINO[index_ii_DocNo])) # use index of case to find if this case have CAPA (use data from IINO)
            # loop in all year in ii data if found match year add count
            for year in range(len(count_unique_Y)):
                if(case_date_Y[index_ii_DocNo] == count_unique_Y[year]):
                    store_stat_acc['data'][year]['all_count'] = store_stat_acc['data'][year]['all_count'] + 1
            # if similarity score greater than 0.7 -> pass criteria (pass_flag = True)
            if(float(top_results[0][i]) > 0.7):
                top_results[0][i] = float(top_results[0][i])
                pass_flag = True
            # if similarity score greater or equal to 0.3 and length of work name > 1 (block error when work name have 1 character (eg. str-a,b(block)))
            elif(float(top_results[0][i]) >= 0.3 and len(split_task[query]) > 1):
                # if find Thai language in work name
                if(clean.contain_thai_word(split_task[query])):
                    token[query] = list(dict.fromkeys(token[query])) # remove duplicate data (same order(สนใจลำดับโดยถ้าเจอคำซ้ำตัดด้านหลังออก))
                    # temporary variable detail
                    temp_detail = 0 # present position
                    len_nearest_detail = 0 # nearest position from previous word
                    # temporary variable name
                    temp_name = 0
                    len_nearest_name = 0
                    # temporary variable cause
                    temp_cause = 0
                    len_nearest_cause = 0
                    # detect fist found word
                    first_word = False
                    # loop in token (Thai)
                    for word in range(len(token[query])):
                        # if word match in detail
                        if((case_detail[index_ii_DocNo].lower()).find(token[query][word]) != -1):
                            # temporary weight = 0 (first found) and length of token = 1 (eg. 'ทาสี' )
                            if(temp_detail == 0 and len(token[query]) == 1):
                                # get present position
                                temp_detail = (case_detail[index_ii_DocNo].lower()).find(token[query][word])
                                # get nearest position from (present position + length of present word)
                                len_nearest_detail = temp_detail + len(token[query][word])
                                # add to  word matching score in each round
                                num_word = num_word+1
                            # temporary weight = 0 (first found) and length of token > 1 (eg. 'รื้อ','นั่งร้าน' )
                            elif(temp_detail == 0 and len(token[query]) > 1):
                                # get present position
                                temp_detail = (case_detail[index_ii_DocNo].lower()).find(token[query][word])
                                # get nearest position from (present position + length of present word)
                                len_nearest_detail = temp_detail + len(token[query][word])
                                # set variable to found
                                first_word = True
                            # position that find word is greater than nearest position from previous word
                            elif((case_detail[index_ii_DocNo].lower()).find(token[query][word]) >= len_nearest_detail):
                                # first found word previously
                                if(first_word):
                                    # add weight
                                    num_word = num_word+1
                                    # set variable to not found
                                    first_word = False
                                # get present position
                                temp_detail = (case_detail[index_ii_DocNo].lower()).find(token[query][word])
                                # add weight from present score + (nearest position from previous word / present position)
                                num_word = num_word +(len_nearest_detail/temp_detail)
                                # get nearest position from (present position + length of present word)
                                len_nearest_detail = temp_detail + len(token[query][word])
                        # same as before (change to find in IncidentName) 
                        elif((case_name[index_ii_DocNo].lower()).find(token[query][word]) != -1):
                            if(temp_name == 0 and len(token[query]) == 1):
                                temp_name = (case_name[index_ii_DocNo].lower()).find(token[query][word])
                                len_nearest_name = temp_name + len(token[query][word])
                                num_word = num_word+1
                            elif(temp_name == 0 and len(token[query]) > 1):
                                temp_name = (case_name[index_ii_DocNo].lower()).find(token[query][word])
                                len_nearest_name = temp_name + len(token[query][word])
                                first_word = True
                            elif((case_name[index_ii_DocNo].lower()).find(token[query][word]) >= len_nearest_name):
                                if(first_word):
                                    num_word = num_word+1
                                    first_word = False
                                temp_name = (case_name[index_ii_DocNo].lower()).find(token[query][word])
                                num_word = num_word + (len_nearest_name/temp_name)
                                len_nearest_name = temp_name + len(token[query][word])
                        # same as before (change to find in Cause)
                        if((case_cause[index_ii_DocNo].lower()).find(token[query][word]) != -1):
                            if(temp_cause == 0 and len(token[query]) == 1):
                                temp_cause = (case_cause[index_ii_DocNo].lower()).find(token[query][word])
                                len_nearest_cause = temp_cause + len(token[query][word])
                                num_word = num_word+1
                            elif(temp_cause == 0 and len(token[query]) > 1):
                                temp_cause = (case_cause[index_ii_DocNo].lower()).find(token[query][word])
                                len_nearest_cause = temp_cause + len(token[query][word])
                                first_word = True
                            elif((case_cause[index_ii_DocNo].lower()).find(token[query][word]) >= len_nearest_cause):
                                if(first_word):
                                    num_word = num_word+1
                                    first_word = False
                                temp_cause = (case_cause[index_ii_DocNo].lower()).find(token[query][word])
                                num_word = num_word + (len_nearest_name/temp_cause)
                                len_nearest_cause = temp_cause + len(token[query][word])
                    # try to block error when Work name don't have length (maybe cut from part-of speech)
                    try:
                        all_num_word = num_word/len(token[query])
                    except:
                        all_num_word = 0
                # when not found Thai language in Work name (working same as search in Thai but change data to _en)
                else:
                    if(len(token_eng[query]) > 0):
                        temp_detail = 0
                        len_nearest_detail = 0
                        temp_name = 0
                        len_nearest_name = 0
                        temp_cause = 0
                        len_nearest_cause = 0
                        for word in range(len(token_eng[query])):
                            # print(token_eng[query][word])
                            if((case_detail_en[index_ii_DocNo].lower()).find(token_eng[query][word]) != -1):
                                if(temp_detail == 0 and len(token_eng[query]) == 1):
                                    temp_detail = (case_detail_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    len_nearest_detail = temp_detail + len(token_eng[query][word])
                                    num_word = num_word+1
                                elif(temp_detail == 0 and len(token_eng[query]) > 1):
                                    temp_detail = (case_detail_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    len_nearest_detail = temp_detail + len(token_eng[query][word])
                                elif((case_detail_en[index_ii_DocNo].lower()).find(token_eng[query][word]) >= len_nearest_detail):
                                    num_word = num_word+1
                                    temp_detail = (case_detail_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    num_word = num_word + (len_nearest_detail/temp_detail)
                                    len_nearest_detail = temp_detail + len(token_eng[query][word])
                            elif((case_name_en[index_ii_DocNo].lower()).find(token_eng[query][word]) != -1):
                                if(temp_name == 0 and len(token_eng[query]) == 1):
                                    temp_name = (case_name_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    len_nearest_name = temp_name + len(token_eng[query][word])
                                    num_word = num_word+1
                                elif(temp_name == 0 and len(token_eng[query]) > 1):
                                    temp_name = (case_name_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    len_nearest_name = temp_name + len(token_eng[query][word])
                                elif((case_name_en[index_ii_DocNo].lower()).find(token_eng[query][word]) >= len_nearest_name):
                                    num_word = num_word+1
                                    temp_name = (case_name_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    num_word = num_word + (len_nearest_name/temp_name)
                                    len_nearest_name = temp_name + len(token_eng[query][word])
                            if((case_cause_en[index_ii_DocNo].lower()).find(token_eng[query][word]) != -1):
                                if(temp_cause == 0 and len(token_eng[query]) == 1):
                                    temp_cause = (case_cause_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    len_nearest_cause = temp_cause + len(token_eng[query][word])
                                    num_word = num_word+1
                                elif(temp_cause == 0 and len(token_eng[query]) > 1):
                                    temp_cause = (case_cause_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    len_nearest_cause = temp_cause + len(token_eng[query][word])
                                elif((case_cause_en[index_ii_DocNo].lower()).find(token_eng[query][word]) >= len_nearest_cause):
                                    num_word = num_word+1
                                    temp_cause = (case_cause_en[index_ii_DocNo].lower()).find(token_eng[query][word])
                                    num_word = num_word + (len_nearest_name/temp_cause)
                                    len_nearest_cause = temp_cause + len(token_eng[query][word])
                        try:
                            all_num_word = num_word/len(token_eng[query])
                        except:
                            all_num_word = 0
                # reset to initial value
                num_word = 0
                # if stored word matching > 0.5 (match more than half of work name) and similarity score > 0.3
                if(all_num_word >= 0.5 and float(top_results[0][i]) > 0.3):
                    top_results[0][i] = ((float(top_results[0][i])) + (all_num_word))/2 # add score to similarity score and balanced
                    if(float(top_results[0][i]) > 0.65):
                        pass_flag = True # if score > 0.65 pass criteria
            # if pass (criteria or similarity score greater or equal to 0.4) and don't pass criteria previously (in case of many Work name)
            if((pass_flag or float(top_results[0][i])>=0.4) and index_ii_DocNo not in work_all):
                # stored work that pass criteria 
                work_all.append(index_ii_DocNo)
                # ------------------- accident level 1 -----------------------------------
                if(case_Incidentlevel[index_ii_DocNo] == 'Level 1' and case_IncidentCat[index_ii_DocNo] == 'Accident' ):
                    # found CAPA -> get
                    if(len(index_capa[0]) > 0):
                        work_lv_1.append(index_ii_DocNo)
                        capa_lv_1.append(index_capa)
                        sim_work_lv_1.append(float(top_results[0][i]))
                        if(pass_flag):
                            work_lv_1_is_relate.append(False) # match case
                        else:
                            work_lv_1_is_relate.append(True) #relate case
                    if(pass_flag): # match case
                        num_1 = num_1 + 1 # count
                        num_all = num_all+1 # count all
                        # stored year statistic
                        for year in range(len(count_unique_Y)):
                            if(case_date_Y[index_ii_DocNo] == count_unique_Y[year]):
                                store_stat_acc['data'][year]['lv1'] = store_stat_acc['data'][year]['lv1'] + 1
                        # stored IncidentClassification statistic
                        for type_acc in range(len(count_unique_classification)):
                            if(case_classification[index_ii_DocNo] == count_unique_classification[type_acc]):
                                store_classification['case_classification'][type_acc]['count'] = store_classification['case_classification'][type_acc]['count'] + 1
                # ------------------- accident level 2 -----------------------------------
                elif(case_Incidentlevel[index_ii_DocNo] == 'Level 2' and case_IncidentCat[index_ii_DocNo] == 'Accident'):
                    if(len(index_capa[0]) > 0):
                        work_lv_2.append(index_ii_DocNo)
                        capa_lv_2.append(index_capa)
                        sim_work_lv_2.append(float(top_results[0][i]))
                        if(pass_flag):
                            work_lv_2_is_relate.append(False)
                        else:
                            work_lv_2_is_relate.append(True)
                    elif(len(index_capa[0]) == 0):
                        work_lv_2.append(['-'])
                        capa_lv_2.append(['-'])
                        sim_work_lv_2.append(['-'])
                        if(pass_flag):
                            work_lv_2_is_relate.append(False)
                        else:
                            work_lv_2_is_relate.append(True)
                    if(pass_flag):
                        num_2 = num_2 + 1
                        num_all = num_all+1
                        for year in range(len(count_unique_Y)):
                            if(case_date_Y[index_ii_DocNo] == count_unique_Y[year]):
                                store_stat_acc['data'][year]['lv2'] = store_stat_acc['data'][year]['lv2'] + 1
                        for type_acc in range(len(count_unique_classification)):
                            if(case_classification[index_ii_DocNo] == count_unique_classification[type_acc]):
                                store_classification['case_classification'][type_acc]['count'] = store_classification['case_classification'][type_acc]['count'] + 1
                # ------------------- accident level 3 -----------------------------------
                elif(case_Incidentlevel[index_ii_DocNo] == 'Level 3' and case_IncidentCat[index_ii_DocNo] == 'Accident'):
                    if(len(index_capa[0]) > 0):
                        work_lv_3.append(index_ii_DocNo)
                        capa_lv_3.append(index_capa)
                        sim_work_lv_3.append(float(top_results[0][i]))
                        if(pass_flag):
                            work_lv_3_is_relate.append(False)
                        else:
                            work_lv_3_is_relate.append(True)
                    if(pass_flag):
                        num_3 = num_3 + 1
                        num_all = num_all+1
                        for year in range(len(count_unique_Y)):
                            if(case_date_Y[index_ii_DocNo] == count_unique_Y[year]):
                                store_stat_acc['data'][year]['lv3'] = store_stat_acc['data'][year]['lv3'] + 1
                        for type_acc in range(len(count_unique_classification)):
                            if(case_classification[index_ii_DocNo] == count_unique_classification[type_acc]):
                                store_classification['case_classification'][type_acc]['count'] = store_classification['case_classification'][type_acc]['count'] + 1
                # ------------------- Near miss -----------------------------------
                elif(case_IncidentCat[index_ii_DocNo] == 'Near Miss'):
                    if(len(index_capa[0]) > 0):
                        work_lv_NM.append(index_ii_DocNo)
                        capa_lv_NM.append(index_capa)
                        sim_work_lv_NM.append(float(top_results[0][i]))
                        if(pass_flag):
                            work_lv_NM_is_relate.append(False)
                        else:
                            work_lv_NM_is_relate.append(True)
                    if(pass_flag):
                        num_NM = num_NM + 1
                        num_all = num_all+1
                        for year in range(len(count_unique_Y)):
                            if(case_date_Y[index_ii_DocNo] == count_unique_Y[year]):
                                store_stat_acc['data'][year]['nm'] = store_stat_acc['data'][year]['nm'] + 1
                        for type_acc in range(len(count_unique_classification)):
                            if(case_classification[index_ii_DocNo] == count_unique_classification[type_acc]):
                                store_classification['case_classification'][type_acc]['count'] = store_classification['case_classification'][type_acc]['count'] + 1
                # ------------------- High Potential Near Miss -----------------------------------
                elif(case_IncidentCat[index_ii_DocNo] == 'High Potential Near Miss'):
                    if(len(index_capa[0]) > 0):
                        work_lv_hNM.append(index_ii_DocNo)
                        capa_lv_hNM.append(index_capa)
                        sim_work_lv_hNM.append(
                            float(top_results[0][i]))
                        if(pass_flag):
                            work_lv_hNM_is_relate.append(False)
                        else:
                            work_lv_hNM_is_relate.append(True)
                    if(pass_flag):
                        num_hNM = num_hNM + 1
                        num_all = num_all+1
                        for year in range(len(count_unique_Y)):
                            if(case_date_Y[index_ii_DocNo] == count_unique_Y[year]):
                                store_stat_acc['data'][year]['hnm'] = store_stat_acc['data'][year]['hnm'] + 1
                        for type_acc in range(len(count_unique_classification)):
                            if(case_classification[index_ii_DocNo] == count_unique_classification[type_acc]):
                                store_classification['case_classification'][type_acc]['count'] = store_classification['case_classification'][type_acc]['count'] + 1
                # reset to initial value (if have case pass criteria)
                pass_flag = False
                num_word = 0
                all_num_word = 0
                num_word = 0
            # reset to initial value (if don't have case pass criteria)
            pass_flag = False
            num_word = 0
            all_num_word = 0
            num_word = 0
    # confirm variable in type list
    work_lv_1 = list(work_lv_1)
    work_lv_2 = list(work_lv_2)
    work_lv_3 = list(work_lv_3)
    work_lv_hNM = list(work_lv_hNM)
    work_lv_NM = list(work_lv_NM)
    # store count all case
    num_all = num_1+num_2+num_3+num_hNM+num_NM
    # if have accident stored data
    if(num_all > 0):
        form_ii["find_count"].append(num_all)
        form_ii["nm"]["ii_count_real"].append(num_NM) # Integer
        form_ii["nm"]["ii_count"].append(round(((num_NM/num_all)*100), 2)) # percent
        form_ii["hnm"]["ii_count_real"].append(num_hNM)
        form_ii["hnm"]["ii_count"].append(round(((num_hNM/num_all)*100), 2))
        form_ii["lv1"]["ii_count_real"].append(num_1)
        form_ii["lv1"]["ii_count"].append(round(((num_1/num_all)*100), 2))
        form_ii["lv2"]["ii_count_real"].append(num_2)
        form_ii["lv2"]["ii_count"].append(round(((num_2/num_all)*100), 2))
        form_ii["lv3"]["ii_count_real"].append(num_3)
        form_ii["lv3"]["ii_count"].append(round(((num_3/num_all)*100), 2))
        
        if not work_lv_3:
            print('\nไม่มีอุบัติเหตุ level 3')
            update_ii_json(work_lv_3, work_lv_3_is_relate,
                           sim_work_lv_3, capa_lv_3, "lv3")
        else: # call function update case that pass criteria to update form_ii 
            update_ii_json(work_lv_3, work_lv_3_is_relate,
                           sim_work_lv_3, capa_lv_3, "lv3")
        # ------------------- accident level 2 -----------------------------------
        if not work_lv_2:
            print('\nไม่มีอุบัติเหตุ level 2')
            update_ii_json(work_lv_2, work_lv_2_is_relate,
                           sim_work_lv_2, capa_lv_2, "lv2")
        else:
            update_ii_json(work_lv_2, work_lv_2_is_relate,
                           sim_work_lv_2, capa_lv_2, "lv2")
        # ------------------- accident level 1 -----------------------------------
        if not work_lv_1:
            print('\nไม่มีอุบัติเหตุ level 1')
            update_ii_json(work_lv_1, work_lv_1_is_relate,
                           sim_work_lv_1, capa_lv_1, "lv1")
        else:
            update_ii_json(work_lv_1, work_lv_1_is_relate,
                           sim_work_lv_1, capa_lv_1, "lv1")
        # ------------------- High Potential Near Miss -----------------------------------
        if not work_lv_hNM:
            print('\nไม่มี High Potential Near Miss')
        else:
            update_ii_json(work_lv_hNM, work_lv_hNM_is_relate,
                           sim_work_lv_hNM, capa_lv_hNM, "hnm")
        # ------------------- Near Miss -----------------------------------
        if not work_lv_NM:
            print('\nไม่มี Near Miss')
        else:
            update_ii_json(work_lv_NM, work_lv_NM_is_relate,
                           sim_work_lv_NM, capa_lv_hNM, "nm")
    # initial variable
    temp = 0
    sum_acc = 100 # initial  [from risk score equation]
    sum_case = 0 # temporary store sum
    fire = 0.5  # initial if not have case fire/explotion [from risk score equation]
    # find if have fire/explotion if found set 1 and exit loop
    for i in range(len(store_classification['case_classification'])):
        if(store_classification['case_classification'][i]['name'] == "Fire & Explosion" and store_classification['case_classification'][i]['count'] > 0):
            fire = 1
            break
    # multiply to initial
    sum_acc = sum_acc * fire
    # stored count year that not have accident
    none_accident = 0
    # loop calculate [from risk score equation]
    for i in range(len(store_stat_acc['data'])):
        if(store_stat_acc['data'][i]['all_count'] != 0):
            temp = 0
            temp = temp + (store_stat_acc['data'][i]['nm']*0.2)
            temp = temp + (store_stat_acc['data'][i]['hnm']*0.4)
            temp = temp + (store_stat_acc['data'][i]['lv1']*0.6)
            temp = temp + (store_stat_acc['data'][i]['lv2']*0.8)
            temp = temp + (store_stat_acc['data'][i]['lv3']*1)
            temp = temp/store_stat_acc['data'][i]['all_count']
            sum_case = sum_case + temp
        else:
            none_accident = none_accident+1
    # block error if don't found accident (all) in every year
    try:
        # max (min_score,min(1,score calculate from year))
        sum_case = max(0.5, min(1, (sum_case/(len(store_stat_acc['data'])-none_accident)) * 100))
    except:
        sum_case = 0.5
    # multiply to initial
    sum_acc = sum_acc * sum_case
    # stored in form _ii to response
    form_ii['risk_score'].append(sum_acc)
    # ------------- find most similar case ---------------------
    # initial accident type
    type_acc_most = ['lv3', 'lv2', 'lv1', 'hnm', 'nm']
    temp_most_sim = [] # temporary store most similar case
    type_most_sim = []  # temporary store type of most similar case
    # loop in accident type
    for i in range(len(type_acc_most)):
        # block error if don't found accident case
        try:
            temp_most_sim.append(form_ii[type_acc_most[i]]['case'][0]['sim_score'][0])
            type_most_sim.append(type_acc_most[i])
        except:
            temp_most_sim = temp_most_sim
    index_most_sim = 0
    index_type_most_sim = ''
    # ------------------- sort ---------------------------------
    for i in range(len(temp_most_sim)):
        if(temp_most_sim[i] > index_most_sim):
            index_most_sim = temp_most_sim[i]
            index_type_most_sim = type_most_sim[i]
    try:
        form_ii['most_similar']['case'].append(form_ii[index_type_most_sim]['case'][0])
        form_ii['most_similar']['type_acc'] = index_type_most_sim
    except:
        form_ii = form_ii
    # ----------------------------------------------------------------------
    if(ResponseCase == 'All ii'):
        form_ii['all_ca'] = list(dict.fromkeys(form_ii['all_ca']))
        form_ii['all_pa'] = list(dict.fromkeys(form_ii['all_pa']))

        return(form_ii)
    elif(ResponseCase == 'Only CAPA'):
        if len(list(dict.fromkeys(form_ii['all_ca']))) == 0 and list(dict.fromkeys(form_ii['all_ca'])) == 0:
            form_ii['all_ca'] = ["No Data"]
            form_ii['all_pa'] = ["No Data"]
        else:
            ca_pa['all_ca'] = list(dict.fromkeys(form_ii['all_ca']))
            ca_pa['all_pa'] = list(dict.fromkeys(form_ii['all_pa']))
        
        return(ca_pa)
