from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models  # Ensure this line is at the top of your file
from kempingdabrowno.users.managers import UserManager

class User(AbstractUser):
    """
    Default custom user model for KempingDabrowno.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class ReservationInquiry(models.Model):
    # Basic information
    full_name = models.CharField(max_length=255, verbose_name=_("Imię i nazwisko"))
    email = models.EmailField(verbose_name=_("Email"))
    phone_number = models.CharField(max_length=15, verbose_name=_("Numer telefonu"))

    # Reservation details
    start_date = models.DateField(verbose_name=_("Data rozpoczęcia"))
    end_date = models.DateField(verbose_name=_("Data zakończenia"))

    # Guests
    num_adults = models.PositiveIntegerField(verbose_name=_("Liczba dorosłych"))
    num_children_0_3 = models.PositiveIntegerField(default=0, verbose_name=_("Liczba dzieci (0-3 lata)"))
    num_children_4_13 = models.PositiveIntegerField(default=0, verbose_name=_("Liczba dzieci (4-13 lat)"))
    num_animals = models.PositiveIntegerField(default=0, verbose_name=_("Liczba zwierząt"))

    # Accommodation
    TENT_CHOICES = [
        ('2p', _('Namiot 2-osobowy')),
        ('3-4p', _('Namiot 3-4 osobowy')),
        ('5-6p', _('Namiot 5-6 osobowy')),
    ]
    tent_type = models.CharField(max_length=5, choices=TENT_CHOICES, blank=True, null=True, verbose_name=_("Rodzaj namiotu"))

    caravan_required = models.BooleanField(default=False, verbose_name=_("Czy wymagana przyczepa/kamper"))

    # Additional options
    electricity_for_tent = models.BooleanField(default=False, verbose_name=_("Prąd i sanitariaty dla namiotu"))
    electricity_for_caravan = models.BooleanField(default=False, verbose_name=_("Prąd i sanitariaty dla przyczepy/kampera"))
    extra_person_count = models.PositiveIntegerField(default=0, verbose_name=_("Liczba dodatkowych osób"))
    waste_disposal = models.BooleanField(default=False, verbose_name=_("Wywóz odpadów"))
    parking_required = models.BooleanField(default=False, verbose_name=_("Parking wymagany"))

    # Beach stay
    num_beach_stay_adults = models.PositiveIntegerField(default=0, verbose_name=_("Liczba dorosłych na plaży"))
    num_beach_stay_children = models.PositiveIntegerField(default=0, verbose_name=_("Liczba dzieci na plaży"))

    # Discount for longer stay
    apply_discount = models.BooleanField(default=False, verbose_name=_("Zastosuj zniżkę za pobyt powyżej 5 dni"))

    # Inquiry creation timestamp
    inquiry_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Data zapytania"))

    # Status fields
    is_confirmed = models.BooleanField(default=False, help_text=_("Czy pobyt został potwierdzony przez camping?"), verbose_name=_("Potwierdzone"))
    is_canceled = models.BooleanField(default=False, help_text=_("Czy rezerwacja została anulowana przez użytkownika?"), verbose_name=_("Anulowane"))

    # Method to calculate the length of stay
    @property
    def length_of_stay(self):
        return (self.end_date - self.start_date).days

    def __str__(self):
        return f"{self.full_name} - {self.start_date} to {self.end_date}"

    # Example method to calculate the total cost (optional and customizable)
    def calculate_total_cost(self):
        # Placeholder: You would implement the logic to calculate total cost based on options selected.
        pass
        
    class Meta:
        verbose_name = _("Rezerwacja")
        verbose_name_plural = _("Rezerwacje")