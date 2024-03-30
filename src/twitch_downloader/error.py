class ChannelNameInputError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'ChannelNameInputError: {self.message}'
    
class HTMLParsingError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'HTMLParsingError: {self.message}'