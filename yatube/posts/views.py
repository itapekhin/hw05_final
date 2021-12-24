from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from posts.models import Group, Post, User, Comments, Follow
from .forms import PostForm, CommentForm
from django.views.decorators.cache import cache_page


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.COL_ZAP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.COL_ZAP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    profile_posts = author.posts.all()
    profile_count = profile_posts.count()
    user = request.user
    following = user.is_authenticated and author.following.exists()
    paginator = Paginator(profile_posts, settings.COL_ZAP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile_count': profile_count,
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_count = author.posts.all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'post_count': post_count,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    error = ''
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        form = form.save(False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author.username)
    else:
        error = 'Данные не корректны'
    context = {
        'form': form,
        'error': error
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user)
    following_a = User.objects.filter(following__in=follow)
    post_list = Post.objects.filter(author__in=following_a)
    paginator = Paginator(post_list, settings.COL_ZAP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = User.objects.get(username=username)
    if request.user is not author:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)

@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = User.objects.get(username=username)
    if request.user is not author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
