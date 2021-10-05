import json
import time

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.db.models import Q
import requests
from django.http import JsonResponse
from django.views.generic import UpdateView, DetailView, DeleteView, CreateView, TemplateView, ListView
from django.shortcuts import render, redirect, get_object_or_404

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

from payments.models import Community, Profile, PaymentOut, PayIn


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
    """ Logs the user in the system. """
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


@login_required(login_url='payment:home')
def Delete_Account(request):
    """
        Delete a user account
    """
    if request.method == 'GET' and request.is_ajax():
        user = request.user
        user.delete()
        return JsonResponse({"message": 'User deleted successfully', "code": True})


@login_required(login_url='payment:home')
def Deactivate_Account(request):
    """
        Deactivate an account, can be reactivated later by the admin
    """
    if request.method == 'GET' and request.is_ajax():
        user = request.user
        user.is_active = False
        user.save()
        return JsonResponse({"message": 'Account deactivated successfully', "code": True})


@login_required(login_url='payment:home')
def profileView(request):
    if request.method == "POST" or request.is_ajax():
        user = request.user
        user.username = request.POST.get("username") if request.POST.get("username") != "" else user.username
        user.first_name = request.POST.get("first_name") if request.POST.get("first_name") != "" else user.first_name
        user.last_name = request.POST.get("last_name") if request.POST.get("last_name") != "" else user.last_name
        user.email = request.POST.get("email") if request.POST.get("email") != "" else user.email
        user.save()
        return JsonResponse({"success":True })
        # perform form submissioins here
    return render(request, "pages/profile.html")


@login_required(login_url='payment:home')
def ResetPassword(request):
    if request.is_ajax() or request.method == "POST":
        password_old = request.POST.get("password_old")
        new_password = request.POST.get("password_new")
        confirm_password = request.POST.get("password_confirm")
        if new_password != confirm_password:
            return JsonResponse({"error": "Passwords are not matching", "status":False})
        elif len(confirm_password) < 8:
            return JsonResponse({"error": "Password is too week", "status":False})

        current_password = request.user.password
        matchcheck = check_password(password_old, current_password)
        if matchcheck:
            user = request.user
            user.set_password(confirm_password)
            user.save()
            return JsonResponse({"status":True})
        else:
            return JsonResponse({"error": "Your old password is wrong, we can't confirm it's really you.", "status": False})


@login_required(login_url='payment:home')
def uploadProfileImage(request):
    if request.method == 'POST':
        img = request.FILES['image']
        profile = get_object_or_404(Profile, user=request.user)
        profile.dp = img
        print(profile)
        profile.save()
        print(profile.dp)
        messages.success(request, message="Profile image uploaded successfully")
        return redirect("payment:profile")
    else:
        return redirect(request.path_info)


@login_required(login_url='payment:home')
def TrasferFunds(user, amount, units):
    # create the pay out locally
    payment = PaymentOut.objects.create(
        amount=amount,
        narration="Purchase of "+str(units)+" units of electricity.",
        beneficiary = user.profile,
        units = units,
        reference = "trasfer-"+str(int(time.time()))
    )
    # generate the transfer payload, mobile money.
    payload = {
          "account_bank": "MPS",
          "account_number": payment.beneficiary.account_number,
          "amount": payment.amount,
          "narration": payment.narration,
          "currency": "UGX",
          "reference": payment.reference,
          "beneficiary_name": payment.beneficiary.user.get_full_name()
        }
    # flutterwave api
    url = 'https://api.flutterwave.com/v3/transfers'
    # generating transfer headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer FLWSECK_TEST-06e17cc7ae4c99be6b3b247ecd217f77-X',
    }
    # do actual transfer
    initiate_request = requests.post(url=url, data=json.dumps(payload), headers=headers)
    make_a_transfer_request = initiate_request.text

    print(make_a_transfer_request)
    # if transfer was successful
    if make_a_transfer_request.status  == "success":
        payment.message = make_a_transfer_request.message
        payment.save()
        return True
    # otherwise
    else:
        return False


@login_required(login_url='payment:home')
def complete_payments(request):
    """
        Complete the transaction from here
    """
    if request.is_ajax():
        status = request.POST.get("status")
        pay_to = request.POST.get("seller_id")
        agura = request.user
        transaction_id = request.POST.get("transaction_id")
        tx_ref = request.POST.get("tx_ref")
        flw_ref = request.POST.get("flw_ref")
        amount = request.POST.get("amount")
        # currency = request.POST.get("currency")
        units = float(request.POST.get("units"))

        # getting the seller instance
        atunda = User.objects.get(pk = pay_to)
        # get atunda's units
        units_owner = Profile.objects.get(user = atunda)
        units_owner.units = round(units_owner.units - units, 1)
        # deduction of units completed here
        units_owner.save()

        # increment the buyer's units
        buyer = Profile.objects.get(user=agura)
        buyer.units = round(buyer.units + units, 1)
        buyer.save()


        # transfer the funds
        # transfer = TrasferFunds(atunda, amount, units)
        # if transfer:
        #     pay_in = PayIn.objects.create(
        #         status=status,
        #         transaction_id=transaction_id,
        #         tx_ref=tx_ref,
        #         flw_ref=flw_ref,
        #         amount=amount,
        #         units=units,
        #         pay_to=buyer,
        #         pay_by=agura
        #     )
        #     if pay_in:
        #         return JsonResponse({"success":True})
        #     else:
        #         return JsonResponse({"success":False})

        payment = PaymentOut.objects.create(
            amount=amount,
            narration="Purchase of " + str(units) + " units of electricity.",
            beneficiary=units_owner,
            units=units,
            reference="trasfer-" + str(int(time.time()))
        )
        # generate the transfer payload, mobile money.
        payload = {
            "account_bank": "MPS",
            "account_number": payment.beneficiary.account_number,
            "amount": payment.amount,
            "narration": payment.narration,
            "currency": "UGX",
            "reference": payment.reference,
            "callback_url": "http://localhost:8000/",
            "debit_currency": "UGX",
        }
        return JsonResponse({"status":True, "data":payload})


@login_required(login_url='payment:home')
def UpdatePayments(request):
    if request.method == "POST" and request.is_ajax():
        user = request.user.profile
        user.address = request.POST.get("address") if request.POST.get("address") else user.address
        user.account_number = request.POST.get("account_number") if request.POST.get("account_number") else user.account_number
        user.save()
        return JsonResponse({"success": True})

class GetMyEarnings(ListView):
    model =PaymentOut
    template_name = "pages/earnings.html"
    context_object_name = "earnings"

    def get_queryset(self, **kwargs):
        queryset =super().get_queryset(**kwargs)
        queryset = PaymentOut.objects.filter(beneficiary = self.request.user.profile)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchases'] = PayIn.objects.filter(pay_by = self.request.user)
        return  context