from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_name',
            'user_name', 'rating', 'comment',
            'created_at'
        ]
        read_only_fields = ['user']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_comment(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Review comment must be at least 10 characters long"
            )
        return value.strip()

    def create(self, validated_data):
        user = self.context['request'].user
        # Check if user already reviewed this product
        if Review.objects.filter(
            user=user,
            product=validated_data['product']
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product"
            )
        
        validated_data['user'] = user
        return super().create(validated_data)
