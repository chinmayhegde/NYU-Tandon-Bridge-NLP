# -*- coding: utf-8 -*-
"""
Piazza data scraping script.
"""

import time
import json
import pickle
from piazza_api import Piazza

# Init piazza instance
p = Piazza()

# Login with username and password
p.user_login(email="ankush.jain@nyu.edu", password="Bridge@123")
# p.get_user_profile()

# Connect to the course site/network (CPRE310in this case)
cpre310 = p.network("j6mbq7px56n6s0")

# Fetch a particular post by post id
# cpre310.get_post("j94qwmczxx957o")

# Fetch all posts from Piazza - gives a generator object
posts = cpre310.iter_all_posts(limit=None)

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
with open('piazza_cpre310_data.pkl', 'wb') as f:
    pickle.dump(data, f)

# Save raw JSON
with open('piazza_cpre310_data.json', 'w') as f:
    json.dump(data, f, indent=4)
