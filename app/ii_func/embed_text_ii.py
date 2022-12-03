import pickle # to load pickle from embed all ii file 

with open('./SMIT_Data/SMIT2_Data/embeddings_ii_new_all.pkl', "rb") as fIn: # open pickle file (same as model_deployment\safety_equip_func\embed_text_safety_measure.py)
    stored_data = pickle.load(fIn) 
    corpus_embeddings = stored_data['embeddings']
