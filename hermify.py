#!/usr/bin/env python
"""Magic script to do the scrapey. Creates new entries for the current date if
available.

Please refer to the README in the Github repo for more structural information.
"""

import json
import datetime as dt
import argparse

from google.cloud import language as lang
from firebase_admin import db

import hermes.firebaseInterface as fbi
from hermes.api import theguardian
from hermes.nappy.tools import Content


# deduplicate function
def dedup(datalist: list, inStock: dict, precision: float = 0.99) -> list:
    """Deduplicate the preprocessed entries in `datalist` with the current
    inventory given by `inStock`.

    Parameters
    ----------
    datalist : list
        `datalist` is a list of preprocessed (but not analysed) dictionaries,
        containing content from an API call.
    inStock : dict
        `inStock` is the full data of the dedup/ node of the firebase. Used to
        deduplicate content by checking against author(s) and sentiment score +
        magnitude.
    precision : float
        `precision` tunes how accurate the overlap of sentiment `score` and
        `magnitude` have to be to be accepted as equal (-> rounding errors..).

    Returns
    -------
    list
        List of deduplicated dictionaries containing the processed content.

    """
    def match(a: float, b: float) -> float:
        """Returns the (absolute) matching percentage of `a` and `b`."""
        a = abs(a)
        b = abs(b)

        # catching edge cases
        if max(a, b) != 0:
            return min(a, b)/max(a, b)
        else:  # if max == 0 => min == 0
            return 1.0

    def flatMate(entry: dict, flattened: list) -> bool:
        """Iterate over all flattened dedups and check if `entry` is there."""
        for d in flattened:
            if set(d['author']) == set(entry['source']['author']):
                senMat = match(entry['sentiment']['overall']['score'],
                               d['score'])
                magMat = match(entry['sentiment']['overall']['magnitude'],
                               d['magnitude'])
                if (senMat >= precision) and (magMat >= precision):
                    print(f"::[diag] Found duplicate {d['title']!r} by"
                          f" {d['author']}.")
                    return True

        return False

    fresh = []  # init
    flattened = []  # for dedup
    # nothing to dedup? ------------------------------------------------------
    if (inStock is None) or (len(inStock) == 0):
        for d in datalist:  # add all the content
            fresh.append(Content(**d).jsonify(nlClient, automagic=True))
        return fresh

    # create flattened list of dedup values -----------------------------------
    # structure is dedup/<daytag>/<random-id>/{dedup key:value pairs}
    for daytag, bundle in inStock.items():
        for i, v in bundle.items():
            flattened.append(v)  # extract value dictionaries

    # and do the deduping -----------------------------------------------------
    for fc in datalist:  # fc = full content
        entry = Content(**fc).jsonify(nlClient, automagic=True)  # parse
        if not flatMate(entry, flattened):
            fresh.append(entry)

    return fresh


# uploading stuff
def upload(entries: list, nodeToday: db.Reference,
           dedupNode: db.Reference) -> None:
    """Upload all entries to Firebase in the data/<today's day tag>/ node and
    add deduplication information in the dedup/ node.

    Parameters
    ----------
    entries : list
        `entries` is the list of processed and analysed `Content` dicts.
    nodeToday : db.Reference
        `nodeToday` is the firebase reference to the current date, e.g.
        `data/2018-12-10/`
    dedupNode : db.Reference
        `dedupNode` is the firebase reference to the dedup node `dedup/`.

    Returns
    -------
    None

    """
    # current days dedup node
    dt = dedupNode.get(shallow=True)
    dt = [] if dt is None else dt
    if nodeToday.key in list(dt):
        dedupToday = fbi.ref(f"dedup/{nodeToday.key}", get=False)
    else:
        dedupToday = dedupNode.child(nodeToday.key)

    for e in entries:
        nodeToday.push(e)  # normal upload
        # redundant part, stored under the corresponding date with random id
        dedupToday.push({"author": e['source']['author'],
                         "title": e['source']['title'],
                         "score": e['sentiment']['overall']['score'],
                         "magnitude": e['sentiment']['overall']['magnitude']})


# #################################### [1] ################################## #
# argparse
parser = argparse.ArgumentParser()
parser.add_argument("configs", type=str,  # nargs="+" <-- use for multiple cfgs
                    help="Path(s) to API configuration(s)")
parser.add_argument("--start", type=str,
                    help="Start date for news period in isoformat YYYY-MM-DD")
parser.add_argument("--end", type=str,
                    help="End date for news period in isoformat YYYY-MM-DD")
parser.add_argument("--creds", type=str,
                    help="Path to firebase credentials")

args = parser.parse_args()

# firebase
if args.creds is not None:
    app = fbi.setup(args.creds)

else:
    app = fbi.setup("../firebase_creds/gpi-it-1225-fba.json")

# natural language API client
nlClient = lang.LanguageServiceClient()  # needs GCP credentials

# iterate over daterange if given
if args.start is None:  # then also ignore the end date
    # populate the days list by just one entry
    days = [dt.datetime.now().isoformat().split("T")[0]]

else:  # set the period up according to arguments
    start = dt.datetime.fromisoformat(args.start)
    if args.end is None:
        end = dt.datetime.now()
    else:
        end = dt.datetime.fromisoformat(args.end)

    days = []
    while start <= end:  # increase start by 1 day until end
        days.append(start.isoformat().split("T")[0])
        start += dt.timedelta(days=1)

# loop over all days
for day in days:
    # ################################## [2] ################################ #
    # create daytag
    with open(args.configs, "r") as config:  # TODO: adapt to multiple configs
        params = json.load(config)

    print(f"::[diag] working on date {day}.")
    today = day
    params['to-date'] = day
    params['from-date'] = day

    # ################################## [3] ################################ #
    # instanciate root node and get its children (in list form)
    rootNode, daytags = fbi.ref('data', get={"shallow": True})
    daytags = [] if daytags is None else list(daytags)
    print(f"::[diag] Found daytags: {daytags}")

    # setup today's node
    if today in daytags:
        nodeToday = fbi.ref(f"data/{today}", get=False)
    else:
        nodeToday = rootNode.child(today)
        daytags.append(today)

    # ################################## [4] ################################ #
    # API call
    print(f"::[diag] done reading The Guardian parameters, calling API now...")
    dataList = theguardian.call(params, ephemeral=True)

    # ################################## [5] ################################ #
    # dedup
    dedupNode, stocktaking = fbi.ref("dedup/", get=True)
    fresh = dedup(dataList, stocktaking)

    # ################################## [6] ################################ #
    # upload
    upload(fresh, nodeToday, dedupNode)
