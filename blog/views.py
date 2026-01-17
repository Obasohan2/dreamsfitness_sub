from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.urls import reverse

from .models import BlogPost, Comment
from .forms import CommentForm, AddPostForm, PostForm


# =========================
# BLOG LIST
# =========================
def BlogList(request):
    posts = BlogPost.objects.all().order_by("-created_on")

    for post in posts:
        post.can_edit = (
            request.user.is_authenticated
            and (request.user.is_staff or post.author_id == request.user.id)
        )

    return render(request, "blog/blog.html", {"posts": posts})


# =========================
# BLOG DETAIL
# =========================
def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.all()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("blog_detail", slug=slug)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog_post = post
            comment.user = request.user
            comment.save()
            return redirect("blog_detail", slug=slug)
    else:
        form = CommentForm()

    return render(
        request,
        "blog/blog_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": form,
        },
    )


# =========================
# COMMENTS
# =========================
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if not (request.user.is_staff or comment.user == request.user):
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog_detail", slug=comment.blog_post.slug)
    else:
        form = CommentForm(instance=comment)

    return render(request, "blog/edit_comment.html", {"form": form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if not request.user.is_staff:
        return HttpResponseForbidden("Admins only")

    slug = comment.blog_post.slug
    comment.delete()
    return redirect("blog_detail", slug=slug)


# =========================
# POSTS
# =========================
@login_required
def add_post(request):
    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect("blog")
    else:
        form = AddPostForm()

    return render(request, "blog/add_post.html", {"form": form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if not (request.user == post.author or request.user.is_staff):
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/add_post.html", {"form": form})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if not (request.user == post.author or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    post.delete()
    return redirect("blog")


# =========================
# LIKES
# =========================
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        post.unlikes.remove(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count(),
        "unlikes_count": post.unlikes.count(),
    })


@login_required
def toggle_unlike(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if request.user in post.unlikes.all():
        post.unlikes.remove(request.user)
        unliked = False
    else:
        post.unlikes.add(request.user)
        post.likes.remove(request.user)
        unliked = True

    return JsonResponse({
        "unliked": unliked,
        "likes_count": post.likes.count(),
        "unlikes_count": post.unlikes.count(),
    })
