from django.urls import path
from .views import show_dish, show_order, get_order, review_order


app_name = 'dish'
urlpatterns = [
    path('dish/', show_dish),
    path('order/', show_order, name='show_order'),
    path('get_order/<slug:dish_id>', get_order, name='get_order'),
    path('review_order/<slug:dish_id>', review_order, name='review_order'),
]
