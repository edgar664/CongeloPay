from django.shortcuts import render
from django.contrib.auth import login as auth_login, logout, authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken # <--- Importante


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)

    if user is not None:
        # Generamos el Token para este usuario específico
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token), # <--- ESTE ES EL TOKEN QUE BUSCAS
            'user': {
                'username': user.username,
                'rol': user.rol.modulo if user.rol else None
            }
        }, status=status.HTTP_200_OK)
    
    return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # <--- Esto bloquea a quien no tenga Token
def perfil_usuario(request):
    user = request.user
    return Response({
        'mensaje': f'Bienvenido {user.username}',
        'email': user.email,
        'rol': user.rol.modulo if hasattr(user, 'rol') else 'Sin rol'
    })
