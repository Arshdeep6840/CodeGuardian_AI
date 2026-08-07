from django.urls import path
from .views import DashboardStatsView, dashboard_page

urlpatterns = [
    path("api/dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("dashboard/", dashboard_page, name="dashboard"),
]
