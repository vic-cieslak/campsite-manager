from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView


from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
# from .models import ReservationInquiry

from kempingdabrowno.users.models import ReservationInquiry
from kempingdabrowno.users.forms import ReservationInquiryForm


from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

# @login_required
def create_reservation_view(request):
    if request.method == 'POST':
        form = ReservationInquiryForm(request.POST)
        if form.is_valid():
            print('form valid!')
            # Create a ReservationInquiry object from form data
            reservation = ReservationInquiry(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                num_adults=form.cleaned_data['num_adults'],
                num_children_0_3=form.cleaned_data['num_children_0_3'],
                num_children_4_13=form.cleaned_data['num_children_4_13'],
                num_animals=form.cleaned_data.get('num_animals', 0),  # Optional field
                tent_type=form.cleaned_data.get('tent_type', None),
                caravan_required=form.cleaned_data.get('caravan_required', False),
                electricity_for_tent=form.cleaned_data.get('electricity_for_tent', False),
                electricity_for_caravan=form.cleaned_data.get('electricity_for_caravan', False),
                extra_person_count=form.cleaned_data.get('extra_person_count', 0),
                waste_disposal=form.cleaned_data.get('waste_disposal', False),
                parking_required=form.cleaned_data.get('parking_required', False),
                num_beach_stay_adults=form.cleaned_data.get('num_beach_stay_adults', 0),
                num_beach_stay_children=form.cleaned_data.get('num_beach_stay_children', 0),
                apply_discount=form.cleaned_data.get('apply_discount', False),
                is_confirmed=False  # Initially not confirmed
            )
            # Save the reservation
            reservation.save()

            # Redirect to the success page after saving the reservation
            return redirect(reverse('reservation_success'))
        else:
            print(form.errors)

    else:
        form = ReservationInquiryForm()

    return render(request, 'pages/create_reservation.html', {'form': form})


def reservation_success_view(request):
    return render(request, 'pages/reservation_success.html')



@login_required
def my_reservations_view(request):
    user_reservations = ReservationInquiry.objects.filter(user=request.user).order_by('-start_date')

    # Add a calculated field for total children in each reservation
    for reservation in user_reservations:
        reservation.total_children = reservation.num_children_0_3 + reservation.num_children_4_13

    context = {
        'reservations': user_reservations,
    }
    return render(request, 'pages/my_reservations.html', context)

def reservation_detail_view(request, id):
    reservation = ReservationInquiry.objects.get(id=id, user=request.user)
    context = {
        'reservation': reservation,
    }
    return render(request, 'pages/reservation_detail.html', context)


@login_required
def cancel_reservation_view(request, id):
    reservation = ReservationInquiry.objects.get(id=id, user=request.user)

    if request.method == 'POST':
        reservation.is_canceled = True
        reservation.save()
        messages.success(request, 'Your reservation has been canceled.')
        return redirect('my_reservations')

    context = {
        'reservation': reservation,
    }
    return render(request, 'pages/cancel_reservation_confirm.html', context)


def dashboard_callback(request, context):
    # You can modify the context here if needed
    return context