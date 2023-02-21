from typing import Any, Dict

from django.forms.utils import ErrorList
from django.template.loader import render_to_string
from grapple.helpers import register_streamfield_block
from grapple.models import GraphQLImage, GraphQLPage, GraphQLString
from wagtail.core import blocks, rich_text
from wagtail.core.blocks.struct_block import StructBlockValidationError
from wagtail.core.rich_text.rewriters import (
    EmbedRewriter,
    LinkRewriter,
    MultiRuleRewriter,
)
from wagtail.images.blocks import ImageChooserBlock

from .rewriters import (
    AddLinkShortcodeRewriter,
    CaptionShortcodeRewriter,
    InboundButtonShortcodeRewriter,
    newline_to_br_rewriter,
)

FRONTEND_REWRITER = None


def expand_db_html(html):
    """
    Expand database-representation HTML into proper HTML usable on front-end templates
    """
    global FRONTEND_REWRITER

    if FRONTEND_REWRITER is None:
        embed_rules = rich_text.features.get_embed_types()
        link_rules = rich_text.features.get_link_types()
        FRONTEND_REWRITER = MultiRuleRewriter(
            [
                LinkRewriter(
                    {
                        linktype: handler.expand_db_attributes
                        for linktype, handler in link_rules.items()
                    }
                ),
                EmbedRewriter(
                    {
                        embedtype: handler.expand_db_attributes
                        for embedtype, handler in embed_rules.items()
                    }
                ),
                # HACK: Temporary fix -@flyte at 13/04/2022, 20:44:57
                # There may be a better way to "register" rewriters but I couldn't quickly
                # find a way to register something that wasn't a LinkRewriter or an
                # EmbedRewriter, so I had to override all of the classes you see in this
                # file 😓
                AddLinkShortcodeRewriter(),
                CaptionShortcodeRewriter(),
                InboundButtonShortcodeRewriter(),
                newline_to_br_rewriter,
            ]
        )

    return FRONTEND_REWRITER(html)


class RichText(rich_text.RichText):
    def __html__(self):
        return render_to_string(
            "wagtailcore/shared/richtext.html", {"html": expand_db_html(self.source)}
        )


class RichTextBlock(blocks.RichTextBlock):
    def get_default(self):
        if isinstance(self.meta.default, RichText):
            return self.meta.default
        else:
            return RichText(self.meta.default)

    def to_python(self, value):
        # convert a source-HTML string from the JSONish representation
        # to a RichText object
        return RichText(value)

    def value_from_form(self, value):
        # Rich text editors return a source-HTML string; convert to a RichText object
        return RichText(value)

    class Meta:
        icon = "doc-full"


# class BlockQuoteBlock(field_block.BlockQuoteBlock):
#     def render_basic(self, value, context=None):
#         if not value:
#             return ""
#         return mark_safe(f"<blockquote>{value}</blockquote>")

CHOICES_LEFT_RIGHT = (
    ("left", "Left"),
    ("right", "Right"),
)


@register_streamfield_block
class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock()
    caption = blocks.CharBlock(required=False)
    external_url = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    graphql_fields = [
        GraphQLImage("image"),
        GraphQLString("alt_text"),
        GraphQLString("caption"),
        GraphQLString("external_url"),
        GraphQLPage("page"),
    ]

    def clean(self, value: Dict[str, Any]):
        errors = {}
        if value.get("external_url") and value.get("page"):
            errors["external_url"] = ErrorList(
                ["Cannot use external URL when a Page is selected"]
            )
        if errors:
            raise StructBlockValidationError(errors)
        return super().clean(value)


@register_streamfield_block
class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    image = ImageChooserBlock(required=False)
    image_alt_text = blocks.CharBlock(required=False)
    image_caption = blocks.CharBlock(required=False)
    image_align = blocks.ChoiceBlock(choices=CHOICES_LEFT_RIGHT, default="right")

    graphql_fields = [
        GraphQLString("quote"),
        GraphQLImage("image"),
        GraphQLString("image_alt_text"),
        GraphQLString("image_caption"),
        GraphQLString("image_align"),
    ]

    def clean(self, value: Dict[str, Any]):
        errors = {}
        if value.get("image") is not None and not value.get("image_alt_text"):
            errors["image_alt_text"] = ErrorList(
                ["This field is required when an image is selected"]
            )
        if errors:
            raise StructBlockValidationError(errors)
        return super().clean(value)


@register_streamfield_block
class FloatingImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock()
    align = blocks.ChoiceBlock(choices=CHOICES_LEFT_RIGHT)
    caption = blocks.CharBlock(required=False)
    external_url = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    graphql_fields = [
        GraphQLImage("image"),
        GraphQLString("alt_text"),
        GraphQLString("align"),
        GraphQLString("caption"),
        GraphQLString("external_url"),
        GraphQLPage("page"),
    ]

    def clean(self, value: Dict[str, Any]):
        errors = {}
        if value.get("external_url") and value.get("page"):
            errors["external_url"] = ErrorList(
                ["Cannot use external URL when a Page is selected"]
            )
        if errors:
            raise StructBlockValidationError(errors)
        return super().clean(value)


@register_streamfield_block
class RelatedContentBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    image_alt_text = blocks.CharBlock()
    heading = blocks.CharBlock(required=False)
    content = blocks.CharBlock(required=False)
    external_url = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    graphql_fields = [
        GraphQLImage("image"),
        GraphQLString("image_alt_text"),
        GraphQLString("heading"),
        GraphQLString("content"),
        GraphQLString("external_url"),
        GraphQLPage("page"),
    ]

    def clean(self, value: Dict[str, Any]):
        errors = {}
        if value.get("external_url") and value.get("page"):
            errors["external_url"] = ErrorList(
                ["Cannot use external URL when a Page is selected"]
            )
        if not value.get("external_url") and not value.get("page"):
            errors["external_url"] = ErrorList(
                ["Either this field or Page must be populated"]
            )
            errors["page"] = ErrorList(
                ["Either this field or External URL must be populated"]
            )
        if not value.get("heading") and not value.get("content"):
            errors["heading"] = ErrorList(["This field and/or Content must be populated"])
            errors["content"] = ErrorList(["This field and/or Heading must be populated"])
        if errors:
            raise StructBlockValidationError(errors)
        return super().clean(value)
