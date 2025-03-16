# openlibrarian_root/utils/Importer.py
import pandas as pd
from utils.OpenAI import get_missing_isbns

class Importer:
    """
    Class to import data from various sources
    """

    def __init__(self, src_file, src_type, src_source):
        self.src_file = src_file
        self.src_type = src_type
        self.src_source = src_source
        self.data = None
        self.model_input = None
        self.to_read = None
        self.read = None
        self.currently_reading = None

    def load_file(self):
        """
        Load the file
        """
        if self.src_type == 'csv':
            self.load_csv()

    def load_csv(self):
        """
        Load a CSV file into a dataframe to manipulate more easily
        """
        self.data = pd.read_csv(self.src_file)
    
    def prepare_data(self):
        """
        Prepare dataframe for parsing
        """
        if self.src_source == 'goodreads':
            self.data = self.data[["Title", "Author", "ISBN13", "Number of Pages", "My Rating", "Date Read", "Exclusive Shelf", "My Review"]]
            self.data = self.data.rename(columns={"Title": "title", "Author": "author", "ISBN13": "isbn13", "Number of Pages": "num_pages", "My Rating": "rating", "Date Read": "date_read", "Exclusive Shelf": "shelf", "My Review": "review"})
            self.data = self.data.dropna(subset=['title', 'author'])
            self.data = self.data.fillna('')
            self.data['author'] = self.data['author'].str.replace(r'\s+', ' ', regex=True).str.strip()
            self.data['isbn13'] = self.data['isbn13'].str.replace('"', '').str.replace('=', '')
            self.data['date_read'] = pd.to_datetime(self.data['date_read'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('')
            self.data['num_pages'] = self.data['num_pages'].apply(lambda x: str(int(x)) if x != '' else x)
            self.data['review'] = self.data['review'].str.replace('', 'NA')
            self.data['shelf'] = self.data['shelf'].str.replace('to-read', 'To Read (want)').str.replace('read', 'Have Read').str.replace('currently-reading', 'Currently Reading')
  

    def get_missing_data(self):
        """
        Prepare missing data for AI model to complete
        """
        missing_data = self.data[self.data['isbn13'] == '']
        model_input = []
        # Iterate through the missing_data and create a list of dictionaries that have "title" and "author" populated
        for index, row in missing_data.iterrows():
            model_input.append({
            "title": row["title"],
            "author": row["author"],
            "isbn": None
            })

        self.model_input = model_input
        self.model_output = get_missing_isbns(model_input)
    
    def update_missing_data(self):
        """
        Take the output of the model and use it to populate the missing 
        """
        if self.model_output != None and type(self.model_output) == list:
            for item in self.model_output:
                self.data.loc[
                    (self.data['title'] == item['title']) & (self.data['author'] == item['author']),
                    'isbn13'
                ] = item['isbn']
    
    def split_data(self):
        """
        Split the data into different groups based on the shelves
        """
        if self.src_source == 'goodreads':
            self.to_read = self.data.where(self.data["shelf"]=="to-read").dropna(how="all")
            self.read = self.data.where(self.data["shelf"]=="read").dropna(how="all")
            self.currently_reading = self.data.where(self.data["shelf"]=="currently-reading").dropna(how="all")
