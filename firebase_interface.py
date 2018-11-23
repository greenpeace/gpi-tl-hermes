#! /usr/bin/env python
"""A collectaion of wrapper functions to interface with Firebase DB."""

from typing import Union, Tuple

import firebase_admin as fa
from firebase_admin import db, credentials


# wrapper functinos ----------------------------------------------------------


def setup(creds: str,
          databaseURL: str = "https://gpi-it-1225.firebaseio.com/") -> fa.App:
    """
    Setup the firebase app instance for communication.

    creds:          str, path to the credentials json file
    databaseURL:    str (optional), the database URL for the database

    Returns an firebase_admin.App instance with given parameters.
    """
    return fa.initialize_app(credentials.Certificate(creds),
                             {"databaseURL": databaseURL})


def ref(node: str = "/",
        get: Union[bool, dict] = True) -> Union[db.reference,
                                                Tuple[dict, db.reference]]:
    """
    Create a database reference representing the node at node path.

    If `get` is True, return the values of the currently specified node, with
    the default values for `etag` and `shallow`. These parameters can be
    exlicitely specified with a dictionary, e.g. `get={"shallow": True}`.

    node:   str (optional), the node path
    get:    bool, dict (optional), specify if and how to access db data.

    Returns a `firebase_admin.db.reference` object or a dictionary (json) of
    database content.
    """
    if isinstance(get, bool):
        noderef = db.reference(node)

        if not get:
            return noderef  # just return the database reference

        else:
            return noderef, noderef.get()  # return db reference and data

    elif isinstance(get, dict):
        noderef = db.reference(node)
        return noderef, noderef.get(**get)  # return db ref, data w/ parameters

    else:
        raise RuntimeError(f"Unknown argument for get parameters: {get}.")
