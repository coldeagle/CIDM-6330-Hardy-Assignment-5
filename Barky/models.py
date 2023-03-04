class Bookmark(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
        if 'title' in kwargs:
            self.title = kwargs['title']
        if 'url' in kwargs:
            self.url = kwargs['url']
        if 'notes' in kwargs:
            self.notes = kwargs['notes']
        if 'date_added' in kwargs:
            self.date_added = kwargs['date_added']

        
