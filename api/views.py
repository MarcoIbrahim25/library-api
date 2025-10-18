from datetime import date, timedelta
from django.db.models import Q
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.decorators import action
from .models import Book, User, Loan
from .serializers import BookSerializer, UserSerializer, LoanSerializer

class IsAdminOrLibrarianOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", None) in ("admin", "librarian"))

class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "role", None) == "admin")

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("title")
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrLibrarianOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        available = self.request.query_params.get("available")
        ordering = self.request.query_params.get("ordering")
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(author__icontains=q) |
                Q(isbn__icontains=q)
            )
        if available is not None:
            val = available.lower()
            if val in ("true", "1", "yes"):
                qs = qs.filter(available_copies__gt=0)
            elif val in ("false", "0", "no"):
                qs = qs.filter(available_copies__lte=0)
        if ordering:
            qs = qs.order_by(ordering)
        return qs

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAdminOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        is_active = self.request.query_params.get("is_active")
        if role:
            qs = qs.filter(role=role)
        if is_active is not None:
            v = is_active.lower()
            if v in ("true", "1", "yes"):
                qs = qs.filter(is_active=True)
            elif v in ("false", "0", "no"):
                qs = qs.filter(is_active=False)
        return qs

class LoanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Loan.objects.select_related("book", "user")
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        overdue = self.request.query_params.get("overdue")
        if getattr(user, "role", None) not in ("admin", "librarian"):
            qs = qs.filter(user=user)
        if overdue is not None and overdue.lower() in ("true", "1", "yes"):
            qs = qs.filter(return_date__isnull=True, due_date__lt=date.today())
        return qs

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        try:
            book_id = int(request.data.get("book_id"))
        except (TypeError, ValueError):
            return Response({"detail": "book_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            days = int(request.data.get("days", 14))
            if days <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"detail": "days must be positive integer"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        if book.available_copies <= 0:
            return Response({"detail": "No available copies"}, status=status.HTTP_400_BAD_REQUEST)
        exists = Loan.objects.filter(user=request.user, book=book, return_date__isnull=True).exists()
        if exists:
            return Response({"detail": "User already has an active loan for this book"}, status=status.HTTP_400_BAD_REQUEST)
        loan = Loan.objects.create(user=request.user, book=book, due_date=date.today() + timedelta(days=days))
        book.available_copies -= 1
        book.save(update_fields=["available_copies"])
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        try:
            loan = Loan.objects.select_related("book", "user").get(pk=pk)
        except Loan.DoesNotExist:
            return Response({"detail": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if getattr(user, "role", None) not in ("admin", "librarian") and loan.user_id != user.id:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if loan.return_date is None:
            loan.return_date = date.today()
            loan.save(update_fields=["return_date"])
            book = loan.book
            book.available_copies += 1
            book.save(update_fields=["available_copies"])
        return Response(status=status.HTTP_204_NO_CONTENT)
