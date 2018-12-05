"""BigQuery table schema for tl-hermes."""

from google.cloud.bigquery import SchemaField as SF

# Schema
hermesSchema = [
    SF('ID', 'STRING', mode='REQUIRED'),
    SF('timestamp', 'TIMESTAMP', mode='REQUIRED'),
    SF('source', 'RECORD', mode='REQUIRED',
       fields=(SF('title', 'STRING'),
               SF('author', 'STRING', mode='REPEATED'),
               SF('date', 'DATETIME'),
               SF('url', 'STRING'),
               SF('body', 'STRING'),
               SF('origin', 'STRING', description='twitter, facebook, ...'),
               SF('tags', 'STRING', mode='REPEATED'),
               SF('misc', 'STRING', mode='REPEATED')
               )
       ),
    SF('sentiment', 'RECORD', mode='NULLABLE',
       fields=(SF('overall', 'RECORD', mode='REQUIRED',
                  fields=(SF('score', 'FLOAT'),
                          SF('magnitude', 'FLOAT'),
                          SF('categories', 'STRING', mode='REPEATED')
                          )
                  ),
               SF('content', 'RECORD', mode='REPEATED',
                  fields=(SF('text', 'STRING'),
                          SF('score', 'FLOAT'),
                          SF('magnitude', 'FLOAT')
                          )
                  )
               )
       )
    ]
