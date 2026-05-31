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
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'dispatcher']


class IsDriverAssignedToOrder(permissions.BasePermission):
    """
    Buyurtmalar (Orders) uchun maxsus xavfsizlik qoidalari:
    - Admin barcha amallarni qila oladi.
    - Dispecher faqat o'zi yaratgan yukni tahrirlaydi yoki o'chiradi (boshqalarnikini faqat ko'radi).
    - Haydovchi o'chira OLMAYDI, faqat o'ziga tegishli yukning statusini o'zgartira oladi.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 1. Admin uchun mutlaq ruxsat
        if request.user.role == 'admin':
            return True
            
        # 2. Dispecher uchun ruxsat
        if request.user.role == 'dispatcher':
            # Hamma yuklarni ko'rishga ruxsat
            if request.method in permissions.SAFE_METHODS:
                return True
            # Tahrirlash yoki o'chirish faqat o'zining yukida ishlaydi
            return obj.dispatcher == request.user
            
        # 3. Haydovchi uchun ruxsat
        if request.user.role == 'driver':
            # Haydovchiga o'chirish qat'iyan taqiqlanadi
            if request.method == 'DELETE':
                return False
            # Faqat o'ziga biriktirilgan mashinadagi yuklarni tahrirlashi mumkin
            if obj.vehicle and obj.vehicle.driver == request.user:
                return True
            return False
            
        return False
