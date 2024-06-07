from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import PostForm
from .models import Post


class ProfileReverseMixin:

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class DispathMixin(PostMixin):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
