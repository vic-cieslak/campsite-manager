from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView


from django.shortcuts import render
from django.utils import timezone
from .models import ReservationInquiry
from datetime import timedelta
from .forms import ReservationInquiryForm

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()



def get_camping_population_data():
    today = timezone.now().date()
    population_data = []

    for i in range(30):
        current_date = today + timedelta(days=i)
        reservations = ReservationInquiry.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date,
            is_confirmed=True,
            is_canceled=False
        )
        
        total_people = sum(
            reservation.num_adults + 
            reservation.num_children_0_3 + 
            reservation.num_children_4_13 + 
            reservation.extra_person_count 
            for reservation in reservations
        )
        
        population_data.append({
            'date': current_date,
            'total_people': total_people
        })

    return population_data

def camping_population_chart_view(request):
    population_data = get_camping_population_data()
    context = {
        'population_data': population_data
    }
    return render(request, 'pages/camping_population_chart.html', context)



def get_current_occupancy():
    today = timezone.now().date()
    reservations = ReservationInquiry.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_confirmed=True,
        is_canceled=False
    )

    # Example thresholds, adjust these based on your camping's capacity
    low_threshold = 40
    high_threshold = 80

    total_people = sum(
        reservation.num_adults + 
        reservation.num_children_0_3 + 
        reservation.num_children_4_13 + 
        reservation.extra_person_count 
        for reservation in reservations
    )

    if total_people <= low_threshold:
        occupancy_level = 'low'
    elif total_people > high_threshold:
        occupancy_level = 'high'
    else:
        occupancy_level = 'medium'

    return total_people, occupancy_level

def current_occupancy_view(request):
    total_people, occupancy_level = get_current_occupancy()
    context = {
        'total_people': total_people,
        'occupancy_level': occupancy_level,
        'today': timezone.now(),  # Dodanie dzisiejszej daty do kontekstu
    }
    return render(request, 'pages/current_occupancy_chart.html', context)




def create_reservation_view(request):
    if request.method == 'POST':
        form = ReservationInquiryForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.is_confirmed = False  # Initially not confirmed
            reservation.save()
            return redirect(reverse('reservation_success'))
    else:
        form = ReservationInquiryForm()

    return render(request, 'pages/create_reservation.html', {'form': form})

def reservation_success_view(request):
    return render(request, 'pages/reservation_success.html')