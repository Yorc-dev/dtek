from collections import OrderedDict

from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    page_size = 5
    page_query_param = "page"
    max_page_size = 110
    page_size_query_param = "page_size"
    count = None

    def paginate_queryset(self, queryset, request, view=None):
        self.count = queryset.count()
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("total", self.count),
                    ("page", self.page.number),
                    ("pages", self.page.paginator.num_pages),
                    ("results", data),
                ],
            ),
        )


class CombinedItemsPagination(PageNumberPagination):
    page_size = 5  # Значение по умолчанию
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100
    all_items_query_param = "all"  # Параметр для отключения пагинации

    def is_all_items_requested(self, request):
        """
        Проверяет, запрашиваются ли все элементы без пагинации.
        """
        all_items = request.query_params.get(self.all_items_query_param)
        return all_items and all_items.lower() == "true"

    def get_page_number(self, request):
        """
        Извлекает номер страницы из параметров запроса.
        """
        page_number = request.query_params.get(self.page_query_param) or 1
        if isinstance(page_number, str) and page_number.isdigit():
            return int(page_number)
        return 1

    def get_page(self, paginator, page_number):
        """
        Возвращает запрошенную страницу пагинатора.
        """
        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def paginate_queryset(self, queryset, request, view=None):
        """
        Пагинирует queryset или возвращает все элементы, если параметр all=true.
        """
        if self.is_all_items_requested(request):
            return None  # Возвращаем весь queryset без пагинации

        # Создаём пагинатор и извлекаем запрошенную страницу
        page_size = self.get_page_size(request)
        paginator = Paginator(queryset, page_size)
        page_number = self.get_page_number(request)
        self.page = self.get_page(paginator, page_number)
        self.request = request

        return list(self.page)

    def get_paginated_response(self, data):
        """
        Формирует ответ с метаинформацией о пагинации.
        """
        return Response(
            OrderedDict(
                [
                    ("total", self.page.paginator.count),
                    ("page", self.page.number),
                    ("pages", self.page.paginator.num_pages),
                    ("results", data),
                ],
            ),
        )