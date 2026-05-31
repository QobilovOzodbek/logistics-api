from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Vehicle, Order, LocationLog
from .serializers import UserSerializer, VehicleSerializer, OrderSerializer, LocationLogSerializer
from .permissions import IsDispatcherOrReadOnly, IsDriverAssignedToOrder
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

class DashboardStatisticsView(APIView):
    """
    Admin va Dispecherlar uchun MUKAMMAL statistika (Xatolarga qarshi himoyalangan)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if user.role == 'driver':
                return Response({"error": "Ruxsat etilmagan!"}, status=403)

            period = request.query_params.get('period', 'monthly')
            now = timezone.now()

            if period == 'daily':
                start_date = now - timedelta(days=1)
            elif period == 'weekly':
                start_date = now - timedelta(days=7)
            elif period == 'monthly':
                start_date = now - timedelta(days=30)
            elif period == 'yearly':
                start_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(days=30)

            period_orders = Order.objects.filter(created_at__gte=start_date)
            total_orders = period_orders.count()
            pending_orders = period_orders.filter(status='pending').count()
            in_transit_orders = period_orders.filter(status='in_transit').count()
            delivered_orders = period_orders.filter(status='delivered').count()

            total_vehicles = Vehicle.objects.count()
            available_vehicles = Vehicle.objects.filter(status='available').count()

            total_revenue = 0
            chart_data = []
            
            if user.role == 'admin':
                delivered_period = period_orders.filter(status='delivered')
                total_revenue = delivered_period.aggregate(total=Sum('price'))['total'] or 0

                daily_revenue = delivered_period.values('created_at__date').annotate(
                    daily_total=Sum('price'), 
                    count=Count('id')
                ).order_by('created_at__date')
                
                for item in daily_revenue:
                    chart_data.append({
                        "date": str(item['created_at__date']),
                        "revenue": item['daily_total'] or 0,
                        "orders": item['count']
                    })

            drivers = CustomUser.objects.filter(role='driver')
            drivers_data = []
            
            for driver in drivers:
                vehicle = Vehicle.objects.filter(driver=driver).first()
                driver_orders = period_orders.filter(vehicle=vehicle) if vehicle else Order.objects.none()
                
                d_total = driver_orders.count()
                d_delivered = driver_orders.filter(status='delivered').count()
                d_revenue = driver_orders.filter(status='delivered').aggregate(t=Sum('price'))['t'] or 0
                
                # HIMOYA: Agar bazada qaysidir qator yo'q bo'lsa, server qulamasligi uchun
                first_name = getattr(driver, 'first_name', '')
                last_name = getattr(driver, 'last_name', '')
                phone = getattr(driver, 'phone_number', getattr(driver, 'phone', 'Kiritilmagan'))
                
                full_name = f"{first_name} {last_name}".strip()
                if not full_name:
                    full_name = driver.username

                drivers_data.append({
                    "id": driver.id,
                    "name": full_name,
                    "phone": phone,
                    "plate_number": getattr(vehicle, 'plate_number', 'Biriktirilmagan') if vehicle else "Biriktirilmagan",
                    "total_orders": d_total,
                    "delivered_orders": d_delivered,
                    "revenue": d_revenue
                })

            drivers_data = sorted(drivers_data, key=lambda x: x.get('revenue', 0), reverse=True)

            return Response({
                "period": period,
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
                    "total_revenue": total_revenue
                },
                "chart_data": chart_data,
                "drivers_stats": drivers_data
            })
            
        except Exception as e:
            # HIMOYA: Agar xato chiqsa, server qotmaydi, balki Front-endga asl sababni aytadi
            import traceback
            print(traceback.format_exc()) # Render loglariga to'liq xatoni yozadi
            return Response({"error": f"Backend xatosi: {str(e)}"}, status=500)
        
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
    
    # FILTR, QIDIRUV VA SARALASH (Sort)
    filterset_fields = ['status', 'pickup_location', 'dropoff_location']
    search_fields = ['cargo_description', 'pickup_location', 'dropoff_location']
    ordering_fields = ['created_at', 'price', 'weight_tons']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'driver':
            return Order.objects.filter(vehicle__driver=user)
        return Order.objects.all()

class LocationLogViewSet(viewsets.ModelViewSet):
    queryset = LocationLog.objects.all()
    serializer_class = LocationLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['vehicle']
    ordering_fields = ['recorded_at']
