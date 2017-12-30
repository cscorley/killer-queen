from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User

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

