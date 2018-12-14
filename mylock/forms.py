from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import password_validation
from .models import CustomUser

class UserForm(ModelForm):
    password = forms.CharField(
        label="password",
        strip=False,
        widget=forms.PasswordInput,
    )

    password_confirmation = forms.CharField(
        label="password_confirmation",
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser

        fields = ["name", "email", "username"]

    def is_valid(self):
        valid = super(UserForm, self).is_valid()

        if not valid:
            self.add_error(valid)

        try:
            CusomUser.objects.get(username=self.cleaned_data["username"])
            self.add_error("username", "Username already exists")

        except:
            pass

        if self.cleaned_data.get("password") != self.cleaned_data.get("password_confirmation"):
            self.add_error("password_confirmation", "The two password fields didn't match")

        if len(self.errors) == 0:
            return True

        else:
            return False

    def login_save(self, commit=True):
        login = User.objects.create_user(username=self.cleaned_data.get("username"))
        login.set_password(self.cleaned_data.get("password"))
        login.is_active = False
        login.save()
        backup_password_toggler = Group.objects.get(name="backup_password_toggler")
        login.groups.add(backup_password_toggler)
