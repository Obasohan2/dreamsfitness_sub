from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm
from django.db.models.functions import Lower


# Create your views here.

def all_products(request):
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey

            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'

            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    return render(request, 'products/products.html', {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    review_form = None
    has_reviewed = False

    if request.user.is_authenticated:
        has_reviewed = product.reviews.filter(user=request.user).exists()

        if request.method == "POST" and not has_reviewed:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Thank you for your review!")
                return redirect("product_detail", product_id=product.id)
        elif not has_reviewed:
            review_form = ReviewForm()

    context = {
        "product": product,
        "review_form": review_form,
        "has_reviewed": has_reviewed,
    }

    return render(request, "products/product_detail.html", context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product = review.product

    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("product_detail", product_id=product.id)

    return render(request, "products/delete_review.html", {
        "review": review,
        "product": product,
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated.")
            return redirect("product_detail", product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "products/edit_review.html", {
        "form": form,
        "review": review,
        "product": review.product,
    })


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    # 🔒 Permission check
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('home')

    # 📦 Get product
    product = get_object_or_404(Product, pk=product_id)

    # 📝 Create form ONCE (pre-populates on GET, updates on POST)
    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
    )

    # ✅ Handle form submission
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect('product_detail', product_id=product.id)
        else:
            # 🔍 Debug during development
            print("FORM ERRORS:", form.errors)
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.'
            )

    # 🎨 Render edit page
    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product,
    })


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect('home')

    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        product.delete()
        messages.success(request, 'Product deleted!')
        return redirect('products')

    # If someone tries to access via GET
    messages.error(request, 'Invalid request.')
    return redirect('products')
