import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from kempingdabrowno.users.models import User, ReservationInquiry

class Command(BaseCommand):
    help = 'Add test data to ReservationInquiry model with associated users'

    def handle(self, *args, **kwargs):
        # Names and emails for users
        full_names = [
            'Jan Kowalski', 'Anna Nowak', 'Michał Wiśniewski', 
            'Katarzyna Zielińska', 'Piotr Kamiński', 'Agnieszka Dąbrowska'
        ]
        emails = [
            'jkowalski@example.com', 'anowak@example.com', 'mwisniewski@example.com', 
            'kzielinska@example.com', 'pkaminski@example.com', 'adabrowska@example.com'
        ]
        phone_numbers = ['600111222', '600222333', '600333444', '600444555', '600555666', '600666777']

        # Create User instances
        users = []
        for full_name, email in zip(full_names, emails):
            # Split the full name into first and last if necessary
            # Adjust this logic if your custom User model has different fields
            user, created = User.objects.get_or_create(
                email=email,  # Ensure the field names match your User model
                defaults={'username': email}  # Add any required fields here, like 'username'
            )
            users.append(user)

        # Helper function to get a date closer to the weekend
        def get_weekend_start_date():
            # Start date biased towards the weekend (Fri, Sat, Sun)
            today = timezone.now().date()
            random_days = random.randint(0, 30)  # Random date in the next 30 days
            future_date = today + timedelta(days=random_days)
            day_of_week = future_date.weekday()  # Monday = 0, Sunday = 6

            # Adjust to move towards Friday (4), Saturday (5), or Sunday (6)
            if day_of_week < 4:  # Move closer to the weekend
                future_date += timedelta(days=(4 - day_of_week))
            return future_date

        # Generate 200 test reservations with more reservations on weekends
        for i in range(200):
            full_name = random.choice(full_names)
            email = random.choice(emails)
            phone_number = random.choice(phone_numbers)

            # Associate the reservation with a random user
            user = random.choice(users)

            # 70% chance of starting the reservation on a weekend
            if random.random() < 0.7:
                start_date = get_weekend_start_date()
            else:
                start_date = timezone.now().date() + timedelta(days=random.randint(0, 30))

            # Length of stay between 1 and 10 days
            length_of_stay = random.randint(1, 10)
            end_date = start_date + timedelta(days=length_of_stay)

            # Variable information
            num_adults = random.randint(1, 4)
            num_children_0_3 = random.randint(0, 2)
            num_children_4_13 = random.randint(0, 3)
            num_animals = random.randint(0, 2)

            tent_type = random.choice(['2p', '3-4p', '5-6p', None])
            caravan_required = random.choice([True, False])

            # Optional services with more variability
            electricity_for_tent = random.choice([True, False]) if tent_type else False
            electricity_for_caravan = caravan_required and random.choice([True, False])
            extra_person_count = random.randint(0, 2) if random.random() < 0.3 else 0  # More variability here
            waste_disposal = random.choice([True, False])
            parking_required = random.choice([True, False])

            num_beach_stay_adults = random.randint(0, num_adults)
            num_beach_stay_children = random.randint(0, num_children_0_3 + num_children_4_13)

            # Apply discount based on length of stay and randomness
            apply_discount = length_of_stay > 5 and random.choice([True, False])
            is_confirmed = random.choice([True, False])
            is_canceled = not is_confirmed and random.choice([True, False])

            # Create and save the reservation inquiry
            reservation = ReservationInquiry(
                user=user,
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

        self.stdout.write(self.style.SUCCESS('Successfully added 200 test reservations with associated users to ReservationInquiry model'))
