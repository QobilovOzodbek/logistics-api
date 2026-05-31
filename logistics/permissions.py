from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Faqat 'admin' roli uchun to'liq ruxsat"""
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser

class IsDispatcherOrReadOnly(permissions.BasePermission):
    """
    Faqat Admin va Dispecherlarga yozish (qo'shish, o'zgartirish, o'chirish) huquqini beradi.
    Haydovchilar faqat o'qiy oladi.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['admin', 'dispatcher']


class IsDriverAssignedToOrder(permissions.BasePermission):
    """
    Buyurtmalar (Orders) uchun maxsus xavfsizlik qoidalari:
    - Admin va Dispecher barcha amallarni qila oladi.
    - Haydovchi o'chira OLMAYDI, faqat o'ziga tegishli yukning statusini o'zgartira oladi.
    """
    def has_permission(self, request, view):
        # Ro'yxatdan o'tgan har qanday foydalanuvchi API ga kira oladi
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 1. Admin uchun mutlaq ruxsat (hamma narsani qila oladi)
        if request.user.role == 'admin':
            return True
            
        # 2. Dispecher uchun ruxsat (qo'shish, tahrirlash, o'chirish)
        if request.user.role == 'dispatcher':
            return True
            
        # 3. Haydovchi uchun cheklovlar
        if request.user.role == 'driver':
            # Haydovchiga buyurtmani o'chirish qat'iyan taqiqlanadi
            if request.method == 'DELETE':
                return False
            # Faqat o'ziga biriktirilgan mashinadagi yuklarni ko'rishi yoki tahrirlashi mumkin
            if obj.vehicle and obj.vehicle.driver == request.user:
                return True
            return False
            
        return False
