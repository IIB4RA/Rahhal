from rest_framework import serializers
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

ROLE_CHOICES = ("resident", "international_tourist")

class RegisterSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    language = serializers.ChoiceField(choices=("en", "ar"), default="en")

    def validate(self, data):
        identifier = data["identifier"].strip()
        password = data["password"]
        confirm_password = data["confirm_password"]

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password":"Passwords do not match"})
        
        if "@" in identifier:
            email = identifier.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError({"identifier": "Email already registered"})
            data["email"] = email
            data["phone"] = ""
        else:
            phone = identifier
            if User.objects.filter(phone=phone).exists():
                raise serializers.ValidationError({"identifier": "phone already registered"})
            data["phone"] = phone
            data["email"] = ""

        return data
    
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        email = validated_data.get("email")
        phone = validated_data.get("phone")
        language = validated_data.get("language")

        user = User(email=email, phone=phone, language=language)
        user.set_password(password)
        user.save()
        return user
    
    

class RoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=ROLE_CHOICES)

    def save(self, user):
        role = self.validated_data["role"]
        user.role = role
        user.save()
        return user
    


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email", 
            "full_name", 
            "nationality", 
            "language",
            "phone",
            "role",
            "status",
            "avatar_url",
            )

        
class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data["identifier"].strip()
        password = data["password"]

        user = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(phone=identifier).first()

        if user and user.check_password(password):
            data["user"] = user
            return data
        
        raise serializers.ValidationError("Invalid phone/email or password")


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email", 
            "full_name", 
            "nationality", 
            "language",
            "phone",
            "avatar_url",
            )

    def validate_email(self, email):
        email = email.strip()
        if not email:
            return email
        user = self.context["request"].user
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email.lower()
    
    def validate_phone(self, phone):
        phone = phone.strip()
        if not phone:
            return phone
        user = self.context["request"].user
        if User.objects.filter(phone=phone).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return phone

   