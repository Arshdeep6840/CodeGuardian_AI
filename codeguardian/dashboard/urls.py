from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    path("api/dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
]
