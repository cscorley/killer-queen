from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction

from hello.forms import UserForm, PlayerForm
from .alert import Alert

class UserUpdateView(UpdateView):
    model = User
    fields = ('username',
              'first_name',
              'last_name',
              'email'
              )

    template_name_suffix = '_update_form'
    success_url = '/'

    #get object
    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        clean = form.cleaned_data

        context = {}
        self.object = context.update(first_name=clean.get('first_name'),
                                     last_name=clean.get('last_name'),
                                     username=clean.get('username'),
                                     email=clean.get('email'),
                                     force_update=False)

        return super(UserUpdateView, self).form_valid(form)

@login_required
@transaction.atomic
def update_profile(request):
    alert = None

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = PlayerForm(request.POST, instance=request.user.player)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            alert = Alert('Your profile was successfully updated!', 'success', 30)
        else:
            alert = Alert('Please correct any errors below', 'error', 30)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = PlayerForm(instance=request.user.player)

    return render(request, 'user_update_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'alert': alert
    })
