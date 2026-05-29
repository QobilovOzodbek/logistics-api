from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Vehicle, Order, LocationLog

# 1. JWT Token uchun maxsus Serializer (Login qilinganda ism va rolni beradi)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Token bilan birga foydalanuvchi ma'lumotlarini ham yuboramiz
        data['role'] = self.user.role
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        return data

# 2. Foydalanuvchilar uchun Serializer
# logistics/serializers.py dagi UserSerializer ni shunga almashtiring:
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Parolni API da o'qishni taqiqlaymiz, faqat yozish mumkin

    def create(self, validated_data):
        # Parolni avtomatik shifrlab bazaga saqlaymiz
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
# 3. Yuk mashinalari uchun Serializer
class VehicleSerializer(serializers.ModelSerializer):
    # Bu qator orqali biz faqat haydovchi ID'sini emas, uning to'liq ma'lumotlarini ham chiqaramiz
    driver_details = UserSerializer(source='driver', read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'plate_number', 'capacity_tons', 'status', 'driver', 'driver_details']

# 4. Buyurtmalar uchun Serializer
class OrderSerializer(serializers.ModelSerializer):
    # Buyurtma ichida mashina va dispecher haqida batafsil ma'lumot bo'lishi uchun
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    dispatcher_details = UserSerializer(source='dispatcher', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'pickup_location', 'dropoff_location', 'cargo_description', 
            'weight_tons', 'price', 'status', 'created_at', 
            'dispatcher', 'dispatcher_details', 
            'vehicle', 'vehicle_details'
        ]

# 5. GPS lokatsiya uchun Serializer
class LocationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationLog
        fields = ['id', 'vehicle', 'latitude', 'longitude', 'recorded_at']