# -*- coding: utf-8 -*-

'''
Useful Resources:
    https://medium.com/nanonets/topic-modeling-with-lsa-psla-lda-and-lda2vec-555ff65b0b05
    https://towardsdatascience.com/nlp-extracting-the-main-topics-from-your-dataset-using-lda-in-minutes-21486f5aa925
    https://iq.opengenus.org/topic-modelling-techniques/
'''

import json
import numpy as np
import pandas as pd


# Import raw json data
with open("data/preprocessed/transcripts.json", "r") as f:
    raw_transcript = json.load(f)

with open("data/preprocessed/ppts.json", "r") as f:
    raw_ppt = json.load(f)


# --- Data Preprocessing ------------------------------------------------------


# Text preprocessing pipeline for the model   
def text_preprocessing(lines):
    lines = " ".join(lines)
    return lines


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








