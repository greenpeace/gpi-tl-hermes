"""Tool collection to interact with Googles Natural Language API."""
import datetime as dt

from tying import Union, List
from six import binary_type

from google.cloud import language as lang

# setup
nlClient = lang.LanguageServiceClient()


class Content:
    """Web content to be analysed and classified."""

    __slots__ = ["_source", "_sentiment"]

    def __init__(self, *, title: str, author: Union[str, List[str]],
                 date: dt.datetime, url: str, body: str, origin: str,
                 tags: Union[str, List[str]], misc: Union[str, List[str]]):
        """Creates a new instance of `Content`.

        Parameters
        ----------
        title : str
            The `title` of the content.
        author : Union[str, List[str]]
            The `author`(s) of the article/tweet/post.
        date : dt.datetime
            The publishing `date`.
        url : str
            The `url` to the Content.
        body : str
            The `body` of the Content, i.e. the actually interesting part.
        origin : str
            `origin`, i.e. from facebook, twitter, any other news site, ...
        tags : Union[str, List[str]]
            `tags`, i.e. hashtags or any other category tags prior to Content
            classification.
        misc : Union[str, List[str]]
            `misc`, i.e. everything that doesn't fit in the keywords above.
        """
        # initialize
        self._source = None
        self._sentiment = None

        # setting values
        self.source = {
            "title": title,
            "author": [author] if isinstance(author, str) else author,
            "date": str(date),
            "url": url,
            "body": body.decode('utf-8') if isinstance(body, binary_type) else body,
            "origin": origin,
            "tags": [tags] if isinstance(tags, str) else tags,
            "misc": [misc] if isinstance(misc, str) else misc
        }
        self.sentiment = dict()  # will be set later

    # properties --------------------------------------------------------------
    @property
    def source(self) -> dict:
        """The Content's source attribute.

        Returns
        -------
        dict
            Contains metadata (if available) like `author`, `title`, `date`
            (published), `url`, `body`, `origin` (twitter, facebook, ..),
            `tags` (any kind of content tags, e.g. hashtags, categories (pre
            natural language classification), and `misc`.
        """
        return self._source

    @source.setter
    def source(self, data: dict) -> None:
        """Set/update the Content's source attribute.

        Parameters
        ----------
        data : dict
            Contains metadata (if available) like `author`, `title`, `date`
            (published), `url`, `body`, `origin` (twitter, facebook, ..),
            `tags` (any kind of content tags, e.g. hashtags, categories (pre
            natural language classification), and `misc`.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dictionary-like object for source "
                            f"attribute, but got {type(data)}.")
        else:
            self._source = data

    @property
    def sentiment(self) -> dict:
        """The Content's sentiment attribute.

        Returns
        -------
        dict
            Contains the Content's `overall` sentiment `score`, `magnitude` and
            `categories`, as well as the `content` specific part, with a
            sentiment `score` and `magnitude` for each `text` snippet (some
            may call them sentences).
        """
        return self._sentiment

    @sentiment.setter
    def sentiment(self, data: dict) -> None:
        """Set/update the Content's sentiment attribute.

        Parameters
        ----------
        data : dict
            Contains the Content's `overall` sentiment `score`, `magnitude` and
            `categories`, as well as the `content` specific part, with a
            sentiment `score` and `magnitude` for each `text` snippet (some
            may call them sentences).
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dictionary-like object for sentiment "
                            f"attribute, but got {type(data)}.")
        else:
            self._sentiment = data

    # methods -----------------------------------------------------------------
    def analyse(self, client: lang.LanguageServiceClient) -> None:

        # preparations
        document = lang.types.Document(
            content=self.source['body'],
            type=lang.enums.Document.Type.PLAIN_TEXT
        )

        # analysis + processing -----------------------------------------------
        annotations = client.analyze_sentiment(document=document)

        # overall
        self.sentiment['overall'] = {
            "score": annotations.document_sentiment.score,
            "magnitude": annotations.document_sentiment.magnitude
        }

        # sentence-wise
        self.sentiment['content'] = []
        for s in annotations.sentences:
            self.sentiment['content'].append({
                "text": s.text.content,
                "score": s.sentiment.score,
                "magnitude": s.sentiment.magnitude
            })
