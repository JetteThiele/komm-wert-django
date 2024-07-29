class MetaInterface(type):
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(instance)

    def __subclasscheck__(cls, subclass) -> bool:
        method_list = [method for method in dir(cls) if method.startswith('__') is False]
        is_subclass = True
        for method in method_list:
            is_subclass = hasattr(subclass, method) and callable(getattr(subclass, method))
            if not is_subclass:
                break
        return is_subclass


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MetaAttributeHolder(object):
    """Abstract base class that provides __repr__.

    The __repr__ method returns a string in the format::
        ClassName(attr=name, attr=name, ...)
    The attributes are determined either by a class-level attribute,
    '_kwarg_names', or by inspecting the instance __dict__.
    """

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            if name.isidentifier():
                arg_strings.append('%s=%r' % (name, value))
            else:
                star_args[name] = value
        if star_args:
            arg_strings.append('**%s' % repr(star_args))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get_kwargs(self):
        return sorted(self.__dict__.items())

    @staticmethod
    def _get_args():
        return []


class Meta:
    interface = MetaInterface
    singleton = MetaSingleton
    attribute_holder = MetaAttributeHolder
