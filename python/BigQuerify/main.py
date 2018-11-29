"""Transform the triggered event from the realtime database into a BQ row."""

# imports
import json

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

# TODO: distinction between write/create?
# TODO: check if table exists or not
# TODO: table-setup in a proper way
# TODO: create BQify-able object

def hello_rtdb(event, context):
    """Triggered by a change to a Firebase RTDB reference.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    import json
    trigger_resource = context.resource
    # print out the resource string that triggered the function
    # print(f"Function triggered by change to: {resource_string}.")
    # now print out the entire event object
    # print(str(event))
    # print(str(context))
    print('Function triggered by change to: %s' % trigger_resource)
    print('Admin?: %s' % event.get("admin", False))
    print('Event:')
    print(json.dumps(event))
