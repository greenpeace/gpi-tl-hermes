"""Transform the triggered event from the realtime database into a BQ row."""

# imports
import json

# google interface
from google.cloud import bigquery

# custom stuff
from schema import hermesSchema

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

    Args:
        delta       dict, path to the changed/new value in key:value pairs
        metadata    cloud function Context, contains event metadata

    Expects the following structure of the delta event:
        {'daytag': {'ID': {'article': {...},
                           'sentiment': {...},
                           'tags': {...}
                           }
                    }
        }
    """
    row = dict()

    # unpacking the delta
    (daytag, bundle), = delta.items()
    (ID, content), = bundle.items()

    # setting row values
    row['ID'] = ID
    row['timestamp'] = metadata.timestamp
    row['articleContent'] = content['article']
    row['sentimentContent'] = content['sentiment']
    row['tags'] = content['tags']

    return [row]


def bigQuerify(event: dict, context: object) -> None:
    """Triggered by a change to a Firebase RTDB reference.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    print(f"New entry to news archive with ID {context.event_id} at"
          " {context.timestamp}.")

    client.insert_rows(table, rowify(event['delta'], context))
