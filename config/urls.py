from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from kempingdabrowno.users.views import camping_population_chart_view
from kempingdabrowno.users.views import current_occupancy_view
from kempingdabrowno.users.views import create_reservation_view
from kempingdabrowno.users.views import reservation_success_view
from kempingdabrowno.users.views import my_reservations_view
from kempingdabrowno.users.views import reservation_detail_view
from kempingdabrowno.users.views import cancel_reservation_view

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("kempingdabrowno.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path('populacja/', camping_population_chart_view, name='populacja'),
    path('obecne-oblozenie/', current_occupancy_view, name='obecne_oblozenie'),
    path('rezerwuj/', create_reservation_view, name='create_reservation'),
    path('rezerwacja-sukces/', reservation_success_view, name='reservation_success'),
    path('moje-rezerwacje/', my_reservations_view, name='my_reservations'),
    path('rezerwacja/<int:id>/', reservation_detail_view, name='reservation_detail'),
    path('rezerwacja/<int:id>/cancel/', cancel_reservation_view, name='cancel_reservation'),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
