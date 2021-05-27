class APIException(Exception):
    def __init__(self, code, message):
        super().__init__(code, message)
        self.code = code
        self.message = message


class ArgumentsError(APIException):
    def __init__(self, *args):
        message = "参数 " + ",".join(args) + " 均空"
        super().__init__(101, message)


class CannotDownloadError(APIException):
    def __init__(self, code, message):
        message = "「{}」 {}".format(code, message)
        super().__init__(102, message)


class UnknownTypeError(APIException):
    def __init__(self, type):
        message = "未知类型：{}".format(type)
        super().__init__(103, message)


class UnsupportTypeError(APIException):
    def __init__(self, type):
        message = "不受支持的类型：{}".format(type)
        super().__init__(104, message)


class IsPreviewError(APIException):
    def __init__(self):
        message = "本视频是预览视频"
        super().__init__(105, message)


class MaxRetryError(APIException):
    def __init__(self):
        message = "超出最大重试次数"
        super().__init__(106, message)
