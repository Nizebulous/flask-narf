# TODO(Dom): No testing here yet

class Deserializer(object):
    """
    Deserializer Base class

    For defining the input object of an endpoint
    """

    def __init__(self, **kwargs):
        super(Deserializer, self).__init__(**kwargs)

    def validate(self):
        pass
