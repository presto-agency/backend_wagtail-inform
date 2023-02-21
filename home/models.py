import graphene
from django.db import models
from grapple.helpers import register_plural_query_field, register_singular_query_field
from grapple.models import (
    GraphQLBoolean,
    GraphQLCollection,
    GraphQLForeignKey,
    GraphQLImage,
    GraphQLString,
)
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet


class FrontPageHeroes(Orderable):
    """Set 3 child pages of home to show at the top of the page"""

    page = ParentalKey("home.FrontPage", related_name="heroes")
    hero = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("hero")]

    graphql_fields = [GraphQLForeignKey("hero", content_type="articles.Article")]

    class Meta(Orderable.Meta):
        unique_together = ["page", "hero"]


class FrontPageFeatured(Orderable):
    """Set up to 6 articles to show in the featured panel the top of the page"""

    page = ParentalKey("home.FrontPage", related_name="featured")
    feature = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("feature")]

    graphql_fields = [GraphQLForeignKey("feature", content_type="articles.Article")]

    class Meta(Orderable.Meta):
        unique_together = ["page", "feature"]


class FrontPageReports(Orderable):
    """Set 4 report articles to show in the report highlight panel
    in the body of the homepage"""

    page = ParentalKey("home.FrontPage", related_name="reports")
    report = models.ForeignKey(
        "articles.ResearchReport",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [PageChooserPanel("report")]

    graphql_fields = [GraphQLForeignKey("report", content_type="articles.ResearchReport")]

    class Meta(Orderable.Meta):
        unique_together = ["page", "report"]


class FrontPagePopularRead(Orderable):
    """Set 4 or 5 articles for the Read tab on the popular panel"""

    page = ParentalKey("home.FrontPage", related_name="popular_read")
    read = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel("read", page_type=["articles.Article"]),
    ]

    graphql_fields = [
        GraphQLForeignKey("read", content_type="articles.Article"),
    ]

    class Meta(Orderable.Meta):
        unique_together = ["page", "read"]


class FrontPagePopularListen(Orderable):
    """Set 4 or 5 articles for the Listen tab on the popular panel"""

    page = ParentalKey("home.FrontPage", related_name="popular_listen")
    listen = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "listen",
            page_type=[
                "articles.Podcast",
            ],
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("listen", content_type="articles.Article"),
    ]

    class Meta(Orderable.Meta):
        unique_together = ["page", "listen"]


class FrontPagePopularWatch(Orderable):
    """Set 4 or 5 articles for the Watch tab on the popular panel"""

    page = ParentalKey("home.FrontPage", related_name="popular_watch")
    watch = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "watch",
            page_type=[
                "articles.Video",
                "articles.Webinar",
            ],
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("watch", content_type="articles.Article"),
    ]

    class Meta(Orderable.Meta):
        unique_together = ["page", "watch"]


class FrontPageTopics(Orderable):
    """Set 4+ topics to feature in the homepage carousel"""

    page = ParentalKey("home.FrontPage", related_name="topics")
    topic = models.ForeignKey(
        "articles.ArticleTopic",
        on_delete=models.CASCADE,
        related_name="+",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.PROTECT,
        help_text="The image to show in the carousel",
    )

    panels = [SnippetChooserPanel("topic"), ImageChooserPanel("image")]

    graphql_fields = [
        GraphQLForeignKey("topic", content_type="articles.ArticleTopic"),
        GraphQLImage("image"),
    ]

    class Meta(Orderable.Meta):
        unique_together = ["page", "topic"]


class FrontPageAuthors(Orderable):
    """Set 4+ authors to feature in the our community panel"""

    page = ParentalKey("home.FrontPage", related_name="authors")
    author = models.ForeignKey(
        "articles.Author",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [SnippetChooserPanel("author")]

    graphql_fields = [GraphQLForeignKey("author", content_type="articles.Author")]

    class Meta(Orderable.Meta):
        unique_together = ["page", "author"]


class FrontPageSevenSmallLeft(Orderable):

    page = ParentalKey("home.FrontPage", related_name="seven_small_left")
    seven_small_left_article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "seven_small_left_article",
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("seven_small_left_article", content_type="articles.Article"),
    ]


class FrontPageSevenTop(Orderable):

    page = ParentalKey("home.FrontPage", related_name="seven_top")
    seven_top_article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "seven_top_article",
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("seven_top_article", content_type="articles.Article"),
    ]


class FrontPageSevenMediumLeft(Orderable):

    page = ParentalKey("home.FrontPage", related_name="seven_medium_left")
    seven_medium_left_article = models.ForeignKey(
        "articles.Webinar",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "seven_medium_left_article",
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("seven_medium_left_article", content_type="articles.Webinar"),
    ]


class FrontPageSevenMediumMiddle(Orderable):

    page = ParentalKey("home.FrontPage", related_name="seven_medium_middle")
    seven_medium_middle_article = models.ForeignKey(
        "articles.CaseStudy",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "seven_medium_middle_article",
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("seven_medium_middle_article", content_type="articles.CaseStudy"),
    ]


class FrontPageSevenMediumRight(Orderable):

    page = ParentalKey("home.FrontPage", related_name="seven_medium_right")
    seven_medium_right_article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "seven_medium_right_article",
            page_type=[
                "articles.Video",
                "articles.VideoDTW",
            ],
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("seven_medium_right_article", content_type="articles.Article"),
    ]

    class Meta(Orderable.Meta):
        unique_together = ["page", "seven_medium_right_article"]


class FrontPageSevenBottomHero(Orderable):

    page = ParentalKey("home.FrontPage", related_name="seven_bottom_hero")
    seven_bottom_hero_article = models.ForeignKey(
        "articles.ProofOfConcept",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        PageChooserPanel(
            "seven_bottom_hero_article",
        ),
    ]

    graphql_fields = [
        GraphQLForeignKey("seven_bottom_hero_article", content_type="articles.ProofOfConcept"),
    ]


@register_singular_query_field("frontpage")
class FrontPage(Page):
    max_count = 1

    seven_panels = [
        MultiFieldPanel(
            [InlinePanel("seven_small_left", max_num=1)],
            heading="Box 1 Small left  - article content",
        ),
        MultiFieldPanel(
            [InlinePanel("seven_top", max_num=1)],
            heading="Box 2 Top 7 hero  - article content",
        ),
        MultiFieldPanel(
            [InlinePanel("seven_medium_left", max_num=1)],
            heading="Box 3 Medium left - Webinars",
        ),
        MultiFieldPanel(
            [InlinePanel("seven_medium_middle", max_num=10)],
            heading="Box 4  Medium middle - Case studies",
        ),
        MultiFieldPanel(
            [InlinePanel("seven_medium_right", max_num=10)],
            heading="Box 5 Medium right - Videos and Videos DTW",
        ),
        MultiFieldPanel(
            [InlinePanel("seven_bottom_hero", max_num=10)],
            heading="Box 6 Bottom hero - Proofs of concept (Catalysts)",
        ),
    ]
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("heroes", max_num=3, min_num=3)],
            heading="Heroes",
        ),
    ]
    featured_panels = [
        MultiFieldPanel(
            [InlinePanel("featured", max_num=6, min_num=4)],
            heading="Featured",
            help_text="These 4-6 articles show in the Featured list panel in the hero section on the homepage",
        ),
    ]
    report_panels = [
        MultiFieldPanel(
            [InlinePanel("reports", max_num=4, min_num=4)],
            heading="Reports",
            help_text="You can only select Research Reports for these 4 articles to go in the Reports highlight panel below the heroes",
        ),
    ]
    topic_panels = [
        MultiFieldPanel(
            [InlinePanel("topics", min_num=4)],
            heading="Topics",
            help_text="These 4+ topics will appear in the carousel on the homepage",
        ),
    ]
    popular_panels = [
        MultiFieldPanel(
            [InlinePanel("popular_read", max_num=5, min_num=4)],
            heading="Popular Read",
            classname="collapsible",
            help_text="These 4-5 articles go in the Read tab of the Most Popular panel on the homepage",
        ),
        MultiFieldPanel(
            [InlinePanel("popular_listen", max_num=5, min_num=4)],
            heading="Popular Listen",
            classname="collapsible",
            help_text="These 4-5 articles go in the Listen tab of the Most Popular panel on the homepage",
        ),
        MultiFieldPanel(
            [InlinePanel("popular_watch", max_num=5, min_num=4)],
            heading="Popular Watch",
            classname="collapsible",
            help_text="These 4-5 articles go in the Watch tab of the Most Popular panel on the homepage",
        ),
    ]
    author_panels = [
        MultiFieldPanel(
            [InlinePanel("authors", max_num=5, min_num=4)],
            heading="Authors",
            help_text="These 4-5 authors show in the From Our Community panel on the homepage",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(seven_panels, heading="The 7"),
            ObjectList(content_panels, heading="Content"),
            ObjectList(featured_panels, heading="Featured"),
            ObjectList(popular_panels, heading="Popular"),
            ObjectList(report_panels, heading="Reports"),
            ObjectList(topic_panels, heading="Topics"),
            ObjectList(author_panels, heading="Authors"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
        ]
    )

    graphql_fields = [
        GraphQLCollection(GraphQLForeignKey, "heroes", "home.FrontPageHeroes"),
        GraphQLCollection(GraphQLForeignKey, "featured", "home.FrontPageFeatured"),
        GraphQLCollection(GraphQLForeignKey, "reports", "home.FrontPageReports"),
        GraphQLCollection(GraphQLForeignKey, "topics", "home.FrontPageTopics"),
        GraphQLCollection(GraphQLForeignKey, "authors", "home.FrontPageAuthors"),
        GraphQLCollection(GraphQLForeignKey, "popular_read", "home.FrontPagePopularRead"),
        GraphQLCollection(GraphQLForeignKey, "popular_listen", "home.FrontPagePopularListen"),
        GraphQLCollection(GraphQLForeignKey, "popular_watch", "home.FrontPagePopularWatch"),
        GraphQLCollection(GraphQLForeignKey, "seven_small_left", "home.FrontPageSevenSmallLeft"),
        GraphQLCollection(GraphQLForeignKey, "seven_top", "home.FrontPageSevenTop"),
        GraphQLCollection(GraphQLForeignKey, "seven_medium_left", "home.FrontPageSevenMediumLeft"),
        GraphQLCollection(GraphQLForeignKey, "seven_medium_middle", "home.FrontPageSevenMediumMiddle"),
        GraphQLCollection(GraphQLForeignKey, "seven_medium_right", "home.FrontPageSevenMediumRight"),
        GraphQLCollection(GraphQLForeignKey, "seven_bottom_hero", "home.FrontPageSevenBottomHero"),
    ]


@register_snippet
@register_singular_query_field("advert")
@register_plural_query_field("adverts", query_params=dict(format=graphene.String()))
class Advert(models.Model):
    FORMAT_CHOICES = (
        ("billboard", "IAB Billboard (970x250)"),
        ("rectangle", "IAB Medium Rectangle (300x250)"),
    )
    LIVE_CHOICES = (
        (False, "Draft"),
        (True, "Live"),
    )
    name = models.CharField(unique=True, blank=False, max_length=50)
    live = models.BooleanField(
        choices=LIVE_CHOICES,
        default=False,
        help_text="Should the advert be showing on the site?",
    )
    url = models.URLField(
        help_text="Where does clicking on the banner send the user? Usually the advertisers website for eg",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        help_text="Please ensure the image is the exact size of the dimensions for the selected format",
    )
    format = models.CharField(
        choices=FORMAT_CHOICES,
        max_length=20,
        default="billboard",
        help_text="The format dictates the position on the homepage, a 'billboard' is horizontal and the rectangle takes up the slot of an article 'card'",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("live"),
        FieldPanel("url"),
        FieldPanel("format"),
        ImageChooserPanel("image"),
    ]

    graphql_fields = [
        GraphQLString("name"),
        GraphQLBoolean("live"),
        GraphQLString("url"),
        GraphQLImage("image"),
        GraphQLString("format"),
    ]

    def __str__(self):
        return f"{self.name} ({self.format})"


class FooterPage(Page):
    about_tm_forum = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("about_tm_forum"),
    ]

    graphql_fields = [
        GraphQLString("about_tm_forum"),
    ]


class MarketoLog(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=127)
    view_class = models.CharField(max_length=127)
    request_data = models.BinaryField()
    request_json = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    response_code = models.IntegerField(null=True, blank=True)
    marketo_request_data = models.JSONField(null=True, blank=True)
    marketo_response_data = models.JSONField(null=True, blank=True)
    marketo_response_code = models.IntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.datetime.isoformat()} {self.endpoint} ({self.view_class}): {self.response_code}"
