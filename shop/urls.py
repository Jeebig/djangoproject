from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('product/<slug:slug>/', views.product_detail, name='product-detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart-add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart-remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart-update'),
    path('cart/clear/', views.cart_clear, name='cart-clear'),
    path('checkout/', views.checkout, name='checkout'),
]
