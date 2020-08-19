class APIException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ArgumentsError(APIException):
    def __init__(self, *args):
        message = ','.join(args) + ' 皆空'
        super().__init__(message)


class CannotDownloadError(APIException):
    def __init__(self, code, message):
        message = '「{}」 {}'.format(code, message)
        super().__init__(message)


class UnknownTypeError(APIException):
    def __init__(self, type):
        message = 'Unknown type {}'.format(type)
        super().__init__(message)


class UnsupportTypeError(APIException):
    def __init__(self, type):
        message = 'Not support {} type'.format(type)
        super().__init__(message)


class IsPreviewError(APIException):
    def __init__(self):
        message = 'This video is preview video'
        super().__init__(message)
