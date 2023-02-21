import graphene
from graphene_django import DjangoObjectType
from wagtail.core.models import Page
from django.db.models import Count
from .models import Article, ArticleTopic, Summits, Author, DTWChannel
from django.contrib.contenttypes.models import ContentType
import datetime


class RelatedArticlePageType(DjangoObjectType):
    class Meta:
        model = Article
        fields = '__all__'
    url = graphene.String()
    page_type = graphene.String()

    def resolve_page_type(self, info):
        return self.specific_class._meta.verbose_name.title()


class RelatedPageType(graphene.ObjectType):

    related_articles = graphene.List(RelatedArticlePageType)
    related_videos = graphene.List(RelatedArticlePageType)
    related_videosdtw = graphene.List(RelatedArticlePageType)


class DTWChannelType(DjangoObjectType):
    class Meta:
        model = DTWChannel
        fields = '__all__'


class DTWSummitType(DjangoObjectType):
    class Meta:
        model = Summits
        fields = '__all__'

    numchild = graphene.Int()


class DTWAuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = '__all__'

    numchild = graphene.Int()


class DTWArticleType(DjangoObjectType):
    class Meta:
        model = Article
        fields = '__all__'

    url = graphene.String()
    numchild = graphene.Int()
    content_type__model = graphene.String()


class DTWArticleTopicType(DjangoObjectType):
    class Meta:
        model = ArticleTopic
        fields = '__all__'

    numchild = graphene.Int()


class DTWContentTypesType(graphene.ObjectType):

    model = graphene.String()
    numchild = graphene.Int()


class DTWParentOfArticlesType(graphene.ObjectType):

    title = graphene.String()
    slug = graphene.String()
    content_type = graphene.String()
    numchild = graphene.Int()


class DTWAllPagesType(graphene.ObjectType):

    page = graphene.Field(DTWChannelType)
    parent_of_articles = graphene.List(DTWParentOfArticlesType)
    content_types = graphene.List(DTWContentTypesType)
    authors = graphene.List(DTWAuthorType)
    summits = graphene.List(DTWSummitType)
    articles = graphene.List(DTWArticleType)
    topics = graphene.List(DTWArticleTopicType)
    count_articles = graphene.Int()


class CustomQuery(graphene.ObjectType):
    related = graphene.Field(RelatedPageType, url_path=graphene.String(), order=graphene.String())

    def resolve_related(self, info, url_path=None, order='-first_published_at'):
        no_errors = True
        current_page = Page.objects.get(url_path__endswith=url_path)
        filter_dict = {}
        try:
            current_page_summit_connection = current_page.article.summits.get(article_id=current_page.id)
            current_page_summit_id = current_page_summit_connection.summit_id
            filter_dict['article__summits__summit__id'] = current_page_summit_id
        except:
            no_errors = False

        try:
            current_page_topics_connection = current_page.article.topics.filter(article_id=current_page.id).all()
            current_page_topics = [item.topic_id for item in current_page_topics_connection]
            filter_dict['article__topics__topic__id__in'] = current_page_topics
        except:
            no_errors = False

        if no_errors:

            parent_page = current_page.get_parent()
            siblings = Page.objects.sibling_of(parent_page)

            for item in siblings:
                content_type = ContentType.objects.prefetch_related('pages').get(pages__pk=item.pk)
                child = Page.objects.child_of(item).exclude(pk=current_page.pk).filter(**filter_dict).values_list('id',flat=True)
                all_articles = Article.objects.filter(pk__in=child).order_by(order)
                if content_type.model == "articlecontainer":
                    related_articles = all_articles
                elif content_type.model == "videocontainer":
                    related_videos = all_articles
                elif content_type.model == "videodtwcontainer":
                    related_videosdtw = all_articles
        else:
            related_articles = []
            related_videos = []
            related_videosdtw = []
        return {"related_articles": related_articles,
                "related_videos": related_videos,
                "related_videosdtw": related_videosdtw}

    #DX-1333
    dtw_allpages = graphene.Field(
        DTWAllPagesType,
        url_path=graphene.String(),
        limit=graphene.Int(),
        offset=graphene.Int(),
        search_title=graphene.String(),
        content_type_model=graphene.String(),
        topic_slug=graphene.String(),
        summit_name=graphene.String(),
        author_display_name=graphene.String(),
        date_start=graphene.String(),
        date_end=graphene.String(),
        order=graphene.String()
    )

    def resolve_dtw_allpages(root, info, url_path, limit=None, offset=None, search_title=None, content_type_model=None, topic_slug=None, summit_name=None, author_display_name=None, date_start=None, date_end=None, order="-first_published_at"):

        filter_dict = {}
        if search_title:
            filter_dict['title__icontains'] = search_title
        if content_type_model:
            filter_dict['content_type__model__in'] = content_type_model.split(',')
        if topic_slug:
            filter_dict['topics__topic__slug__in'] = topic_slug.split(',')
        if summit_name:
            filter_dict['summits__summit__name__in'] = summit_name.split(',')
        if author_display_name:
            filter_dict['authors__author__display_name__in'] = author_display_name.split(',')
        if date_start:
            filter_dict['first_published_at__gte'] = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        if date_end:
            filter_dict['first_published_at__lte'] = datetime.datetime.strptime(date_end, '%Y-%m-%d') + datetime.timedelta(days=1)

        page = DTWChannel.objects.get(url_path__endswith=url_path)
        parent_of_articles = page.get_children()

        children = []
        for item in parent_of_articles:
            children.append(item.get_children())

        all_articles_id = []
        for item in children:
            for obj in item:
                all_articles_id.append(obj.article.pk)

        content_types = ContentType.objects.prefetch_related('pages').filter(pages__pk__in=all_articles_id).annotate(numchild=Count('pk'))

        summits = Summits.objects.prefetch_related('articlesummitsconnection_set').filter(articlesummitsconnection__article_id__in=all_articles_id).annotate(numchild=Count('pk'))

        authors = Author.objects.prefetch_related('articles').filter(articles__article_id__in=all_articles_id).annotate(numchild=Count('pk'))

        topics = ArticleTopic.objects.prefetch_related('articletopicconnection_set').filter(articletopicconnection__article_id__in=all_articles_id).annotate(numchild=Count('pk'))

        count_articles = Article.objects.filter(pk__in=all_articles_id, **filter_dict).count()

        if limit:
            article_limit = limit
            article_offset = None
            if offset:
                article_offset = (offset * limit)
                article_limit = (offset * limit) + limit

            articles = Article.objects.filter(pk__in=all_articles_id, **filter_dict).order_by(order)[article_offset:article_limit]
        else:
            articles = Article.objects.filter(pk__in=all_articles_id, **filter_dict).order_by(order)

        return {"page": page,
                "parent_of_articles": parent_of_articles,
                "content_types": content_types,
                "authors": authors,
                "summits": summits,
                "topics": topics,
                "count_articles": count_articles,
                "articles": articles}