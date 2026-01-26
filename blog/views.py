from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import BlogPost, Comment
from .forms import CommentForm, AddPostForm, PostForm


# =========================
# BLOG LIST
# =========================
def BlogList(request):
    posts = (
        BlogPost.objects
        .select_related("author", "category")
        .prefetch_related("likes", "unlikes", "comments")
        .filter(slug__isnull=False)
        .order_by("-created_on")
    )

    return render(request, "blog/blog.html", {"posts": posts})


# =========================
# BLOG DETAIL + ADD COMMENT
# =========================
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.select_related("user").order_by("created_on")

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
            messages.success(request, "Comment added successfully.")
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
# ADD POST (USER + ADMIN)
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
            messages.success(request, "Post created successfully.")
            return redirect("blog")
    else:
        form = AddPostForm()

    return render(request, "blog/add_post.html", {"form": form})


# =========================
# EDIT POST (AUTHOR ONLY)
# =========================
@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    # ADMIN CANNOT EDIT OTHER USERS' POSTS
    if request.user != post.author:
        return HttpResponseForbidden("You can only edit your own posts.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("blog_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/edit_post.html", {
        "form": form,
        "post": post,
    })


# =========================
# DELETE POST (AUTHOR OR ADMIN)
# =========================
@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    if request.user != post.author and not request.user.is_staff:
        return HttpResponseForbidden("You can only delete your own posts.")

    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("blog")


# =========================
# EDIT COMMENT (AUTHOR ONLY)
# =========================
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # ADMIN CANNOT EDIT OTHER USERS' COMMENTS
    if request.user != comment.user:
        return HttpResponseForbidden("You can only edit your own comments.")

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect("blog_detail", slug=comment.blog_post.slug)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "blog/edit_comment.html",
        {
            "form": form,
            "comment": comment,
        },
    )


# =========================
# DELETE COMMENT (AUTHOR OR ADMIN)
# =========================
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user and not request.user.is_staff:
        return HttpResponseForbidden("You can only delete your own comments.")

    slug = comment.blog_post.slug
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect("blog_detail", slug=slug)


# =========================
# REACTIONS (AJAX)
# =========================
@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

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
@require_POST
def toggle_unlike(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

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
