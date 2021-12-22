from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from foodgram.paginations import CustomPageNumberPaginator
from foodgram.permissions import IsAdmin
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import CustomUser, Follow
from users.serializers import CustomUserSerializer, FollowSerializer

FOLLOW_MESSAGE = 'Вы подписались на автора! =)'
UNFOLLOW_MESSAGE = 'Вы отписались от автора! =('


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPaginator
    permission_classes = (permissions.AllowAny, )

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated, IsAdmin]
        )
    def following(self, request):
        user = self.request.user
        context = {'request': request}
        queryset = Follow.objects.filter(follower=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowSerializer(
                page,
                context=context,
                many=True
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            queryset,
            context=context,
            many=True
            )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated, IsAdmin]
    )
    def followunfollow(self, request, id):
        author = get_object_or_404(CustomUser, id=id).id
        follower = request.user.id
        in_follow = Follow.objects.filter(
            author=author,
            follower=request.user
        ).exists()

        if request.method == 'GET':
            data = {'author': author, 'follower': follower}
            context = {'request': request}
            serializer = FollowSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                {'status': FOLLOW_MESSAGE},
                status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE' and in_follow:
            Follow.objects.get(
                author=author,
                follower=request.user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': UNFOLLOW_MESSAGE},
                        status=status.HTTP_400_BAD_REQUEST)
