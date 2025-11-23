from django.contrib import admin
from django.apps import apps
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from urllib.parse import urlencode
import json

from .models import CustomUser


def send_password_reset_email(modeladmin, request, queryset):
    for user in queryset:
        if user.email:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', args=[uid, token])
            )
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n{reset_url}',
                'admin@example.com',  # TODO: replace with real FROM email
                [user.email],
                fail_silently=False,
            )
    modeladmin.message_user(request, "Password reset email(s) sent.")

send_password_reset_email.short_description = "Send password reset email"


class DynamicModelAdmin(admin.ModelAdmin):
    show_duplicate_button = True

    class Media:
        js = ("admin/js/toggle_column.js",)

    actions = ["duplicate_entry"]

    def duplicate_entry(self, request, queryset):
        obj = queryset.first()
        if not obj:
            self.message_user(request, "No object selected to duplicate.", level="warning")
            return redirect(".")
        return redirect(self.get_duplicate_url(obj))

    def get_duplicate_url(self, obj):
        opts = self.model._meta
        add_url = reverse(f'admin:{opts.app_label}_{opts.model_name}_add')

        params = {
            field.name: getattr(obj, field.name)
            for field in obj._meta.fields
            if field.name != "id"
        }
        return f"{add_url}?{urlencode(params)}"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/duplicate/', self.admin_site.admin_view(self.duplicate_view),
                 name='admin_duplicate_entry'),
            path('toggle_columns/', self.admin_site.admin_view(self.toggle_columns),
                 name='admin_toggle_columns'),
        ]
        return custom_urls + urls

    def duplicate_view(self, request, object_id):
        obj = self.model.objects.get(pk=object_id)
        return redirect(self.get_duplicate_url(obj))

    def duplicate_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Duplicate</a>',
            self.get_duplicate_url(obj)
        )
    duplicate_button.short_description = "Duplicate"

    def get_list_display(self, request):
        if 'list_display' in self.__class__.__dict__:
            fields = list(self.list_display)
        else:
            fields = [field.name for field in self.model._meta.fields]

        extra_fields = ['duplicate_button'] if self.show_duplicate_button else []
        user_hidden_columns = request.session.get(f'hidden_columns_{self.model._meta.model_name}', [])
        return [col for col in fields + extra_fields if col not in user_hidden_columns]

    def toggle_columns(self, request):
        if request.method == "POST":
            data = json.loads(request.body)
            request.session[f'hidden_columns_{self.model._meta.model_name}'] = data.get('hidden_columns', [])
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        if 'list_display' in self.__class__.__dict__:
            all_fields = list(self.list_display)
        else:
            all_fields = [field.name for field in self.model._meta.fields]

        extra_context["all_fields"] = all_fields
        extra_context["hidden_columns"] = request.session.get(
            f'hidden_columns_{self.model._meta.model_name}',
            []
        )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CustomUser)
class CustomUserAdmin(DynamicModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'color', 'phone_number')
    ordering = ('username',)
    actions = DynamicModelAdmin.actions + [send_password_reset_email]


# Dynamically register all models in 'api'
app_label = 'api'
app_config = apps.get_app_config(app_label)

for model in app_config.get_models():
    if model is CustomUser:
        continue
    try:
        admin.site.register(model, DynamicModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass