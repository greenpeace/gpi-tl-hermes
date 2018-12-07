"""Actual script that does the magic."""
import datetime as dt

from google.cloud import language as lang

import hermes.firebaseInterface as fbi
from hermes.nappy.tools import Content

# TODO: insert API stuff here

# initial setup
app = fbi.setup("path/to/credentials")

# main workflow ---------------------------------------------------------------
# from API
data = some.API.call()

today = dt.datetime.now().isoformat().split("T")[0]

rootNode, children = fbi.ref('/', get={"shallow": True})
children = [] if children is None else list(children.keys())

if today in children:
    nodeToday = fbi.ref(today, get=False)
else:
    nodeToday = rootNode.child(today)
