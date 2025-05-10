from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order, OrderItem
from .serializers import OrderSerializer
from .discounts import calculate_discounts

# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get('items')
        if not items:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        order_items = []
        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
                quantity = int(item['quantity'])
                order_items.append({'product': product, 'quantity': quantity})
            except (Product.DoesNotExist, KeyError, ValueError):
                return Response({'error': 'Invalid product or quantity'}, status=status.HTTP_400_BAD_REQUEST)

        final_total, discounts = calculate_discounts(request.user, order_items)

        order = Order.objects.create(user=request.user, total=final_total, discounts=discounts)
        for item in order_items:
            OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)        