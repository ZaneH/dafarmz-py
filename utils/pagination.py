from typing import Generic, TypeVar

T = TypeVar('T')


class PaginationHelper(Generic[T]):
    def __init__(self, data=None, per_page=1):
        self.data: list[T] = data or []
        self.per_page = per_page
        self.page = 0

    def get_page(self):
        start = self.page * self.per_page
        end = start + self.per_page
        return self.data[start:end]

    def next_page(self):
        self.page += 1
        return self.get_page()

    def previous_page(self):
        self.page -= 1
        return self.get_page()

    def has_next_page(self):
        return (self.page + 1) * self.per_page < len(self.data)

    def has_previous_page(self):
        return self.page > 0
