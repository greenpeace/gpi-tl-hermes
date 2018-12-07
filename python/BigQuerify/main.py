"""Transform the triggered event from the realtime database into a BQ row."""

# imports
import json

# google interface
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


def rowify(delta: dict, metadata: object) -> list:
    """Transform datadelta + metadata into a list of dicts with field-keys.
    Expects the following structure of the delta event:
        {'daytag': {'ID': {'source': {...},
                           'sentiment': {...},
                           }
                    }
        }
    see `tl-hermes/python/BigQuerify/schema.py` for more details.

    Parameters
    ----------
    delta : dict
        The `delta` contains the path to the changed/new value in key: value
        pairs.
    metadata : object (actually google.cloud.functions.Context)
        The event `metadata`.

    Returns
    -------
    list
        Elements are dictionaries with a structure tied to the `hermes` table.

    """
    row = dict()

    # unpacking the delta
    (daytag, bundle), = delta.items() if delta is not None else (("", None),)
    (ID, content), = bundle.items() if bundle is not None else (("", None),)

    if bundle is not None:
        if content is not None:  # None means deleted node
            print(f"New entry to news archive with ID {metadata.event_id} at"
                  f" {metadata.timestamp}.")

            # we assume here that the structure is almost perfect now
            row['ID'] = ID
            row['timestamp'] = metadata.timestamp
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

        else:  # prints are logged directly
            print(f"Node {daytag}/{ID} has been deleted at "
                  f"{metadata.timestamp}.")

    else:
        print(f"Node {daytag}/ has been deleted at {metadata.timestamp}.")

    return []


def bigQuerify(event: dict, context: object) -> None:
    """Triggered by a change to a Firebase RTDB reference. Forwards the new
    data to BigQuery, prints any returned errors.

    Parameters
    ----------
    event : dict
        `event` payload.
    context : object (actually google.cloud.functions.Context)
        The `context` is the metadata of the event.

    """
    rows = rowify(event['delta'], context)
    if rows:
        error = client.insert_rows(table, rows)

        if error:
            print(f"BigQuery responded with {error}")

        else:
            print("BigQuery reported no errors.")
