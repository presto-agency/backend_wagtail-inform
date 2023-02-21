from home import models as home_models
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.core import hooks
from wagtail.documents.wagtail_hooks import DocumentsMenuItem
from wagtail.snippets.wagtail_hooks import SnippetsMenuItem

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf.urls import url

from wagtail.contrib.modeladmin.helpers import ButtonHelper
from django.contrib.admin.utils import quote
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q

from . import models
from .queries import CustomQuery

HIDDEN_MENU_ITEMS = (
    SnippetsMenuItem,
    DocumentsMenuItem,
)


@hooks.register("construct_main_menu")
def hide_snippets_menu_item(request, menu_items):
    def is_shown(item) -> bool:
        for menu_item_type in HIDDEN_MENU_ITEMS:
            if isinstance(item, menu_item_type):
                return False
        return True

    menu_items[:] = list(filter(is_shown, menu_items))


# ******************************
# **         Snippets         **
# ******************************


class SnippetAdminBase(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


class AdvertAdmin(SnippetAdminBase):
    model = home_models.Advert


class ArticleCategoryAdmin(SnippetAdminBase):
    model = models.ArticleCategory


class ArticleSourceAdmin(SnippetAdminBase):
    model = models.ArticleSource


class ArticleTopicAdmin(SnippetAdminBase):
    model = models.ArticleTopic


class AuthorAdmin(SnippetAdminBase):
    model = models.Author
    list_display = ["first_name", "last_name", "email", "get_avatar_url", "get_biography"]
    search_fields = ["display_name"]


class CompanyAdmin(SnippetAdminBase):
    model = models.Company


class EventSpeakerAdmin(SnippetAdminBase):
    model = models.EventSpeaker


class VuetifyIconAdmin(SnippetAdminBase):
    model = models.VuetifyIcon


class SummitsAdmin(SnippetAdminBase):
    model = models.Summits
    list_display = SnippetAdminBase.list_display + ["get_logo_url"]


@modeladmin_register
class SnippetGroup(ModelAdminGroup):
    menu_label = "Lists"
    items = (
        AdvertAdmin,
        ArticleCategoryAdmin,
        ArticleSourceAdmin,
        ArticleTopicAdmin,
        AuthorAdmin,
        CompanyAdmin,
        EventSpeakerAdmin,
        VuetifyIconAdmin,
        SummitsAdmin,
    )


# ******************************
# **         Articles         **
# ******************************

class ModelButtonHelper(ButtonHelper):

    def move_button(self, pk, classnames_add=[], classnames_exclude=[]):
        cn = self.finalise_classname(classnames_add, classnames_exclude)
        return {
            'url': f"/admin/pages/{quote(pk)}/move/",
            'label': _('Move'),
            'classname': cn,
            'title': _('Move this %(model_name)s') % {
                'model_name': self.verbose_name,
            },
        }

    def copy_button(self, pk, classnames_add=[], classnames_exclude=[]):
        cn = self.finalise_classname(classnames_add, classnames_exclude)
        return {
            'url': self.url_helper.get_action_url('copy', quote(pk)),
            'label': _('Copy'),
            'classname': cn,
            'title': _('Copy this %(model_name)s') % {
                'model_name': self.verbose_name,
            },
        }

    def get_buttons_for_obj(self, obj, exclude=[], classnames_add=[], classnames_exclude=[]):
        pk = quote(getattr(obj, self.opts.pk.attname))
        ph = self.permission_helper
        usr = self.request.user
        btns = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)

        if "copy" not in exclude and ph.user_can_create(usr) or ph.user_can_edit_obj(usr, obj):
            btns.append(self.copy_button(pk, classnames_add, classnames_exclude))

        if "move" not in exclude and ph.user_can_create(usr) or ph.user_can_edit_obj(usr, obj):
            btns.append(self.move_button(pk, classnames_add, classnames_exclude))

        return btns


class YearFilter(SimpleListFilter):

    title = 'Years'
    parameter_name = 'first_published_at__year'

    def lookups(self, request, model_admin):
        data = []
        all_years = model_admin.model.objects.filter(~Q(first_published_at__year=None)).values('first_published_at__year').annotate(cnt=Count('first_published_at__year')).order_by('-first_published_at__year')
        if all_years:
            for x in all_years:
                data.append((x['first_published_at__year'], f"{x['first_published_at__year']} ({x['cnt']})"))
        return data

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(first_published_at__year=self.value())


class ArticleAdminBase(ModelAdmin):
    list_filter = [YearFilter, "first_published_at", "topics__topic", "authors__author"]
    list_display = ["title", "first_published_at", "last_published_at", "authors", "live"]
    search_fields = ["title", "body"]

    def authors(self, obj: models.Article):
        return ", ".join(obj.authors.values_list("author__display_name", flat=True))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-first_published_at')

    button_helper_class = ModelButtonHelper


class ArticleAdmin(ArticleAdminBase):
    model = models.Article
    list_display = ArticleAdminBase.list_display + ["content_type_name"]
    list_filter = ["sources__source"] + ArticleAdminBase.list_filter


class ResearchReportAdmin(ArticleAdminBase):
    model = models.ResearchReport
    list_filter = ["sources__source"] + ArticleAdminBase.list_filter


class CaseStudyAdmin(ArticleAdminBase):
    model = models.CaseStudy
    list_filter = ["sources__source"] + ArticleAdminBase.list_filter


class WebinarAdmin(ArticleAdminBase):
    model = models.Webinar
    list_display = ["title", "first_published_at", "start", "end", "authors", "live"]
    list_filter = ["sources__source"] + ArticleAdminBase.list_filter


class EBookAdmin(ArticleAdminBase):
    model = models.EBook


class PodcastAdmin(ArticleAdminBase):
    model = models.Podcast


class ProofOfConceptAdmin(ArticleAdminBase):
    model = models.ProofOfConcept


class SurveyAdmin(ArticleAdminBase):
    model = models.Survey


class VideoAdmin(ArticleAdminBase):
    model = models.Video


class VideoDTWAdmin(ArticleAdminBase):
    model = models.VideoDTW
    list_display = ["title", "first_published_at", "is_video_file", "get_summit", "live"]


class WhitePaperAdmin(ArticleAdminBase):
    model = models.WhitePaper


@modeladmin_register
class ArticleGroup(ModelAdminGroup):
    menu_label = "Articles"
    items = [
        ArticleAdmin,
        CaseStudyAdmin,
        EBookAdmin,
        PodcastAdmin,
        ProofOfConceptAdmin,
        ResearchReportAdmin,
        SurveyAdmin,
        VideoAdmin,
        VideoDTWAdmin,
        WebinarAdmin,
        WhitePaperAdmin,
    ]


# ******************************
# **          Images          **
# ******************************

from taggit.models import Tag
from wagtail.images.models import Image
from django.db.models import F, Func

@modeladmin_register
class TagAdmin(ModelAdmin):
    model = Tag
    list_display = ["name", "slug"]
    search_fields = ["name", "slug"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(field_lower=Func(F('name'), function='LOWER')).order_by('field_lower')


class CountryAdmin(ModelAdmin):
    model = models.Country
    list_display = ["name"]
    search_fields = ["name"]


class LocationAdmin(ModelAdmin):
    model = models.Location
    list_display = ["name", "country"]
    search_fields = ["name", "country"]


class CompanyLogoImagesAdmin(ModelAdmin):
    model = Image
    menu_label = "Logos"
    list_display = ["file", "title"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(tags__slug="company-logo")


@modeladmin_register
class CompaniesGroup(ModelAdminGroup):
    menu_label = "Companies"
    items = (
        CompanyLogoImagesAdmin,
        CountryAdmin,
        LocationAdmin,
    )


@hooks.register("register_rich_text_features")
def add_blockquote_default(features):
    features.default_features.append("blockquote")


@modeladmin_register
class GenerateTopicsAdmin(ModelAdmin):
    model = models.GenerateTopics
    list_display = ["name", "parent_top", "get_generate"]
    instance_pk = None

    def admin_view(self, request, instance_pk):
        self.instance_pk = instance_pk
        count = models.get_generate(self.instance_pk)
        if count > 0:
            user_message = f"Added in {str(count)} Articles"
        else:
            user_message = f"Don`t added Topic"
        return HttpResponseRedirect('/admin/articles/generatetopics', messages.success(request, user_message))

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        add_generate_url = url(
            self.url_helper.get_action_url_pattern('generate'),
            self.admin_view,
            name=self.url_helper.get_action_url_name('generate')
        )
        return urls + (add_generate_url,)


@hooks.register("register_schema_query")
def add_my_custom_query(query_mixins):
    query_mixins.append(CustomQuery)