"""Class definition for The Guardian news API."""

import os
import json
import requests as req
import datetime as dt


def call(params: dict) -> None:
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

    """
    # setup of local storage
    LOCAL_STORAGE = os.path.join("temp", "articles")
    os.makedirs(LOCAL_STORAGE, exist_ok=True)

    # API endpoint
    ENDPOINT = "http://content.guardianapis.com/search"

    start = dt.datetime.fromisoformat(params['from-date'])
    end = dt.datetime.fromisoformat(params['to-date'])

    while end >= start:
        # setup of filename day-wise
        datestr = start.strftime("%Y-%m-%d")
        datestr = f"{datestr}_{params['q'].replace(' ', '_')}"
        filename = os.path.join(LOCAL_STORAGE, f"{datestr}.json")

        if not os.path.exists(filename):
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

            with open(filename, "w") as f:
                f.write(json.dumps(articleList, indent=2))

        start += dt.timedelta(days=1)
