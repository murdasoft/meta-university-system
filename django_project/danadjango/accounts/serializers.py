from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'first_name',
            'last_name',
            'role',
            'phone_number',
            'avatar',
            'is_active',
            'date_joined',
            'created_at',
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(required=True, max_length=255, label='ФИО')
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password_confirm',
            'full_name',
        ]
    
    def validate_password(self, value):
        """Валидация пароля - минимум 6 символов"""
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        
        # Проверка уникальности email
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже существует"})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        full_name = validated_data.pop('full_name')
        
        # Используем email как username
        # Сохраняем ФИО в full_name и first_name
        user = User.objects.create_user(
            username=validated_data['email'],  # email как username
            password=password,
            email=validated_data['email'],
            full_name=full_name,
            first_name=full_name,  # Для совместимости
        )
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Кастомный сериализатор для JWT токенов (авторизация по email)"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    @classmethod
    def get_token(cls, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['role'] = user.role
        return refresh
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError(
                {"detail": "Email и пароль обязательны"}
            )
        
        # Находим пользователя по email
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": ["Пользователь с таким email не найден"]}
            )
        
        # Проверяем пароль
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": ["Неверный пароль"]}
            )
        
        # Сохраняем пользователя
        self.user = user
        
        # Генерируем токены
        refresh = self.get_token(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса восстановления пароля"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения восстановления пароля"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_new_password(self, value):
        """Валидация пароля - минимум 6 символов"""
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs
