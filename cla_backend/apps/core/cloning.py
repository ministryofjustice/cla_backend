def clone_model(cls, pk, config={}):
    """
    NOTE: it does not support cloning many2many and one2many
    fields by design. This is to keep the cloning logic simple
    If you do need to, clone the related objects manually
    """
    if not pk:
        return None

    cloned = cls.objects.get(pk=pk)

    excludes = config.get("excludes", [])
    clone_fks = config.get("clone_fks", [])
    override_values = config.get("override_values", {})

    cloned.pk = None

    # excludes
    for field in excludes:
        fk_field = cls._meta.get_field(field)
        setattr(cloned, field, fk_field.get_default())

    # fks
    for field in clone_fks:
        if field in override_values:
            continue

        fk_field = cls._meta.get_field(field)
        fk_id = getattr(cloned, "%s_id" % fk_field.name)
        fk_clazz = fk_field.rel.to
        cloned_fk = fk_clazz.clone_from_obj(fk_id)
        setattr(cloned, fk_field.name, cloned_fk)

    # overrides
    for field, value in override_values.items():
        setattr(cloned, field, value)

    cloned.save(force_insert=True)

    return cloned


class CloneModelMixin(object):
    cloning_config = {
        "excludes": [],  # these will be set to default vals
        "clone_fks": [],  # fk to be cloned (new obj, new id), other fks will be referenced instead
        "override_values": {},  # dict of val to override during the cloning op
    }

    @classmethod
    def clone_from_obj(cls, pk, config=None):
        config = config or cls.cloning_config
        return clone_model(cls, pk, config)
