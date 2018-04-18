from .helpers import kong_client_using_settings


# pylint: disable=too-few-public-methods
class DeleteKongOnDeleteMixin:
    def delete(self, using=None, keep_parents=False):

        self.delete_kong(kong_client_using_settings())

        return super().delete(using=using, keep_parents=keep_parents)


# pylint: disable=too-few-public-methods
class ManageKongOnSaveMixin:
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.manage_kong(kong_client_using_settings())

        return super().save(force_insert=force_insert,
                            force_update=force_update,
                            using=using,
                            update_fields=update_fields)
