from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Faqat 'admin' roli uchun to'liq ruxsat"""
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser

class IsDispatcherOrReadOnly(permissions.BasePermission):
    """
    Faqat dispecherlar ma'lumotni to'liq tahrirlay oladi/qo'sha oladi.
    Boshqalar (haydovchilar) faqat o'qishi mumkin.
    """
    def has_permission(self, request, view):
        # Agar so'rov o'qish uchun bo'lsa (GET), ruxsat beramiz
        if request.method in permissions.SAFE_METHODS:
            return True
        # Aks holda, foydalanuvchi dispecher bo'lishi shart
        return request.user.role in ['dispatcher', 'admin']

class IsDriverAssignedToOrder(permissions.BasePermission):
    """
    Haydovchi faqat o'ziga biriktirilgan yukning statusini o'zgartira oladi.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'dispatcher':
            return True # Dispecherga hamma narsa ruxsat
        if request.user.role == 'driver':
            # Haydovchi faqat mashinasiga ulangan buyurtmani ko'rishi/tahrirlashi mumkin
            return obj.vehicle and obj.vehicle.driver == request.user
        return False