from rest_framework import serializers
from .models import Book, User, Loan

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "isbn",
            "total_copies", "available_copies",
            "publish_date", "created_at", "updated_at"
        ]

    def create(self, validated_data):
        if "available_copies" not in validated_data:
            validated_data["available_copies"] = validated_data.get("total_copies", 1)
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password",
            "role", "is_active", "date_joined", "created_at", "updated_at"
        ]
        read_only_fields = ["date_joined", "created_at", "updated_at"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_password(User.objects.make_random_password())
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id", "user", "book",
            "checkout_date", "due_date", "return_date"
        ]
        read_only_fields = ["checkout_date", "return_date"]
