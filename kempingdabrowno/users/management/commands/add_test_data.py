import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from kempingdabrowno.users.models import ReservationInquiry

class Command(BaseCommand):
    help = 'Add test data to ReservationInquiry model'

    def handle(self, *args, **kwargs):
        # Basic data for the reservations
        full_names = ['John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Brown', 'Emma Davis', 'Michael Miller']
        emails = ['johndoe@example.com', 'janesmith@example.com', 'alicej@example.com', 'bobb@example.com', 'emmad@example.com', 'michaelm@example.com']
        phone_numbers = ['123456789', '987654321', '456789123', '321654987', '654321987', '789123456']

        # Generate 200 test reservations
        for i in range(200):
            full_name = random.choice(full_names)
            email = random.choice(emails)
            phone_number = random.choice(phone_numbers)

            # Start date is within the next 30 days
            start_date = timezone.now().date() + timedelta(days=random.randint(0, 30))
            # Length of stay between 1 and 10 days
            length_of_stay = random.randint(1, 10)
            end_date = start_date + timedelta(days=length_of_stay)

            num_adults = random.randint(1, 4)
            num_children_0_3 = random.randint(0, 2)
            num_children_4_13 = random.randint(0, 3)
            num_animals = random.randint(0, 2)

            tent_type = random.choice(['2p', '3-4p', '5-6p', None])
            caravan_required = random.choice([True, False])

            electricity_for_tent = random.choice([True, False])
            electricity_for_caravan = caravan_required and random.choice([True, False])
            extra_person_count = random.randint(0, 2)
            waste_disposal = random.choice([True, False])
            parking_required = random.choice([True, False])

            num_beach_stay_adults = random.randint(0, num_adults)
            num_beach_stay_children = random.randint(0, num_children_0_3 + num_children_4_13)

            apply_discount = random.choice([True, False])
            is_confirmed = random.choice([True, False])
            is_canceled = not is_confirmed and random.choice([True, False])

            # Create and save the reservation inquiry
            reservation = ReservationInquiry(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                start_date=start_date,
                end_date=end_date,
                num_adults=num_adults,
                num_children_0_3=num_children_0_3,
                num_children_4_13=num_children_4_13,
                num_animals=num_animals,
                tent_type=tent_type,
                caravan_required=caravan_required,
                electricity_for_tent=electricity_for_tent,
                electricity_for_caravan=electricity_for_caravan,
                extra_person_count=extra_person_count,
                waste_disposal=waste_disposal,
                parking_required=parking_required,
                num_beach_stay_adults=num_beach_stay_adults,
                num_beach_stay_children=num_beach_stay_children,
                apply_discount=apply_discount,
                is_confirmed=is_confirmed,
                is_canceled=is_canceled,
            )
            reservation.save()

        self.stdout.write(self.style.SUCCESS('Successfully added 200 test reservations to ReservationInquiry model'))