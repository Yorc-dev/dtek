def shared_pre_delete(sender, instance, **kwargs):
    for field in instance._meta.many_to_many:
        field_name = field.name
        related_manager = getattr(instance, field_name)
        if related_manager:
            related_manager.clear()
