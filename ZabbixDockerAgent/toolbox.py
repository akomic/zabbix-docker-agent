class AppError(Exception):
    def __init__(self, *args):
        self.raw_response = args[0]
        super(AppError, self).__init__(
            u'AppError')
