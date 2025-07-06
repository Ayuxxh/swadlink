
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from  cafes.models import Cafe
from menu.models import Menu
import csv
from io import TextIOWrapper
from utils.decorators import owner_or_superuser_required


@owner_or_superuser_required
def dashboard(request,cafe , owner, slug):

    return render(request,'dashboard/owner/dashboard.html', {"cafe": cafe, "owner":owner})

@owner_or_superuser_required
def view_orders(request,cafe , owner,  slug):

    return render(request,'dashboard/owner/view_order_history.html', {"cafe": cafe})



@owner_or_superuser_required
def download_reports(request,cafe , owner,  slug):

    return render(request,'dashboard/owner/report.html', {"cafe": cafe})

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



@owner_or_superuser_required
def employee(request,cafe , owner,  slug):
    return render(request,'dashboard/employee/employee_dashboard.html',{ "cafe": cafe})

@owner_or_superuser_required
def kot(request,cafe , owner,  slug):
    return render(request,'dashboard/employee/kot.html', { "cafe": cafe})
