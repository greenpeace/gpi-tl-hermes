"""Actual script that does the magic.

Refer to the README for more structural info (TODO).
"""

import datetime as dt

from google.cloud import language as lang

import hermes.firebaseInterface as fbi
from hermes.nappy.tools import Content


# helper function
def duplicate(children: list, searchstring: str,
              endnodes: list = ["title", "url", "author"]) -> bool:
    for child in children:
        childnode, ids = fbi.ref(child, get={"shallow": True})
        for i in ids:
            results = [fbi.ref(f"{child}/{i}/source/{s}")[1] for s in endnodes]
            if searchstring in results:
                return True

    return False


# #################################### [1] ################################## #
# firebase
app = fbi.setup("../firebase_creds/gpi-it-1225-fba.json")

# natural language API client
nlClient = lang.LanguageServiceClient()  # needs GCP credentials (TODO: see README)

# #################################### [2] ################################## #
# create daytag
today = dt.datetime.now().isoformat().split("T")[0]

# #################################### [3] ################################## #
# instanciate root node and get its children (in list form)
rootNode, children = fbi.ref('/', get={"shallow": True})
children = [] if children is None else list(children)

# setup today's node
if today in children:
    nodeToday = fbi.ref(today, get=False)
else:
    nodeToday = rootNode.child(today)
    children.append(today)

# #################################### [4] ################################## #
# API call
data = {}  # response of some API + processing

# #################################### [5] ################################## #
# deduplication
if not duplicate(children, data['title']):
    entry = Content(**data)  # [i]
    nodeToday.push(entry.jsonify(automagic=True)  # [ii]
