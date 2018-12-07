"""This script sets up the BigQuery table `hermes` in dataset `tl_hermes`."""

from google.cloud import bigquery
from google.cloud.bigquery import Table

from schema import hermesSchema

# init
ds = "tl_hermes"
t = "hermes"

client = bigquery.Client()

# dataset
ds_ref = client.dataset(ds)
ds = client.get_dataset(ds_ref)

# table
t_ref = ds.table(t)
table = Table(t_ref, schema=hermesSchema)
table = client.create_table(table)
