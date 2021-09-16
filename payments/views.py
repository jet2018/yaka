from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import UpdateView, DetailView, DeleteView, CreateView, TemplateView, ListView
from django.shortcuts import render, redirect

# Create your views here.
# TODO 1. create an acount
# TODO 2. Login
# TODO 3. Forgot Password ***
# TODO 4. Setup profile
# TODO 5. Delete account
# TODO 6. Reset password
# TODO 7. Pay for electricity
# TODO 8. Transfer payments to final owners
# TODO 9. Transfer the paid for units to the right owner
from django.contrib import messages, auth

from payments.models import Community


class Dashboard(TemplateView):
    template_name = "pages/home.html"


def create_account(request):
    if request.is_ajax():
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")

        # create user
        check_for_username = User.objects.filter(username=username)
        check_for_email = User.objects.filter(email=email)
        if check_for_username.exists():
            messages.error(request, message="Username already taken",
                           extra_tags="text-light alert alert-danger")
            return JsonResponse({"error": "Username already taken"})
        elif check_for_email.exists():
            messages.error(request, message="Email already taken",
                           extra_tags="text-light alert alert-danger")
            return JsonResponse({"error": "Email already taken"})
        elif last_name == "" or first_name == "":
            messages.error(request, message="First and last name are required",
                           extra_tags="text-light alert alert-danger")
            return JsonResponse({"error": "First and last name are required"})
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            user.save()
            # return from here
            user_now = auth.authenticate(username=username, password=password)
            if user_now is not None:
                auth.login(request, user)
                messages.success(request, "You have logged in successfully.")
                return JsonResponse({"success": "Session started successfully"}, safe=False)


def login(request):
    if request.is_ajax():
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "" or password == "":
            return JsonResponse({"error": "Username and password are required."}, safe=False)
        else:
            login_attempt = auth.authenticate(
                username=username, password=password)
            if login_attempt is not None:
                auth.login(request, login_attempt)
                messages.success(request, "You have logged in successfully.")
                return JsonResponse({"success": "Session started successfully"}, safe=False)
            else:
                messages.error(
                    request, "No user is associated with these credentials.")
                return JsonResponse({"error": "No user is associated with these credentials."}, safe=False)


@login_required(login_url='payment:home')
def Join_Community(request, pk):
    user = request.user
    community = Community.objects.get(pk=pk)
    community.members.add(user)
    messages.success(
        request, message="You have joined %s community successfully" % community.name)
    return redirect("payment:community_mine")


@login_required(login_url='payment:home')
def Quit_Community(request, pk):
    user = request.user
    community = Community.objects.get(pk=pk)
    community.members.remove(user)
    messages.success(
        request, message="You have quit %s community successfully" % community.name)
    return redirect("payment:community_mine")


class CommunityDetailView(LoginRequiredMixin, DetailView):
    """
        View the details of one Community
    """
    login_url = 'payment:home'
    template_name = "pages/single_community.html"
    context_object_name = "community"
    queryset = Community.objects.all()


@login_required(login_url='payment:home')
def update_units(request):
    if request.is_ajax():
        units = request.POST.get("units")
        user = request.user.profile
        user.units = units
        user.save()
        return JsonResponse({"units": float(user.units)}, safe=False)


class CommunityView(LoginRequiredMixin, TemplateView):
    login_url = 'payment:home'
    template_name = 'pages/my_community.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created'] = Community.objects.filter(
            created_by=self.request.user)
        context['joined'] = self.request.user.community_set.all()
        return context


class AllCommunities(ListView):
    """
    Return all communites for users to join
    """
    model = Community
    context_object_name = "communities"
    template_name = "pages/all_communities.html"


class CreateCommunity(LoginRequiredMixin, CreateView):
    """
        Create a community, user must be authorised
    """
    login_url = "payment:home"
    model = Community
    success_url = "/my-community"
    template_name = 'pages/create_community.html'
    fields = ['name', 'village', 'sub_county', 'district', 'country', 'about']

    def form_valid(self, form):
        # attach curently logged in user as the creater
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class UpdateCommunity(LoginRequiredMixin, UpdateView):
    """
        Create a community, user must be authorised
    """
    login_url = "payment:home"
    model = Community
    success_url = "/my-community"
    template_name = 'pages/update_community.html'
    fields = ['name', 'village', 'sub_county', 'district', 'country', 'about']

    # def form_valid(self, form):
    #     # attach curently logged in user as the creater
    #     form.instance.created_by =  self.request.user
    #     return super().form_valid(form)


@login_required(login_url='payment:home')
def delete_community(request, pk):
    try:
        community = Community.objects.get(pk=pk)
        if community.created_by != request.user:
            messages.error(
                request, message="You have no permissions to do this action")
            return redirect("payment:community_mine")

        community.delete()
        messages.info(request, message="Community deleted successfully.")
        return redirect("payment:community_mine")
    except Community.DoesNotExist:
        messages.info(request, message="Community nolonger exists.")
        return redirect("payment:community_mine")


@login_required(login_url='payment:home')
def Logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        messages.success(request, message="You are logged out successfully")
        return redirect(request.path_info)
    else:
        messages.error(request, message="You are not logged in to logout")
        return redirect(request.path_info)


def profileView(request):
    if request.method == "POST" or request.is_ajax():
        pass
        # perform form submissioins here
    return render(request, "pages/profile.html")