
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from  cafes.models import Cafe
from menu.models import Menu
from orders.models import Order
import csv
from io import TextIOWrapper
from utils.decorators import owner_or_superuser_required, owner_employee_or_admin_required
from django.db.models import  Sum,  Count

from django.core.paginator import Paginator
from django.utils.timezone import now, timedelta

from .utils import get_timeframe_parts, generate_sales_series, parse_date, generate_csv_response
from .report_builder import build_order_report


from django.utils.timezone import localtime



@owner_or_superuser_required
def dashboard(request,cafe , owner, slug):
    filter_type = request.GET.get('filter', 'daily')

    from_date, to_date, trunc, delta = get_timeframe_parts(filter_type)

    orders = Order.objects.filter(cafe=cafe, created_at__range=(from_date, to_date))
    print("FROM:", from_date)
    print("TO:", to_date)
    print("ORDERS:", orders.count())


    total_revenue = sum(order.total_amount for order in orders)
    estimated_profit = sum(order.estimated_profit for order in orders)
    avg_order = Order.get_average_order_value(orders)

    top_employee = (
        orders.values('created_by__name')
        .annotate(order_count=Count('id'))
        .order_by('-order_count')
        .first()
    )
    sales_over_time = generate_sales_series(orders, from_date, to_date, trunc, delta)   

    bestsellers = (
        orders.values('items__menu_item__name')
        .annotate(quantity_sold=Sum('items__quantity'))
        .order_by('-quantity_sold')[:5]
    )

    bestseller_chart = [
    {
        "item": item['items__menu_item__name'],
        "quantity": item['quantity_sold']
    }
    for item in bestsellers
    ]



    timeframes = ['daily', 'weekly', 'monthly', 'yearly']

    context = {
        "cafe": cafe,
        "owner": owner,
        "selected_filter": filter_type,
        "total_revenue": total_revenue,
        "total_orders": orders.count(),
        "avg_order": avg_order,
        "estimated_profit": estimated_profit,
        "recent_orders": orders.order_by('-created_at')[:5],
        "top_employee": top_employee,
        "timeframes": timeframes,
        "timeframes": ['daily', 'weekly', 'monthly', 'yearly'],
        "sales_over_time": sales_over_time,
         "bestseller_chart": bestseller_chart,
    }
    return render(request,'dashboard/owner/dashboard.html', context)




@owner_or_superuser_required
def view_orders(request,cafe , owner,  slug):
    # Get 30 days ago datetime
    thirty_days_ago = now() - timedelta(days=30)

    # Filter orders for this cafe in last 30 days, newest first
    order_qs = Order.objects.filter(
        cafe=cafe,
        created_at__gte=thirty_days_ago
    ).prefetch_related('items__menu_item', 'table').order_by('-created_at')

    # Pagination
    paginator = Paginator(order_qs, 10)  # 10 orders per page
    page_number = request.GET.get("page")
    orders_page = paginator.get_page(page_number)

    return render(request, 'dashboard/owner/view_order_history.html', {
        "cafe": cafe,
        "orders": orders_page
    })


@owner_or_superuser_required
def download_reports(request,cafe , owner,  slug):
    report_type = request.GET.get("report", "orders")
    filter_type = request.GET.get("filter", "daily")
    custom_from = parse_date(request.GET.get("from"))
    custom_to = parse_date(request.GET.get("to"))

    from_date, to_date, trunc, delta = get_timeframe_parts(filter_type, custom_from, custom_to)

    # Build the actual report
    if report_type == "orders":
        report_data = build_order_report(cafe, from_date, to_date)
    else:
        report_data = []

    # Download CSV
    if request.GET.get("download") == "1":
        return generate_csv_response(report_data, filename_prefix=f"{cafe.slug}_{report_type}")

    headers = list(report_data[0].keys()) if report_data else []
    report_preview = report_data[:10]



    context = {
        "cafe": cafe,
        "report": report_data,
        "report_preview": report_preview,
        "report_type": report_type,
        "headers": headers,
        "current_filter": filter_type,
        "current_report": report_type,
            "filter_options": [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("custom", "Custom Range"),
    ],
    }

    return render(request, 'dashboard/owner/report.html', context)

@owner_or_superuser_required
def upload_menu(request,cafe , owner,  slug):


    menu_items = Menu.objects.filter(cafe=cafe).order_by('category', 'name')
    # ✅ If user clicked "Download Current Menu"
    if request.method == "GET" and request.GET.get("download") == "1":

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{cafe.slug}_menu.csv"'

        writer = csv.writer(response)
        writer.writerow(['name', 'price', 'cost', 'category', 'description', 'is_veg'])

        for item in menu_items:
            writer.writerow([
                item.name,
                item.price,
                item.cost,
                item.category,
                item.description,
                'TRUE' if item.is_veg else 'FALSE'
            ])
        return response

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')

        if not csv_file:
            messages.error(request, "No file selected")
            return redirect('menu:edit_menu', slug=cafe.slug)
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect('dashboard:edit_menu', slug=cafe.slug)
        try:
            # Step 1: Read and parse the CSV file safely
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(file_data)

            # Step 2: Validate the headers before doing anything destructive
            required_columns = {'name', 'price', 'cost', 'category', 'description', 'is_veg'}
            if not reader.fieldnames or not required_columns.issubset(set(field.lower() for field in reader.fieldnames)):
                messages.error(request, "CSV must contain all columns: name, price, cost, category, description, is_veg")
                return redirect('dashboard:edit_menu', slug=cafe.slug)

            # Step 3: Collect all new menu items into a list (don't delete yet)
            new_items = []
            for row in reader:
                name = row.get('name', '').strip()
                price = row.get('price', '0').strip()
                cost = row.get('cost', '0').strip()
                category = row.get('category', '').strip().lower()
                description = row.get('description', '').strip()
                is_veg_raw = row.get('is_veg', 'true').strip().lower()

                is_veg = is_veg_raw in ['1', 'true', 'yes']

                if name and price:
                    new_items.append(Menu(
                        cafe=cafe,
                        name=name,
                        price=price,
                        cost=cost,
                        category=category,
                        description=description,
                        is_veg=is_veg
                    ))

                # Step 4: If there are valid items, then replace the existing menu
                if not new_items:
                    messages.error(request, "CSV is valid but contains no valid rows.")
                    return redirect('dashboard:edit_menu', slug=cafe.slug)

        # ✅ Only delete now — after validation passed
            Menu.objects.filter(cafe=cafe).delete()
            Menu.objects.bulk_create(new_items)

            messages.success(request, f"{len(new_items)} menu items uploaded and replaced successfully.")
            return redirect('dashboard:edit_menu', slug=cafe.slug)

        except Exception as e:
            messages.error(request, f"Something went wrong: {e}")
            return redirect('dashboard:edit_menu', slug=cafe.slug)

    return render(request, "dashboard/owner/update_menu.html", {"menu_items": menu_items, "cafe": cafe})



@owner_employee_or_admin_required
def employee(request,cafe , user,  slug):
    cafe = get_object_or_404(Cafe, slug=cafe.slug)
    


    orders = Order.objects.filter(
        cafe=cafe,
        status__in=['active', 'served']
    ).prefetch_related('items__menu_item', 'table')  # optional optimization

    context  = {
        "cafe": cafe,
        "orders" : orders,
    }
    return render(request,'dashboard/employee/employee_dashboard.html', context)

@owner_employee_or_admin_required
def mark_order_served(request, order_id, slug,cafe, owner):
    try:

        order = Order.objects.get(id=order_id, cafe=cafe, status='active')
        order.status = 'served'
        order.save()
        return JsonResponse({'success': True})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)


@owner_employee_or_admin_required
def kot_data(request,slug, cafe, owner):

    orders = Order.objects.filter(cafe=cafe, status='active').prefetch_related('items__menu_item', 'customer').order_by('-created_at')
    data = {
        "orders": [
            {
                "id": o.id,
                "order_code": o.order_code.split('-')[-1],
                "created_at": o.created_at.strftime('%Y-%m-%d %H:%M'),
                "items": [{"name": i.menu_item.name, "qty": i.quantity} for i in o.items.all()],
                "customer_name": o.customer.name,
                "total": float(o.total_amount)
            } for o in orders
        ]
    }
    return JsonResponse(data)

@owner_employee_or_admin_required
def kot(request,cafe , user,  slug):

    orders = Order.objects.filter(
        cafe=cafe,
        status='active'
    ).select_related(
        'table'
    ).prefetch_related(
        'items__menu_item'
    ).order_by('-created_at')
    
    context= {
        'orders' : orders,
        'cafe' : cafe
    }




    return render(request,'dashboard/employee/kot.html', context)

from django.db.models import Q

@owner_employee_or_admin_required
def employee_live_orders(request, slug, cafe, user):

    orders = Order.objects.filter(
        cafe=cafe,  
        status__in=['active', 'served'] ).select_related('table').prefetch_related('items__menu_item', 'customer').order_by('-created_at')

    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'table': order.table.table_number if order.table.table_number else "N/A",
            'time': localtime(order.created_at).strftime("%I:%M %p"),
            'total': round(order.total_amount),
            'order_code' :  str(order.order_code).split('-')[-1],
            'total_amount': order.total_amount,
            'items': [
                {'name': i.menu_item.name, 'qty': i.quantity}
                for i in order.items.all()
            ]
        })

    return JsonResponse({'orders': data})



@owner_employee_or_admin_required
def cancel_order(request, order_id, cafe, user, slug):
    order = get_object_or_404(Order, id=order_id, cafe=cafe)

    # Optional: only allow cancel if active
    if order.status not in ['active', 'served']:
        
        return JsonResponse({'success': False, 'error': 'Cannot cancel this order.'}, status=400)

    order.cancel_order()
    print('cancelled')
    return JsonResponse({'success': True})


@owner_employee_or_admin_required
def close_order(request, order_id, cafe, user, slug):

    order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id, cafe=cafe)

    if request.method == 'POST':

        print('posting')
        order = get_object_or_404(Order, id=order_id, cafe=cafe)
        payment_method = request.POST.get('payment')
        order.status = 'completed'
        order.payment_mode = payment_method
        order.save()

       
        return redirect('dashboard:employee_dashboard', slug = cafe.slug)

    
        
        
    context = {'cafe' : cafe,
               'order' : order,
               'order_code': str(order.order_code).split('-')[-1]
               }
    return render(request, 'orders/close_order.html', context)

