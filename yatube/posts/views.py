from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from posts.forms import PostForm

from .models import Group, Post

User = get_user_model()


def index(request):
    """View - функция для главной страницы проекта."""

    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View - функция для страницы с постами, отфильтрованными по группам."""

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,

    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """View - функция для страницы с постами пользователя,
       вошедшего на сайт.
    """

    author = get_object_or_404(User, username=username)
    count = author.posts.all().count()
    paginator = Paginator(author.posts.all(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'author': author,
               'count': count,
               'page_obj': page_obj,

               }
    return render(request, 'posts/profile.html', context)


def post_view(request, post_id):
    """View - функция для страницы определенного поста."""

    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.filter(author=post.author).count()

    context = {'post': post,
               'count': count,
               }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """View - функция для создания поста."""

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
        return render(request, 'posts/create_post.html', {"form": form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {"form": form, })


@login_required
def post_edit(request, post_id):
    """View - функция для редактирования проекта."""

    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', pk=post_id)
    else:
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {"form": form, 'post': post, "is_edit": is_edit, })
