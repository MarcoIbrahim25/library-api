from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView, TokenRefreshView as BaseTokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {"token": data["access"]}

class MyTokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class TokenRefreshView(BaseTokenRefreshView):
    serializer_class = TokenRefreshSerializer
