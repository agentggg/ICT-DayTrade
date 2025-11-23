from rest_framework import serializers
from ict.api.models import *
from datetime import timezone
utc = timezone.utc

# Serializer for CustomUser model
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

# Serializer for Role model
class RoleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"

# Serializer for Instrument model
class InstrumentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = "__all__"

# Serializer for Instrument model
class CandleSerializers(serializers.ModelSerializer):
    instrument = InstrumentSerializers(read_only=True)
    
    class Meta:
        model = Candle
        fields = "__all__"
        