from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatGroup, GroupMessage
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageCreateForm
from django.contrib.auth.models import User
from django.http import Http404

# Create your views here.
@login_required
def chat_view(request, chatroom_name="public-chat"):
    print("Chat view fun is triggered")
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    print("Chat group name: ", chat_group)
    chat_messages = chat_group.chat_messages.all()[:30]   # type: ignore[attr-defined]
    print("Chat Message: ", chat_messages)
    form = ChatMessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        
    print("Is HTMX:", request.htmx and request.htmx.request)
    print("Method:", request.method)
    print("GET:", request.GET)
    print("POST:", request.POST)

    if request.htmx:
        print("Inside if block")
        form = ChatMessageCreateForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message': message,
                'user': request.user
            }
            return render(request, 'a_rtchat/partials/chat_message_p.html', context)
        
    context = {
        'chat_messages': chat_messages, 
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name
    }

    print("Context dict: ", context)
        
    return render(request, 'a_rtchat/chat.html', context)


def get_or_create_chatroom(request, username):
    if request.user.username == username: 
        return redirect('home')
    
    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user, request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom.group_name)
