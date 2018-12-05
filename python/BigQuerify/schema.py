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

# Example
'''
import datetime as dt

testrow = [{"ID": "satehusa",
            "timestamp": str(dt.datetime.now(tz=dt.timezone.utc).isoformat()),
            "source": {"title": "hurr",
                       "author": "durr",
                       "date": str(dt.datetime(2054, 11, 7, 14, 5)),
                       "url": "www.fancyburr.nurr",
                       "body": "I am a body text.\nveeeeeeeeeeeeeeeeeeeeeery long \n mimomaseouha",
                       "origin": "twitter",
                       "tags": ["taggy", "swaggy"],
                       "misc": ["miscy"]
                       },
            "sentiment": {"overall": {"score": 1.4567,
                                      "magnitude": 665234.4,
                                      "categories": ["nifty", "schwifty", "drifty"]
                                      },
                          "content": [
                            {"text": "I am one sentence.",
                             "score": 0.2,
                             "magnitude": 5
                             },
                            {"text": "I am another sentence",
                             "score": 0.4,
                             "magnitude": 5
                             }
                          ]
                          }
            }]
'''
