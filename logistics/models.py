from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Foydalanuvchilar (Dispecher va Haydovchi)
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Boshqaruvchi'),
        ('dispatcher', 'Dispecher'),
        ('driver', 'Haydovchi'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='dispatcher')
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# 2. Transport vositalari (Yuk mashinalari)
class Vehicle(models.Model):
    STATUS_CHOICES = (
        ('available', 'Bo\'sh'),
        ('on_trip', 'Band (Yo\'lda)'),
        ('maintenance', 'Ta\'mirda'),
    )
    driver = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'driver'})
    plate_number = models.CharField(max_length=15, unique=True, help_text="Davlat raqami (Masalan: 80A123BC)")
    capacity_tons = models.DecimalField(max_digits=5, decimal_places=2, help_text="Yuk ko'tarish hajmi (tonna)")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.plate_number} - {self.capacity_tons}t"

# 3. Buyurtmalar (Logistika yuklari)
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('assigned', 'Mashina biriktirildi'),
        ('in_transit', 'Yo\'lda'),
        ('delivered', 'Yetkazib berildi'),
    )
    dispatcher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='dispatched_orders', limit_choices_to={'role': 'dispatcher'})
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    
    pickup_location = models.CharField(max_length=255, help_text="Yukni olish manzili")
    dropoff_location = models.CharField(max_length=255, help_text="Yukni yetkazish manzili")
    cargo_description = models.TextField(help_text="Yuk haqida ma'lumot")
    weight_tons = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pickup_location} -> {self.dropoff_location} | {self.get_status_display()}"

# 4. GPS lokatsiya loglari (Kuzatuv uchun)
class LocationLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']