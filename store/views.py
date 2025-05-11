from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order, OrderItem
from .serializers import OrderSerializer,ProductSerializer
from .discounts import calculate_discounts
from rest_framework.exceptions import ValidationError

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
        try:
            items = request.data.get('items')
            if not items:
                raise ValidationError("No items provided.")

            order_items = []
            for item in items:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    quantity = int(item['quantity'])
                    if quantity <= 0:
                        raise ValidationError("Quantity must be greater than 0.")
                    order_items.append({'product': product, 'quantity': quantity})
                except Product.DoesNotExist:
                    raise ValidationError(f"Product with ID {item.get('product_id')} does not exist.")
                except (KeyError, ValueError):
                    raise ValidationError("Invalid product or quantity format.")

            final_total, discounts = calculate_discounts(request.user, order_items)

            order = Order.objects.create(user=request.user, total=final_total, discounts=discounts)
            for item in order_items:
                OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e.detail if hasattr(e, 'detail') else str(e))}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
    
class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            products = Product.objects.select_related('category').all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Unable to fetch products'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   