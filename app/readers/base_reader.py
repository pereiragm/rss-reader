"""
Credits: https://www.jcchouinard.com/read-rss-feed-with-python/
"""
import logging
import datetime as dt

from bs4 import BeautifulSoup
import requests
from requests import HTTPError, Response

# from app.schemas.feed import FeedBase
# from app.schemas.feed import FeedBase2 as FeedBase
from app.schemas.feed import FeedRssReader as FeedBase
from app.schemas.post import PostBase

logger = logging.getLogger(__name__)

# e.g., "Tue, 16 May 2023 22:41:12 +0200"
# RSS_DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
RSS_DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"  # tweakers


def dt_from_str(dt_input: str) -> dt.datetime:
    _suported_formats = (
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",  # Tue, 16 May 2023 22:41:12 +0200
    )

    dt_out = None
    for f in _suported_formats:
        try:
            dt_out = dt.datetime.strptime(dt_input, f)
        except ValueError:
            continue

    if not dt_out:
        Exception(f"Format not known: {dt_input}")

    return dt_out


class RSSFeedReader:
    """
    Abstraction able to request a content from an RSS feed, parse
    its information and build a structured data model.
    """

    def __init__(self, rss_url: str, parser: str = "lxml") -> None:
        self.base_log = f"[{self.__class__.__name__}] -"
        self.url = rss_url
        self.parser = parser
        self.response = self._make_request()
        self.soup = BeautifulSoup(self.response.text, self.parser)
        self._model = self._build_model()

    def _make_request(self) -> Response | None:
        response = requests.get(self.url)
        response.raise_for_status()
        return response

    def _build_model(self) -> FeedBase:
        def get_datetime_utc(dt_input: str) -> dt.datetime:
            dt_out = dt_from_str(dt_input)
            return dt_out.astimezone(tz=dt.timezone.utc)

        posts = [
            PostBase(
                title=item.title.text,
                description=item.description.text,
                link=item.link.next_sibling.text,
                pub_date=get_datetime_utc(item.pubdate.text),
            )
            for item in self.soup.rss.channel.find_all(
                "item"
            )  # Get list with <item> tags
        ]

        feed = FeedBase(
            title=self.soup.rss.channel.title.text,
            description=self.soup.rss.channel.description.text,
            link=self.soup.rss.channel.link.next_sibling.text,
            language=self.soup.rss.channel.language.text,
            last_build_date=get_datetime_utc(self.soup.rss.channel.lastbuilddate.text),
            posts=posts,
        )

        return feed

    @property
    def model(self) -> FeedBase:
        return self._model
