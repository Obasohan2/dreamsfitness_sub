import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .models import BlogPost, Comment, Category
from .forms import AddPostForm, PostForm, CommentForm


# ====================================================
# BLOG LIST (ALL POSTS)
# ====================================================
class PostList(ListView):
    model = BlogPost
    template_name = "blog/blog.html"
    context_object_name = "posts"
    paginate_by = 8

    def get_queryset(self):
        return (
            BlogPost.objects
            .exclude(slug__isnull=True)
            .exclude(slug="")
            .select_related("author", "category")
            .order_by("-created_on")
        )


# ====================================================
# CATEGORY POSTS
# ====================================================
class CategoryPostList(ListView):
    model = BlogPost
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = 8

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs["category_slug"]
        )

        return (
            BlogPost.objects
            .filter(category=self.category)
            .exclude(slug__isnull=True)
            .exclude(slug="")
            .select_related("author", "category")
            .order_by("-created_on")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


# ====================================================
# POST DETAIL + COMMENTS
# ====================================================
def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.select_related("user")
    comment_form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("account_login")

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
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
        }
    )


# ====================================================
# ADD POST
# ====================================================
@login_required
def add_post(request):
    if request.method == "POST":
        form = AddPostForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            messages.success(request, "Post created successfully.")
            return redirect("blog")
    else:
        form = AddPostForm()

    return render(
        request,
        "blog/add_post.html",
        {"form": form}
    )


# ====================================================
# EDIT POST
# ====================================================
@login_required
def edit_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "You are not allowed to edit this post.")
        return redirect("post_detail", slug=slug)

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("post_detail", slug=slug)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/edit_post.html",
        {
            "form": form,
            "post": post,
        }
    )


# ====================================================
# DELETE POST
# ====================================================
@login_required
@require_POST
def delete_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "You are not allowed to delete this post.")
        return redirect("post_detail", slug=slug)

    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect("blog")


# ====================================================
# LIKE / UNLIKE (AJAX)
# ====================================================
@login_required
@require_POST
def post_reaction(request):
    data = json.loads(request.body)
    post = get_object_or_404(BlogPost, id=data.get("post_id"))
    reaction = data.get("reaction")
    user = request.user

    if reaction == "like":
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
        else:
            post.unlikes.remove(user)
            post.likes.add(user)

    elif reaction == "unlike":
        if post.unlikes.filter(id=user.id).exists():
            post.unlikes.remove(user)
        else:
            post.likes.remove(user)
            post.unlikes.add(user)

    return JsonResponse({
        "success": True,
        "likes": post.likes.count(),
        "unlikes": post.unlikes.count(),
    })

# ====================================================
# EDIT COMMENT
# ====================================================
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not allowed to edit this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    if request.method == "POST":
        form = CommentForm(
            request.POST,
            instance=comment
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully.")
            return redirect("post_detail", slug=comment.post.slug)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "blog/edit_comment.html",
        {
            "form": form,
            "comment": comment,
        }
    )


# ====================================================
# DELETE COMMENT
# ====================================================
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not allowed to delete this comment.")
        return redirect("post_detail", slug=comment.post.slug)

    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect("post_detail", slug=comment.post.slug)
