from django.conf.urls import url
from . import views
from .views import CheckoutView

urlpatterns = [
    url(r'^$', views.landing),
    url(r'^home$', views.home),
    url(r'^signin$', views.signin),
    url(r'^signup$', views.signup),
    url(r'^register$', views.register),
    url(r'^login_post$', views.login_post),
    url(r'^signout$', views.signout),
    url(r'^products$', views.show_all_products),
    url(r'^products/show/(?P<product_id>[0-9]+)$', views.show_product),
    url(r'^products/search$', views.product_search),
    url(r'^products/search/(?P<sortby>[a-z\\-]+)$', views.product_sortby),
    url(r'^category/(?P<category>[a-z]+)$', views.show_category),
    url(r'^cart$', views.view_cart),
    url(r'^add_to_cart$', views.add_to_cart),
    url(r'^cart/update/(?P<orderitem_id>[0-9]+)$', views.update_cart),
    url(r'^cart/delete/(?P<orderitem_id>[0-9]+)$', views.delete_cart),
    url(r'^checkout$', CheckoutView.as_view(), name='checkout'),
    url(r'^check_promo$', views.check_promo),
    url(r'^checkout/shipping_info$', views.shipping_info),
    url(r'^checkout/payment_options$', views.payment_options),
    url(r'^checkout/complete$', views.payment_complete),
    url(r'^payment-done$', views.payment_done, name='payment_done'),
    url(r'^payment-cancelled$', views.payment_cancelled, name='payment_cancelled'),
    url(r'^charge$', views.charge),
    url(r'^account$', views.account),
    url(r'^account/orders/(?P<order_id>[0-9]+)$', views.show_order),
]
