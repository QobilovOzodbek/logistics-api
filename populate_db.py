import os
import django
import random
from decimal import Decimal

# 1. Django loyiha muhitini ulash (Skript bazani taniy olishi uchun)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# 2. Biz yaratgan modellarni chaqirish
from logistics.models import CustomUser, Vehicle, Order, LocationLog

def populate():
    print("Ma'lumotlar bazasiga yozish boshlandi. Kuting...")

    dispatchers = []
    drivers = []
    
    # 10 ta Dispecher va 10 ta Haydovchi yaratamiz
    for i in range(1, 11):
        # Dispecher
        disp, created = CustomUser.objects.get_or_create(
            username=f"dispatcher_{i}",
            defaults={
                "first_name": f"Dispecher",
                "last_name": f"{i}",
                "role": "dispatcher",
                "phone_number": f"+9989011122{i:02d}"
            }
        )
        if created:
            disp.set_password("parol123")
            disp.save()
        dispatchers.append(disp)

        # Haydovchi
        driver, created = CustomUser.objects.get_or_create(
            username=f"driver_{i}",
            defaults={
                "first_name": f"Haydovchi",
                "last_name": f"{i}",
                "role": "driver",
                "phone_number": f"+9989099988{i:02d}"
            }
        )
        if created:
            driver.set_password("parol123")
            driver.save()
        drivers.append(driver)

    print("✅ 10 ta dispecher va 10 ta haydovchi yaratildi.")

    # 10 ta Yuk mashinasi yaratamiz va har biriga bittadan haydovchi biriktiramiz
    vehicles = []
    statuses = ['available', 'on_trip', 'maintenance']
    
    for i in range(10):
        veh, created = Vehicle.objects.get_or_create(
            plate_number=f"01A{100+i}BC",
            defaults={
                "driver": drivers[i], # OneToOneField bo'lgani uchun har biriga alohida haydovchi
                "capacity_tons": Decimal(random.uniform(5.0, 20.0)).quantize(Decimal("0.00")),
                "status": random.choice(statuses)
            }
        )
        vehicles.append(veh)

    print("✅ 10 ta yuk mashinasi yaratildi.")

    # 10 ta Buyurtma (Yuk) yaratamiz
    cities = ["Toshkent", "Samarqand", "Qarshi", "Navoiy", "Urganch", "Nukus", "Farg'ona", "Andijon", "Namangan", "Jizzax"]
    order_statuses = ['pending', 'assigned', 'in_transit', 'delivered']

    for i in range(10):
        pickup = random.choice(cities)
        dropoff = random.choice([c for c in cities if c != pickup]) # Olish va yetkazish manzili bir xil bo'lib qolmasligi uchun
        
        Order.objects.get_or_create(
            cargo_description=f"Yuk №{i+1}: Sanoat tovarlari",
            defaults={
                "dispatcher": random.choice(dispatchers),
                "vehicle": random.choice(vehicles),
                "pickup_location": pickup,
                "dropoff_location": dropoff,
                "weight_tons": Decimal(random.uniform(1.0, 15.0)).quantize(Decimal("0.00")),
                "price": Decimal(random.randint(500000, 5000000)).quantize(Decimal("0.00")),
                "status": random.choice(order_statuses)
            }
        )

    print("✅ 10 ta buyurtma yaratildi.")

    # 10 ta GPS Lokatsiya (kuzatuv nuqtalari) yaratamiz
    for i in range(10):
        LocationLog.objects.create(
            vehicle=random.choice(vehicles),
            latitude=Decimal(random.uniform(39.0, 42.0)).quantize(Decimal("0.000000")),
            longitude=Decimal(random.uniform(64.0, 70.0)).quantize(Decimal("0.000000"))
        )
        
    print("✅ 10 ta GPS lokatsiya loglari yozildi.")
    print("🎉 Barcha ma'lumotlar muvaffaqiyatli qo'shildi! Admin panelga kirib tekshirishingiz mumkin.")

if __name__ == "__main__":
    populate()