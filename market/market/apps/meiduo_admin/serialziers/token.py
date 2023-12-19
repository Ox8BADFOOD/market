from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from typing import Any, Dict, Optional, Type, TypeVar

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        """
        往token的有效负载 playload里添加数据
        """
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        token['email'] = user.email
        # ...

        return token

    def validate(self, attrs: dict[str, Any]) -> Dict[str, str]:
        """
        此方法为响应数据结构处理
        """
        data = super().validate(attrs)
        data['token'] = data['access']
        data.pop('access')
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data

