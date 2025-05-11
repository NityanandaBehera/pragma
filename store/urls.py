from django.urls import path
from store.views import *
urlpatterns = [
    path('signup/', RegisterView.as_view(), name='user-signup'),
    path('signin/', LoginView.as_view(), name='user-signin'),
    path('orders/create/', CreateOrderView.as_view(), name='create_order'),
    path('products/', ProductListView.as_view(), name='product-list'),
]