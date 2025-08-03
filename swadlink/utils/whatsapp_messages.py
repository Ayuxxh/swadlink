import requests

def send_kpi_nightly(cafe, total_revenue, total_orders, avg_order_value, upi, cash, top_item, cafe_slug, estimated_profit):
    url = "https://api.gupshup.io/wa/api/v1/msg"
    
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": "olzjtvucwkmmo5roxs7vk6zhiphfbx84",
    }

    cafe_data = {
        "cafe_name": "Chai Junction",
        "revenue": "₹6,420",
        "total_orders": "48",
        "avg_order_value": "₹133.75",
        "upi_total": "₹4,250",
        "cash_total": "₹2,170",
        "top_item": "Masala Chai",
        "dashboard_link": "https://swad.link/chai-junction/stats",
        "estimated_profit" : 'est'
    }

    message = f"""Hi, Owner! 🌙  
Here’s your daily report for *{{ cafe_name }}* 🧾

📊 Total Revenue: ₹{{ total_revenue }}  
📦 Total Orders: {{ total_orders }}  
💰 Avg Order Value: ₹{{ avg_order_value }}  

💳 UPI: ₹{{ upi_total }}  
💵 Cash: ₹{{ cash_total }}  

🔥 Top Item: {{ top_item }}  

💸 Estimated Profit Today: ₹{{ estimated_profit }}  

🔍 See more at: {{ cafe_dashboard_link }}

Powered by **Qrunch** – Where every order tells a story."""

    data = {
        "channel": "whatsapp",
        "source": "917834811114",
        "destination": "917219063932",  # replace with cafe owner's number
        "message": f'{message}',
        "src.name": "Swadlink"
    }

    response = requests.post(url, headers=headers, data=data)
    print(response.status_code, response.text)

send_kpi_nightly()
