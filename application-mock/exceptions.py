class EmptyEntry(Exception):

    def __str__(self):
        return 'There can be no empty boxes'


class InvalidPath(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path + ' is not a valid path'


class IncorrectNumberOfImages(Exception):
    def __init__(self, path, expected_count):
        self.path = path
        self.expected_count = expected_count

    def __str__(self):
        return 'LP file requires ' + self.path + ' folder to have ' + str(self.expected_count) + ' images per output'


class InvalidLPStructure(Exception):
    def __init__(self, line):
        self.line = line

    def __str__(self):
        return 'Line ' + self.line + ' violates LP file structure'


class InvalidDomeSize(Exception):
    def __init__(self, size):
        self.size = size

    def __str__(self):
        return self.size + ' is not a valid dome size'


class InvalidProcessor(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path + ' is not a valid PTM or HSH executable'


class ProcessingFailed(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        pass
