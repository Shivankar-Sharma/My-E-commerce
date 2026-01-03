from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth, User
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile, Product, Option
from .services.base_service import BaseService
import os
from django.conf import settings


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request=request, user=user)
            return redirect("home")
        else:
            print("wrong username or password")
            return redirect("login")
    else:
        return render(request, "login.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        user = auth.authenticate(username=username, password=password, email=email)
        if user is not None:
            return redirect("login")
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.save()
            return redirect("login")
    else:
        return render(request, "register.html")


def logout(request):
    auth.logout(request)
    return redirect("login")


@login_required(login_url="/login")
def index(request):
    context = {"user": request.user, **BaseService.get_user_details(request.user.id)}
    return render(request, "index.html", context)


@login_required(login_url="/login")
def profile(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phonenumber = request.POST.get("phonenumber")
        address1 = request.POST.get("address1")
        address2 = request.POST.get("address2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postcode = request.POST.get("postcode")
        user = request.user
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        if password:
            user.set_password(password)
        user.save()
        update_session_auth_hash(request, user)

        UserProfile.objects.update_or_create(
            user_id=user.id,
            defaults={
                "address": ";".join([address1, address2]),
                "phone": phonenumber,
                "city": city,
                "state": state,
                "zipcode": postcode,
            },
        )

        return redirect("profile")
    else:
        context = {
            "username": request.user.username,
            "firstname": request.user.first_name,
            "lastname": request.user.last_name,
            "email": request.user.email,
            **BaseService.get_user_details(request.user.id),
        }
        return render(request, "profile.html", context)


@login_required(login_url="/login")
def profile_picture_upload(request):
    try:
        if request.method == "POST":
            image = request.FILES.get("image")
            if not image:
                return JsonResponse({"error": "no image"}, status=400)

            user = UserProfile.objects.filter(user_id=request.user.id).first()
            user_profile_old = None
            if user:
                user_profile_old = os.path.join(
                    settings.BASE_DIR, "media/" + str(user.profile_pic)
                )

            UserProfile.objects.update_or_create(
                user_id=request.user.id,
                defaults={
                    "profile_pic": image,
                },
            )

            if user_profile_old:
                if os.path.exists(user_profile_old):
                    os.remove(user_profile_old)

            return JsonResponse(
                {
                    "success": True,
                    "status": 200,
                    "message": "Upload success",
                }
            )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return render(request, "profile.html")


@login_required(login_url="/login")
def product_listing(request):
    try:
        product_list = Product.objects.all()
        product_list = product_list.order_by("-id")
        return render(request, "productList.html", {"products": product_list})
    except Exception as e:
        print(e)


@login_required(login_url="/login")
def product_details(request):
    try:
        return render(request, "productDetails.html")
    except Exception as e:
        print(e)


@login_required(login_url="/login")
def product_create_update(request, product_code=None):
    product = None

    if product_code:
        product = get_object_or_404(Product, product_code_other=product_code)
    else:
        product = Product()

    options = {}
    option_list = Option.objects.all()
    for option in option_list:
        field_name = option.field_name.replace(" ", "_")
        options.setdefault(field_name, []).append(
            {
                "option_id": option.pk,
                "option_value": option.value,
            }
        )

    if request.method == "POST":
        try:
            BaseService.set_product_data(product, request.POST)
            product.save()
            message = (
                "Product Updated Successfully!"
                if product_code
                else "Product Created Successfully!"
            )
            return redirect("product-update", product_code=product.product_code_other)
        except Exception as e:
            return render(
                request,
                "productDetails.html",
                {"error": str(e), "product": product, "options": options},
            )

    return render(
        request, "productDetails.html", {"product": product, "options": options}
    )


@login_required(login_url="/login")
def product_delete(request, product_code=None):
    if product_code:
        product = get_object_or_404(Product, product_code_other=product_code)

        if product:
            product.delete()

    return redirect("products")


@login_required(login_url="/login")
def option_listing(request):
    try:
        option_list = Option.objects.all()
        option_list = option_list.order_by("-id")
        print(option_list)
        return render(request, "optionList.html", {"options": option_list})
    except Exception as e:
        print(e)


@login_required(login_url="/login")
def option_details(request):
    try:
        return render(request, "optionDetails.html")
    except Exception as e:
        print(e)


@login_required(login_url="/login")
def option_create_update(request, option_id=None):
    option = None

    if option_id:
        option = get_object_or_404(Option, pk=option_id)
    else:
        option = Option()

    if request.method == "POST":
        try:
            field_name = request.POST.get("field_name")
            field_value = request.POST.get("option_value")
            option.field_name = field_name
            option.value = field_value
            option.save()
            message = (
                "Option Updated Successfully!"
                if option_id
                else "Option Created Successfully!"
            )
            return redirect("option-update", option_id=option.pk)
        except Exception as e:
            return render(request, "optionDetails.html", {"error": str(e)})

    return render(request, "optionDetails.html", {"option": option})


@login_required(login_url="/login")
def option_delete(request, option_id=None):
    if option_id:
        option = get_object_or_404(Option, pk=option_id)

        if option:
            option.delete()

    return redirect("options")
