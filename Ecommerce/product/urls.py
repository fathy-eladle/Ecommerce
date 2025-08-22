from django.urls import path
from .views import AdminProductListCreateView, AdminProductRetriveUpdateDestroyView,ProductListView,AdminCategoryListCreateView,AdminCategoryRetriveUpdateDestroyView,CategoryListView,ProductRetriveView,CategoryRetriveView
urlpatterns = [
    # products url
    path('admin/products/',AdminProductListCreateView.as_view()),
    path('admin/products/<int:pk>/',AdminProductRetriveUpdateDestroyView.as_view()),
    path('products/',ProductListView.as_view()),
    path('products/<int:pk>/',ProductRetriveView.as_view()),
    
    #categories url
    path('admin/categories/',AdminCategoryListCreateView.as_view()),
    path('admin/categories/<int:pk>/',AdminCategoryRetriveUpdateDestroyView.as_view()),
    path('categories/',CategoryListView.as_view()),
    path('categories/<int:pk>/',CategoryRetriveView.as_view()),
    
]