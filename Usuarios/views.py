from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Todos los campos son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Quitamos espacios pero dejamos las mayúsculas intactas
    username = str(username).strip()

    # Django verifica la contraseña de forma encriptada (ya es 100% exacta)
    user = authenticate(username=username, password=password)

    if user is not None:
        # EL CANDADO DEFINITIVO PARA EL USUARIO:
        # Si el usuario en la BD es 'ED' y el input fue 'ed', 
        # la base de datos los conecta, pero esta línea de Python los rebota.
        if user.username != username:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({'error': 'Esta cuenta ha sido deshabilitada'}, status=status.HTTP_403_FORBIDDEN)
            
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'rol': user.rol.modulo if hasattr(user, 'rol') and user.rol else None
            }
        }, status=status.HTTP_200_OK)
    
    return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_usuario(request):
    """
    Logout seguro para JWT. Invalida el refresh token en el backend.
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Se requiere el token de refresco'}, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist() # <--- Requiere 'rest_framework_simplejwt.token_blacklist' en INSTALLED_APPS
        
        return Response({'mensaje': 'Sesión cerrada correctamente'}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({'error': 'Token inválido o ya expirado'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle]) # <--- Límite normal para usuarios logueados
def perfil_usuario(request):
    user = request.user
    return Response({
        'mensaje': f'Bienvenido {user.username}',
        'email': user.email,
        'rol': user.rol.modulo if hasattr(user, 'rol') and user.rol else 'Sin rol'
    })