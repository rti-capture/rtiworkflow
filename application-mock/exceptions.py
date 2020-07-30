class EmptyEntry(Exception):

    def __str__(self):
        return 'There can be no empty boxes'


class NotDigit(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value) + ' is not a valid int'


class InvalidPath(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path + ' is not a valid path'


class NotWithinRange(Exception):
    def __init__(self, value, min_value, max_value):
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    def __str__(self):
        return str(self.value) + ' -> is not within Range(' + str(self.min_value) + ', ' + str(self.max_value) + ')'


class InvalidProcessor(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path + ' is not a valid PTM or HSH executable'


class NotExpectedCount(Exception):
    def __init__(self, expected_count, count):
        self.expected_count = expected_count
        self.count = count

    def __str__(self):
        return 'Expected Count:' + self.expected_count + '\n' + 'Actual Count:' + self.count


class ProcessingFailed(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        pass
