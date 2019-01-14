"""Transform the given Realtime database node into a BigQuery row entry."""

import firebase_admin as fa
from firebase_admin import db
from google.cloud import bigquery

# bigquery setup --------------------------------------------------------------
client = bigquery.Client()
dataset_id = "tl_hermes"
table_id = "hermes"

# references
ds_ref = client.dataset(dataset_id)
table_ref = ds_ref.table(table_id)

ds = client.get_dataset(ds_ref)
table = client.get_table(table_ref)

# realtime database init ------------------------------------------------------
app = fa.initialize_app(options={"databaseURL": "https://gpi-it-1225.firebaseio.com/"})


def rowify(path: str, meta: dict) -> list:
    """Transforms the content found at `path` into a list of dicts with field-
    keys.

    Parameters
    ----------
    path : str
        `path` is the full path to the newly generated node in realtime
        database.
    meta : dict
        `meta` contains meta information as creation timestamp of the database
        entry.

    Returns
    -------
    list
        Elements are dictionaries with a structure tied to the `hermes` table.

    """
    node = db.reference(path)  # get reference
    content = node.get()

    row = dict()

    if content is not None:  # found data in path reference
        [daytag, ID] = node.path.split('/')[-2:]  # FIXME ?

        row['ID'] = ID
        row['timestamp'] = meta['timestamp']  # TODO

        for key, value in content.items():  # keys = source, sentiment
            row[key] = value  # lift one level of nested entries

        # replace number-indexed dicts with lists --> BigQuery REPEATED
        # BigQuery doesn't like dictionaries when it expects arrays/lists
        for arg in ["author", "tags", "misc"]:
            row['source'][arg] = list(row['source'][arg].values())

        cats = list(row['sentiment']['overall']['categories'].values())
        row['sentiment']['overall']['categories'] = cats

        con = list(row['sentiment']['content'].values())
        row['sentiment']['content'] = con

        return [row]

    else:
        print(f"Node {node.path} could not be found.")

    return []


def bigQuerify(request) -> None:
    """Triggered by a HTTP request from a `hermify` script.

    Parameters
    ----------
    request : flask.Request
        `request` is a HTTP request object. Contains the path to a new entry
        in the realtime database and potetial helpful info in the data arg.

    """
    payload = request.get_json()  # unpack request
    # node = db.reference(payload['path'])

    rows = rowify(payload['path'], payload['meta'])
    if rows:
        error = client.insert_rows(table, rows)

        if error:
            print(f"BigQuery responded with {error}")

        else:
            print("BigQuery reported no errors.")
