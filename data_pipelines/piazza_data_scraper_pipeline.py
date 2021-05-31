# -*- coding: utf-8 -*-
"""
Piazza data scraping script.

Just enter the user credentials and piazza course site id
"""

import time
import json
import pickle
from piazza_api import Piazza

# Init piazza instance
p = Piazza()

# Login with username and password
p.user_login(email="user@nyu.edu", password="Bridge@123") # CHANGE ME
# p.get_user_profile()

# Connect to the course site/network (CPRE310in this case)
course_site = p.network("j6mbq7px56n6s0") # CHANGE ME

# Fetch a particular post by post id
# course_site.get_post("j94qwmczxx957o")

# Fetch all posts from Piazza - gives a generator object
posts = course_site.iter_all_posts(limit=None)

# List to store fetched data data
data = []

# Iterate posts from the generator object
cnt = 0
for post in posts:
    print(cnt)
    # IMPORTANT timeout else the Piazza API will return too many requests error
    time.sleep(1)
    data.append(post)
    cnt+=1
    
# Save pickle
with open('piazza_course_data.pkl', 'wb') as f:
    pickle.dump(data, f)

# Save raw JSON
with open('piazza_course_data.json', 'w') as f:
    json.dump(data, f, indent=4)
