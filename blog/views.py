from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
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
            return redirect("login")

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
def blog_create(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully.")
            return redirect("blog_list")
    else:
        form = BlogPostForm()

    return render(
        request,
        "blog/blog_create.html",
        {"form": form},
    )
