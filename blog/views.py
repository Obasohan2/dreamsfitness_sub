from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from .models import BlogPost
from .forms import AddPostForm, PostForm, CommentForm


class PostList(ListView):
    model = BlogPost
    template_name = "blog/blog.html"
    context_object_name = "posts"

    def get_queryset(self):
        return BlogPost.objects.exclude(slug="").exclude(slug__isnull=True)
    

def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.all()
    comment_form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect("account_login")

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
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully.")
            return redirect("blog")
        
    else:
        form = AddPostForm()

    return render(request, "blog/add_post.html", {"form": form})


@login_required
def edit_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if request.user != post.author:
        messages.error(request, "You are not allowed to edit this post.")
        return redirect("post_detail", slug=slug)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("post_detail", slug=slug)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/edit_post.html", {
        "form": form,
        "post": post,
    })


@login_required
def delete_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if request.user != post.author and not request.user.is_superuser:
        messages.error(request, "You are not allowed to delete this post.")
        return redirect("post_detail", slug=slug)

    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("blog")



@login_required
def toggle_reaction(request, post_id, reaction):
    post = get_object_or_404(BlogPost, id=post_id)

    if reaction == "like":
        post.unlikes.remove(request.user)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

    elif reaction == "unlike":
        post.likes.remove(request.user)
        if request.user in post.unlikes.all():
            post.unlikes.remove(request.user)
        else:
            post.unlikes.add(request.user)

    return JsonResponse({
        "likes_count": post.total_likes(),
        "unlikes_count": post.total_unlikes(),
    })
