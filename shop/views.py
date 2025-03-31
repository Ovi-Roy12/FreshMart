from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User 
from .models import Product, Cart, Order , Testimonial

def home(request):
    products = Product.objects.all()
    testimonials = Testimonial.objects.all()
    return render(request, 'home.html', {'products': products,'testimonials': testimonials})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("register")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")
    return render(request, "register.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")  
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    if request.method == "POST":
        order = Order.objects.create(user=request.user, total_price=total)
        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect('home')
    return render(request, 'checkout.html', {'total': total})

@login_required
def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, user=request.user, product__id=product_id)  # Fixed reference
        cart_item.delete()
        messages.success(request, "Item removed from cart successfully!")
    return redirect("view_cart")
