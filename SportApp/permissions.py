from rest_framework import permissions, request, request


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        #  Lectura: Permitido a todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Solo permito escribir si soy el dueño del objeto
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
            
        
        if hasattr(obj, 'equipo') and hasattr(obj.equipo, 'usuario'):
            return obj.equipo.usuario == request.user
        
        
        return False
    