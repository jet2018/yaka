from django.contrib import admin

# Register your models here.
from payments.models import PaymentOut, Profile, Notification, Community

# admin.register()
admin.site.site_header = "LightUs"
class ProfileAdmin(admin.ModelAdmin):
    exclude = ['currency', 'account_bank']

admin.site.register(PaymentOut)
admin.site.register(Community)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Notification)