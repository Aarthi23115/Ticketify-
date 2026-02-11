from rest_framework import serializers


class QRValidateSerializer(serializers.Serializer):
    token = serializers.CharField()
    device_info = serializers.CharField(required=False, allow_blank=True)
