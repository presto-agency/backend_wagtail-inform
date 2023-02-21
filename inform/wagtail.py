from django.db.models import ProtectedError
from django.urls import reverse
from wagtail.admin import messages
from wagtail.core.models import Page
from wagtail.images import get_image_model
from wagtail.images.views.images import delete


def delete_image(request, image_id):
    """
    Images are protected from deletion using models.PROTECT when they are used.
    This causes 500 error in Wagtail admin.
    This wrapper of the Wagtail image delete view handles this gracefully.
    """
    try:
        result = delete(request, image_id)
    except ProtectedError as pe:
        image = get_image_model().objects.get(id=image_id)
        item = next(iter(pe.protected_objects))
        item_class_name = str(item._meta.verbose_name)

        if isinstance(item, Page):
            edit_link = reverse("wagtailadmin_pages:edit", args=(item.id,))
        else:
            edit_link = None

        messages.error(
            request,
            f"Image {image.title} cannot be removed because it's used in "
            f"{str(item)}.",
            buttons=[
                messages.button(
                    edit_link, text=f"Go to the conflicting {item_class_name}"
                )
            ] if edit_link else None,
        )

        # POST means that the view will try (unsuccessfully) to remove the image,
        # so we change that to GET.
        request.method = "GET"
        result = delete(request, image_id)

    return result
