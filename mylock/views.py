from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_validation_token, account_verification_token
from django.core.mail import send_mail
from .models import CustomUser, Log
from .forms import UserForm
from background_task import background
import mylock.main
from mylock.pin_code import get_code
import subprocess

import sys
sys.path.append("/home/pi/smartLock")
from facial_recognition import train_new_user

import serial
for i in range(10):
    try:
        ser = serial.Serial('/dev/ttyACM' + str(i), 9600)
        break
    except:
        pass

# Create your views here.

@login_required
def home(request):
    context = {}
    if not request.user.is_superuser:
      context["fingerprint_ID"] = CustomUser.objects.filter(username=request.user.username).values_list("fingerprint_ID", flat=True)[0]
    return render(request, 'mylock/home.html', context)

@login_required
def users(request):
    context = {}
    context["users_list"] = [str(i) for i in CustomUser.objects.all()]
    return render(request, 'mylock/users.html', context)

@login_required
@user_passes_test(lambda i: i.is_superuser, login_url='mylock:home')
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            login_user = form.login_save()
            current_site = get_current_site(request)
            subject = 'Validate your account'
            message = render_to_string('mylock/validation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_validation_token.make_token(user),
            })
            from_email = "CW2B3.smartLock@gmail.com"
            to_email = "CW2B3.smartLock@gmail.com"
            send_mail(subject, message, from_email, [to_email])

            return render(request, 'mylock/add_user.html', {'text': 'Please confirm your email address to complete the registration'})
    else:
        form = UserForm()

    return render(request, 'mylock/add_user.html', {'form': form})

def validate_request(request, uidb64, token):
    context = {}
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_validation_token.check_token(user, token):
            current_site = get_current_site(request)
            subject = 'Verificate your account'
            message = render_to_string('mylock/verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_verification_token.make_token(user),
            })
            from_email = "CW2B3.smartLock@gmail.com"
            to_email = CustomUser.objects.filter(username=user).values_list("email", flat=True)[0]
            send_mail(subject, message, from_email, [to_email])
    return render(request, 'mylock/validate_account.html', context)

def verificate_account(request, uidb64, token):
    context = {}
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_verification_token.check_token(user, token):
        login_user = User.objects.get(username=user)
        user.is_active = True
        user.save()
        login_user.is_active = True

        login_user.save()
        context["text"] = "Thank you for your email confirmation. Now you can login your account."
    else:
        context["text"] = "Activation link is invalid!"
    return render(request, 'mylock/verificate_account.html', context)

@user_passes_test(lambda i: not i.is_superuser and CustomUser.objects.filter(username=i.username).values_list("fingerprint_ID", flat=True)[0] == "", login_url='mylock:home')
def setup_fingerprint(request, new_user):
    context = {}
    context["title"] = "Setup your account"
    if (request.GET.get('fingerprint_button')):
        subprocess.call("/home/pi/smartLock/kill_authenticate")
        mylock.main.add_new_fingerprint(new_user)
        return HttpResponseRedirect(reverse('mylock:setup_facial_recognition_explanation', kwargs={'new_user': new_user}))
    return render(request, 'mylock/setup_fingerprint.html', context)

@login_required
@user_passes_test(lambda i: not i.is_superuser, login_url='mylock:home')
def setup_facial_recognition_explanation(request, new_user):
    context = {}
    context["title"] = "Setup your account"
    if(request.GET.get('photo_button')):
        mylock.main.start_picture_procedure()
        return HttpResponseRedirect(reverse('mylock:setup_facial_recognition', kwargs={'new_user': new_user, 'photo_number': 0}))
    return render(request, 'mylock/setup_facial_recognition_explanation.html', context)

@login_required
@user_passes_test(lambda i: not i.is_superuser, login_url='mylock:home')
def setup_facial_recognition(request, new_user, photo_number):
    context = {}
    context["title"] = "Setup your account"
    context["text"] = str(photo_number) + "/5 photos taken"
    context["photo_number"] = photo_number
    context["next_photo_number"] = photo_number + 1
    if photo_number < 0 or photo_number > 5:
        return HttpResponseRedirect(reverse('mylock:home'))
    elif 0 < photo_number < 5:
        mylock.main.add_new_face(new_user, photo_number)
    elif photo_number == 5:
        mylock.main.add_new_face(new_user, photo_number)
        context["succes_message"] = "Setup completed!"
        finish_new_user()
    return render(request, 'mylock/setup_facial_recognition.html', context)

@background(schedule=1)
def finish_new_user():
    subprocess.Popen(["python3", "/home/pi/smartLock/authenticate.py"])
    train_new_user()

@login_required
def user_detail(request, user):
    context = {}
    context["title"] = "Details from user: " + str(user)
    context["user"] = str(user)
    detail = CustomUser.objects.get(username=user)
    context["user_detail"] = detail.details()
    return render(request, 'mylock/user_detail.html', context)

@login_required
@user_passes_test(lambda i: i.is_superuser, login_url='mylock:home')
def delete_user(request, user):
    context = {}
    delete_info = CustomUser.objects.get(username=user)
    delete_info.delete()
    delete_login = User.objects.get(username=user)
    delete_login.delete()
    mylock.main.delete_user_photos(user)
    return render(request, 'mylock/delete_user.html', context)

@login_required
def log(request):
    context = {}
    context["title"] = "List with the log of the lock"
    context["log_list"] = [str(i).split(",") for i in Log.objects.all()][::-1]
    return render(request, 'mylock/log.html', context)

@login_required
@user_passes_test(lambda i: not i.is_superuser, login_url='mylock:home')
@permission_required('mylock.can_see_backup_password', login_url='mylock:home')
def backup_password(request):
    context = {}
    context["title"] = "Backup password"
    if(request.GET.get('backup_password_button')):
        pincode = get_code()
        ser.write(str(pincode).encode())
        subject = "Backup password"
        message = "Your backup password is: " + str(pincode)
        from_email = "CW2B3.smartLock@gmail.com"
        to_email = CustomUser.objects.filter(username=request.user.username).values_list("email", flat=True)[0]
        send_mail(subject, message, from_email, [to_email])
        backup_password_toggler = Group.objects.get(name="backup_password_toggler")
        permission = Permission.objects.get(name="Can see backup password")
        backup_password_toggler.permissions.remove(permission)
        log = Log(username = request.user.username, timestamp= timezone.now())
        log.save()
        return HttpResponseRedirect(reverse('mylock:home'))
    return render(request, 'mylock/backup_password.html', context)
