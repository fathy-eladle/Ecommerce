from django.urls import path
from .views import (
    ReviewCreateView,
    ReviewListView,
    UserReviewListView,
    ReviewUpdateDeleteView
)

urlpatterns = [
    path('reviews/create/', ReviewCreateView.as_view(), name='review-create'),
    path('products/<int:product_id>/reviews/', ReviewListView.as_view(), name='product-reviews'),
    path('reviews/my-reviews/', UserReviewListView.as_view(), name='user-reviews'),
    path('reviews/<int:pk>/', ReviewUpdateDeleteView.as_view(), name='review-detail'),
]
