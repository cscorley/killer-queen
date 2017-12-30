from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

def user_password_change(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('new_password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SetPasswordForm(request.user)

    form.fields['new_password1'].help_text = "Your password must contain at least 8 characters.  Your password can't be: too similar to your other personal information, a commonly used password, or all numbers."

    return render(request, 'generic-form.html', {'form': form,
                                                 'header': 'Update password',
                                                 'button': 'Update',
                                                  })