from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from .forms import CommentForm, PostForm, UserForm
from .models import Category, Post, User, Comment
from core.filters import post_filter, get_filter, user_post_filter
from core.canstants import POST_COUNT
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (CreateView,
                                  UpdateView,
                                  DeleteView,
                                  DetailView,
                                  ListView)


def get_pagination(post_list, request):
    paginator = Paginator(post_list, POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    post_object = None
    pk_url_kwargs = 'post_id'

    def get_queryset(self):
        self.post_object = get_object_or_404(Post, pk=self.kwargs['pk'])
        if self.post_object.author == self.request.user:
            return user_post_filter().filter(pk=self.kwargs['pk'])
        return get_filter().filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        context['comments'] = self.object.post.all().select_related(
            'author'
        )
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = post_filter()
    paginate_by = str(POST_COUNT)


def category_post(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )

    post_list = get_filter().filter(category=category)
    page_obj = get_pagination(post_list, request)
    return render(request, 'blog/category.html', {'page_obj': page_obj, 'category': category_slug})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user_post_filter().filter(author_id=user.id).order_by('-pub_date')
    page_obj = get_pagination(post_list, request)
    return render(request, 'blog/profile.html', {'profile': user, 'page_obj': page_obj})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    post_object = None

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(
            Post, pk=kwargs['post_id'],)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    context = {'comment': comment}
    if comment.author == request.user:
        if request.method == 'POST':
            comment.delete()
            return redirect('blog:post_detail', pk=post_id)
        return render(request, 'blog/comment.html', context)
