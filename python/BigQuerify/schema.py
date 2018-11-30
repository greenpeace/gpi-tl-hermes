"""BigQuery table schema for tl-hermes."""

from google.cloud.bigquery import SchemaField

# Schema
hermesSchema = [
    SchemaField('ID', 'STRING', mode='REQUIRED'),
    SchemaField('timestamp', 'TIMESTAMP', mode='REQUIRED'),
    SchemaField('articleContent', 'RECORD', mode='NULLABLE'),  # nested?
    SchemaField('sentimentContent', 'RECORD', mode='NULLABLE'),  # nested?,
    ]
