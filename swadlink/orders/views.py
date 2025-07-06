from django.shortcuts import render

def get_customer_details(request, slug):
    return render(request,'orders/get_customer_details.html')


def select_items(request, slug):
    return render(request,'orders/select_items.html')

def summmary(request, slug):
    return render(request,'orders/summary.html')



def update_items(request, slug):
    return render(request,'orders/summary.html')