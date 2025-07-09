import random
import time
import re
from datetime import timedelta, time as time_obj, datetime as dt

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, localtime
from django.db.utils import IntegrityError
from pytz import timezone as pytz_timezone

from orders.models import Order, Table
from cafes.models import Cafe
from accounts.models import CustomUser
from customer.models import GlobalCustomerDB



def generate_order_code(cafe, created_at):
    IST = pytz_timezone('Asia/Kolkata')
    created_local = localtime(created_at, timezone=IST)

    # Adjust the date to reflect the 4 AM café day start
    if created_local.time() < time_obj(4, 0):
        cafe_day = (created_local - timedelta(days=1)).date()
    else:
        cafe_day = created_local.date()

    day_str = cafe_day.strftime('%Y-%m-%d')
    cafe_slug = cafe.slug.upper()
    prefix = f"{cafe_slug}-{day_str}"

    # 4 AM to 4 AM next day
    start_of_day = make_aware(dt.combine(cafe_day, time_obj(4, 0)), IST)
    end_of_day = start_of_day + timedelta(days=1)

    order_codes = Order.objects.filter(
        cafe=cafe,
        created_at__range=(start_of_day, end_of_day),
        order_code__startswith=prefix
    ).values_list('order_code', flat=True)

    max_number = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")

    for code in order_codes:
        match = pattern.match(code)
        if match:
            num = int(match.group(1))
            if num > max_number:
                max_number = num

    next_number = max_number + 1
    return f"{prefix}-{next_number:03d}-{random.randint(100, 999)}"


class Command(BaseCommand):
    help = "Generate fake SwadLink orders for testing across a year"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=365)
        parser.add_argument('--orders-per-day', type=int, default=20)

    def handle(self, *args, **kwargs):
        days = kwargs['days']
        orders_per_day = kwargs['orders_per_day']

        cafes = list(Cafe.objects.all())
        customers = list(GlobalCustomerDB.objects.all())
        users = list(CustomUser.objects.all())
        tables = list(Table.objects.all())

        if not cafes or not customers or not users:
            self.stdout.write(self.style.ERROR("Missing cafés, customers, or users."))
            return

        total = 0
        for day_offset in range(days):
            for _ in range(orders_per_day):
                created_at = make_aware(dt.now() - timedelta(days=day_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59)))

                cafe = random.choice(cafes)
                customer = random.choice(customers)
                created_by = random.choice(users)
                table = random.choice(tables) if tables else None
                MAX_TRIES = 5
                for attempt in range(MAX_TRIES):
                    try:
                        order = Order(
                            cafe=cafe,
                            customer=customer,
                            created_by=created_by,
                            status=random.choice(['active', 'completed', 'served']),
                            table=table,
                            created_at=created_at
                        )
                        order.order_code = generate_order_code(cafe, created_at)
                        order.save()
                        break  # ✅ success
                    except IntegrityError as e:
                        if "order_code" in str(e):
                            time.sleep(random.uniform(0.01, 0.08))  # ✅ backoff before retry
                        else:
                            raise
                else:
                    self.stdout.write(self.style.WARNING("⚠️ Could not generate unique order_code after retries."))

