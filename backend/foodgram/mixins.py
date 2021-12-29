from rest_framework import mixins, viewsets


class MixinsSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    pass
