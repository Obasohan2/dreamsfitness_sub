from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from .models import BlogPost
from .forms import CommentForm, BlogPostForm


class PostList(ListView):
    """View to list blog posts"""
    model = BlogPost
    template_name = "blog/blog.html"
    context_object_name = "posts"


def post_detail(request, slug):
    """View to show a single blog post in detail"""

    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.all()
    comment_form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("account_login")  # allauth-safe

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, "Comment added successfully.")
            return redirect("post_detail", slug=slug)

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


@login_required
def add_post(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully.")
            return redirect("blog") 
    else:
        form = BlogPostForm()

    return render(
        request,
        "blog/add_post.html",
        {"form": form},
    )


@login_required
def edit_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if not request.user.is_superuser:
        messages.error(request, "Not authorized.")
        return redirect("post_detail", slug=slug)

    form = BlogPostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Post updated successfully.")
        return redirect("post_detail", slug=slug)

    return render(
        request,
        "blog/edit_post.html",
        {
            "form": form,
            "post": post,  
        },
    )


@login_required
def delete_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if not request.user.is_superuser:
        messages.error(request, "Not authorized.")
        return redirect("post_detail", slug=slug)

    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("blog")
