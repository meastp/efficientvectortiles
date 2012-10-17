#
# this file contains the abstract base class for data formats
#

import abc

class BaseFormat :
    __metaclass__ = abc.ABCMeta
    
    #whether the format is binary
    @abc.abstractproperty
    def is_binary(self):
        return NotImplementedError
    
    #the list of database tables/layers this format uses
    @property
    def table_list(self):
        return self.db_table_list
    
    #table_list for reverse lookup
    @property
    def table_list_reversed(self):
        return self.db_table_list_reverse
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = list()
        
        self.db_table_list = dict()
        self.db_table_list_reverse = dict()
    
    def get_query_list(self):
        return self.query
    
    @abc.abstractmethod
    def process_data(self, query_result):
        return NotImplementedError
