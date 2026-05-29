from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Vehicle, Order, LocationLog

# 1. Foydalanuvchilar (Dispecher va Haydovchi) uchun admin panel
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'phone_number', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone_number')
    
    # Yangi maydonlarni (role, phone_number) admin panelda tahrirlash uchun qo'shamiz
    fieldsets = UserAdmin.fieldsets + (
        ('Logistika ma\'lumotlari', {'fields': ('role', 'phone_number')}),
    )

# 2. Transport vositalari uchun
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'capacity_tons', 'status', 'driver')
    list_filter = ('status',)
    search_fields = ('plate_number', 'driver__username', 'driver__first_name')
    list_editable = ('status',) # Ro'yxatning o'zidan turib statusni o'zgartirish imkoniyati

# 3. Buyurtmalar uchun
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'pickup_location', 'dropoff_location', 'weight_tons', 'status', 'vehicle', 'dispatcher')
    list_filter = ('status', 'created_at')
    search_fields = ('pickup_location', 'dropoff_location', 'cargo_description')
    list_editable = ('status',)
    date_hierarchy = 'created_at' # Yuqorida sana bo'yicha chiroyli filtr paydo bo'ladi

# 4. GPS lokatsiya loglari
@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'latitude', 'longitude', 'recorded_at')
    list_filter = ('recorded_at', 'vehicle')
    readonly_fields = ('recorded_at',) # Bu maydonni faqat o'qish mumkin bo'ladi