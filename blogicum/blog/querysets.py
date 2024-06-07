from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.models import Post
from core.canstants import POST_COUNT


def limited_access_posts():
    query_set = (Post.objects.all().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    )
    return query_set


def displayed_posts(queryset=Post.objects.all()):
    filtred_queryset = (queryset.
                        annotate(comment_count=Count('post')).order_by("-pub_date"))

    return filtred_queryset


def get_paginate(post_list, request):
    paginator = Paginator(post_list, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
