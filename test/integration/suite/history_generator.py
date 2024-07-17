

class HistoryGenerator:

    def __init__(self, amount_files):
        self.amount_files = amount_files

    def create(self):
        existing_files = []
        files = []
        for i in range(self.amount_files):
            file = "/path/to/dir/file%d" % (i)
            existing_files.append(file)
            files.append(file)
        file_history = '\n'.join(files)
        return file_history, existing_files

    def get_first_files(self, n):
        files = []
        for i in range(n):
            file_no = self.amount_files - (i+1)
            file = f"/path/to/dir/file{file_no}"
            files.append(file)
        return files

    def get_last_files(self, n):
        files = []
        for i in range(n):
            file_no = i
            file = f"/path/to/dir/file{file_no}"
            files.append(file)
        return files

    def get_first_file(self, offset=0):
        file_no = self.amount_files - (1+offset)
        file = f"/path/to/dir/file{file_no}"
        return file
