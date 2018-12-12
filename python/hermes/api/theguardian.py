"""Class definition for The Guardian news API."""

import os
import json
import requests as req
import datetime as dt

from typing import Optional, Union


def call(params: dict, ephemeral: bool = True) -> Optional[list]:
    """Call The Guardian content API with given parameters.

    Creates the folder structure ./temp/articles/ and places json-like files
    named by date in there, containing the date-specific results.

    Parameters
    ----------
    params : dict
        `params` contains values like `to-date` and `from-date`, a search value
        like `q`, etc. Please refer to
            https://open-platform.theguardian.com/documentation/search
        for an in-depth exlaination of the possible values.

    ephemeral : bool
        Set `ephemeral` to `False` if instead of writing to files the content
        should be returned as a list of dictionaries containing the processed
        responses.
    """
    # setup of local storage
    LOCAL_STORAGE = os.path.join("temp", "articles")
    os.makedirs(LOCAL_STORAGE, exist_ok=True)

    # API endpoint
    ENDPOINT = "http://content.guardianapis.com/search"

    start = dt.datetime.fromisoformat(params['from-date'])
    end = dt.datetime.fromisoformat(params['to-date'])

    fullContent = []

    while end >= start:
        # setup of filename day-wise
        datestr = start.strftime("%Y-%m-%d")
        filename = f"{datestr}_{params['q'].replace(' ', '_')}"
        filename = os.path.join(LOCAL_STORAGE, f"{filename}.json")

        articleList = []
        # day-wise
        params['from-date'] = datestr
        params['to-date'] = datestr

        # iterate over all pages
        currentPage = 1
        totalPages = 1
        while currentPage <= totalPages:
            params['page'] = currentPage
            # API CALL
            data = req.get(ENDPOINT, params).json()
            articleList.extend(data['response']['results'])

            currentPage += 1
            totalPages = data['response']['pages']

        if ephemeral:
            fullContent.extend(articleList)
        else:
            with open(filename, "w") as f:
                    f.write(json.dumps(articleList, indent=2))

        start += dt.timedelta(days=1)

    if ephemeral:
        processed = [process(d) for d in fullContent]
        return processed


def process(data: dict) -> dict:
    # title, author, date, url, body, origin, tags, misc
    diet = {
        "title": data['webTitle'],
        "author": [data['fields']['byline']],  # needs to be list
        "date": data['webPublicationDate'],
        "url": data['webUrl'],
        "body": data['fields']['bodyText'],
        "origin": "The Guardian",
        "tags": [d['webTitle'] for d in data['tags']],
        "misc": [""]
    }

    return diet
