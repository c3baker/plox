class PloxError(Exception):
    def __init__(self, line, message):
        super().__init__(message)
        self.line = line
        self.message = message

    def get_error_message(self):
        return "Error on line " + str(self.line) + ": " + self.message

class PloxIterator:

    def __init__(self, element_list):
        self._list = element_list
        self._index = 0

    def list_end(self):
        return True if self._index >= len(self._list) else False

    def get_index(self):
        return self._index

    def get_current(self):
        if self.list_end():
            return None
        return self._list[self._index]

    def previous(self):
        if self._index == 0:
            return None
        return self._list[self._index - 1]

    def advance(self):
        item = self.peek()
        if item is None:
            return
        self._index += 1
        return item

    def peek(self):
        if self.list_end():
            return None
        return self._list[self._index]

    def seek(self, symbol):
        if symbol is None:
            return False
        while self.peek() is not None:
            value = self.advance()
            if value == symbol:
                return True
        return False

    def peek_next(self):
        return None if self.list_end() else self._list[self._index + 1]

def report_error(error):
    if not isinstance(error, PloxError):
        raise Exception("report_error can only report a Plox Exception!")
    print("[ Line %d ] %s" % (error.line, error.get_error_message()))