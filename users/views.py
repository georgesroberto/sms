from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Role


# Register View
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        # Validate email uniqueness
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'register.html')

        # Create the user with selected role
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
        )

        messages.success(request, f"{user.username} Account created successfully! Please log in.")
        return redirect('users:login')

    return render(request, 'register.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user using email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users:dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('users:login')

# Dashboard View
@login_required
def dashboard(request):
    user = request.user
    if user.is_role('admin'):
        return render(request, 'users/admin_dashboard.html')
    elif user.is_role('vendor'):
        return render(request, 'users/vendor_dashboard.html')
    else:
        messages.error(request, "Invalid role. Please contact the administrator.")
        return redirect('users:logout')
