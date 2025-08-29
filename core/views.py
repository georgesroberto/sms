from django.shortcuts import render, redirect

# Create your views here.
# Landing Page
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'index.html')