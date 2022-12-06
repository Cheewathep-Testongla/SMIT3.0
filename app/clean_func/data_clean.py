import pandas as pd
import re
from collections import Counter

# ----- function remove space (start,end), carriage return(\r), new line/enter(\n), tab(\t)
def remove_space(text):
    text = text.replace('\r', '')
    text = text.replace('\n', '')
    text = text.replace('\t', '')
    text = text.strip()
    return text
# -----------------------------------------------------------------------------------------
correct_data = pd.read_csv("./SMIT_Data/SMIT2_Data/dictionary/correct_word_th.csv", encoding='utf-8').to_numpy() # call file correct data - for normalization
initial_data = pd.read_csv("./SMIT_Data/SMIT2_Data/dictionary/initial.csv", encoding='utf-8').to_numpy() # call file stored initial -> full text
# --------- thai dict for tokenizing -------------------
thai_dict = []
f = open("./SMIT_Data/SMIT2_Data/dictionary/dictionary.txt", "r",encoding='utf-8')
Lines = f.readlines()
f.close()
count = 0
# Strips the newline character
for line in Lines:
    count += 1
    thai_dict.append(line.strip())
# ----------- stored quantity word to remove -----------------------
quantity_dict = []
f = open("./SMIT_Data/SMIT2_Data/dictionary/quantity.txt", "r",encoding='utf-8')
Lines = f.readlines()
f.close()
count = 0
# Strips the newline character
for line in Lines:
    count += 1
    quantity_dict.append(line.strip())
# normal dictionary (from public dictionary + word from screen in ii data) use regex find word and count word (Counter) (English)
WORDS_one = Counter(re.findall(r'\w+', (open('./SMIT_Data/SMIT2_Data/dictionary/en_dict.txt',encoding='utf-8').read()).lower()))
# normal dictionary (from public dictionary + word from screen in ii data) use regex find word and count word (Counter) (Thai)
dic_th_one = Counter(re.findall(r'([\u0E00-\u0E7F]+)', (open('./SMIT_Data/SMIT2_Data/dictionary/th_dict.txt',encoding='utf-8').read()).lower()))
# specific dictionary (from WPR_OneDoc.Work name) use regex find word and count word (Counter) (English)
work_freq_en = Counter(re.findall(r'\w+', (open('./SMIT_Data/SMIT2_Data/dictionary/dataset_not_clean_syllable_freq.txt',encoding='utf-8').read()).lower()))
# specific dictionary (from WPR_OneDoc.Work name) use regex find word and count word (Counter) (Thai)
work_freq_th = Counter(re.findall(r'([\u0E00-\u0E7F]+)', (open('./SMIT_Data/SMIT2_Data/dictionary/dataset_not_clean_syllable_freq.txt',encoding='utf-8').read()).lower()))
# combine normal and specific dictionary (English) - to correct data
WORDS = WORDS_one + work_freq_en
# combine normal and specific dictionary (Thai) - to correct data
dic_th = dic_th_one + work_freq_th
# ------ tag equipment data ----------------------------------
# !!! (currently use) !!!
data_elec = pd.read_csv('./SMIT_Data/SMIT2_Data/tag/Electrical List Report Temp.csv') # use Tag Name,Tag Description,Tag Type
data_equip = pd.read_csv('./SMIT_Data/SMIT2_Data/tag/Equipment List Report Temp.csv') # use Tag Name,Tag Description,Tag Type
data_instru = pd.read_csv('./SMIT_Data/SMIT2_Data/tag/Instrument Index Report Temp.csv') # use Tag No(->Tag Name),Tag Description,Tag Type
# !!! (don't use)
data_line = pd.read_csv('./SMIT_Data/SMIT2_Data/tag/Line List Report Temp.csv') # use Tag Name, Fluid (usually don't found : present -> don't use)
# data_moc = pd.read_csv('data/tag/Tag_List_MOC.csv')# use TagName(->Tag Name),Description(->Tag Description),Area  (form don't math with data in currently use)

data_instru.rename({'Tag No': 'Tag Name'}, axis=1, inplace=True) # change name to the same as other data
# data_moc.rename({'Description': 'Tag Description'}, axis=1, inplace=True) # change name to the same as other data
# data_moc.rename({'TagName': 'Tag Name'}, axis=1, inplace=True) # change name to the same as other data

data_equip['Tag Description'].fillna("-", inplace = True) # fill empty with '-'
data_instru['Tag Description'].fillna("-", inplace=True)  # fill empty with '-'
data_line['Fluid'].fillna("-", inplace = True) # fill empty with '-'
# data_moc['Tag Description'].fillna("-", inplace=True)  # fill empty with '-'

data_elec_tag_name = list(data_elec['Tag Name'].to_numpy()) # stored Electrical List Report Temp (name) in list
data_equip_tag_name= list(data_equip['Tag Name'].to_numpy()) # stored Equipment List Report Temp (name) in list
data_instru_tag_name = list(data_instru['Tag Name'].to_numpy()) # stored Instrument Index Report Temp (name) in list

tag_name_dict = list(data_elec_tag_name + data_equip_tag_name + data_instru_tag_name) # combine all tag equipment data (name) into one list

data_elec_list_des = list(data_elec['Tag Description'].to_numpy()) # stored Electrical List Report Temp (description) in list
data_equip_list_des = list(data_equip['Tag Description'].to_numpy()) # stored Equipment List Report Temp (description) in list
data_instru_list_des = list(data_instru['Tag Description'].to_numpy()) # stored Instrument Index Report Temp (description) in list

tag_des_dict = list(data_elec_list_des + data_equip_list_des + data_instru_list_des) # combine all tag equipment data (description) into one list

data_elec_list_type = list(data_elec['Tag Type'].to_numpy()) # stored Electrical List Report Temp (type) in list
data_equip_list_type = list(data_equip['Tag Type'].to_numpy()) # stored Equipment List Report Temp (type) in list
data_instru_list_type = list(data_instru['Tag Type'].to_numpy()) # stored Instrument Index Report Temp (type) in list

tag_type_dict = list(data_elec_list_type + data_equip_list_type + data_instru_list_type) # combine all tag equipment data (type) into one list

tag_dict = Counter(tag_name_dict) # count tag equipment (each tag have 1) - for correct

# -------- Work name -for levenshtein distance (correct sentences by find similar Work name) ----------------
# !!! SQL query command
# select_sql = "SELECT WorkName FROM [dbo].[WPR_OneDoc]"
df_work_name_db = pd.read_csv("./SMIT_Data/SMIT2_Data/work permit/Permit Data.csv", encoding='utf-8')
# drop empty
df_work_name_db = df_work_name_db.dropna()
# stored work name in list
list_work_name = list(df_work_name_db["WorkName"].to_numpy())
# loop use function remove_space
for i in range(len(list_work_name)):
    list_work_name[i] = remove_space(list_work_name[i])
# count work name - for use probability with levenshtein distance (most used is most probability to match)
list_work_name_freq = Counter(list_work_name)
# collect unique - for compare in levenshtein distance (save time than use all work (maybe work name have some repeat word))
list_work_name = list(set(list_work_name))

