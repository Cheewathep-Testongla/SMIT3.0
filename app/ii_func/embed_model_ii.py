# Taken from
# https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html#sphx-glr-auto-examples-compose-plot-column-transformer-mixed-types-py

import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle

# Call model
model_url = './Model/SentenceTransformer'
model_ii = SentenceTransformer(model_url)
# Select data from database
df_relate_case = pd.read_csv("./SMIT_Data/data/ii/ii_split_column_translate_all_display.csv", encoding='utf-8')

# corpus
df_corpus = df_relate_case.assign(incident_all_detail_en=df_relate_case.IncidentName_en.astype(str) + ', ' +
                                    df_relate_case.IncidentDetail_en.astype(str) + ', ' + df_relate_case.Cause_en.astype(str))

corpus = df_corpus["IncidentDetail_en"].to_numpy()
corpus_embeddings_v3 = model_ii.encode(corpus)
# corpus_embeddings_v3 = model_v3.encode(corpus)
# corpus_embeddings_dotv3 = model_dotv3.encode(corpus)
# corpus_embeddings_b = model_b.encode(corpus)
# hkl.dump(corpus_embeddings_v3, 'encode_th_en.hkl')

#Store sentences & embeddings on disc
name = 'new_all'
name_file = 'embeddings_ii_'+name+'.pkl'
# print(name_file)
with open(name_file, "wb") as fOut:
    pickle.dump({'embeddings': corpus_embeddings_v3},
                fOut, protocol=pickle.HIGHEST_PROTOCOL)
