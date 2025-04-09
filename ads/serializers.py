from rest_framework import serializers
from .models import Ad

# class CarBrandSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CarBrand
#         fields = "__all__"
#
# class CarModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CarModel
#         fields = "__all__"
#
# class AdSerializer(serializers.ModelSerializer):
#     brand = CarBrandSerializer()
#     model = CarModelSerializer()
#
#     class Meta:
#         model = Ad
#         fields = "__all__"
