from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Vehicle, Order, LocationLog
from .serializers import UserSerializer, VehicleSerializer, OrderSerializer, LocationLogSerializer
from .permissions import IsDispatcherOrReadOnly, IsDriverAssignedToOrder
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count

class DashboardStatisticsView(APIView):
    """
    Admin va Dispecherlar uchun umumiy statistika API'si
    """
    permission_classes = [IsAuthenticated] # Xavfsizlik

    def get(self, request):
        user = request.user
        
        # Haydovchilar statistikani ko'ra olmaydi
        if user.role == 'driver':
            return Response({"error": "Ruxsat etilmagan!"}, status=403)

        # 1. Yuklar statistikasi
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        in_transit_orders = Order.objects.filter(status='in_transit').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        
        # 2. Mashinalar statistikasi
        total_vehicles = Vehicle.objects.count()
        available_vehicles = Vehicle.objects.filter(status='available').count()

        # 3. Moliya (Faqat Adminga ko'rinadi)
        total_revenue = 0
        if user.role == 'admin':
            revenue_data = Order.objects.filter(status='delivered').aggregate(total=Sum('price'))
            total_revenue = revenue_data['total'] or 0

        return Response({
            "orders": {
                "total": total_orders,
                "pending": pending_orders,
                "in_transit": in_transit_orders,
                "delivered": delivered_orders
            },
            "vehicles": {
                "total": total_vehicles,
                "available": available_vehicles
            },
            "financials": {
                "total_revenue": total_revenue # Dispecherga 0 bo'lib boradi, Adminga asl summa
            }
        })
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsDispatcherOrReadOnly]

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated, IsDispatcherOrReadOnly]
    
    # FILTR VA QIDIRUV
    filterset_fields = ['status', 'capacity_tons']
    search_fields = ['plate_number', 'driver__first_name']
    ordering_fields = ['capacity_tons']

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsDriverAssignedToOrder]
    
    # FILTR, QIDIRUV VA SARALASH
    filterset_fields = ['status', 'pickup_location', 'dropoff_location']
    search_fields = ['cargo_description', 'pickup_location', 'dropoff_location']
    ordering_fields = ['created_at', 'price', 'weight_tons']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'driver':
            return Order.objects.filter(vehicle__driver=user)
        return Order.objects.all()

    # ==========================================
    # 1. YANGI BUYURTMA YARATILGANDA
    # ==========================================
    def perform_create(self, serializer):
        order = serializer.save()
        # Agar buyurtmaga mashina biriktirilgan bo'lsa, uni darhol "Band" qilamiz
        if order.vehicle:
            order.vehicle.status = 'on_trip'
            order.vehicle.save()

    # ==========================================
    # 2. BUYURTMA TAHRIRLANGANDA / YETKAZILGANDA
    # ==========================================
    def perform_update(self, serializer):
        # Tahrirlashdan oldingi eski holatni va eski mashinani eslab qolamiz
        old_order = self.get_object()
        old_vehicle = old_order.vehicle

        # Yangi o'zgarishlarni saqlaymiz
        order = serializer.save()

        # Agar dispecher mashinani boshqasiga almashtirgan bo'lsa, eskisini bo'shatib yuboramiz
        if old_vehicle and old_vehicle != order.vehicle:
            old_vehicle.status = 'available'
            old_vehicle.save()

        # Agar buyurtma holati "Yetkazildi" ga o'zgarsa (Haydovchi tugmani bossa)
        if order.status == 'delivered' and order.vehicle:
            order.vehicle.status = 'available'  # Mashina bo'shadi
            order.vehicle.save()
            
        # Agar yangi mashina biriktirilgan bo'lsa yoki hali yo'lda bo'lsa
        elif order.status in ['pending', 'in_transit'] and order.vehicle:
            order.vehicle.status = 'on_trip' # Mashina band qilindi
            order.vehicle.save()

class LocationLogViewSet(viewsets.ModelViewSet):
    queryset = LocationLog.objects.all()
    serializer_class = LocationLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['vehicle']
    ordering_fields = ['recorded_at']
