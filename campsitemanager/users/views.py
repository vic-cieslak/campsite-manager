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

from campsitemanager.users.models import ReservationInquiry
from campsitemanager.users.forms import ReservationInquiryForm

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.staticfiles import finders
import qrcode
import os
from io import BytesIO

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
        if not request.user.is_authenticated:
            # Redirect to login page if the user is not authenticated
            return redirect(f"{reverse('account_login')}?next={request.path}")
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
                # num_beach_stay_adults=form.cleaned_data.get('num_beach_stay_adults', 0),
                # num_beach_stay_children=form.cleaned_data.get('num_beach_stay_children', 0),
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



def reservation_pdf_view(request, id):
    reservation = ReservationInquiry.objects.get(id=id, user=request.user)

    # Ścieżka do logo Kemping z folderu statycznego
    logo_path = finders.find('images/kemping_logo.png')

    # Przygotuj odpowiedź HTTP z odpowiednim typem treści
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reservation_{reservation.id}.pdf"'

    # Ścieżka do fontu DejaVu Sans obsługującego polskie znaki
    font_path = finders.find('fonts/DejaVuSans.ttf')

    # Sprawdzenie, czy plik fontu został znaleziony
    if font_path:
        # Rejestracja nowego fontu w reportlab
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        font_name = 'DejaVu'
    else:
        # Jeśli font nie zostanie znaleziony, użyj domyślnego fontu
        font_name = 'Helvetica'


    # Ustawienia dla formatu A4
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    p.setTitle(f"Reservation_{reservation.id}")
    
    # Dodaj logo Kemping, jeśli plik istnieje
    if logo_path:
        logo = ImageReader(logo_path)
        p.drawImage(logo, 40, height - 100, width=120, height=50, mask='auto')
    

    # Dodaj mały tekst pod logo
    p.setFont(font_name, 10)  # Ustawiamy mniejszy rozmiar czcionki
    p.drawString(40, height - 120, _("Wydrukuj tę stronę i okaż ją przy wjeździe na kemping"))

    # Dodaj nagłówek
    p.setFont(font_name, 16)
    p.drawString(40, height - 150, _("Reservation Details"))
    
    # Separator
    p.setStrokeColor(colors.grey)
    p.setLineWidth(1)
    p.line(40, height - 160, width - 40, height - 160)

    # Zmienne do trzymania pozycji tekstu
    y_position = height - 180
    line_spacing = 20

    # Stylizowane pola rezerwacji
    p.setFont(font_name, 12)
    
    def draw_field(label, value):
        nonlocal y_position
        p.drawString(40, y_position, f"{label}: {value}")
        y_position -= line_spacing
    
    # Wstawienie szczegółów rezerwacji
    draw_field(_("Full Name"), reservation.full_name)
    draw_field(_("Email"), reservation.email)
    draw_field(_("Phone Number"), reservation.phone_number)
    draw_field(_("Start Date"), reservation.start_date)
    draw_field(_("End Date"), reservation.end_date)
    draw_field(_("Number of Adults"), reservation.num_adults)
    draw_field(_("Number of Children (0-3 years)"), reservation.num_children_0_3)
    draw_field(_("Number of Children (4-13 years)"), reservation.num_children_4_13)
    draw_field(_("Number of Animals"), reservation.num_animals)

    # Dodanie dodatkowych pól
    draw_field(_("Tent Type"), reservation.get_tent_type_display() if reservation.tent_type else _("No tent required"))
    draw_field(_("Caravan Required"), _("Yes") if reservation.caravan_required else _("No"))
    draw_field(_("Electricity for Tent"), _("Yes") if reservation.electricity_for_tent else _("No"))
    draw_field(_("Electricity for Caravan"), _("Yes") if reservation.electricity_for_caravan else _("No"))
    draw_field(_("Extra Person Count"), reservation.extra_person_count)
    draw_field(_("Waste Disposal"), _("Yes") if reservation.waste_disposal else _("No"))
    draw_field(_("Parking Required"), _("Yes") if reservation.parking_required else _("No"))
    draw_field(_("Number of Adults at Beach"), reservation.num_beach_stay_adults)
    draw_field(_("Number of Children at Beach"), reservation.num_beach_stay_children)
    draw_field(_("Discount Applied"), _("Yes") if reservation.apply_discount else _("No"))
    
    # Separator
    y_position -= 10
    p.line(40, y_position, width - 40, y_position)
    y_position -= line_spacing
    
    # Statusy rezerwacji
    p.setFont(font_name, 14)
    draw_field(_("Reservation Status"), _("Confirmed") if reservation.is_confirmed else _("Pending"))
    draw_field(_("Cancellation Status"), _("Canceled") if reservation.is_canceled else _("Active"))

    # Tworzenie statycznego kodu QR
    qr_code_data = "https://example.com/your-static-url"  # Statyczna wartość QR
    qr = qrcode.make(qr_code_data)

    # Konwertuj kod QR do formatu obrazka
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)

    # Wstawienie kodu QR do PDF
    qr_image = ImageReader(qr_io)
    p.drawImage(qr_image, width - 200, 100, width=100, height=100)  # Rozmiar i pozycja kodu QR
    
    # Finalizacja PDF
    p.showPage()
    p.save()

    return response

