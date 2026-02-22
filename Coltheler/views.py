from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth, User
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from .models import UserProfile, Product, Option, ImportJobs, PoTemplate, Asset
from .services.base_service import BaseService
from .services.tasks import import_product_task, import_po_template_task
import os
from django.conf import settings
from django.core.paginator import Paginator


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


@login_required(login_url="/coltheler/login")
def index(request):
    context = {"user": request.user, **BaseService.get_user_details(request.user.id)}
    return render(request, "index.html", context)


@login_required(login_url="/coltheler/login")
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


@login_required(login_url="/coltheler/login")
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


@login_required(login_url="/coltheler/login")
def product_listing(request):
    try:
        products_qs = Product.objects.all()

        paginator = Paginator(products_qs, 50)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        return render(request, "productList.html", {"page_obj": page_obj})
    except Exception as e:
        print(e)


@login_required(login_url="/coltheler/login")
def product_details(request):
    try:
        return render(request, "productDetails.html")
    except Exception as e:
        print(e)


@login_required(login_url="/coltheler/login")
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


@login_required(login_url="/coltheler/login")
def product_delete(request, product_code=None):
    if product_code:
        product = get_object_or_404(Product, product_code_other=product_code)

        if product:
            product.delete()

    return redirect("products")


@login_required(login_url="/coltheler/login")
def option_listing(request):
    try:
        options_qs = Option.objects.all()

        paginator = Paginator(options_qs, 20)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        return render(request, "optionList.html", {"page_obj": page_obj})
    except Exception as e:
        print(e)


@login_required(login_url="/coltheler/login")
def option_details(request):
    try:
        return render(request, "optionDetails.html")
    except Exception as e:
        print(e)


@login_required(login_url="/coltheler/login")
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


@login_required(login_url="/coltheler/login")
def option_delete(request, option_id=None):
    if option_id:
        option = get_object_or_404(Option, pk=option_id)

        if option:
            option.delete()

    return redirect("options")


@login_required(login_url="/coltheler/login")
def import_products(request):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"message": "No file provided"}, status=400)

    asset = _create_asset_from_upload(file, request.user, "imports/products")
    file_path = os.path.join(settings.MEDIA_ROOT, asset.file.name)

    job = ImportJobs.objects.create(
        file_path=file_path,
        status="pending",
    )

    import_product_task.delay(job.pk)

    return JsonResponse({"message": "Import started", "job_id": job.pk})


@login_required(login_url="/coltheler/login")
def import_status(request, job_id=None):
    job = ImportJobs.objects.get(pk=job_id)
    return JsonResponse(
        {"status": job.status, "processed": job.processed_rows, "total": job.total_rows}
    )


@login_required(login_url="/coltheler/login")
def po_template_listing(request):
    try:
        po_template_qs = PoTemplate.objects.all()

        paginator = Paginator(po_template_qs, 50)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)
        return render(request, "poTemplateList.html", {"page_obj": page_obj})
    except Exception as e:
        print(e)


@login_required(login_url="/coltheler/login")
def po_template_details(request):
    po_template = PoTemplate()
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
            BaseService.set_po_template_data(po_template, request.POST)
            po_template.save()
            return redirect(
                "po-template-details-create",
                reference=po_template.reference,
                sku=po_template.sku,
            )
        except Exception as e:
            return render(
                request,
                "poTemplateDetails.html",
                {"error": str(e), "poTemplate": po_template, "options": options},
            )

    return render(
        request,
        "poTemplateDetails.html",
        {"poTemplate": po_template, "options": options},
    )


@login_required(login_url="/coltheler/login")
def po_template_create_update(request, reference=None, sku=None):
    po_template = None

    if reference and sku:
        po_template = get_object_or_404(PoTemplate, reference=reference, sku=sku)
    else:
        po_template = PoTemplate()

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
            BaseService.set_po_template_data(po_template, request.POST)
            po_template.save()
            return redirect(
                "po-template-details-create",
                reference=po_template.reference,
                sku=po_template.sku,
            )
        except Exception as e:
            return render(
                request,
                "poTemplateDetails.html",
                {"error": str(e), "poTemplate": po_template, "options": options},
            )

    return render(
        request,
        "poTemplateDetails.html",
        {"poTemplate": po_template, "options": options},
    )


@login_required(login_url="/coltheler/login")
def po_template_delete(request, reference=None, sku=None):
    if reference and sku:
        po_template = get_object_or_404(PoTemplate, reference=reference, sku=sku)

        if po_template:
            po_template.delete()

    return redirect("po-templates")


@login_required(login_url="/coltheler/login")
def import_po_template(request):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"message": "No file provided"}, status=400)

    asset = _create_asset_from_upload(file, request.user, "imports/po-templates")
    file_path = os.path.join(settings.MEDIA_ROOT, asset.file.name)

    job = ImportJobs.objects.create(
        file_path=file_path,
        status="pending",
    )

    import_po_template_task.delay(job.pk)

    return JsonResponse({"message": "Import started", "job_id": job.pk})


@login_required(login_url="/coltheler/login")
def import_jobs_listing(request):
    try:
        jobs_qs = ImportJobs.objects.all().order_by("-created_at")
        paginator = Paginator(jobs_qs, 50)
        page = request.GET.get("page")
        page_obj = paginator.get_page(page)

        media_root = os.path.normpath(settings.MEDIA_ROOT)
        job_rel_paths = []
        job_rows = []

        for job in page_obj.object_list:
            rel_path = None
            normalized = os.path.normpath(job.file_path or "")
            if normalized.startswith(media_root + os.sep):
                rel_path = normalized[len(media_root) + 1 :].replace("\\", "/")
                job_rel_paths.append(rel_path)
            job_rows.append({"job": job, "rel_path": rel_path})

        asset_map = {}
        if job_rel_paths:
            assets = _asset_queryset_for_user(request.user).filter(file__in=job_rel_paths)
            for asset in assets:
                asset_map[str(asset.file)] = asset

        for row in job_rows:
            asset = asset_map.get(row["rel_path"])
            row["asset"] = asset
            row["display_path"] = row["rel_path"] or "Unavailable"
            if asset:
                if asset.relative_dir:
                    row["asset_open_url"] = (
                        f"{reverse('asset-library')}?path={asset.relative_dir}"
                    )
                else:
                    row["asset_open_url"] = reverse("asset-library")
            else:
                row["asset_open_url"] = None

        return render(request, "importList.html", {"page_obj": page_obj, "job_rows": job_rows})
    except Exception as e:
        print(e)


def _asset_queryset_for_user(user):
    queryset = Asset.objects.select_related("uploaded_by").order_by(
        "relative_dir", "original_name"
    )
    if user.is_superuser:
        return queryset
    return queryset.filter(uploaded_by=user)


def _normalize_asset_path(path):
    if not path:
        return ""
    clean = str(path).replace("\\", "/").strip("/")
    if ".." in clean.split("/"):
        return ""
    return clean


def _format_size(size):
    units = ["B", "KB", "MB", "GB"]
    value = float(size or 0)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024


def _create_asset_from_upload(uploaded_file, user, relative_dir):
    asset = Asset(
        uploaded_by=user,
        original_name=os.path.basename(uploaded_file.name),
        size=uploaded_file.size or 0,
        content_type=getattr(uploaded_file, "content_type", "") or "",
        relative_dir=relative_dir,
    )
    asset.file = uploaded_file
    asset.save()
    asset.relative_dir = relative_dir
    asset.save(update_fields=["relative_dir", "updated_at"])
    return asset


@login_required(login_url="/coltheler/login")
def asset_listing(request):
    current_path = _normalize_asset_path(request.GET.get("path", ""))
    queryset = _asset_queryset_for_user(request.user)

    folders = set()
    files = []
    for asset in queryset:
        asset_dir = _normalize_asset_path(asset.relative_dir)
        asset_name = os.path.basename(asset.file.name)

        if current_path:
            if asset_dir == current_path:
                files.append(
                    {
                        "asset": asset,
                        "name": asset_name,
                        "size_display": _format_size(asset.size),
                    }
                )
            elif asset_dir.startswith(current_path + "/"):
                remainder = asset_dir[len(current_path) + 1 :]
                next_folder = remainder.split("/", 1)[0]
                if next_folder:
                    folders.add(next_folder)
        else:
            if asset_dir:
                folders.add(asset_dir.split("/", 1)[0])
            else:
                files.append(
                    {
                        "asset": asset,
                        "name": asset_name,
                        "size_display": _format_size(asset.size),
                    }
                )

    folder_items = []
    for folder in sorted(folders):
        path = f"{current_path}/{folder}" if current_path else folder
        folder_items.append({"name": folder, "path": path})

    breadcrumbs = []
    if current_path:
        parts = current_path.split("/")
        acc = []
        for part in parts:
            acc.append(part)
            breadcrumbs.append({"name": part, "path": "/".join(acc)})
    parent_path = "/".join(current_path.split("/")[:-1]) if current_path else ""

    return render(
        request,
        "assetList.html",
        {
            "folder_items": folder_items,
            "files": files,
            "current_path": current_path,
            "parent_path": parent_path,
            "breadcrumbs": breadcrumbs,
            "is_superuser": request.user.is_superuser,
        },
    )


@login_required(login_url="/coltheler/login")
def asset_upload(request):
    if request.method != "POST":
        return redirect("asset-library")

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return redirect("asset-library")

    asset = Asset(
        uploaded_by=request.user,
        original_name=os.path.basename(uploaded_file.name),
        size=uploaded_file.size or 0,
        content_type=getattr(uploaded_file, "content_type", "") or "",
    )
    asset.file = uploaded_file
    asset.save()

    relative_path = asset.file.name
    if relative_path.startswith("assets/"):
        relative_path = relative_path[len("assets/") :]
    relative_dir = os.path.dirname(relative_path)
    asset.relative_dir = "" if relative_dir == "." else relative_dir
    asset.save(update_fields=["relative_dir", "updated_at"])

    return redirect("asset-library")


@login_required(login_url="/coltheler/login")
def asset_download(request, asset_id):
    asset = get_object_or_404(_asset_queryset_for_user(request.user), pk=asset_id)
    return FileResponse(
        asset.file.open("rb"),
        as_attachment=True,
        filename=asset.original_name or os.path.basename(asset.file.name),
    )


@login_required(login_url="/coltheler/login")
def asset_delete(request, asset_id):
    if request.method != "POST":
        return redirect("asset-library")

    asset = get_object_or_404(_asset_queryset_for_user(request.user), pk=asset_id)
    current_path = _normalize_asset_path(request.POST.get("path", ""))
    asset.file.delete(save=False)
    asset.delete()

    if current_path:
        return redirect(f"{reverse('asset-library')}?path={current_path}")
    return redirect("asset-library")
