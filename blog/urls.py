from django.urls import path
from django.views.generic import TemplateView

from .views import *

app_name = 'blog'
urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('terms/', TemplateView.as_view(template_name='terms_and_conditions.html'), name='terms'),
    path('cookies-policy/', TemplateView.as_view(template_name='cookie_policy.html'), name='cookies-policy'),
    path("python/", PythonPageView.as_view(), name="python-page"),
    path("cyber-security/", CyberSecurityPageView.as_view(), name="cyber-security-page"),
    path("software-development/", SoftwareDevelopmentPageView.as_view(), name="software-development-page"),
    path("ui-ux/", UiUxPageView.as_view(), name="ui-ux-page"),
    path("mobile-pc/", MobilePcPageView.as_view(), name="mobile-pc-page"),
    path("job-updates/", JobUpdatesPageView.as_view(), name="job-updates-page"),
    path("crypto/", CryptoPageView.as_view(), name="crypto-page"),
    path("ai/", AIPageView.as_view(), name="ai-page"),
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
