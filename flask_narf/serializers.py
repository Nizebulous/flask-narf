from flask.ext.narf.fields import Field


class Serializer(object):
    """
    Serializer Base class

    For defining the output object of an endpoint
    """

    def __init__(self, raw_data=None, **kwargs):
        """
        Initialize the Serializer

        Collect all the defined Field's for easy access
        """
        super(Serializer, self).__init__(**kwargs)
        self.raw_data = raw_data
        self.fields = []
        for field_name, field in self.__class__.__dict__.items():
            if isinstance(field, Field):
                field.bind(self, field_name, raw_data)
                self.fields.append(field)
