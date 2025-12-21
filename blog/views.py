from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import ListView
from django.contrib import messages
from .forms import PostForm, AddPostForm
from .models import BlogPost, Comment


class PostList(ListView):
    """view to create the post on the blog"""
    model = BlogPost
    template_name = 'blog/blog.html'


def post_detail(request, slug):
    """ View to show a particular blog post in detail """

    post = BlogPost.objects.filter(slug=slug).first()
    comments = Comment.objects.filter(blog_id=post)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Action not allowed')
            return redirect(reverse('home'))
        else:
            user = request.user
            body = request.POST.get('body', '')
            comment = Comment(user=user, body=body, blog_id=post)
            comment.save()

    template = 'blog/post_detail.html'
    context = {
        'post': post,
        'comments': comments,
    }

    return render(request, template, context)


def delete_comment(request, comment_id):
    """
    A view to delete comments by admin
    """
    if not request.user.is_superuser:
        messages.error(
            request, 'You are not authorized to perform this action!!')
        return redirect(
            reverse('blog'))

    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    messages.success(request, 'The comment was removed!')
    return redirect(reverse('blog'))


def editPost(request, slug):
    """
    A view for admin to edit blog posts

    """
    if not request.user.is_superuser:
        messages.error(
            request, 'You are not authorized to perform this action!')
        return redirect(reverse('home'))

    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == 'POST':
        postForm = PostForm(request.POST, request.FILES, instance=post)
        if postForm.is_valid():
            postForm.save()
            messages.success(request, 'Successfully updated the post!')
            return redirect('blog')
        else:
            messages.error(request, 'Failed to update the post. \
                Please ensure the form is valid.')

    else:
        postForm = PostForm(instance=post)
        messages.info(
            request, f'You are currently in editing mode: {post.slug}')

    template = 'blog/edit_post.html'
    context = {
        'postForm': postForm,
        'post': post,
    }

    return render(request, template, context)


def deletePost(request, slug):
    """
    A view to delete posts
    """
    if not request.user.is_superuser:
        messages.error(
            request, 'You are not authorized to perform this action!!')
        return redirect(reverse('home'))

    post = get_object_or_404(BlogPost, slug=slug)
    post.delete()
    messages.success(request, 'The post was deleted!')
    return redirect(reverse('blog'))


def addPost(request, ):

    """
    A view to add blog post &

    """
    if not request.user.is_superuser:
        messages.error(
             request, 'You are not authorized to perform this action!!')
        return redirect(reverse('home'))

    template = 'blog/add_post.html'

    form = AddPostForm(request.POST or None, request.FILES or None)

    context = {
         'form': form,
     }

    if request.method == "POST":
        form = AddPostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.save()
            messages.success(
                request, 'A new blog has been successfully added')
            return redirect('blog')
        else:
            messages.error(
                request, 'An error occurred. \
                    Please ensure the form is valid.')
    else:
        form = AddPostForm()

    return render(request, template, context)