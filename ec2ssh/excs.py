class UsageError(Exception):
    pass


class AWSError(Exception):
    def __init__(self, response):
        self.response = response
        super(AWSError, self).__init__('Error: %s' % response.error)
