class APIException(Exception):
    def __init__(self, code, message):
        super().__init__(code, message)
        self.code = code
        self.message = message


class ArgumentsError(APIException):
    def __init__(self, *args):
        message = ",".join(args) + " are all empty"
        super().__init__(101, message)


class CannotDownloadError(APIException):
    def __init__(self, code, message):
        message = "「{}」 {}".format(code, message)
        super().__init__(102, message)


class UnknownTypeError(APIException):
    def __init__(self, type):
        message = "Unknown type {}".format(type)
        super().__init__(103, message)


class UnsupportTypeError(APIException):
    def __init__(self, type):
        message = "Not support {} type".format(type)
        super().__init__(104, message)


class IsPreviewError(APIException):
    def __init__(self):
        message = "This video is preview video"
        super().__init__(105, message)
