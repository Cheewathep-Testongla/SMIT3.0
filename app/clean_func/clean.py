from typing import Callable, List, Set, Tuple, Dict

import pandas as pd 
import re # use regex
import deepcut # for tokenization
from pythainlp.spell.pn import NorvigSpellChecker # for correct
# from pythainlp.corpus import thai_stopwords # for remove stop word
from pythainlp import word_tokenize # tokenizing sentences by syllable (พยางค์)
from pythainlp.tag import pos_tag_sents # part-o-speech (thai)

import nltk # library nlp (English)
from nltk.stem import WordNetLemmatizer # for lemmatization
from nltk.corpus import wordnet # get part-of-speech

from fuzzywuzzy import fuzz  # levenshtein distance

nltk.download('universal_tagset') # load part-of-speech with universal tag (eg. N = NOUN)
nltk.download('punkt') # load tokenizer
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger') # load tagger of part-of-speech
nltk.download('wordnet') # load part-of-speech
#---------------------------------------------------------------------
from .data_clean import *

# -------------------- remove space ------------------------------------------------
def remove_space(text:str) -> str:
    """
    remove space (start,end), carriage return(\r), new line/enter(\n), tab(\t)
    """
    text = text.replace('\r','')
    text = text.replace('\n','')
    text = text.replace('\t','')
    text = text.strip()
    return text
# -------------------- levenshtein distance ------------------------------------------------
def sim_work_prob(word:str, N:int=sum(list_work_name_freq.values())) -> float: 
    """
    variable -> list_work_name_freq from `data_clean.py`
    Probability of dictionary english word in WPR_OneDoc.WorkName
    """
    return list_work_name_freq[word] / N

def find_sim_work(text:str) -> str:
    """
    fine similar sentences (assume the most match sentences is correct (eg. find 'scaffold' more than 'scafold'))
    algorithm : levenshtein distance
    library : fuzzywuzzy -> calculate ratio between length of sentences and levenshtein distance ((length of sentences - levenshtein distance)/length of sentences)
    """
    work_max = []
    for i in range(len(list_work_name)):
        sim_score_work_name = fuzz.ratio(text,list_work_name[i])
        if(sim_score_work_name > 90):
            work_max.append(list_work_name[i])
    sim_work = sorted(work_max, key=sim_work_prob, reverse=True) # sort from probability (the most appear sentences is the most similar sentences)
    if(len(sim_work)>0):
        return sim_work[0] # return the most similar sentences
    else:
        return text # return input sentences
# ---------------------- find tag description ----------------------------------------------------
def tag_description(tag:List[str]) -> List[str]:
    """
    Search tag in data tag equipment
    """
    form_tag = []
    # response model equal to data_res_correct_tag
    form_tag_res = {
        "TagName" : "",
        "Type" : "",
        "Description":""
    }
    # loop find description of tag equipment
    for i in range(len(tag)):
        # block error if not found
        try:
            index_tag = tag_name_dict.index(tag[i].upper())
            form_tag_res['TagName'] = tag_name_dict[index_tag]
            form_tag_res['Type'] = tag_type_dict[index_tag]
            form_tag_res["Description"] = tag_des_dict[index_tag]
            form_tag.append(form_tag_res)
        except:
            form_tag.append(form_tag_res)
        # reset to initial
        form_tag_res = {
                "TagName" : "",
                "Type" : "",
                "Description":""
            }
    return form_tag
# ----------------------------------- norvig (eng) ----------------------------------------------------
def word_en(word:str, N:int=sum(WORDS.values())) -> float: 
    """
    variable -> WORDS from `data_clean.py`
    Probability of dictionary english word in en_dict.txt (each word have frequency count = 1) 
    and dataset_not_clean_syllable_freq.txt (each word have frequency count depending on value of item in `WPR_OneDoc` column `WorkName`)
    """
    return WORDS[word] / N

def tag_en(word:str, N:int=sum(tag_dict.values())) -> float: 
    """
    variable -> tag_dict from `data_clean.py`
    Probability of `tag_equipment` in folder data/tag/... .
    """
    return tag_dict[word] / N

def correction_en(word:str,isWord:bool) -> str: 
    """
    variable -> isWord(use to select between correct word(isWord = True) or tag equipment(isWord = False))
    Most probable spelling correction for word.
    """
    if(isWord):
        return max(candidates(word,isWord), key=word_en)
    else:
        return max(candidates(word,isWord), key=tag_en)

def candidates(word:str,isWord:bool) -> List[str]: 
    """
    variable -> isWord(use to select between correct word(isWord = True) or tag equipment(isWord = False))
    Generate possible spelling corrections for word.
    isWord:True -> get all word that programe generate
    isWord:False -> get first match tag_equipment
    probability equation -> probability  word(that generate from `known`) count/all word count)
    """
    if(isWord):
        return sorted((known([word],isWord) + known(edits1_word(word),isWord) + known(edits2(word,isWord),isWord)) or [word], key=word_en,reverse=True)
    else:
        return sorted(known([word],isWord) or known(edits1_tag(word),isWord) or known(edits2(word,isWord),isWord) or [word] , key=tag_en,reverse=True)

def known(words:str,isWord:bool) -> List[str]: 
    "The subset of `words` that appear in the dictionary of WORDS."
    if(isWord):
        return list(w for w in words if w in WORDS)
    else:
        return list(w for w in words if w in tag_dict)

def edits1_word(word:str) -> Set[str]:
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    # print('insert -> ', set(inserts))
    return set(deletes + transposes + replaces + inserts)

def edits1_tag(word:str) -> Set[str]:
    "All edits that are one edit away from `word`."
    letters    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-" '
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word:str,isWord:bool) -> Set[str]: 
    "All edits that are two edits away from `word`."
    if(isWord):
        return set(e2 for e1 in edits1_word(word) for e2 in edits1_word(e1))
    else:
        return set(e2 for e1 in edits1_tag(word) for e2 in edits1_tag(e1))

# ------------------------- remove quantity ---------------------------------------------------------
def remove_quantity(text:str) -> str:
    regex_quantity = ''
    for i in range(len(quantity_dict)):
        if(i<(len(quantity_dict)-1)):
            regex_quantity += '('+quantity_dict[i]+')|'
        else:
            regex_quantity += '('+quantity_dict[i]+')'
    clean = re.sub(regex_quantity," ",text)
    return clean
# ----------------- check if text have number in it -----------------------------------------------------
def num_there(s:str) -> bool:
    return any(i.isdigit() for i in s)
# --------------------- replace tag when user input with comma ex.[str-123,456 -> str-123,str-456]----------------------------
def initial_tag_to_full(text_test_tag:str) -> str:
    temp_split = re.split(r'\,|\s|\/',text_test_tag) # split tag equipment
    index = [] # temporary stored index
    tag_from_index = [] # temporary stored tag
    old_tag = [] # temporary stored tag from old sentences
    new_tag = [] # temporary stored tag that change to full
    # loop in list that split tag equipment
    for i in range(len(temp_split)):
        test_tag = find_tag(temp_split[i]) # find tag into list
        test_tag.remove('5ส') # remove if find '5ส' in list
        # block error from not found tag
        try:
            index.append(i)  # stored position of tag (from temp_split)
            tag_from_index.append(test_tag[0]) # get position 0 because initial tag equipment usually in form str-609,781 (first found tag equipment is the main tag equipment)
        except:
            i = i
    # change initial to full tag
    for i in range(len(tag_from_index)):  # loop in tag that get from function temp_split
        for j in range(index[i]+1, len(temp_split)):  # loop in tag that split into list
            if(temp_split[j].isdigit() or len(temp_split[j])==1 or num_there(temp_split[j])): # if list of split original sentences is 1.number or 2.length of text is 1 or 3. have number in it -> pass
                old_tag.append(temp_split[j]) # stored old tag
                temp_split[j]= tag_from_index[i][:(len(tag_from_index[i])-len(temp_split[j]))] + temp_split[j] # replace from behind (eg. [str-609,781] -> 781 pass -> str-781)
                new_tag.append(temp_split[j]) # stored tag that pass replacing
    # replace in old sentences (tag with str-a,b) to full (str-a,str-b)
    for i in range(len(old_tag)):
        find_replace_tag =  text_test_tag.find(old_tag[i]) # find position of tag in sentences
        text_test_tag = text_test_tag.replace(text_test_tag[find_replace_tag-1],',') # add ',' in front of that position
        text_test_tag = text_test_tag.replace(old_tag[i],new_tag[i]) # replace new tag
    return(text_test_tag)
# ------------------------------------------split th-en-number with space----------------------------------------------------------------
def split_th_en_number(text:str) -> str:
    res = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", text)
    res = re.sub(' +', ' ',res)
    res = res.strip()
    return res

# ---------------------------remove empty space from list------------------------------------------
def remove_space_emp_element(token:List[str]) -> List[str]:
    token_delete_space = [[instance for instance in sublist if not instance.isspace()] for sublist in token]
    token_del_emp = [[instance for instance in sublist if len(instance)>0] for sublist in token_delete_space]
    list2 = [x for x in token_del_emp if x != []]
    return list2
# ---------------------------remove thai vowels in front of English word------------------------------------------
def remove_th_vowels(text:str) -> str:
    detect_vowel = []
    for word in text:
        detect_vowel.append(re.sub(r'(^[\u0E30-\u0E3A\u0E47-\u0E4E]+)', "", word))
    return detect_vowel
# ---------------------------detect symbol in word------------------------------------------
def detect_symbol(text:str) -> bool:
    """
    if in text have symbol return true
    """
    re_test = re.compile(r'[^\u0E00-\u0E7Fa-zA-Z]')
    # print('symbol ')
    return bool(len(re.findall(re_test,text)))
# ---------------------------remove ()------------------------------------------
def remove_data_parentheses (text:str) -> str:
    text = re.sub(r"\([^()]*\)", "", text)
    return text
# ---------------------------screen part-of-speech if don't pass criteria remove that word------------------------------------------
def check_pos_th(token:List[str]) -> List[str]:
    new_token = []
    list_pos_tag = pos_tag_sents(token,corpus='orchid_ud')[0] # get part-of-speech
    for i in range(len(list_pos_tag)):
        if(list_pos_tag[i][1] != 'AUX' and list_pos_tag[i][1] != 'ADP' and list_pos_tag[i][1] != 'CCONJ' and list_pos_tag[i][1] != 'PUNCT' and list_pos_tag[i][0] != 'งาน'):
            new_token.append(list_pos_tag[i][0])
    token = new_token
    return token
# ---------------------------lemmatization (English) ------------------------------------------
# ---------------------------get word type------------------------------------------
def get_wordnet_pos(word:str) -> str:
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word],tagset='universal')[0][1][0].upper()
    # print(tag)
    tag_dict = {"A": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV
                }
    try:
        type_tag = tag_dict.get(tag)
    except:
        type_tag =  ''
    return type_tag
# ----------- lemmatization --------------------------
def lemmatize_en(text:str) -> str:
    lemmatizer = WordNetLemmatizer()
    # 
    try:
        lem_text = lemmatizer.lemmatize(text, get_wordnet_pos(text))
    except:
        lem_text = lemmatizer.lemmatize(text)
    return lem_text
# ---------- screen part-of-speech if don't pass criteria remove that word -----------------
def check_pos_en(text:str) ->List[str]:
    new_token = []
    token = nltk.word_tokenize(text)
    list_pos_tag = nltk.pos_tag(token,tagset='universal')
    for i in range(len(list_pos_tag)):
        if(list_pos_tag[i][1] == 'NOUN' or list_pos_tag[i][1] == 'ADJ' or list_pos_tag[i][1] == 'VERB' ):
            new_token.append(lemmatize_en(list_pos_tag[i][0]))
    new_token = remove_space_emp_element([new_token])
    try:
        new_token = new_token[0]
    except:
        new_token = new_token
    return new_token
# ------------------ tokenization (thai) -----------------------------------------------
def tokenize_deepcut(clean:str,tag:List[str]) -> List[str]:
    custom_dict = thai_dict[:] + tag[:] # combine thai dictionary with tag to prevent tokenization to split it
    token = deepcut.tokenize(clean,custom_dict=custom_dict)
#     remove_sw = remove_stop_word(token)## remove stop word
    remove_vowel  = remove_th_vowels(token) # found in case ุุb/v
    token_out = []
    for i in range(len(remove_vowel)):
        if(remove_vowel[i] != ' '):
            token_out.append(remove_vowel[i])
    token = remove_num(remove_vowel)## remove number from text such as date
    token = remove_space_emp_element([token]) # remove empty element in list
    return token_out
# ------------------ correction ------------------------------------
def correct_word(original_text:str) -> str:
    original_text = normalizer(original_text) # use with thai or english that have many form to write
    similar_word = find_sim_work(original_text) # find similar Work name from WPR_OneDoc use levenshtein distance
    # if not found sentences that pass criteria
    if(similar_word != ""):
        original_text = similar_word
    tag = find_tag(original_text) # for correct tag
    text = remove_tag(original_text) # for correct word
    token = word_tokenize(text) # tokenization by พยางค์

    checker = NorvigSpellChecker(custom_dict=dic_th) # call correction in Thai
    wrong_text = [] # temporary stored wrong word
    correct_text = []  # temporary stored correct word

    token[:] = [ele for ele in token if ele.strip()] # remove space (in front/last of)
    # loop in token
    for word in range(len(token)):
        # token is not have number in it
        if not(num_there(token[word])):
            # length of token(word) is greater than 2 and not have symbol in it
            if(len(token[word])>=2 and not(detect_symbol(token[word]))):
                # if it have Thai language in it
                if(contain_thai_word(token[word])):
                    # correction use library 'pythainlp'
                    temp = checker.spell(token[word])
                    # if 1. correct word is not the same as before 2.(1.don't found การันต์ in it (because from test word that have การันต์ come from wrong tokenization) or 2. found การันต์ not in first position) 3. length of word greater than 1 4. token is not empty
                    if(temp[0] != token[word] and (token[word].find('์') == -1 or token[word].find('์')>1) and len(token[word])>1 and token[word]!=''):
                        wrong_text.append(token[word]) # stored wrong word
                        correct_text.append(temp[0]) # stored the most probability correct
                # if not found Thai language and not found in dictionary (save time)
                elif(not contain_thai_word(token[word]) and not(token[word] in WORDS)):
                    temp = candidates(token[word],isWord=True) # correcting use function
                    # if 1. correct word is not the same as before 2. length of word greater than 1 3. token is not empty
                    if(temp[0] != token[word] and len(token[word])>1 and token[word]!=''):
                        wrong_text.append(token[word])
                        correct_text.append(temp[0])
    wrong_tag = [] # wrong tag
    correct_tag = [] # correct tag
    # correcting tag
    for word in range(len(tag)):
        temp = correction_en(tag[word].upper(),isWord=False) # use correct function
        # if 1. correct word is not the same as before 2. length of word greater than 1 3. token is not empty
        if(temp != tag[word] and len(tag[word])>1 and tag[word]!=''):
            wrong_tag.append(tag[word])
            correct_tag.append(temp)
    # replace wrong word by correct word in old sentences (word)
    for i in range(len(wrong_text)):
        try:
            original_text = re.sub("("+wrong_text[i]+")",correct_text[i],original_text)
        except:
            original_text = original_text
    # replace wrong word by correct word in old sentences (tag)
    for i in range(1,len(wrong_tag)):
        try:
            original_text = re.sub("("+wrong_tag[i]+")",correct_tag[i],original_text)
        except:
            text = original_text
    return original_text
# ------------------ find if word contain Thai language -------------------------
def contain_thai_word(text:str) -> bool:
    pattern = re.compile('([\u0E00-\u0E7F]+)')
    found = re.search(pattern, text)
    # print('have th func -> ',bool(found))
    return bool(found)

# --- for remove stop word (problem: public stop word is cut useful word when use with this project (eg. ไม่ใช่งานบนที่สูง -> งานบนสูง)) -----------
# def remove_stop_word(text:List[str]) -> List[str]:
#     list_stopwords = list(thai_stopwords())
#     remove_sw_th = [word for word in text if word not in list_stopwords]
#     return remove_sw_th

# ------------ remove number/symbol from list of token -------------------
def remove_num(text:List[str]) -> List[str]:
    remove_num = [' ' if word.isnumeric() else word for word in text]
    w = [k for k in remove_num if k not in (' ',',','/','-','\t','\n','  ','+','(',')')]
    return w
# ------------- remove tag from sentences --------------------------
def remove_tag(text:str) -> str:
    remove_tag = re.compile("(([a-zA-z0-9]+(\s?\-|\d|\s?\"\s?|\s?\/\s?)(\s\d)?){1,6}([a-zA-Z0-9])*)")
    text = remove_tag.sub(" ",text)
    return text
# find tag in sentences -----------------------------------
def find_tag(text:str) -> List[str]:
    tag = ['5ส']
    re_tag_list = "(([a-zA-z0-9]+(\s?\-|\d|\s?\"\s?|\s?\/\s?)(\s\d)?){1,6}([a-zA-Z0-9])*)"
    all_tag = re.findall(re_tag_list,text) # find all match pattern stored in list
    for i in range (len(all_tag)):
        tag.append(all_tag[i][0])
    tag = list(set(tag)) # remove repeat tag
    tag = remove_num(tag) ## remove number from tag
    return tag
# ------- replace initial word to full word use dictionary -----------------
def initial_word_to_full(text:str) -> str:
    for i in range(len(initial_data)):
        text = re.sub('(\s('+initial_data[i][0]+')\s)|(^\s?('+initial_data[i][0]+')\s)|(\s('+initial_data[i][0]+')\s?$)|(^('+initial_data[i][0]+')$)', " "+initial_data[i][1]+" ", text)
    return text
# ------------ normalization (thai) - change word to same pattern ----------------------------------
def normalizer(text:str) -> str:
    clean = re.sub('(\s?(\/)\s?)', "/", text)
    clean = re.sub(r'(\s?\-\s)|(\s\-\s)|(\s\-\s?)',"-",clean)
    clean = re.sub('(เเ)', "แ", clean)
    clean = re.sub(r"\s?[.]\s?", " ", clean)
    for i in range(len(correct_data)):
        clean = re.sub("("+correct_data[i][0]+")",correct_data[i][1],clean)
    return clean
# ---------- replace tag code by description if found match in data ---------------------
def replace_tag(text:str) -> str:
    # text = initial_tag_to_full(text) # test in Work name : changing tag wrong
    tag = find_tag(text) # find tag
    find_data_tag = tag_description(tag) # find description
    # loop in description and replace it
    for i in range(len(find_data_tag)):
        if(find_data_tag[i]["Type"]!=""):
            text = re.sub("("+tag[i]+")",find_data_tag[i]["Type"].lower(),text)
    return text

# ------- main function to call another function follow work flow ------------------------------
def cleaning(sentences:List[str],view = False) -> List[str]:
    """
    view = True -> use when return correcting sentences to user
    view = False -> use when search
    """
    words = []
    for i in range(1):
        sentences[i] = remove_space(sentences[i])
        sentences[i] = normalizer(sentences[i])
        sentences[i] = sentences[i].lower()  ##lower
        if(view == False):
            sentences[i] = replace_tag(sentences[i])
            sentences[i] = split_th_en_number(sentences[i])
            sentences[i] = initial_word_to_full(sentences[i])
        else:
            sentences[i] = split_th_en_number(sentences[i])
        sentences[i] = correct_word(sentences[i])
        sentences[i] = normalizer(sentences[i]) ##lemmatize
        words.append(sentences[i].strip())
        ##---------------------------------------------------------
    return words ## return words after prepare and tag code
