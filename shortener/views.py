from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import F, Sum, Count
from django.utils import timezone
from datetime import timedelta

from .forms import UserRegisterForm, URLForm
from .models import URL, Click
from .utils import get_client_ip, generate_unique_code


def home(request):
    if request.method == "POST":
        form = URLForm(request.POST)

        if form.is_valid():
            url_obj = form.save(commit=False)
            if request.user.is_authenticated:
                url_obj.user = request.user

            url_obj.short_code = generate_unique_code()
            url_obj.save()

            short_url = request.build_absolute_uri(f"/{url_obj.short_code}")
            return render(
                request,
                "shortener/home.html",
                {
                    "form": URLForm(),
                    "short_url": short_url,
                    "show_signup_prompt": not request.user.is_authenticated,
                },
            )
        return render(request, "shortener/home.html", {"form": form})
    return render(request, "shortener/home.html", {"form": URLForm()})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"Welcome, {user.username}! Your account is ready."
            )
            return redirect("dashboard")
    else:
        form = UserRegisterForm()

    return render(request, "shortener/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard(request):
    url_list = request.user.urls.all()
    total_clicks = url_list.aggregate(total=Sum("click_count"))["total"] or 0
    total_urls = url_list.count()

    paginator = Paginator(url_list, 10)
    page_number = request.GET.get("page")
    urls = paginator.get_page(page_number)

    return render(
        request,
        "shortener/dashboard.html",
        {"urls": urls, "total_clicks": total_clicks, "total_urls": total_urls},
    )


@login_required
def create_url(request):
    if request.method == "POST":
        form = URLForm(request.POST)
        if form.is_valid():
            url_obj = form.save(commit=False)
            url_obj.user = request.user

            custom_code = form.cleaned_data.get("custom_short_code")
            if custom_code:
                url_obj.short_code = custom_code
                url_obj.custom_code = True
            else:
                url_obj.short_code = generate_unique_code()

            url_obj.save()
            short_url = request.build_absolute_uri(f"/{url_obj.short_code}")
            messages.success(request, "URL shortened successfully!")

            return render(
                request,
                "shortener/create_url.html",
                {
                    "form": URLForm(),
                    "short_url": short_url,
                    "created_url": url_obj,
                },
            )
        return render(request, "shortener/create_url.html", {"form": form})
    return render(request, "shortener/create_url.html", {"form": URLForm()})


@login_required
def edit_url(request, short_code):
    url_obj = get_object_or_404(URL, short_code=short_code)
    if url_obj.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this URL.")

    form = URLForm(request.POST or None, instance=url_obj)
    if request.method == "POST" and form.is_valid():
        url_obj = form.save(commit=False)
        custom_code = form.cleaned_data.get("custom_short_code")
        if custom_code:
            url_obj.short_code = custom_code
            url_obj.custom_code = True
        url_obj.save()
        messages.success(request, "URL updated successfully!")
        return redirect("dashboard")

    return render(request, "shortener/edit_url.html", {"form": form, "url": url_obj})


@login_required
def delete_url(request, short_code):
    url_obj = get_object_or_404(URL, short_code=short_code)
    if url_obj.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this URL.")

    if request.method == "POST":
        url_obj.delete()
        messages.success(request, f"Short URL '{short_code}' deleted.")
        return redirect("dashboard")
    return render(request, "shortener/delete_confirm.html", {"url": url_obj})


def redirect_url(request, short_code):
    url_obj = get_object_or_404(URL, short_code=short_code)

    URL.objects.filter(pk=url_obj.pk).update(click_count=F("click_count") + 1)

    Click.objects.create(
        url=url_obj,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        referrer=request.META.get("HTTP_REFERER", "")[:2000],
    )

    return redirect(url_obj.original_url)


@login_required
def analytics(request):
    user_urls = request.user.urls.all()
    total_urls = user_urls.count()
    total_clicks = user_urls.aggregate(total=Sum("click_count"))["total"] or 0

    most_clicked = user_urls.order_by("-click_count").first()
    least_clicked = user_urls.filter(click_count__gt=0).order_by("click_count").first()

    week_ago = timezone.now() - timedelta(days=7)
    recent_clicks = Click.objects.filter(
        url__user=request.user,
        clicked_at__gte=week_ago,
    ).count()

    daily_clicks = []

    for i in range(6, -1, -1):  # 6, 5, 4, 3, 2, 1, 0
        day = timezone.now() - timedelta(days=i)
        # __date is a Django lookup that extracts just the date portion.
        count = Click.objects.filter(
            url__user=request.user,
            clicked_at__date=day.date(),
        ).count()
        daily_clicks.append({"date": day.strftime("%b %d"), "count": count})

    top_urls = user_urls.order_by("-click_count")[:5]
    return render(
        request,
        "shortener/analytics.html",
        {
            "total_urls": total_urls,
            "total_clicks": total_clicks,
            "most_clicked": most_clicked,
            "least_clicked": least_clicked,
            "recent_clicks": recent_clicks,
            "daily_clicks": daily_clicks,
            "top_urls": top_urls,
        },
    )


@login_required
def url_detail_analytics(request, short_code):
    url_obj = get_object_or_404(URL, short_code=short_code)

    if url_obj.user != request.user:
        return HttpResponseForbidden("You don't have permission to view this.")

    unique_visitors = url_obj.clicks.values("ip_address").distinct().count()

    top_referrers = (
        url_obj.clicks.exclude(referrer="")
        .values("referrer")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    return render(
        request,
        "shortener/url_detail.html",
        {
            "url": url_obj,
            "total_clicks": url_obj.click_count,
            "unique_visitors": unique_visitors,
            "recent_clicks": url_obj.clicks.all()[:20],
            "top_referrers": top_referrers,
        },
    )
