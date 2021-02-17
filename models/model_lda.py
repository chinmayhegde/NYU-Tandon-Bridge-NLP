# -*- coding: utf-8 -*-

'''
Useful Resources:
    https://medium.com/nanonets/topic-modeling-with-lsa-psla-lda-and-lda2vec-555ff65b0b05
    https://towardsdatascience.com/nlp-extracting-the-main-topics-from-your-dataset-using-lda-in-minutes-21486f5aa925
    https://iq.opengenus.org/topic-modelling-techniques/
'''

import re
import json
import gensim
import spacy
import textacy
import numpy as np
import pandas as pd
from copy import deepcopy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer


# Import raw json data
with open("../data/preprocessed/transcripts.json", "r") as f:
    raw_transcript = json.load(f)

with open("../data/preprocessed/ppts.json", "r") as f:
    raw_ppt = json.load(f)


# --- Data Preprocessing ------------------------------------------------------

# Init Spacy
nlp = spacy.load('en_core_web_lg')
# Define the stop words list
stop_words = set(stopwords.words('english'))
# Define stemmer
stemmer = PorterStemmer()
# Define lemmatizer
lemmatizer = WordNetLemmatizer()
# Define tf-idf vectorizer
vectorizer = TfidfVectorizer()


# Text preprocessing pipeline for the model
def text_preprocessing_1(lines):
    # Join lines into a string
    line = " ".join(lines)
    # Lowercase
    line = line.lower()
    # Remove symbols and numbers
    line = re.sub(r'[^a-zA-Z]+', ' ', line)
    # Normalizing whitespaces
    line = line.split()
    # Remove stopwords and discards words of length < 3
    line = [token for token in line if token not in stop_words and len(token) > 3]
    # Lemmatize the verbs and then stem
    line = [stemmer.stem(lemmatizer.lemmatize(token, pos='v')) for token in line]
    # Join words to string
    # line = ' '.join(line)
    return line


# def text_preprocessing_2(line):
#     # SpaCy noun chunk extraction
#     line = nlp(line)
#     noun_extract = textacy.extract.noun_chunks(line)
#     line = [str(i) for i in noun_extract]
#     # noun_extract = ' '.join([str(i) for i in noun_extract])

#     # Tokenize sentences
#     # line = word_tokenize(noun_extract)
#     # Remove Stop Words and single character words
    
#     # Lemmatize the verbs and then stem
#     # line = [stemmer.stem(lemmatizer.lemmatize(token, pos='v')) for token in line]
#     # Rejoin to string
#     return line


# Converts raw data to dataframe where each doc is a slide or transcript para
def convert_to_dataframe(raw_ppt, explode_col, text_col):
    df = pd.DataFrame(raw_ppt)
    df = df.explode(explode_col)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = pd.concat([df, pd.DataFrame(df[explode_col].to_list())], axis=1)
    df.drop(explode_col, axis=1, inplace=True)
    df[text_col] = df[text_col].apply(text_preprocessing_1)
    return df


# Apply conversion
df_ppt = convert_to_dataframe(raw_ppt, "ppt", "slide_text")
df_transcript = convert_to_dataframe(raw_transcript, "transcript", "data")


# --- LDA Model Training ------------------------------------------------------

num_topics = 7
# docs = df_ppt["slide_text"].to_list()
# docs = df_transcript["data"].to_list()
docs = df_ppt["slide_text"].to_list() + df_transcript["data"].to_list()

# Gensim corpus dict
dictionary = gensim.corpora.Dictionary(docs)

# Convert each doc to BoW (with word counts)
corpus = [dictionary.doc2bow(doc) for doc in docs]


# --- TF-IDF Filtering ---

tfidf = gensim.models.TfidfModel(corpus, id2word = dictionary)
low_value = 0.012
low_value_words = []
for bow in corpus:
    low_value_words += [id for id, value in tfidf[bow] if value < low_value]
dictionary_old = deepcopy(dictionary)
dictionary.filter_tokens(bad_ids=low_value_words)
docs_bow = [dictionary.doc2bow(doc) for doc in docs]
# Function to print words
low_value_words_conv = []
for i in low_value_words:
    low_value_words_conv.append(dictionary_old[i])


# --- LDA Model ---

# Train LDA model
lda =  gensim.models.LdaMulticore(docs_bow,
                                  num_topics=num_topics,
                                  id2word=dictionary,
                                  passes=1,
                                  workers=4)

# lda = gensim.models.ldamodel.LdaModel(corpus=docs_bow,
#                num_topics=num_topics,
#                id2word=dictionary,
#                update_every=1,
#                chunksize=10000,
#                passes=1)

# Print topics
for t in range(lda.num_topics):
    print(lda.print_topic(t), end="\n\n")


# --- Predictions -------------------------------------------------------------

# Raw preds
prob_raw = []

for probs in lda[docs_bow]:
    cnt = 0
    prob_list = []
    for i in range(num_topics):
        val = None
        for p in probs:
            if p[0] == i:
                val = p[1]
        if val == None:
            prob_list.append(0)
        else:
            prob_list.append(val)
    prob_raw.append(prob_list)
        
# Raw prob to dataframe
prob_raw_df = pd.DataFrame(prob_raw, columns=['Topic_1', 'Topic_2',
                                              'Topic_3', 'Topic_4',
                                              'Topic_5', 'Topic_6',
                                              'Topic_7'])   

# Add module number 
prob_raw_df['module_number'] = df_ppt['module_number'].to_list() + df_transcript['module_number'].to_list()


# Aggregate Probabilities on Module Number - MEAN
prob_mean_df = prob_raw_df.groupby(['module_number']).mean()


# Aggregate Probabilities on Module Number - MAX
prob_max_df = prob_raw_df.groupby(['module_number']).max()

# Function to find clusters
def find_cluster(df):
    clusters = []
    for index, row in df.iterrows():
        for j in range(len(list(row))):
            if list(row)[j] == max(list(row)):
                clusters.append(j+1)
    return clusters

# Compute clusters
prob_mean_df['cluster'] = find_cluster(prob_mean_df)
prob_max_df['cluster'] = find_cluster(prob_max_df)



# --- Visualization - Network -------------------------------------------------

# Module names for Viz Labels
module_names_dict = df_transcript[["module_number", "module_name"]].to_dict(orient="record")
decode = {}
for i in module_names_dict:
    decode[i["module_number"]] = i["module_name"]


viz_data_1 = {"nodes": [],
            "links": []
            }

# Add topic nodes
for i in range(num_topics):
    viz_data_1["nodes"].append({"id": "TOPIC "+str(i+1), 
                                "group": int(i+1)})

# Add module nodes
for index, row in prob_mean_df.iterrows():
    viz_data_1["nodes"].append({"id": "M "+str(index)+" "+decode[index], 
                                "group": int(row['cluster'])})

# Add links
for index, row in prob_mean_df.iterrows():
    row_list = list(row)[:-1]
    for i in range(num_topics):
        
        if row[i] > 0.2:
            viz_data_1["links"].append({"source": "M "+str(index)+" "+decode[index], 
                                        "target":"TOPIC "+str(i+1), 
                                        "value": row_list[i]*10})


# --- Save JSON ---
# THE VISUALIZATION RESULTS ARE NOT REPRODUCIBLE. SAVE IT CAREFULY.

# with open("../visualization/v1/viz_lda.json", "w") as f:
#     json.dump(viz_data_1, f, indent = 4)


# Command to run the D3.JS visualization from cmd/terminal
# python -m http.server
