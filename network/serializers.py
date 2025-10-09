from rest_framework import serializers

from .models import NetworkObject


class NetworkObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkObject
        fields = "__all__"
        read_only_fields = ["debt_to_supplier"]
