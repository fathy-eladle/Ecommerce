from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .serializer import ProductSerializer , CategorySerializer
from .models import Category, Product
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.


##################### product control open ################################
class AdminProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter,DjangoFilterBackend,OrderingFilter]
    search_fields = ['^name', '=price', 'description']  
    filterset_fields = {
    'price': ['exact', 'lt', 'gt', 'lte', 'gte'],
    'category': ['exact'],
    'created_at': ['date__gt', 'date__lt'],
    'is_available':['exact']
      }
    ordering_fields = ['category__name','name','price','created_at']    

    def get_queryset(self):
        queryset= Product.objects.select_related('category')
        ordering = self.request.query_params.get('ordering')
        if ordering in self.ordering_fields:
          queryset = queryset.order_by(ordering)
        else:
          queryset =queryset.order_by('name')  
        return queryset  

    
class AdminProductRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    ordering_fields = ['name', 'price', 'category__name']
    search_fields = ['name', '^price', 'description']
    filterset_fields = {
        'price': ['exact', 'lt', 'gt', 'lte', 'gte'],
        'category': ['exact'],
        'created_at': ['date__gt', 'date__lt'],
        'is_available':['exact']
         }
    filter_backends = [SearchFilter,OrderingFilter,DjangoFilterBackend]
    
class ProductRetriveView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
############################# product control close #####################################
    
############################# category control open  #####################################
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    search_fields = ['name']
    ordering_fields = ['name']
    filter_backends = [SearchFilter,OrderingFilter]
    
class AdminCategoryRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering_fields = ['name']
    search_fields = ['name']
    filter_backends = [SearchFilter,OrderingFilter]
    
class CategoryRetriveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
  ############################# category control close#####################################
    
    