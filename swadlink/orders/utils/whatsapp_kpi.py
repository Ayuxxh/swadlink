# orders/utils/kpi.py

from decimal import Decimal
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from orders.models import Order
from cafes.models import Cafe
from dashboard.utils import get_timeframe_parts
import requests

def get_kpi_for_cafe(cafe, filter_type='daily'):
    from_date, to_date, trunc, delta = get_timeframe_parts(filter_type)

    orders = Order.objects.filter(cafe=cafe, created_at__range=(from_date, to_date)).prefetch_related('items__menu_item')

    orders = orders.annotate(
        order_total=Sum(
            ExpressionWrapper(
                F('items__quantity') * F('items__menu_item__price'),
                output_field=DecimalField()
            )
        )
    )

    total_revenue = orders.aggregate(total=Sum('order_total'))['total'] or Decimal('0.00')
    upi_revenue = orders.filter(payment_mode='UPI').aggregate(total=Sum('order_total'))['total'] or Decimal('0.00')
    cash_revenue = orders.filter(payment_mode='CASH').aggregate(total=Sum('order_total'))['total'] or Decimal('0.00')

    estimated_profit = sum(order.estimated_profit for order in orders if hasattr(order, 'estimated_profit'))
    avg_order = Order.get_average_order_value(orders) if hasattr(Order, 'get_average_order_value') else 0

    active_served_count = orders.filter(status='completed').count()

    top_item_data = (
        orders.values('items__menu_item__name')
        .annotate(total_quantity=Sum('items__quantity'))
        .order_by('-total_quantity')
        .first()
    )

    return {
        'revenue': str(total_revenue),
        'upi_total': str(upi_revenue),
        'cash_total': str(cash_revenue),
        'estimated_profit': str(estimated_profit),
        'avg_order_value': str(avg_order),
        'total_orders': active_served_count,
        'top_item':  top_item_data['items__menu_item__name'] if top_item_data else 'N/A',
        "cafe_name": cafe.name,


        "dashboard_link": f"https://Qrahi.com/{cafe.slug}/dashboard",

        

    }





def send_kpi_nightly(phone, kpi):
    url = "https://api.gupshup.io/wa/api/v1/msg"
    print("messsage sending success")
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": "olzjtvucwkmmo5roxs7vk6zhiphfbx84",
    }


    print(kpi['cafe_name'])


    message = f"""Hi, Owner! 🌙  
Here’s your daily report for *{ kpi['cafe_name'] }* 🧾

📊 Total Revenue: ₹{ kpi['revenue'] }  
📦 Total Orders: { kpi['total_orders'] }  
💰 Avg Order Value: ₹{ kpi['avg_order_value'] }  

💳 UPI: ₹{ kpi['upi_total'] }  
💵 Cash: ₹{ kpi['cash_total']  }  

🔥 Top Item: { kpi['top_item'] } 

💸 Estimated Profit Today: ₹{ kpi['estimated_profit'] }  

🔍 See more at: { kpi['dashboard_link']}

Powered by *Qrahi* – Where every order tells a story."""
    

    data = {
        "channel": "whatsapp",
        "source": "917834811114",
        "destination": f"91{phone}",  # replace with cafe owner's number
        "message": f'{message}',
        "src.name": "Swadlink"
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.status_code, response.text)

# send_kpi_nightly()



def send_bill(order):
    url = "https://api.gupshup.io/wa/api/v1/msg"

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": "olzjtvucwkmmo5roxs7vk6zhiphfbx84",
    }


    message = f' Hi, { order.customer.name }, here is your bill, {order.total_amount}'

    print('hi')

#     message = f"""Hi, Owner! 🌙  
# Here’s your daily report for *{ details['cafe_name'] }* 🧾

# 📊 Total Revenue: ₹{ details['revenue'] }  
# 📦 Total Orders: { details['total_orders'] }  
# 💰 Avg Order Value: ₹{ details['avg_order_value'] }  

# 💳 UPI: ₹{ details['upi_total'] }  
# 💵 Cash: ₹{ details['cash_total']  }  

# 🔥 Top Item: { details['top_item'] } 

# 💸 Estimated Profit Today: ₹{ details['estimated_profit'] }  

# 🔍 See more at: { details['dashboard_link']}

# Powered by *Qrahi* – Where every order tells a story."""
    

    data = {
        "channel": "whatsapp",
        "source": "917834811114",
        "destination": f"917219063932",  # replace with cafe owner's number
        "message": f'{message}',
        "src.name": "Swadlink"
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.status_code, response.text)