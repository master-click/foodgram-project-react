from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    def get_page_size(self, request):
        if request.query_params.get('is_in_shopping_cart'):
            return 999
        return 6
