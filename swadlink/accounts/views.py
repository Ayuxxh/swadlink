from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib import messages
from  accounts.forms import CustomLoginForm
from cafes.models import Cafe
from django.contrib.auth import login

class CafeLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm

    def dispatch(self, request, *args, **kwargs):
        self.cafe = get_object_or_404(Cafe, slug=kwargs.get('slug'))

        if request.user.is_authenticated:
            if self._user_belongs_to_cafe(request.user, self.cafe):
                return redirect(f'/{self.cafe.slug}/dashboard/')
            else:
                messages.error(request, "You are not authorized for this café.")
                return redirect(f'/{self.cafe.slug}/login/')


                
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.get_user()

        if not self._user_belongs_to_cafe(user, self.cafe):
            messages.error(self.request, "You do not belong to this café.")
            return redirect(f'/{self.cafe.slug}/login/')

        login(self.request, user)

        # 1️⃣ Handle ?next=
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return redirect(next_url)

        # 2️⃣ Redirect by role
        if user.role == 'owner':
            return redirect('dashboard:dashboard', slug=self.cafe.slug)
        elif user.role == 'employee':
            return redirect('dashboard:employee_dashboard', slug=self.cafe.slug)
        elif user.is_superuser:
           return redirect('dashboard:dashboard', slug=self.cafe.slug)

        # fallback
        return redirect('/')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cafe'] = self.cafe
        return context

    def _user_belongs_to_cafe(self, user, cafe):
    # ✅ Superusers can access all cafés
        if user.is_superuser:
            return True

        # ✅ Owners or employees of this cafe
        return (
            cafe.owners.filter(id=user.id).exists() or
            cafe.employees.filter(id=user.id).exists()
        )




from django.contrib.auth import logout
from django.views import View


class CafeLogoutView(View):
    def get(self, request, slug):
        logout(request)
        return redirect(f'/{slug}/login/') 
    

