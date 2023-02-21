from django.db import models
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.core import hooks
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail_feeds.models import RSSFeedsSettings


# noinspection SpellCheckingInspection
@register_setting
class ArticleTypesSettings(BaseSetting):
    """
    Settings for each article type.
    For now, it stores icons and colours associated with each type.
    """

    article_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+", null=True
    )
    webinar_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+", null=True
    )
    researchreport_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+",
        verbose_name="Research report icon", null=True
    )
    ebook_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+",
        verbose_name="eBook icon", null=True
    )
    survey_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+", null=True
    )
    casestudy_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+",
        verbose_name="Case study icon", null=True
    )
    proofofconcept_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+",
        verbose_name="Proof of concept icon", null=True
    )
    podcast_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+", null=True
    )
    video_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+", null=True
    )
    whitepaper_icon = models.ForeignKey(
        "articles.VuetifyIcon", on_delete=models.PROTECT, related_name="+", null=True
    )

    panels = [
        SnippetChooserPanel("article_icon"),
        SnippetChooserPanel("webinar_icon"),
        SnippetChooserPanel("researchreport_icon"),
        SnippetChooserPanel("ebook_icon"),
        SnippetChooserPanel("survey_icon"),
        SnippetChooserPanel("casestudy_icon"),
        SnippetChooserPanel("proofofconcept_icon"),
        SnippetChooserPanel("podcast_icon"),
        SnippetChooserPanel("video_icon"),
        SnippetChooserPanel("whitepaper_icon"),
    ]

    class Meta:
        verbose_name = "Article types"
        verbose_name_plural = "Article types"


@register_setting(icon="mail")
class ArticlesRSSFeedsSettings(RSSFeedsSettings):
    """Custom settings for the RSS feed."""

    feed_size = models.PositiveIntegerField(
        verbose_name="Feed size",
        help_text="How many articles should there be in the feed? "
        "Larger the number, longer the time to generate the feed.",
        default=500,
    )

    last_changed_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        verbose_name = "RSS feed"
        verbose_name_plural = "RSS feeds"


@hooks.register("construct_settings_menu")
def hide_rssfeedssettings(_request, menu_items):
    """
    Hides the original settings for the RSS feed, since
    we use our extended version instead.
    """
    menu_items[:] = [item for item in menu_items if "wagtail_feeds" not in item.url]
