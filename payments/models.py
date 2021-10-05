from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class Profile(models.Model):
    """
        User profile, shows the units they have for sale,
        their address so as to estimate their neighborhood,
        their bank account which is actually their phone numbers as momo is deployed
        account_bank which will always be MPS by default, can never be changed
    """
    units = models.FloatField(default=0.0)
    dp = models.ImageField(upload_to="users", blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True, help_text="What is your neighbourhood, please first look at what other people have added")
    account_bank = models.CharField("This should be MPS", blank=True, null=True, max_length=4, default="MPS")
    account_number = models.CharField("Phone number", max_length=14, help_text="Should be phone number not back account number as mobile money is being used", blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(default='UGX', max_length=4)

    def __str__(self):
        return  self.user.get_full_name()

    @property
    def default_total(self):
        return "UGX."+str(self.units * 550)

class PaymentOut(models.Model):
    """
        Transfering money from flutterwave to one's MOMO acc
        {
          "account_bank": "MPS",
          "account_number": "233542773934",
          "amount": 50,
          "narration": "UGX momo transfer",
          "currency": "UGX",
          "reference": "ugx-momo-transfer",
          "beneficiary_name": "Kwame Adew"
        }
    """
    amount = models.IntegerField()
    narration = models.CharField(max_length=200)
    reference = models.CharField(unique=True, max_length=50)
    beneficiary = models.ForeignKey(Profile, on_delete=models.CASCADE)
    units = models.FloatField()
    status = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=100, blank=True, null=True)
    placed_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  self.beneficiary.user.get_full_name()

class PayIn(models.Model):
    """
        Shows what one has paid for.
    """
    status = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=15, null=True, blank=True)
    tx_ref = models.CharField(max_length=100, blank=True)
    flw_ref = models.CharField(max_length=100, blank=True)
    amount = models.CharField(max_length=10, blank=True)
    units = models.IntegerField(default=0)
    pay_to = models.ForeignKey(User, on_delete=models.CASCADE)
    pay_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="innitiator")

    def __str__(self):
        return self.pay_by.get_full_name()



"""
paying out
{
   "tx_ref":"MC-1585230950508",
   "amount":"1500",
   "email":"user@gmail.com",
   "phone_number":"054709929220",
   "currency":"UGX",
   "redirect_url":"https://rave-webhook.herokuapp.com/receivepayment",
   "network":"MTN"
}
"""

class Notification(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=True, blank=True)
    sent_on = models.DateTimeField(auto_now=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.sender.get_full_name() +" to "+ self.receiver.get_full_name()

class Community(models.Model):
    name = models.CharField(max_length=250, help_text="Community's unique, it must be unique.", unique=True)
    district = models.CharField(max_length=250, help_text="The district from which this community is found.")
    country = models.CharField(max_length=250, default="Uganda", help_text="Country in which this community is found")
    sub_county = models.CharField(max_length=250, help_text="Sub county from which the community spans")
    village = models.CharField(max_length=250, help_text="The village the community will span")
    about = models.TextField(help_text="Write something about this community")
    members = models.ManyToManyField(User, help_text="Members of the community", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    created_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_members(self):
        return self.members.count()
# some signals

@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    if kwargs['created']:
        Profile.objects.create(user=kwargs['instance'])

@receiver(post_save, sender=Community)
def befpre_community_save(sender, instance, **kwargs):
    if kwargs['created']:
        user = instance.created_by
        if instance.members.filter(id=user.id).exists():
            instance.members.remove(user)
        else:
            instance.members.add(user)