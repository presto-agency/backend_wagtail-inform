"""
Classes used to modify article content.

Generally used from the ./manage.py shell in order to make permanent changes to the
article content in the database.
"""

from abc import ABC
import html
import re
from typing import Generic, Iterator, List, Optional, Type, TypeVar

import shortcodes
from django.db.models import QuerySet
from wagtail.core.blocks import RichTextBlock

from .models import Article

ArticleT = TypeVar("ArticleT", bound=Article)


class ContentFilter(ABC):
    def __init__(self, replace_with: Optional[str] = None):
        if replace_with is None:
            replace_with = " "
        self.replace_with = replace_with

    def filter(self, content: str) -> str:
        pass


class NBSPFilter(ContentFilter):
    def filter(self, content: str) -> str:
        return content.replace("&nbsp;", self.replace_with).replace(
            "\xa0", self.replace_with
        )


class AMPFilter(ContentFilter):
    def filter(self, content: str) -> str:
        return content.replace("&amp;", self.replace_with)


class ShortcodeFilterInboundButton(ContentFilter):
    @staticmethod
    def inbound_button_handler(args, kwargs, context, content):
        target = kwargs.get("target", "")
        if target:
            target = f' target="{target}"'
        return f"""<a href="{kwargs['url']}"{target}>{content}</a>"""

    def filter(self, content: str) -> str:
        parser = shortcodes.Parser(start="[", end="]", ignore_unknown=True)
        parser.register(self.inbound_button_handler, "inbound_button", "/inbound_button")
        return parser.parse(content)


# class ShortcodeAddlink(ContentFilter):
#     @staticmethod
#     def handler(args, kwargs, context):
#         pass

#     def filter(self, content: str) -> str:
#         from .rewriters import AddLink

#         parser = shortcodes.Parser(start="[", end="]", ignore_unknown=True)
#         parser.register(self.handler, "addlink")
#         # Remove the spaces between the attrib name, equals and the value
#         content_fixed = re.sub(
#             r"(\s(?:post_id|show_images|target|description)+)\s*?=\s*?(['\"])",
#             r"\1=\2",
#             html.unescape(content),
#         )
#         try:
#             return parser.parse(content_fixed)
#         except shortcodes.ShortcodeSyntaxError:
#             return content


class ContentLocator(ABC):
    @classmethod
    def filter_content(cls, article: ArticleT, content_filter: ContentFilter) -> ArticleT:
        pass

    @classmethod
    def filter_all(
        cls, qs: QuerySet[ArticleT], content_filter: ContentFilter
    ) -> Iterator[ArticleT]:
        for article in qs:
            yield cls.filter_content(article, content_filter)


class ArticleBodyRichTexts(ContentLocator):
    @classmethod
    def filter_content(cls, article: ArticleT, content_filter: ContentFilter) -> ArticleT:
        for block in article.body:
            if not isinstance(block.block, RichTextBlock):
                continue
            block.value.source = content_filter.filter(block.value.source)
        return article


class ArticleExcerpt(ContentLocator):
    @classmethod
    def filter_content(cls, article: ArticleT, content_filter: ContentFilter) -> ArticleT:
        article.excerpt = content_filter.filter(article.excerpt)
        return article


class ArticleTitle(ContentLocator):
    @classmethod
    def filter_content(cls, article: ArticleT, content_filter: ContentFilter) -> ArticleT:
        article.title = content_filter.filter(article.title)
        return article
