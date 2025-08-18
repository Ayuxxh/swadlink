from orders.models import Order

def build_order_report(cafe, from_date, to_date):
    orders = Order.objects.filter(
        cafe=cafe,
        created_at__range=(from_date, to_date)
    ).prefetch_related("items__menu_item", "table", "customer")

    report_data = []
    for order in orders:
        item_summary = ", ".join(
            f"{item.menu_item.name} x{item.quantity}"
            for item in order.items.all()
        )
        report_data.append({
            "order_id": order.order_code,
            "customer": order.customer.name,
            "table": order.table.table_number if order.table else "—",
            "status": order.status.title(),
            "created": order.created_at,
            "amount": float(order.total_amount_pre_calculated),
            "items": item_summary
        })

    return report_data
