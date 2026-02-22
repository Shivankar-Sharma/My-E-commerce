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
from . import views


urlpatterns = [
    path("home/", views.index, name="home"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/upload-image", views.profile_picture_upload, name="upload-image"),
    path("products/", views.product_listing, name="products"),
    path("product-details/", views.product_create_update, name="product-create"),
    path(
        "product-details/<str:product_code>/",
        views.product_create_update,
        name="product-update",
    ),
    path(
        "product-delete/<str:product_code>/",
        views.product_delete,
        name="product-delete",
    ),
    path("options/", views.option_listing, name="options"),
    path("option-details/", views.option_create_update, name="option-create"),
    path(
        "option-details/<str:option_id>/",
        views.option_create_update,
        name="option-update",
    ),
    path("option-delete/<str:option_id>/", views.option_delete, name="option-delete"),
    path("import-products/", views.import_products, name="import-products"),
    path("imports/", views.import_jobs_listing, name="imports"),
    path("asset-library/", views.asset_listing, name="asset-library"),
    path("asset-library/upload/", views.asset_upload, name="asset-upload"),
    path(
        "asset-library/<int:asset_id>/download/",
        views.asset_download,
        name="asset-download",
    ),
    path(
        "asset-library/<int:asset_id>/delete/",
        views.asset_delete,
        name="asset-delete",
    ),
    path("import-status/<str:job_id>/", views.import_status, name="import-status"),
    path("po-templates/", views.po_template_listing, name="po-templates"),
    path(
        "po-template-details/",
        views.po_template_create_update,
        name="po-template-details",
    ),
    path(
        "po-template-details/<str:reference>/<str:sku>/",
        views.po_template_create_update,
        name="po-template-details-create",
    ),
    path(
        "po-template-delete/<str:reference>/<str:sku>",
        views.po_template_delete,
        name="po-template-delete",
    ),
    path("import-po-templates/", views.import_po_template, name="import-po-templates"),
]
