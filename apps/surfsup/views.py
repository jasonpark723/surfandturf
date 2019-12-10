from __future__ import unicode_literals
import stripe
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from .models import Product, OrderItem, Order, Category, User, PromoCode, ShippingAddress
import bcrypt
from .forms import CheckoutForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta, date


stripe.api_key = settings.STRIPE_SECRET_KEY


def landing(request):
    if 'uid' not in request.session:
        guest = User.objects.create(first_name="guest", last_name="guest",
                                    email="guest@mail.com", password_hash='guest')
        request.session['uid'] = guest.id
    context = {
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, 'surfsup/index.html', context)


def home(request):
    if not Order.objects.filter(user=User.objects.get(
            id=request.session['uid']), ordered=False):
        Order.objects.create(user=User.objects.get(
            id=request.session['uid']))
    current_order = Order.objects.filter(user=User.objects.get(
        id=request.session['uid']), ordered=False)[0]

    # Pagination
    all_products = Product.objects.all()
    # paginator = Paginator(all_products, 4)
    # page = request.GET.get('page')
    # try:
    #     items = paginator.page(page)
    # except PageNotAnInteger:
    #     items = paginator.page(1)
    # except EmptyPage:
    #     items = paginator.page(paginator.num_pages)

    # index = items.number - 1
    # max_index = len(paginator.page_range)
    # start_index = index - 5 if index >= 5 else 0
    # end_index = index + 5 if index <= max_index - 5 else max_index
    # page_range = paginator.page_range[start_index:end_index]
    # ?page=2

    context = {
        'products': all_products[:4],
        # 'items': items,
        "current_order": current_order,
        'user': User.objects.get(id=request.session['uid'])
        # 'page_range': page_range,
    }
    return render(request, 'surfsup/home-page.html', context)


def signin(request):
    # display login page
    context = {
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, 'surfsup/login-page.html', context)


def signup(request):
    # display registration form
    context = {
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, 'surfsup/registration.html', context)


def register(request):
    # handle registration
    if request.method == "POST":
        # validations
        errors = User.objects.registration_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags="signup")
            return redirect('/signup')

        # if no errors
        new_user = User.objects.register(request.POST)
        if 'uid' not in request.session:
            request.session['uid'] = new_user.id
        messages.success(request, "successfully logged in")
        return redirect('/home')


def login_post(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email'])
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password_hash.encode()):
                request.session['uid'] = logged_user.id
                messages.success(request, "successfully logged in")
                return redirect('/home')
        messages.error(request, "Invalid credentials. Please try again")
    return redirect('/signin')


def signout(request):
    del request.session['uid']
    messages.success(request, "where u going?")
    return redirect('/')


def show_all_products(request):
    current_order = Order.objects.filter(user=User.objects.get(
        id=request.session['uid']), ordered=False)[0]
    context = {
        'products': Product.objects.all(),
        'current_order': current_order,
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, "surfsup/all_products.html", context)


def show_product(request, product_id):
    current_order = Order.objects.filter(user=User.objects.get(
        id=request.session['uid']), ordered=False)[0]
    top5 = Order.objects.popular_items()
    print(top5)
    best1 = Product.objects.get(id=top5[0][0])
    best2 = Product.objects.get(id=top5[1][0])
    best3 = Product.objects.get(id=top5[2][0])
    context = {
        'product': Product.objects.filter(id=product_id).first(),
        'current_order': current_order,
        'user': User.objects.get(id=request.session['uid']),
        'best1': best1,
        'best2': best2,
        'best3': best3,
    }
    return render(request, 'surfsup/product-page.html', context)


def show_category(request, category):
    products_in_category = Category.objects.filter(
        name=category)[0].products.all()
    context = {
        'category': category,
        'products_in_category': products_in_category[:4],
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, "surfsup/category.html", context)


def product_search(request):
    print(request.POST)
    filtered_products = Product.objects.filter_search(request.POST)
    if not filtered_products:
        return render(request, "surfsup/no_match.html")
    context = {
        'products': filtered_products
    }
    return render(request, "surfsup/search_result.html", context)


def product_sortby(request, sortby):
    filtered_products = Product.objects.filter_search(request.POST)
    print(filtered_products)
    if not filtered_products:
        return render(request, "surfsup/no_match.html")
    if sortby == "price-asc":
        print(sortby)
        filtered_products = filtered_products.order_by('-price')
    elif sortby == "price-desc":
        print(sortby)
        filtered_products = filtered_products.order_by('price')
    context = {
        'products': filtered_products,
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, "surfsup/search_result.html", context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        current_order = Order.objects.filter(user=User.objects.get(
            id=self.request.session['uid']), ordered=False)[0]
        context = {
            'user': User.objects.get(id=self.request.session['uid']),
            'current_order': current_order
        }
        return render(self.request, 'surfsup/checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        if form.is_valid():
            print("The form is valid")
            return redirect('/checkout')


def view_cart(request):
    current_order = Order.objects.filter(user=User.objects.get(
        id=request.session['uid']), ordered=False)[0]
    context = {
        "current_order": current_order,
        'user': User.objects.get(id=request.session['uid'])
    }
    # print(zipped_list)
    return render(request, 'surfsup/cart.html', context)


def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST['product_id']

        # get product and quantity
        product = get_object_or_404(Product, id=product_id)
        quantity = request.POST['quantity']
        user = User.objects.get(id=request.session['uid'])

        # create order if none exist
        if user.orders.all().filter(ordered=False):
            # if there is current order
            current_order = user.orders.all().filter(ordered=False)[0]

            # check if product exist in order
            if current_order.items.all().filter(item=product):
                # if found, update the quantity
                exisiting_order_item = current_order.items.all().get(item=product)
                exisiting_order_item.quantity += int(quantity)
                exisiting_order_item.save()

            else:
                # if product is not found in order item, create new orderitem and add to order
                new_order_item = OrderItem.objects.create(
                    item=product, quantity=quantity)
                current_order.items.add(new_order_item)

        else:
            # if there is no current order, create a new order
            new_order = Order.objects.create(user=user)
            new_order_item = OrderItem.objects.create(
                item=product, quantity=quantity)
            new_order.items.add(new_order_item)
        messages.success(request, "successfully added to cart")
    return redirect(f"/products/show/{product_id}")


def update_cart(request, orderitem_id):
    if request.method == "POST":
        # find the order item
        order_item = OrderItem.objects.get(id=orderitem_id)
        # update quantity
        order_item.quantity = int(request.POST['quantity'])
        order_item.save()
        messages.success(request, "cart updated")
    return redirect('/cart')


def delete_cart(request, orderitem_id):
    if request.method == "POST":
        order_item = OrderItem.objects.get(id=orderitem_id)
        order_item.delete()
        messages.success(request, "item removed")
        return redirect('/cart')


def check_promo(request):
    result = PromoCode.objects.filter(code=request.POST['promocode'].upper())
    current_order = Order.objects.filter(user=User.objects.get(
        id=request.session['uid']), ordered=False)[0]
    if result:

        current_order.promo_valid = True
        current_order.promo_rate = result[0].discount
        current_order.save()

        messages.success(request, "promo applied!")

        final_amount = current_order.applypromo(result[0].discount)
        context = {
            "current_order": current_order,
            "final_amount": round(final_amount, 2),
            "promo_discount": round(float(current_order.final_total())*result[0].discount, 2),
            "code": result[0].code,
            'user': User.objects.get(id=request.session['uid'])
        }
    else:
        context = {
            "current_order": current_order,
        }
        return render(request, 'surfsup/invalidpromo.html', context)

    return render(request, 'surfsup/promo.html', context)


def shipping_info(request):
    ShippingAddress.objects.create(
        street=request.POST['address1'],
        street2=request.POST['address2'],
        state=request.POST['state'],
        country=request.POST['country'],
        zipcode=request.POST['zipcode'],
        ordered_by=User.objects.get(id=request.session['uid']),
        order=Order.objects.filter(user=User.objects.get(
            id=request.session['uid']), ordered=False)[0],
    )
    return redirect('/checkout/payment_options')


def payment_options(request):
    user = User.objects.get(id=request.session['uid'])
    order = user.orders.all().filter(ordered=False)[0]
    host = request.get_host()

    if order.promo_valid:
        total = order.applypromo(order.promo_rate)
    else:
        total = order.final_total()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % Decimal(total).quantize(
            Decimal('.01')),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)

    context = {
        'key': settings.STRIPE_PUBLISHABLE_KEY,
        'order': order,
        'total': round(total),
        'form': form,
        'current_order': Order.objects.filter(user=User.objects.get(
            id=request.session['uid']), ordered=False)[0],
        'user': User.objects.get(id=request.session['uid'])
    }
    return render(request, 'surfsup/payment_option.html', context)


# paypal charging


@csrf_exempt
def payment_done(request):
    user = User.objects.get(id=request.session['uid'])
    order = user.orders.all().filter(ordered=False)[0]
    order.ordered = True
    order.save()
    Order.objects.create(user=User.objects.get(
        id=request.session['uid']))
    return redirect('/checkout/complete')


@csrf_exempt
def payment_cancelled(request):
    return redirect('/checkout/payment_options')


# payment complete page
def charge(request):
    if request.method == "POST":
        user = User.objects.get(id=request.session['uid'])
        order = user.orders.all().filter(ordered=False)[0]
        if order.promo_valid:
            total = order.applypromo(order.promo_rate)
        else:
            total = order.final_total()

        charge = stripe.Charge.create(
            amount=round(total),
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        order.ordered = True
        order.save()
        Order.objects.create(user=User.objects.get(
            id=request.session['uid']))

        return redirect('/checkout/complete')


def payment_complete(request):
    user = User.objects.get(id=request.session['uid'])
    order = user.orders.all().filter(ordered=True).last()
    today = date.today()
    delivery_date = today + timedelta(days=5)
    context = {
        'order': order,
        'address': order.shipping_address.all().last(),
        'promo_percent': round(order.promo_rate*100),
        'promo_saving': round(float(order.final_total())*order.promo_rate),
        'final_total': round(order.applypromo(order.promo_rate)),
        'delivery_date': delivery_date,
        'user': User.objects.get(id=request.session['uid'])

    }
    return render(request, "surfsup/payment_complete.html", context)


def account(request):
    user = User.objects.get(id=request.session['uid'])
    context = {
        'user': user,
        'order_history': Order.objects.filter(user=user, ordered=True),
    }
    return render(request, 'surfsup/account.html', context)


def show_order(request, order_id):
    user = User.objects.get(id=request.session['uid'])
    order = Order.objects.get(id=order_id)
    today = date.today()
    delivery_date = today + timedelta(days=5)
    context = {
        'order': order,
        'address': order.shipping_address.all().last(),
        'promo_percent': round(order.promo_rate*100),
        'promo_saving': round(float(order.final_total())*order.promo_rate),
        'final_total': round(order.applypromo(order.promo_rate)),
        'delivery_date': delivery_date,
        'user': user

    }
    return render(request, "surfsup/show_order.html", context)
