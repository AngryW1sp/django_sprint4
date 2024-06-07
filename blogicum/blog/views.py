from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserForm
from .mixins import DispathMixin, PostMixin, ProfileReverseMixin
from .models import Category, Comment, Post, User
from .querysets import displayed_posts, get_paginate, limited_access_posts
from core.canstants import POST_COUNT


class PostCreateView(ProfileReverseMixin, PostMixin,
                     LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(DispathMixin, LoginRequiredMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(ProfileReverseMixin, DispathMixin,
                     LoginRequiredMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    post_object = None
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        self.post_object = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.post_object.author == self.request.user:
            return displayed_posts().filter(pk=self.kwargs['post_id'])
        return (displayed_posts(limited_access_posts()).
                filter(pk=self.kwargs['post_id']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.post.all().select_related(
            'author'
        )
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = displayed_posts(queryset=limited_access_posts())
    paginate_by = POST_COUNT


def category_post(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )

    post_list = (displayed_posts(limited_access_posts())
                 .filter(category=category))
    page_obj = get_paginate(post_list, request)
    return render(request, 'blog/category.html',
                  {'page_obj': page_obj, 'category': category_slug})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = (displayed_posts()
                 .filter(author_id=user.id))
    page_obj = get_paginate(post_list, request)
    return render(request, 'blog/profile.html',
                  {'profile': user, 'page_obj': page_obj})


class ProfileUpdateView(ProfileReverseMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    post_object = None

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post, pk=self.kwargs['post_id'],)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if instance.author == request.user:
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    context = {'comment': comment}
    if comment.author == request.user:
        if request.method == 'POST':
            comment.delete()
            return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
