from rest_framework import status

class Error(Exception):
    pass

class DsapException(Exception):
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code

class DsapNoAnswerException(DsapException):
    pass

class DsapEppException(DsapException):
    pass

class InvalidCdsException(DsapException):
    pass