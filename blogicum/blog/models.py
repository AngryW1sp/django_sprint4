from django.contrib.auth import get_user_model
from django.db import models

from core.canstants import MAX_FIELD_LENGTH
from core.models import PublishingModel

User = get_user_model()


class Category(PublishingModel):
    title = models.CharField(max_length=MAX_FIELD_LENGTH,
                             verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=("Идентификатор страницы для URL; разрешены "
                   "символы латиницы, цифры, дефис и подчёркивание."),
    )

    class Meta:

        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(PublishingModel):
    name = models.CharField(max_length=MAX_FIELD_LENGTH,
                            verbose_name="Название места"
                            )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(PublishingModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author_posts",
        verbose_name="Автор публикации",
        null=True
    )
    title = models.CharField(max_length=MAX_FIELD_LENGTH,
                             verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text=("Если установить дату и время "
                   "в будущем — можно делать отложенные публикации."),
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="location_posts",
        verbose_name="Местоположение",

    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="category_posts",
        verbose_name="Категория",
    )
    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name="Автор поста")
    post = models.ForeignKey(
        Post,
        null=True,
        on_delete=models.CASCADE,
        related_name='post',
        verbose_name='Пост'

    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = "comments"
        ordering = ('created_at',)

    def __str__(self):
        return f'Комментарий от {self.author}'
