#! /usr/bin/env python
"""A collectaion of wrapper functions to interface with Firebase DB."""

from typing import Union, Tuple, Optional

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


def exists(key: str, node: str = "/", deepsearch: bool = False) -> bool:
    """Check if `key` exists as child in `node`.

    Default is a shallow search. If `deepsearch` is True, recursively search
    nested dictionaries for `key`.

    key:        str, the key to search for
    node:       str (optional), the root node to start searching from
    deepsearch: bool (optional), recursively search all child nodes of `node`

    Returns True if key already exists in node, False otherwise.
    """
    noderef = db.reference(node)  # create reference instance

    if not deepsearch:
        nodekeys = noderef.get(shallow=True)

        if isinstance(nodekeys, str):
            nodekeys = [nodekeys]
        else:
            nodekeys = list(nodekeys.keys())

        exists = key in nodekeys  # check if key is shallow nodekeys
        return exists

    else:
        # define recursive dict search ----------------------------------------
        def recursiveSearch(key: str,
                            object: Union[dict, str]) -> Optional[bool]:
            """Recursively search all childs of `object` for `key`."""
            if isinstance(object, str):  # check if lowest level is reached
                if object == key:
                    return True  # return true if found

            elif isinstance(object, list):  # checking for key in lists
                if key in object:
                    return True

            elif isinstance(object, dict):
                for k, v in object.items():
                    if k == key:  # check if key is
                        return True
                    else:
                        result = recursiveSearch(key, v)
                        if result is not None:
                            return result

        # actual else branch --------------------------------------------------
        res = recursiveSearch(key, noderef.get())  # search result
        return False if res is None else res


def create(baseref: db.Reference, path: str) -> db.Reference:
    """Create a childnode to `path` from `baseref`."""
    return baseref.child(path)
