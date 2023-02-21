from __future__ import annotations

import json
from functools import cached_property
from typing import List, Optional

import graphene
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.shortcuts import get_object_or_404

from graphql import ResolveInfo
from grapple.helpers import register_plural_query_field, register_singular_query_field
from grapple.models import (
    GraphQLCollection,
    GraphQLForeignKey,
    GraphQLImage,
    GraphQLInt,
    GraphQLStreamfield,
    GraphQLString,
    GraphQLDocument,
    GraphQLSnippet,
)

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.search.index import FilterField, RelatedFields, SearchField
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail_color_panel.fields import ColorField
from wagtail_icon_picker.edit_handlers import MaterialDesignIconsPickerPanel
from wagtail_icon_picker.fields import IconField

from .blocks import (
    FloatingImageBlock,
    ImageBlock,
    QuoteBlock,
    RelatedContentBlock,
    RichTextBlock,
)

# Models declared in settings.py
from .settings import ArticlesRSSFeedsSettings, ArticleTypesSettings  # noqa

# ******************************
# **         Snippets         **
# ******************************
from .widgets import AdminTimezoneDateTimeInput

from wagtailorderable.models import Orderable as WagOrderable
from datetime import datetime


@register_snippet
class Country(models.Model):
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ["name"]

    name = models.CharField(max_length=255)
    panels = [
        FieldPanel("name"),
    ]
    def __str__(self):
        return self.name


@register_snippet
class Location(models.Model):
    class Meta:
        ordering = ["country", "name"]

    country = models.ForeignKey("articles.Country", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)

    panels = [
        SnippetChooserPanel("country"),
        FieldPanel("name"),
    ]
    def __str__(self):
        return f"{self.country} - {self.name}"


@register_snippet
class Company(index.Indexed, models.Model):
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["name"]

    name = models.CharField(max_length=255)
    logo = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL
    )
    privacy_policy_url = models.URLField(null=True, blank=True)
    location = models.ForeignKey("articles.Location", null=True, blank=True, on_delete=models.SET_NULL)
    city = models.CharField(max_length=127, blank=True)
    country = models.ForeignKey("articles.Country", null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=63, blank=True)
    website = models.URLField(null=True, blank=True)
    sector = models.CharField(max_length=127, blank=True)
    role = models.CharField(max_length=127, blank=True)
    summary = models.TextField(blank=True)
    member_type = models.CharField(max_length=127, blank=True)
    is_member = models.BooleanField(null=True)
    membership_start_date = models.DateField(null=True, blank=True)
    member_level = models.CharField(max_length=127, blank=True)
    owner_email = models.EmailField(null=True, blank=True)
    owner_name = models.CharField(max_length=127, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_name = models.CharField(max_length=127, blank=True)
    contact_phone = models.CharField(max_length=127, blank=True)
    hide_in_member_list = models.BooleanField(null=True)

    panels = [
        ImageChooserPanel("logo"),
        FieldPanel("name"),
        FieldPanel("privacy_policy_url"),
        SnippetChooserPanel("country"),
        SnippetChooserPanel("location"),
        FieldPanel("city"),
        FieldPanel("address"),
        FieldPanel("postal_code"),
        FieldPanel("website"),
        FieldPanel("sector"),
        FieldPanel("role"),
        FieldPanel("summary"),
        FieldPanel("member_type"),
        FieldPanel("is_member"),
        FieldPanel("membership_start_date"),
        FieldPanel("member_level"),
        FieldPanel("owner_email"),
        FieldPanel("owner_name"),
        FieldPanel("contact_email"),
        FieldPanel("contact_name"),
        FieldPanel("contact_phone"),
        FieldPanel("hide_in_member_list"),
    ]

    graphql_fields = [
        GraphQLString("name"),
        GraphQLImage("logo"),
        GraphQLString("privacy_policy_url"),
        GraphQLString("website"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return self.name


@register_snippet
class EventSpeaker(index.Indexed, models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=255)
    avatar = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.PROTECT, null=True, blank=True
    )
    job_title = models.CharField(max_length=255, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.job_title:
            return f"{self.name} - {self.job_title}"
        return self.name

    panels = [
        FieldPanel("name"),
        FieldPanel("job_title"),
        SnippetChooserPanel("company"),
        ImageChooserPanel("avatar"),
        FieldPanel("about"),
    ]

    graphql_fields = [
        GraphQLString("name"),
        GraphQLString("job_title"),
        GraphQLSnippet("company", "articles.Company"),
        GraphQLImage("avatar"),
        GraphQLString("about"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
        index.SearchField("job_title", partial_match=True),
        index.SearchField("company", partial_match=True),
    ]


@register_snippet
@register_singular_query_field("author")
@register_plural_query_field("authors")
class Author(index.Indexed, models.Model):
    class Meta:
        ordering = ["first_name", "last_name"]

    first_name = models.CharField(max_length=127, blank=True)
    last_name = models.CharField(max_length=127, blank=True)
    display_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.PROTECT, null=True, blank=True
    )
    # TODO: Tasks pending completion -@flyte at 07/04/2022, 13:11:25
    # Does this need to be required? Where does it come from post WP export?
    username = models.CharField(max_length=127)
    biography = RichTextField(blank=True, null=True)
    wp_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.display_name} <{self.email}>"

    def featured_articles(self, _info: ResolveInfo):
        return (
            self.articles.select_related("article")
            .filter(article__live=True)
            .order_by("-article__first_published_at")[:3]
        )

    def get_avatar_url(self):
        if self.avatar:
            return mark_safe('<img src="%s" width="100"/>' % self.avatar.file.url)
        else:
            return 'No photo'

    get_avatar_url.short_description = 'Photo'

    def get_biography(self):
        if self.biography:
            return 'Yes'
        else:
            return 'No'

    get_biography.short_description = 'Biography'

    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("display_name"),
        FieldPanel("job_title"),
        SnippetChooserPanel("company"),
        FieldPanel("email"),
        ImageChooserPanel("avatar"),
        FieldPanel("username"),
        FieldPanel("wp_id"),
        FieldPanel("biography"),
    ]

    graphql_fields = [
        GraphQLString("first_name"),
        GraphQLString("last_name"),
        GraphQLString("display_name"),
        GraphQLString("job_title"),
        GraphQLSnippet("company", "articles.Company"),
        GraphQLImage("avatar"),
        GraphQLString("biography"),
        GraphQLCollection(
            GraphQLForeignKey, "articles", content_type="articles.ArticleAuthorsOrderable"
        ),
        GraphQLCollection(
            GraphQLForeignKey,
            "featured_articles",
            content_type="articles.ArticleAuthorsOrderable",
            is_queryset=True,
        ),
    ]

    search_fields = [
        index.SearchField("display_name", partial_match=True),
    ]


@register_snippet
@register_singular_query_field("topic")
@register_plural_query_field("topics")
class ArticleTopic(index.Indexed, models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=127, unique=True)
    slug = models.SlugField(max_length=127, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    graphql_fields = [GraphQLString("name"), GraphQLString("slug")]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]


@register_snippet
@register_singular_query_field("source")
@register_plural_query_field("sources")
class ArticleSource(index.Indexed, models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=127)
    label_text = models.CharField(
        max_length=63,
        help_text=(
            "The text to display on the label at the top-left corner of the Article's "
            "thumbnail image in Article lists. Leave blank to not add a label."
        ),
        blank=True,
    )
    label_text_mobile = models.CharField(
        max_length=63,
        help_text=(
            "The same as the Label text field above, but a shorter version to be "
            "displayed on mobile layouts."
        ),
        blank=True,
    )
    text = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.name

    graphql_fields = [
        GraphQLString("name"),
        GraphQLString("label_text"),
        GraphQLString("label_text_mobile"),
        GraphQLString("text"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]


@register_snippet
@register_singular_query_field("category")
@register_plural_query_field("categories")
class ArticleCategory(index.Indexed, models.Model):
    """
    Comes from the <category domain="category"> elements of the WP export.
    Might not need this because it's essentially the same thing as Topics, but it's here
    just so that we're not throwing data away unintentionally.
    """

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Article Categories"

    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    graphql_fields = [GraphQLString("name")]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]


@register_snippet
class ArticleArea(index.Indexed, models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    graphql_fields = [GraphQLString("name")]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]


@register_snippet
class ArticleVertical(index.Indexed, models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    graphql_fields = [GraphQLString("name")]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]


@register_snippet
class VuetifyIcon(models.Model):
    """
    Model storing a name of a Vuetify icon and the associated primary colour.
    It is used in settings.ArticleTypesSettings.
    """

    icon = IconField()
    color = ColorField()

    panels = [
        MaterialDesignIconsPickerPanel("icon"),
        NativeColorPanel("color"),
    ]

    graphql_fields = [
        GraphQLString("icon"),
        GraphQLString("color"),
    ]

    def __str__(self):
        return f"{self.icon} ({self.color})"


@register_snippet
class Summits(index.Indexed, models.Model):
    class Meta:
        ordering = ["name"]
        verbose_name = "Summit"
        verbose_name_plural = "Summits"

    name = models.CharField(max_length=255, blank=True)
    logo = models.ForeignKey("wagtailimages.Image", on_delete=models.PROTECT, null=True, blank=True)
    description = RichTextField(blank=True, null=True)
    text = RichTextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    def get_logo_url(self):
        if self.logo:
            return mark_safe('<img src="%s" width="100"/>' % self.logo.file.url)
        else:
            return 'No logo'

    get_logo_url.short_description = 'Logo'

    panels = [
        FieldPanel("name"),
        ImageChooserPanel("logo"),
        FieldPanel("description"),
        FieldPanel("text"),
    ]

    graphql_fields = [
        GraphQLString("name"),
        GraphQLString("description"),
        GraphQLString("text"),
        GraphQLImage("logo"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]


# ******************************
# ** Linking models (M2M etc) **
# ******************************


class ArticleCompanyAbstractConnection(models.Model):
    """
    Defines an abstract connection between an article and company.
    See the subclasses.
    """

    article = ParentalKey("Article", related_name="+")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("company")]

    graphql_fields = [GraphQLForeignKey("company", content_type="articles.Company")]

    @property
    def company_name(self):
        """
        Circumvents https://github.com/wagtail/wagtail/issues/3910.
        :return: The name of the company.
        """
        return self.company.name

    class Meta:
        abstract = True


class ArticleCompanyConnection(ArticleCompanyAbstractConnection):
    """
    Article mentions, or is about the company.
    """

    article = ParentalKey("Article", related_name="companies")


class ArticleCompanySponsorConnection(ArticleCompanyAbstractConnection):
    """
    Sponsors of an Article.
    Not necessarily exposed on an the Wagtail admin for all types of Article.
    """

    article = ParentalKey("Article", related_name="sponsors")


class WebinarEventSpeakerConnection(models.Model):
    webinar = ParentalKey("Webinar", related_name="speakers")
    speaker = models.ForeignKey(EventSpeaker, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("speaker")]

    graphql_fields = [GraphQLForeignKey("speaker", content_type="articles.EventSpeaker")]


class ArticleAuthorsOrderable(Orderable):
    article = ParentalKey("articles.Article", related_name="authors")
    author = models.ForeignKey(Author, related_name="articles", on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("author")]

    graphql_fields = [
        GraphQLForeignKey("author", content_type="articles.Author"),
        GraphQLForeignKey("article", content_type="articles.Article"),
    ]

    @property
    def author_display_name(self):
        """
        Circumvents https://github.com/wagtail/wagtail/issues/3910.
        :return: The display name of the author.
        """
        return self.author.display_name


class ArticleTopicConnection(Orderable):
    article = ParentalKey("Article", related_name="topics")
    topic = models.ForeignKey(ArticleTopic, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("topic")]

    graphql_fields = [GraphQLForeignKey("topic", content_type="articles.ArticleTopic")]

    @property
    def topic_name(self):
        """
        Circumvents https://github.com/wagtail/wagtail/issues/3910.
        :return: The name of the topic.
        """
        return self.topic.name


class ArticleSourceConnection(models.Model):
    article = ParentalKey("Article", related_name="sources")
    source = models.ForeignKey(ArticleSource, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("source")]

    graphql_fields = [GraphQLForeignKey("source", content_type="articles.ArticleSource")]

    @property
    def source_name(self):
        """
        Circumvents https://github.com/wagtail/wagtail/issues/3910.
        :return: The name of the source.
        """
        return self.source.name


class ArticleAreaConnection(models.Model):
    article = ParentalKey("Article", related_name="areas")
    area = models.ForeignKey(ArticleArea, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("area")]

    graphql_fields = [GraphQLForeignKey("area", content_type="articles.ArticleArea")]

    @property
    def area_name(self):
        """
        Circumvents https://github.com/wagtail/wagtail/issues/3910.
        :return: The name of the area.
        """
        return self.area.name


class ArticleVerticalConnection(models.Model):
    article = ParentalKey("Article", related_name="verticals")
    vertical = models.ForeignKey(ArticleVertical, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("vertical")]

    graphql_fields = [
        GraphQLForeignKey("vertical", content_type="articles.ArticleVertical")
    ]

    @property
    def vertical_name(self):
        """
        Circumvents https://github.com/wagtail/wagtail/issues/3910.
        :return: The name of the vertical.
        """
        return self.vertical.name


class ArticleSummitsConnection(Orderable):
    article = ParentalKey("Article", related_name="summits")
    summit = models.ForeignKey(Summits, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("summit")]

    graphql_fields = [GraphQLForeignKey("summit", content_type="articles.Summits")]

    @property
    def summit_name(self):
        return self.summit.name

    @property
    def summit_logo(self):
        return self.summit.get_logo_url


class ArticleCategoryConnection(models.Model):
    article = ParentalKey("Article", related_name="categories")
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("category")]

    graphql_fields = [
        GraphQLForeignKey("category", content_type="articles.ArticleCategory")
    ]


# ******************************
# **        Containers        **
# ******************************


@register_singular_query_field("container")
class Container(Page):
    gather_content_folder_id = models.UUIDField(null=True, blank=True)

    subheader = models.CharField(
        max_length=255,
        help_text="Subheader to appear on the page of the container.",
        blank=True,
        default="",
    )

    content_panels = Page.content_panels + [
        FieldPanel("subheader"),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("gather_content_folder_id"),
    ]

    graphql_fields = [
        GraphQLString("subheader"),
    ]

    @classmethod
    def get_indexed_objects(cls):
        """Hide model from search results"""
        return cls.objects.none()


class ArticleContainer(Container):
    subpage_types = [
        "articles.Article",
    ]

    @property
    def count_article(self):
        return self.get_children().prefetch_related('content_type').all().count()

    graphql_fields = Container.graphql_fields + [
        GraphQLString("count_article"),
    ]


class WebinarContainer(Container):
    subpage_types = [
        "articles.Webinar",
    ]


class ResearchReportContainer(Container):
    subpage_types = [
        "articles.ResearchReport",
    ]


class EBookContainer(Container):
    subpage_types = [
        "articles.EBook",
    ]


class SurveyContainer(Container):
    subpage_types = [
        "articles.Survey",
    ]


class CaseStudyContainer(Container):
    subpage_types = [
        "articles.CaseStudy",
    ]


class ProofOfConceptContainer(Container):
    subpage_types = [
        "articles.ProofOfConcept",
    ]


class PodcastContainer(Container):
    subpage_types = [
        "articles.Podcast",
    ]


class VideoContainer(Container):
    subpage_types = [
        "articles.Video",
    ]

    @property
    def count_video(self):
        return self.get_children().prefetch_related('content_type').all().count()

    graphql_fields = Container.graphql_fields + [
        GraphQLString("count_video"),
    ]


class VideoDTWContainer(Container):
    subpage_types = [
        "articles.VideoDTW",
    ]

    @property
    def count_video_dtw(self):
        return self.get_children().prefetch_related('content_type').all().count()

    graphql_fields = Container.graphql_fields + [
        GraphQLString("count_video_dtw"),
    ]


class WhitePaperContainer(Container):
    subpage_types = [
        "articles.WhitePaper",
    ]


@register_singular_query_field("dtw_channel")
class DTWChannel(Page):
    subpage_types = [
        ArticleContainer,
        VideoDTWContainer,
        VideoContainer,
    ]
    subheader = models.CharField(
        max_length=255,
        help_text="Subheader to appear on the page of the container.",
        blank=True,
        default="",
    )

    content_panels = Page.content_panels + [
        FieldPanel("subheader"),
    ]
    graphql_fields = [
        GraphQLString("subheader"),
    ]


# ******************************
# **          Pages           **
# ******************************


class MarketoMixin(models.Model):
    class Meta:
        abstract = True

    marketo_formid = models.IntegerField(
        "Marketo form ID",
        blank=True,
        null=True,  # TODO: These should not be blank and null, but need to be for the import
        help_text="An ID for the formId field sent to Marketo when a user downloads or signs up for a webinar.",
    )
    marketo_programid = models.IntegerField(
        "Marketo program ID",
        blank=True,
        null=True,
        help_text="An ID for the programId field sent to Marketo when a user uses a form to download or signs up for a webinar.",
    )
    marketo_panels = [
        FieldPanel("marketo_formid"),
        FieldPanel("marketo_programid"),
    ]
    graphql_fields = [
        GraphQLInt("marketo_formid"),
        GraphQLInt("marketo_programid"),
    ]


@register_singular_query_field("article")
@register_plural_query_field(
    "articles",
    query_params=dict(
        topics__topic__id=graphene.Int(),
        topics__topic__slug__in=graphene.List(graphene.String),
        content_type__model__in=graphene.List(graphene.String),
        title__icontains=graphene.String(),
    ),
    keep_default_query_params=True,
)
class Article(Page):
    parent_page_types = ["articles.ArticleContainer"]
    subpage_types: List[str] = []

    thumbnail = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.PROTECT, null=True, blank=True
    )
    excerpt = models.TextField(blank=True)
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="full title")),
            ("paragraph", RichTextBlock()),
            ("image", ImageBlock()),
            ("embed", EmbedBlock(max_width=800, max_height=400)),
            ("quote", QuoteBlock()),
            ("floating_image", FloatingImageBlock()),
            ("related_content", RelatedContentBlock()),

        ]
    )
    wp_id = models.IntegerField(blank=True, null=True, unique=True)
    wp_url = models.CharField(max_length=500, blank=True, null=True)
    # HACK: Temporary fix -@flyte at 10/04/2022, 18:31:09
    # A store for all of the authors listed in the <category domain="author"> elements
    # which we don't necessarily have information for. Putting it all in here for the
    # moment so that we don't lose the data and can add their user data later on.
    # Maybe write a management command that runs through all of these and matches them up
    # to Author snippets once they've been added manually. Uses newline separators.
    wp_authors = models.TextField(blank=True)
    indicator_of_time = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='if the field is empty then calculation is done automatically'
    )

    content_panels = Page.content_panels + [
        FieldPanel("first_published_at"),
        ImageChooserPanel("thumbnail"),
        FieldPanel("indicator_of_time"),
        FieldPanel("excerpt"),
        StreamFieldPanel("body"),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("wp_id"),
        FieldPanel("wp_url"),
    ]

    tags_panels = [
        InlinePanel("authors", label="Authors"),
        InlinePanel("topics", label="Topics"),
        InlinePanel("sources", label="Sources"),
        InlinePanel("companies", label="Companies"),
        InlinePanel("sponsors", label="Sponsors"),
        InlinePanel("areas", label="Areas"),
        InlinePanel("verticals", label="Verticals"),
        InlinePanel("summits", label=mark_safe("Summits <b>for use with DTW source tags ONLY</b>"), max_num=1),
    ]

    @classmethod
    @property
    def edit_handler(cls):
        """
        Set up as a property so that it'll use subclass panels if they're set.
        """
        return TabbedInterface(
            [
                ObjectList(cls.content_panels, heading="Content"),
                ObjectList(cls.tags_panels, heading="Tags"),
                ObjectList(cls.promote_panels, heading="Promote"),
                ObjectList(cls.settings_panels, heading="Settings"),
            ]
        )

    @property
    def content_type_name(self):
        return self.specific_class._meta.verbose_name.title()

    def content_type_icon(self, info: ResolveInfo) -> Optional[VuetifyIcon]:
        if self.specific_class is None:
            return None
        attribute = f"{self.specific_class._meta.model_name}_icon"
        settings = ArticleTypesSettings.for_request(info.context)
        return getattr(settings, attribute)

    @property
    def feed_image(self):
        """Define the image for the Atom feed."""
        return self.thumbnail

    graphql_fields = [
        GraphQLString("indicator_of_time"),
        GraphQLImage("thumbnail"),
        GraphQLString("excerpt"),
        GraphQLStreamfield("body"),
        GraphQLString("wp_url"),
        GraphQLInt("wp_id"),
        GraphQLString("content_type_name"),
        GraphQLForeignKey("content_type_icon", "articles.VuetifyIcon"),
        GraphQLCollection(
            GraphQLForeignKey, "authors", "articles.ArticleAuthorsOrderable"
        ),
        GraphQLCollection(GraphQLForeignKey, "topics", "articles.ArticleTopicConnection"),
        GraphQLCollection(
            GraphQLForeignKey, "sources", "articles.ArticleSourceConnection"
        ),
        GraphQLCollection(
            GraphQLForeignKey, "companies", "articles.ArticleCompanyConnection"
        ),
        GraphQLCollection(
            GraphQLForeignKey, "sponsors", "articles.ArticleCompanySponsorConnection"
        ),
        GraphQLCollection(GraphQLForeignKey, "areas", "articles.ArticleAreaConnection"),
        GraphQLCollection(
            GraphQLForeignKey, "verticals", "articles.ArticleVerticalConnection"
        ),
        GraphQLCollection(
            GraphQLForeignKey, "summits", "articles.ArticleSummitsConnection"
        ),
    ]

    def thumbnail_url(self):
        """For indexing."""
        return self.thumbnail.file.url if self.thumbnail else None

    search_fields = Page.search_fields + [
        FilterField("thumbnail_url"),
        FilterField("full_url"),
        SearchField("excerpt"),
        SearchField("body"),
        FilterField("content_type_name"),
        RelatedFields("authors", [SearchField("author_display_name")]),
        RelatedFields("topics", [SearchField("topic_name")]),
        RelatedFields("sponsors", [SearchField("company_name")]),
        RelatedFields("companies", [SearchField("company_name")]),
        RelatedFields("sources", [SearchField("source_name")]),
        RelatedFields("areas", [SearchField("area_name")]),
        RelatedFields("verticals", [SearchField("vertical_name")])
    ]


class Webinar(MarketoMixin, Article):
    parent_page_types = ["articles.WebinarContainer"]

    start = models.DateTimeField(default=datetime.now)
    end = models.DateTimeField(default=datetime.now)

    view_url = models.URLField(blank=True, null=True, max_length=511)
    register_url = models.URLField(blank=True, null=True, max_length=511)
    location = models.CharField(max_length=127, blank=True)
    region = models.CharField(max_length=127, blank=True)

    content_panels = Article.content_panels + [
        FieldPanel("start", widget=AdminTimezoneDateTimeInput),
        FieldPanel("end", widget=AdminTimezoneDateTimeInput),
        FieldPanel("view_url"),
        FieldPanel("location"),
        FieldPanel("region"),
    ]

    tags_panels = [
        InlinePanel("speakers", label="Speakers"),
    ] + Article.tags_panels

    settings_panels = (
        MarketoMixin.marketo_panels
        + Page.settings_panels
        + [
            FieldPanel("wp_id"),
            FieldPanel("wp_url"),
        ]
    )

    graphql_fields = (
        Article.graphql_fields
        + [
            GraphQLString("start"),
            GraphQLString("end"),
            GraphQLString("view_url"),
            GraphQLString("location"),
            GraphQLString("region"),
            GraphQLCollection(
                GraphQLForeignKey, "speakers", "articles.WebinarEventSpeakerConnection"
            ),
        ]
        + MarketoMixin.graphql_fields
    )

    class Meta:
        ordering = ('-start',)


class ResearchReport(Article):
    parent_page_types = ["articles.ResearchReportContainer"]

    report_file = models.FileField(
        null=True,
        blank=True,
        upload_to="reports",
    )
    view_online_url = models.URLField(null=True, blank=True)

    content_panels = Article.content_panels + [
        FieldPanel("report_file"),
        FieldPanel("view_online_url"),
    ]

    settings_panels = (
        Page.settings_panels
        + [
            FieldPanel("wp_id"),
            FieldPanel("wp_url"),
        ]
    )

    graphql_fields = Article.graphql_fields

    @cached_property
    def download_url(self):
        return self.report_file.url


class EBook(Article):
    parent_page_types = ["articles.EBookContainer"]

    ebook_file = models.FileField(
        null=True,
        blank=True,
        upload_to="ebooks",
    )

    content_panels = Article.content_panels + [
        FieldPanel("ebook_file"),
    ]

    settings_panels =Page.settings_panels

    graphql_fields = Article.graphql_fields

    @cached_property
    def download_url(self):
        return self.ebook_file.url


class Survey(Article):
    parent_page_types = ["articles.SurveyContainer"]


class CaseStudy(MarketoMixin, Article):
    parent_page_types = ["articles.CaseStudyContainer"]

    casestudy_file = models.FileField(
        null=True,
        blank=True,
        upload_to="casestudies",
    )

    @cached_property
    def download_url(self):
        return self.casestudy_file.url

    content_panels = Article.content_panels + [
        FieldPanel("casestudy_file"),
    ]

    settings_panels = Page.settings_panels

    graphql_fields = Article.graphql_fields

    class Meta:
        verbose_name_plural = "Case Studies"


class ProofOfConcept(Article):
    parent_page_types = ["articles.ProofOfConceptContainer"]


class Podcast(Article):
    parent_page_types = ["articles.PodcastContainer"]


class Video(Article):
    parent_page_types = ["articles.VideoContainer"]

    transcription = RichTextField(blank=True)

    content_panels = Article.content_panels + [
        FieldPanel("transcription"),
    ]

    graphql_fields = Article.graphql_fields + [
        GraphQLString("transcription"),
    ]


class VideoDTW(Article, WagOrderable):
    parent_page_types = ["articles.VideoDTWContainer"]
    transcription = RichTextField(blank=True)
    related = models.BooleanField(default=False)
    video_dtw_name = models.FileField(
        null=True,
        blank=True,
        upload_to="videodtw",
    )

    @cached_property
    def download_url(self):
        if self.video_dtw_name:
            return self.video_dtw_name.url
        else:
            return 'None'

    @cached_property
    def get_sort_order(self):
        return self.sort_order

    def get_summit(self):
        return self.summits.get().summit_logo()

    def is_video_file(self):
        if self.video_dtw_name:
            return "Yes"
        else:
            return "No"

    is_video_file.short_description = 'videos'

    content_panels = Article.content_panels + [
        FieldPanel("transcription"),
        FieldPanel("related"),
        FieldPanel("video_dtw_name"),
    ]

    graphql_fields = Article.graphql_fields + [
        GraphQLString("indicator_of_time"),
        GraphQLString("transcription"),
        GraphQLString("related"),
        GraphQLString("video_dtw_name"),
        GraphQLString("download_url"),
        GraphQLString("get_sort_order"),
    ]


class WhitePaper(Article):
    parent_page_types = ["articles.WhitePaperContainer"]

    whitepaper_file = models.FileField(
        null=True,
        blank=True,
        upload_to="whitepapers",
    )

    content_panels = Article.content_panels + [
        FieldPanel("whitepaper_file"),
    ]

    settings_panels = Page.settings_panels

    graphql_fields = Article.graphql_fields

    @cached_property
    def download_url(self):
        return self.whitepaper_file.url


class TopicsPageTopics(Orderable):
    """Set 4+ topics to feature in the hero of the topics page"""

    page = ParentalKey("articles.TopicsPage", related_name="topics")
    topic = models.ForeignKey(
        "articles.ArticleTopic",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [SnippetChooserPanel("topic")]

    graphql_fields = [GraphQLForeignKey("topic", content_type="articles.ArticleTopic")]


class TopicsPage(Page):
    max_count = 1
    subtitle = models.CharField(max_length=127, default="Browse Inform topics from A - Z")

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("subtitle"),
        ]
        + [
            MultiFieldPanel(
                [InlinePanel("topics", min_num=4)],
                heading="Topics",
            ),
        ]
    )

    graphql_fields = [
        GraphQLString("subtitle"),
        GraphQLCollection(GraphQLForeignKey, "topics", "articles.TopicsPageTopics"),
    ]


class ArticleBodyBackup(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="body_backups"
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    body = models.JSONField()

    @classmethod
    def backup(cls, article: Article) -> ArticleBodyBackup:
        return ArticleBodyBackup.objects.create(
            article=article, body=list(article.body.raw_data)
        )

    def restore(self):
        article: Article = self.article
        self.backup(article)
        article.body = json.dumps(self.body)
        article.save(update_fields=["body"])


@register_snippet
class GenerateTopics(ClusterableModel):
    name = models.CharField(max_length=500, blank=True, null=True)
    parent_top = models.ForeignKey(ArticleTopic, on_delete=models.CASCADE, related_name="+", null=True)

    panels = [
        FieldPanel('name'),
        SnippetChooserPanel("parent_top", heading='Parent topic',),
        InlinePanel("topics", label="List of Topics"),
    ]

    def get_generate(self):
        return mark_safe(f"<a href='generate/{self.pk}' class='button button-small button-secondary' type='button'>Generate</a>")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Generate Topic'


class GenerateTopicsConnection(models.Model):
    parent_topic = ParentalKey("GenerateTopics", related_name='topics')
    topic = models.ForeignKey(ArticleTopic, on_delete=models.CASCADE)
    panels = [SnippetChooserPanel("topic")]


def get_generate(instance_pk):

    modelname = ArticleTopicConnection

    parent_topic = get_object_or_404(GenerateTopics, pk=instance_pk)
    parent_topic_id = parent_topic.parent_top_id
    list_of_topics = list(GenerateTopicsConnection.objects.filter(parent_topic_id=instance_pk).values_list('topic_id', flat=True))

    list_article_topics_with_parent_topic = list(ArticleTopicConnection.objects.filter(topic_id=parent_topic_id).values_list('article_id', flat=True))
    list_article_topics_without_parent_topic = list(ArticleTopicConnection.objects.exclude(article_id__in=list_article_topics_with_parent_topic).values_list('article_id', 'topic_id',))

    count_added_topics = 0
    d = dict()
    for key, value in list_article_topics_without_parent_topic:
        d[key] = d.get(key, []) + [value]
    for key, value in d.items():
        for x in list_of_topics:
            if x in value:
                count_added_topics += 1
                modelname.objects.create(article_id=key, topic_id=parent_topic_id, sort_order=0)
                break
    return count_added_topics