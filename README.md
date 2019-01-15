# tl-hermes
News Aggregations and Sentiment Analysis app

[![TechLab Presentation](https://drive.google.com/uc?export=view&id=1Fk0ZrI2UoEKlj7TvQm38FJSZhSPTbvK0)](https://drive.google.com/open?id=1-4NuBl5tVsD18jViMEJYk7vmN4eaE9TA)

### Using the `hermes` python module
Add `export PYTHONPATH=/path/to/tl-hermes/python/` to your favourite *sh's configuration file. Then hermes can be used e.g. with
```Python
import hermes.firebaseInterface as fbi
from hermes.nappy.tools import Content
from hermes.api import theguardian
```

### Structure of the `hermify` script
  1. Firebase + NaturalLanguage app/client setup
  2. Create day tag, e.g. "2018-12-11"
  3. Get list of childnodes of '/' in RTDB and create/reference the nodeToday
  4. Make an API call + parse the response into dict/json-like object
  5. Create `Content` instance & do sentiment analysis
  6. Deduplication -> check if content of response is in RTDB and if not:
     1. Push content to RTDB (returns the randomly generated node key)
     2. Send a `POST` request to a cloud function, which extracts the newly generated content from RTDB and pushes it into BigQuery

### How to use the `hermify` script
  1. Create a folder `api_configs` in the same directory as `hermes.py`. 
  2. Place an API config like the example config in `python/hermes/api/guardian_example_settings.json` in `api_configs` and adapt the contents accordingly (side note: empty strings for one or both of the date sections will result in the script just requesting today's data.
  3. call the script with `python hermify.py` (python 3 of course)

### Dependencies
`Python==3.7.1`
For packages, please refer to the [requirements.txt](python/requirements.txt). Install them via `pip install -r requirements.txt`.
