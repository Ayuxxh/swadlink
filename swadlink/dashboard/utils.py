from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import timezone as dt_timezone
from django.db.models import Sum
from pytz import timezone as pytz_timezone

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def get_timeframe_parts(filter_type, custom_from=None, custom_to=None):


    IST = pytz_timezone('Asia/Kolkata')

    now = timezone.now()  # stays in UTC



    if filter_type == 'custom' and custom_from and custom_to:
        from_date = timezone.make_aware(datetime.combine(custom_from, datetime.min.time()), IST)
        to_date = timezone.make_aware(datetime.combine(custom_to, datetime.max.time()), IST)
        trunc = TruncDay('created_at')
        delta = timedelta(days=1)

    elif filter_type == 'daily':
        from_date = now - timedelta(days=1)
        to_date = now
        trunc = TruncHour('created_at')
        delta = timedelta(hours=1)
    elif filter_type == 'weekly':
        from_date = now - timedelta(days=7)
        to_date = now
        trunc = TruncDay('created_at')
        delta = timedelta(days=1)
    elif filter_type == 'monthly':
        from_date = now - timedelta(days=30)
        to_date = now
        trunc = TruncDay('created_at')
        delta = timedelta(days=1)
    elif filter_type == 'yearly':
        from_date = now - timedelta(days=365)
        to_date = now
        trunc = TruncMonth('created_at')
        delta = 'monthly'
    else:
        from_date = now - timedelta(days=1)
        to_date = now
        trunc = TruncHour('created_at')
        delta = timedelta(hours=1)

    return from_date.astimezone(dt_timezone.utc), to_date.astimezone(dt_timezone.utc), trunc, delta

def generate_sales_series(orders, from_date, to_date, trunc, delta):
    # 1. Raw data grouped by period (datetime)
    raw_sales = (
        orders.annotate(period=trunc)
        .values('period')
        .annotate(total=Sum('items__menu_item__price'))
        .order_by('period')
    )

    # 2. Convert to dict with string keys
    period_totals = {
        entry['period'].strftime('%Y-%m-%dT%H:00:00' if delta == timedelta(hours=1)
                                 else '%Y-%m-%d' if delta != 'monthly'
                                 else '%Y-%m'): 
        float(entry['total']) if entry['total'] else 0
        for entry in raw_sales
    }

    # 3. Build complete time series
    sales_over_time = []
    cursor = from_date

    while cursor <= to_date:
        if delta == timedelta(hours=1):
            rounded = cursor.replace(minute=0, second=0, microsecond=0)
            key = rounded.strftime('%Y-%m-%dT%H:00:00')
        elif delta == timedelta(days=1):
            rounded = cursor.date()
            key = rounded.strftime('%Y-%m-%d')
        elif delta == 'monthly':
            rounded = cursor.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            key = rounded.strftime('%Y-%m')
        else:
            key = ''

        sales_over_time.append({
            "period": key,
            "total": period_totals.get(key, 0)
        })

        # Increment time
        if delta == 'monthly':
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1)
        else:
            cursor += delta

    return sales_over_time



from django.http import HttpResponse
import csv

def generate_csv_response(report_data, filename_prefix):
    if not report_data:
        return HttpResponse("No data available to download", content_type="text/plain")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_report.csv"'

    writer = csv.writer(response)
    
    headers = list(report_data[0].keys())
    writer.writerow(headers)

    for row in report_data:
        writer.writerow([row.get(h, '') for h in headers])

    return response









