from feelflow.models import Message, Room
from rest_framework.serializers import ModelSerializer


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
