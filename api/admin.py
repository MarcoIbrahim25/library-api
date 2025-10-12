from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Book, Loan


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        # مهم: سيب بس الحقول القابلة للعرض هنا، ومش لازم تضيف created_at/updated_at هنا
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role"),
        }),
    )

    # دول Read-only عشان ما يحصلش FieldError
    readonly_fields = ("last_login", "date_joined", "created_at", "updated_at")

    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "isbn", "total_copies", "available_copies", "publish_date")
    search_fields = ("title", "author", "isbn")
    list_filter = ("publish_date",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "checkout_date", "due_date", "return_date")
    list_filter = ("return_date",)
    search_fields = ("user__username", "book__title", "book__isbn")
