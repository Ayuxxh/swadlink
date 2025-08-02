from customer.models import GlobalCustomerDB, CafeCustomerDB
from .models import Order, Table, OrderItem
from cafes.models import Cafe
from accounts.models import  CustomUser 
from menu.models import Menu
import json
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

def get_customer_details(request, slug):

    cafe = get_object_or_404(Cafe, slug=slug)
    tables = Table.objects.filter(cafe=cafe, is_active=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        table_number = request.POST.get('table')
        instructions = request.POST.get('instructions')



        # Step 1: Create or update Global Customer
        global_customer, created = GlobalCustomerDB.objects.get_or_create(
            phone=phone,
        )
        if not created:
            global_customer.name = name
            global_customer.visit_count += 1
            global_customer.last_visit = timezone.now()
            global_customer.save()
        else:
            global_customer.update_visit(amount_spent=0)  # default, update later if needed

        # Step 2: Create CafeCustomerDB if doesn't exist
        CafeCustomerDB.objects.get_or_create(
            phone=phone,
            cafe=cafe
        )

        # Step 3: Table selection
        table = get_object_or_404(Table, table_number=table_number, cafe=cafe)


        request.session['customer_info'] = {
            'name': name,
            'phone': phone,
            'table': table_number,
            'instructions': instructions,
        }



        print(request.session['customer_info'])
        

        return redirect('orders:create_order.select_items', slug=cafe.slug)

    return render(request, 'orders/get_customer_details.html', {
        'tables': tables,
        "cafe" : cafe
    })

def select_items(request, slug):    
    cafe = get_object_or_404(Cafe, slug=slug)
    menu_items = Menu.objects.filter(cafe=cafe)

    customer_info = request.session.get("customer_info")
    print(customer_info, 1)
    if not customer_info:
        return redirect('orders:create_order.get_customer_details', slug=slug)
    
    request.session['customer_info'] = customer_info


    return render(request, 'orders/select_items.html', {
        'menu_items': menu_items,
        'cafe': cafe,
        "customer": customer_info
    })



def summmary(request, slug):
    if request.method == "POST":
        cafe = get_object_or_404(Cafe, slug=slug)

        cart_data_json = request.POST.get("cart_data")

        try:
            cart = json.loads(cart_data_json)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        customer_data = request.session['customer_info'] 

        # Extract customer info
        name = customer_data.get("name")
        phone = customer_data.get("phone")
        table_number = customer_data.get("table")

        print([name, phone, table_number])


        if not all([name, phone, table_number]):
            return JsonResponse({"error": "Incomplete customer data"}, status=400)

        # Get or create customer
        global_customer, created = GlobalCustomerDB.objects.get_or_create(
            phone=phone, defaults={"name": name}
        )
        if not created:
            global_customer.name = name
            global_customer.save()

        # Link to this cafe if needed
        CafeCustomerDB.objects.get_or_create(cafe=cafe, phone=phone)



        # Get table
        table = get_object_or_404(Table, cafe=cafe,  table_number=table_number)

        # Create Order
        order = Order.objects.create(
            cafe=cafe,
            customer=global_customer,
            table=table,
            created_by=request.user if request.user.is_authenticated else None,
        )



        # Add Items
        for key, quantity in cart.items():
            try:
                menu_item = Menu.objects.get(id=key)
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            except Menu.DoesNotExist:
                continue


        cart_summary = []
        for menu_id, quantity in cart.items():
            try:
                menu_item = Menu.objects.get(id=menu_id)
                cart_summary.append({
                    "name": menu_item.name,
                    "price": float(menu_item.price),
                    "qty": quantity,
                    "subtotal": float(menu_item.price) * quantity,
                })
            except Menu.DoesNotExist:
                continue

        return render(request, "orders/summary.html",  {
            "cart": cart_summary,
            "customer": name,
            "cafe": cafe,
        })

    return JsonResponse({"error": "Invalid request fallback"}, status=400)



def print_bill(request, order_id, slug):

    cafe = get_object_or_404(Cafe, slug=slug)
    order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id, cafe=cafe)
    order_code =  str(order.order_code).split('-')[-1]
    return render(request, 'orders/bill.html', {'order': order, 'cafe' : cafe, 'order_code': order_code})
