"""
Classes that change how the HTML is rendered for rich text blocks.

Used to deal with WordPress shortcodes that exist in the imported data, among other
things.
"""

import html
import re
from typing import Optional

import shortcodes
from pydantic import BaseModel, HttpUrl, ValidationError


class AddLink(BaseModel):
    externalimage: HttpUrl
    externallink: str
    label: Optional[str]
    category: Optional[int]
    post_id: Optional[int]
    show_images: Optional[bool]
    target: Optional[bool]
    description: Optional[str]


class AddLinkShortcodeRewriter:
    @staticmethod
    def handler(args, kwargs, context):
        try:
            addlink = AddLink(**kwargs)
        except ValidationError:
            return ""
        return f"""\
<a href="{addlink.externallink}"><img src="{addlink.externalimage}"></img></a>"""

    def __call__(self, content: str) -> str:
        parser = shortcodes.Parser(start="[", end="]", ignore_unknown=True)
        parser.register(self.handler, "addlink")
        # Remove the spaces between the attrib name, equals and the value
        content_fixed = re.sub(
            r"(\s(?:post_id|show_images|target|description)+)\s*?=\s*?(['\"])",
            r"\1=\2",
            html.unescape(content),
        )
        try:
            return parser.parse(content_fixed)
        except shortcodes.ShortcodeSyntaxError:
            return content


class Caption(BaseModel):
    id: str
    align: str
    width: int


class CaptionShortcodeRewriter:
    @staticmethod
    def handler(args, kwargs, context, content):
        # caption = Caption(**kwargs)
        match = re.match(r"^(.+>)([^>]+)$", content)
        if not match:
            print("Didn't match content")
            return content
        html_content, caption = match.groups()
        return f"""\
<figure>
  {html_content}
  <figcaption>{caption.strip()}</figcaption>
</figure>"""

    def __call__(self, content: str) -> str:
        parser = shortcodes.Parser(start="[", end="]", ignore_unknown=True)
        parser.register(self.handler, "caption", "/caption")
        content_fixed = html.unescape(content)
        try:
            return parser.parse(content_fixed)
        except shortcodes.ShortcodeSyntaxError:
            return content


class InboundButton(BaseModel):
    url: HttpUrl
    target: str
    font_size: Optional[int]
    color: Optional[str]
    text_color: Optional[str]
    icon: Optional[str]
    width: Optional[str]


class InboundButtonShortcodeRewriter:
    @staticmethod
    def handler(args, kwargs, context, content):
        button = InboundButton(**kwargs)
        return f"""\
<a href="{button.url}" target="{button.target}">{content}</a>"""

    def __call__(self, content: str) -> str:
        parser = shortcodes.Parser(start="[", end="]", ignore_unknown=True)
        parser.register(self.handler, "inbound_button", "/inbound_button")
        content_fixed = html.unescape(content)
        try:
            return parser.parse(content_fixed)
        except shortcodes.ShortcodeSyntaxError:
            return content


def newline_to_br_rewriter(content: str) -> str:
    return content.replace("\n", "<br />")
