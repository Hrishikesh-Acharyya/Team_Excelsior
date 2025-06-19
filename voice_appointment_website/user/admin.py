from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User  


"""
Since we defined a custom user model, we need to register it with a custom admin site.
list_display allows us to specify which fields to display in the admin list view.
search_fields allows us to specify which fields are searchable in the admin interface.
ordering allows us to specify the default ordering of the user list in the admin interface. Here the users are sorted by full name.
fieldsets allows us to group fields into sections in the admin form. last_login is automatically managed by Django and does not need to be included in the fieldsets.


"""

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('phone_number', 'full_name', 'email', 'is_staff', 'is_superuser', 'is_active')

    def clean(self):
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get('is_superuser', False)
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if is_superuser:
            if not password1 or not password2:
                raise forms.ValidationError("Superuser must have a password.")
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        is_superuser = self.cleaned_data.get('is_superuser', False)
        password = self.cleaned_data.get("password1")
        if is_superuser and password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user

class customUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    model = User
    list_display = ['phone_number', 'full_name', 'email', 'is_staff', 'is_active','is_superuser']
    search_fields = ['phone_number', 'full_name', 'email','is_active', 'is_staff']
    ordering = ['full_name']

    fieldsets = (
        ('UserInfo', {'fields': ('phone_number', 'full_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',), #django built in css class makes the form wider
            'description': 'Fields marked with * are required.',
            'fields': ('phone_number', 'full_name', 'email', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            # Hide password fields for regular users in the add form
            if not request.user.is_superuser:
                form.base_fields['password1'].required = False
                form.base_fields['password2'].required = False
            return form

admin.site.register(User, customUserAdmin)