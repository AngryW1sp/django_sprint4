from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog'


urlpatterns = [
    # Главная страница
    path('',
         views.PostListView.as_view(),
         name='index'),
    # Содержание поста
    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    # Посты в категории
    path('category/<slug:category_slug>/',
         views.category_post,
         name='category_posts'),
    # Создание поста
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    # Создание комментария
    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),

    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment,
         name='edit_comment'),

    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.comment_delete,
         name='delete_comment'),

    path('posts/<int:post_id>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),

    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),

    path('profile/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),

    path('profile/<username>/',
         views.profile,
         name='profile'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
