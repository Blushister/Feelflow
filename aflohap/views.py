import pickle

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

from .forms import MyUserCreationForm, RoomForm, UserForm
from .models import Message, Room, Topic, User


# Page de connexion
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "L'utilisateur n'existe pas.")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "L'utilisateur ou le mot de passe est incorrect.")

    context = {'page':page}
    return render(request, 'pages/login_register.html', context)

# Deconnexion de l'utilisateur
def logoutUser(request):
    logout(request)
    return redirect('home')

# Enregistrement de l'utilisateur
def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Une erreur s'est produite lors de la création du compte")

    return render(request, 'pages/login_register.html', {'form':form})

# Page d'acceuil
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:4]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'pages/home.html', context )

# Charger le modèle et le vectorizer
with open('C:\\Users\\curveo\\Documents\\webapp\\aflohap\\naive_bayes_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('C:\\Users\\curveo\\Documents\\webapp\\aflohap\\vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Gestion des salles
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message_body = request.POST.get('body')

        # Transforme le texte du message en vecteurs
        message_vectors = vectorizer.transform([message_body])

        # Prédiction du sentiment
        sentiment = model.predict(message_vectors)

        message = Message.objects.create(
            user=request.user,
            room=room,
            body=message_body,
            sentiment='P' if sentiment[0] == 1 else 'N'  # 0 = Négative 1 = Positive
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'pages/room.html', context)

# Partie qui gere le profile de l'utilisateur ces messages poster sur quel salles est-il ext..
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'pages/profile.html', context)

# Partie pour la création de la salle
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics':topics}
    return render(request, 'pages/room_form.html', context)

# MAJ de la salles (changement de nom, de sujets) (User creator Only)
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("Vous n'avez pas accès à cette section du site!!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form' : form, 'topics':topics, 'room':room}
    return render(request, 'pages/room_form.html', context)

# Partie pour la suppréssion d'une sale (User creator Only)
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, "pages/delete.html", {'obj':room})

# Partie pour la suppréssion d'un message (User creator Only)
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, "pages/delete.html", {'obj':message})

# Partie mise a jour du profile
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'pages/update-user.html', {'form':form})

# Affichage de la liste des sujets de discutions
def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'pages/topics.html',{'topics':topics})

# Affichage des derniers messages postée
def activityPage(request):
    room_messages = Message.objects.all()
    return render(request,'pages/activity.html',{'room_messages':room_messages})
