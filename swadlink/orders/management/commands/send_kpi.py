# send_kpi_reports.py
from cafes.models import Cafe
from orders.utils.whatsapp_kpi import get_kpi_for_cafe, send_kpi_nightly

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send nightly KPI reports via WhatsApp"

    def handle(self, *args, **kwargs):
        cafes = Cafe.objects.all()
        for cafe in cafes:
            kpi = get_kpi_for_cafe(cafe, filter_type='daily')
            # message = self.format_message(cafe, kpi)
            send_kpi_nightly(cafe.phone, kpi)

    def format_message(self, cafe, kpi):
        return (
            f"*{cafe.name}* - Daily Report 📊\n"
            f"Revenue: ₹{kpi['total_revenue']}\n"
            f"Orders: {kpi['order_count']}\n"
            f"Avg Order: ₹{kpi['avg_order_value']}\n"
            f"UPI: ₹{kpi['upi']} | Cash: ₹{kpi['cash']}\n"
            f"Top Staff: {kpi['top_employee']}\n"
            f"Est. Profit: ₹{kpi['estimated_profit']}\n"
            f"_SwadLink – Grow with insights._"
        )
