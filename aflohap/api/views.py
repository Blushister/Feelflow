# from django.http import JsonResponse
from aflohap.models import Message, Room
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import MessageSerializer, RoomSerializer


@api_view(['GET'])
# Les routes de l'api et le moyen d'acceder a differente chose dessus
def getRoutes(request):
    routes = [
        'GET /api/',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)

# Permet de récuperer tout les salles et leurs messages
@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

# Permet de récuperer une salle en particuler (Spécifier ID) et ces messages associers
@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    messages = Message.objects.filter(room=room)
    room_serializer = RoomSerializer(room, many=False)
    message_serializer = MessageSerializer(messages, many=True)
    return Response({'room': room_serializer.data, 'messages': message_serializer.data})
