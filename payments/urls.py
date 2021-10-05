from django.urls import path
from .views import CreateCommunity, UpdateCommunity, Dashboard, Logout, login, update_units, \
    create_account, CommunityView, CommunityDetailView, delete_community, AllCommunities, Join_Community, \
    Quit_Community, profileView, uploadProfileImage, complete_payments, ResetPassword, Delete_Account, \
    Deactivate_Account, UpdatePayments, GetMyEarnings

app_name = 'payment'
urlpatterns = [
    path("", Dashboard.as_view(), name="home"),
    path("logout", Logout, name="logout"),
    path("login", login, name="login"),
    path("register", create_account, name="register"),
    path("my-community", CommunityView.as_view(), name="community_mine"),
    path("update_units", update_units, name="update_units"),
    path("join/<pk>", Join_Community, name="join"),
    path("quit/<pk>", Quit_Community, name="quit"),
    path("delete_community/<pk>", delete_community, name="delete_community"),
    path("community_details/<pk>", CommunityDetailView.as_view(),
         name="community_details"),
    path("create_community", CreateCommunity.as_view(), name="create_community"),
    path("update_community/<pk>", UpdateCommunity.as_view(),
         name="update_community"),
    path("all_communities", AllCommunities.as_view(), name="all_communities"),
    path("me", profileView, name="profile"),
    path("me/upload_image", uploadProfileImage, name="image"),
    path("update/passowrd", ResetPassword, name="update_password"),
    path("pay", complete_payments, name="pay"),
    path("delete", Delete_Account, name="delete_account"),
    path("deactivate", Deactivate_Account, name="deactivate"),
    path("update_payments", UpdatePayments, name="update_payments"),
    path("history", GetMyEarnings.as_view(), name="history"),


]
