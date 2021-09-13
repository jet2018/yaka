from django.urls import  path
from .views import ProfileUpdate, CreateCommunity, UpdateCommunity, Dashboard, Logout, login, update_units, \
    create_account, CommunityView, delete_community, AllCommunities

app_name = 'payment'
urlpatterns = [
    path("", Dashboard.as_view(), name="home"),
    path("logout", Logout, name="logout"),
    path("login", login, name="login"),
    path("register", create_account, name="register"),
    path("my-community", CommunityView.as_view(), name="community_mine"),
    path("update_units", update_units, name="update_units"),
    path("delete_community/<pk>", delete_community, name="delete_community"),
    path("create_community", CreateCommunity.as_view(), name="create_community"),
    path("update_community/<pk>", UpdateCommunity.as_view(), name="update_community"),
    path("all_communities", AllCommunities.as_view(), name="all_communities"),
]