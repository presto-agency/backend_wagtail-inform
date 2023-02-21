import datetime
import hashlib
from email.utils import format_datetime

from django.apps import apps
from django.conf import settings
from django.db.models import Max
from django.http import HttpResponse, HttpResponseNotAllowed
from wagtail_feeds import feeds
from wagtail_feeds.feeds import ExtendedFeed

from articles.settings import ArticlesRSSFeedsSettings


class ArticleFeed(ExtendedFeed):
    def items(self):
        """
        Restrict the feed size to the value set in the Wagtail settings.
        If not set, 500 articles is the default.
        """
        feed_size = (
            self.feed_settings.feed_size if self.feed_settings is not None else 500
        )
        return super().items()[:feed_size]

    def __call__(self, request, *args, **kwargs):
        """
        Update the RSS settings from the database,
        so we do not have to restart after each change.

        Set the cache headers as well.
        The last change of the settings and the articles functions as
        the Last-Modified header.
        It is hashed together with the secret key to get
        a cryptographically secure ETag.
        """
        self.feed_settings = ArticlesRSSFeedsSettings.for_request(request)
        if self.feed_settings is not None:
            self.title = self.feed_settings.feed_title
            self.link = self.feed_settings.feed_link
            self.description = self.feed_settings.feed_description
            self.author_email = self.feed_settings.feed_author_email
            self.author_link = self.feed_settings.feed_author_link
            self.item_description_field = self.feed_settings.feed_item_description_field
            self.item_content_field = self.feed_settings.feed_item_content_field
            feeds.feed_model_name = self.feed_settings.feed_model_name
            feeds.feed_app_label = self.feed_settings.feed_app_label
            feeds.feed_model = apps.get_model(
                app_label=self.feed_settings.feed_app_label,
                model_name=self.feed_settings.feed_model_name,
            )
            feeds.use_feed_image = self.feed_settings.feed_image_in_content
            feeds.feed_item_date_field = self.feed_settings.feed_item_date_field
            feeds.is_date_field_datetime = (
                self.feed_settings.is_feed_item_date_field_datetime
            )

        if request.method == "GET":
            # Get the feed
            response = super().__call__(request, *args, **kwargs)
        elif request.method == "HEAD":
            # Return just the ETag
            response = HttpResponse()
        else:
            return HttpResponseNotAllowed(["HEAD", "GET"])

        # Calculate and set the ETag
        last_change = max(
            feeds.feed_model.objects.aggregate(Max("last_published_at"))[
                "last_published_at__max"
            ],
            self.feed_settings.last_changed_at,
        ).astimezone(datetime.timezone.utc)
        last_change_http = format_datetime(dt=last_change, usegmt=True)
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Last-Modified"] = last_change_http
        response.headers["ETag"] = hashlib.sha1(
            (settings.SECRET_KEY + last_change_http).encode("ascii")
        ).hexdigest()

        return response
