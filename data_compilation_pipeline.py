# -*- coding: utf-8 -*-
"""
    This pipeline compiles the Non-SRT transcripts and PPT text into a single JSON
    file. The schema is as follows:

        [
            {
            "module_number": 0,
            "module_name":"",
            "file_name": "",
            "transcript":[
                 {
                     "title": "",
                     “data": ["", ...],
                 }, ...
             ],
            "ppt":["", ...]
            }, ...
        ]

"""

import os
import json
from docx import Document # pip install python-docx
from pptx import Presentation # pip install python-pptx

# Raw data location
loc_transcript = "data/Non-SRT Transcript/"
loc_ppt = "data/PPT/"

# Processed JSON dict
data = []

# Create module level JSON structure
for f in os.listdir(loc_transcript):
    file = f.split(".")
    if file[1] == "docx":
        file = file[0].split()
        data.append({
            "module_number": int(file[1]),
            "module_name": ' '.join(file[2:]),
            "file_name": f,
            "transcript": [],
            "ppt": []
            })

# Sort JSON
data.sort(key=lambda x: x['module_number'])


# Check if the para is a title or not
def if_title(doctext):
    words = doctext.split(" ")
    w = words[len(words)-1]
    try:
        float(w)
        result = True
    except:
        result = False
    if (result):
        return True
    return False


# Extract transcript text - Nikita
for d in data:
    doc = Document(loc_transcript + d["file_name"])
    #print(d["file_name"])

    # Doc is a word document object. We can extract paragraphs from this obj.
    # Check out the "python-docx" library documentation
    para_count  = 0 # Count of para in the doc obj
    transcript_data = [] # Data for every title in topic:transcript
    for t in doc.paragraphs:
        para_count += 1

        # Ignore if the para line is the heading, say 'Week 1 Module 1 Fundamentals of System Hardware'
        if para_count == 1:
            continue

        resTitle = if_title(t.text)
        #print(resTitle)

        # Append transcript title and data
        if (resTitle) and (not transcript_data):
            title = t.text

        elif (resTitle):
            d['transcript'].append({
                "title": title,
                "data": transcript_data
            })
            title = t.text
            transcript_data.clear()

        elif not(resTitle):
            transcript_data.append(t.text)


# Extract PPT text - Ankush
# for file in os.listdir(loc_ppt):
#     ppt = Presentation(loc_ppt)
#     print(file)

print(data) # Check here if data JSON is collected properly