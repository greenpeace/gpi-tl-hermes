# tl-hermes
News Aggregations and Sentiment Analysis app

### Using the `hermes` python module
Add `export $PYTHONPATH=/path/to/tl-hermes/python/` to your favourite *sh's configuration file. Then hermes can be used e.g. with
```Python
import hermes.firebaseInterface as fbi
from hermes.nappy.tools import Content
```

### Structure of the `hermify` script
  1. Firebase + NaturalLanguage app/client setup
  2. Create day tag, e.g. "2018-12-11"
  3. Get list of childnodes of '/' in RTDB and create/reference the nodeToday
  4. Make an API call + parse the response into dict/json-like object
  5. Create `Content` instance & do sentiment analysis
  6. Deduplication -> check if content of response is in RTDB and if not:
     1. Push content to RTDB (automatically added to BigQuery)
