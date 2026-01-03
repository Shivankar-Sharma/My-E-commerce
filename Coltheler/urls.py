"""
URL configuration for MyEcomm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import (
    index,
    login,
    register,
    logout,
    profile,
    profile_picture_upload,
    product_listing,
    product_create_update,
    product_delete,
    option_listing,
    option_create_update,
    option_delete,
)


urlpatterns = [
    path("home/", index, name="home"),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("logout/", logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("profile/upload-image", profile_picture_upload, name="upload-image"),
    path("products/", product_listing, name="products"),
    path("product-details/", product_create_update, name="product-create"),
    path(
        "product-details/<str:product_code>/",
        product_create_update,
        name="product-update",
    ),
    path("product-delete/<str:product_code>/", product_delete, name="product-delete"),
    path("options/", option_listing, name="options"),
    path("option-details/", option_create_update, name="option-create"),
    path("option-details/<str:option_id>/", option_create_update, name="option-update"),
    path("option-delete/<str:option_id>/", option_delete, name="option-delete"),
]
