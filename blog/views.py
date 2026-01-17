from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import BlogPost, Comment, Category
from .forms import CommentForm, BlogPostForm


def BlogList(request):
    posts = BlogPost.objects.all().order_by("-created_on")

    for post in posts:
        post.can_edit = (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or post.author_id == request.user.id
            )
        )

    return render(request, "blog/blog.html", {"posts": posts})


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    comments = post.comments.all()

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog_post = post
            comment.save()
            return redirect("blog_detail", pk=pk)
    else:
        comment_form = CommentForm()

    return render(
        request,
        "blog/blog_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
        },
    )

# =========================
# COMMENTS
# =========================

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Admin can edit ANY comment
    # Non-admin can edit ONLY their own (email-based)
    if not (request.user.is_staff or comment.email == request.user.email):
        return HttpResponseForbidden("You are not allowed to edit this comment.")

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog_detail", pk=comment.blog_post.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, "blog/edit_comment.html", {"form": form})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # ADMIN CAN DELETE ANY COMMENT
    if not request.user.is_staff:
        return HttpResponseForbidden("Admins only")

    post_pk = comment.blog_post.pk
    comment.delete()
    return redirect("blog_detail", pk=post_pk)


# =========================
# POSTS
# =========================

@login_required
def add_post(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect("blog")
    else:
        form = BlogPostForm()

    return render(request, "blog/post_form.html", {"form": form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    # Author OR Admin
    if not (request.user == post.author or request.user.is_staff):
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog_detail", pk=pk)
    else:
        form = BlogPostForm(instance=post)

    return render(request, "blog/post_form.html", {"form": form})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)

    # ADMIN CAN DELETE ANY POST
    # Author can delete their own
    if not (request.user == post.author or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    post.delete()
    return redirect("blog")

