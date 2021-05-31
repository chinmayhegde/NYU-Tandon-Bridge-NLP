import json
import numpy as np
import pandas as pd



# Extracts followups from the post data 
def extract_followup_post(fu, level, post_id, tags, instr_candidate):
    fu_doc = {}
    try:
        fu_doc['post_id'] = post_id
    except:
        pass
    try:
        fu_doc['followup_id'] = fu['id']
    except:
        pass
    try:
        fu_doc['followup_level'] = level
    except:
        pass
    try:
        fu_doc['anon'] = fu['anon']
    except:
        try:
            fu_doc['anon'] = fu['history'][0]['anon']
        except:
            pass
    try:
        fu_doc['subject'] = fu['subject']
    except:
        try:
            fu_doc['subject'] = fu['history'][0]['subject']
        except:
            pass
    try:
        fu_doc['content'] = fu['content']
    except:
        try:
            fu_doc['content'] = fu['history'][0]['content']
        except:
            pass
    try:
        fu_doc['data'] = fu['data']
    except:
        pass
    try:
        fu_doc['created'] = fu['created']
    except:
        pass
    try:
        fu_doc['type'] = fu['type']
    except:
        pass
    try:
        fu_doc['uid'] = fu['uid']
    except:
        try:
            fu_doc['uid'] = fu['history'][0]['uid']
        except:
            pass
    try:
        if 'instructor-note' in tags:
            if fu['uid'] == instr_candidate: 
                fu_doc['is_instructor'] = True
            else:
                fu_doc['is_instructor'] = False    
        else:
            fu_doc['is_instructor'] = False
    except:
        pass
    return fu_doc



# Load JSON
with open('piazza_bridge_s20_24_raw_data.json', 'r') as f:
    data = json.load(f)
    
    

# Extract the information about 
data_creator = []
data_posts = []
data_followups = []

for i in data:
    # Extract user who created the post
    for j in i['change_log']:
        if j['type'] == 'create':
            data_creator.append(j)
        
        
    # Extract post data
    data_posts.append(i['history'][0])
    data_posts[-1]['post_id'] = i['id']

    # Flag the creator as instructor if "instructor-note" tag is present
    if 'instructor-note' in i['tags']:
        data_creator[-1]['is_instructor'] = True
        data_posts[-1]['is_instructor'] = True
    else:
        data_creator[-1]['is_instructor'] = False
        data_posts[-1]['is_instructor'] = False
    
    # Extract followup data
    # if i['status'] != 'private':
    # Followup level 1
    for fu1 in i['children']:
        fu1_doc = extract_followup_post(fu1, 1, i['id'], i['tags'], i['history'][0]['uid'])
        if 'content' in fu1_doc or 'subject' in fu1_doc:
            data_followups.append(fu1_doc)
        # Followup level 2 (replies to followup)
        for fu2 in fu1['children']:
            fu2_doc = extract_followup_post(fu2, 2, i['id'], i['tags'], i['history'][0]['uid'])
            if 'content' in fu2_doc or 'subject' in fu2_doc:
                data_followups.append(fu2_doc)
            
            # Redundant level - no data found at this level in any post
            # for fu3 in fu2['children']:
            #     fu3_doc = extract_followup_post(fu3, 3, i['id'])
            #     if 'content' in fu3_doc or 'subject' in fu3_doc:
            #         data_followups.append(fu3_doc)
            
                
                
                
# Convert to dataframe
df_creator = pd.DataFrame(data_creator)
df_posts = pd.DataFrame(data_posts)
df_followups = pd.DataFrame(data_followups)

df_posts.to_csv('piazza_posts_data.csv')
df_followups.to_csv('piazza_followups_data.csv')
