"""Actual script that does the magic.

Refer to the README for more structural info (TODO).
"""

import datetime as dt

from google.cloud import language as lang

import hermes.firebaseInterface as fbi
from hermes.api import theguardian
from hermes.nappy.tools import Content


# helper function
def duplicate(children: list, searchdict: dict,
              precision: float = 0.99) -> bool:
    # more helper functions:
    def match(a: float, b: float) -> float:
        """Returns the (absolute) matching percentage of `a` and `b`."""
        a = abs(a)
        b = abs(b)
        return min(a, b)/max(a, b)

    # iterate over all daytags
    for child in children:
        # get daytag reference and it's IDs
        childnode, ids = fbi.ref(child, get={"shallow": True})
        ids = list(ids)

        # iterate over all IDs and check for an already existing article
        for i in ids:
            # get values for author, and overall sentiment and magnitude
            _, author = fbi.ref(f"{child}/{i}/source/author")
            _, overall = fbi.ref(f"{child}/{i}/sentiment/overall")

            # check if author(s) are same
            if (set(author) == set(searchdict['author'])):
                # check if sentiment and magnitude match the precision crit.
                senMat = match(searchdict['sentiment'], overall['score'])
                magMat = match(searchdict['magnitude'], overall['magnitude'])
                if (senMat >= precision) and (magMat >= precision):
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
with open("path/to/api/config.json", "r") as config:
    params = json.load(config)
dataList = theguardian.call(params, ephemeral=True)

# #################################### [5] ################################## #
# Content instance
for data in dataList:
    entry = Content(**data).jsonify(automagic=True)  # NL API call
    searchdict = {
        "author": entry['source']['author'],
        "sentiment": entry['sentiment']['overall']['score'],
        "magnitude": entry['sentiment']['overall']['magnitude']
    }

    # ################################## [6] ################################ #
    # deduplication
    if not duplicate(children, searchdict):
        nodeToday.push(entry)  # [i]
