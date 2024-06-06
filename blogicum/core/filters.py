from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def get_filter():
    query_set = (Post.objects.all().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    )
    return query_set


def user_post_filter():
    query_set = (Post.objects.all().filter(
    ).annotate(comment_count=Count('post'))
        .order_by("-pub_date")
    )

    return query_set


def post_filter():
    query_set = (Post.objects.all().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(comment_count=Count('post'))
        .order_by("-pub_date")
    )
    return query_set
