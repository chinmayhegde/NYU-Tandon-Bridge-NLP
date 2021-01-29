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
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer


# Import raw json data
with open("data/preprocessed/transcripts.json", "r") as f:
    raw_transcript = json.load(f)

with open("data/preprocessed/ppts.json", "r") as f:
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


# Text preprocessing pipeline for the model   
def text_preprocessing(lines):
    # Join lines into a string
    line = " ".join(lines)
    # Lowercase
    line = line.lower()
    # Remove symbols and numbers
    line = re.sub(r'[^a-zA-Z]+', ' ', line)
    # Normalizing whitespaces
    line = ' '.join(line.split())
    
    # SpaCy noun chunk extraction
    line = nlp(line)
    noun_extract = textacy.extract.noun_chunks(line)
    line = [str(i) for i in noun_extract]
    # noun_extract = ' '.join([str(i) for i in noun_extract])
    
    # Tokenize sentences
    # line = word_tokenize(noun_extract)
    # Remove Stop Words and single character words
    line = [token for token in line if token not in stop_words and len(token) > 3]
    # Lemmatize the verbs and then stem
    # line = [stemmer.stem(lemmatizer.lemmatize(token, pos='v')) for token in line]
    return line


# Converts raw data to dataframe where each doc is a slide or transcript para
def convert_to_dataframe(raw_ppt, explode_col, text_col):
    df = pd.DataFrame(raw_ppt)
    df = df.explode(explode_col)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = pd.concat([df, pd.DataFrame(df[explode_col].to_list())], axis=1)
    df.drop(explode_col, axis=1, inplace=True)
    df[text_col] = df[text_col].apply(text_preprocessing)
    return df


# Apply conversion
df_ppt = convert_to_dataframe(raw_ppt, "ppt", "slide_text")
df_transcript = convert_to_dataframe(raw_transcript, "transcript", "data")


# --- LDA Model Training ------------------------------------------------------


# docs = df_ppt["slide_text"].to_list()
# docs = df_transcript["data"].to_list()
docs = df_ppt["slide_text"].to_list() + df_transcript["data"].to_list()

# Gensim corpus dict
dictionary = gensim.corpora.Dictionary(docs)

# Convert each doc to BoW (with word counts)
docs_bow = [dictionary.doc2bow(doc) for doc in docs]

# Train LDA model
lda =  gensim.models.LdaMulticore(docs_bow,
                                  num_topics =10 , 
                                  id2word = dictionary,                                    
                                  passes = 1,
                                  workers = 4)

# Print topics
lda.print_topics()







