import traceback
import sys
import os
#from setuptools.command.easy_install import get_exe_prefixes

class CustomException(Exception):
    def __init__ (self ,error_message , error_details:sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_error_message(error_message, error_details)

    #@staticmethod
    # def get_detailed_error_message(error_message,error_details:sys):
    #     _ , _ , exc_tb=  error_details.exc_info()
    #     file_name = exc_tb.tb_frame.f_code.co_filename        
    #     line_number = exc_tb.tb_lineno
    #     return f"Error in {file_name} , line {line_number} : {error_message}"
    def get_detailed_error_message(self, error_message, error_details: Exception):
            exc_type, exc_obj, exc_tb = sys.exc_info()
            return f"{error_message} | Exception type: {exc_type}, Details: {str(error_details)}, Line: {exc_tb.tb_lineno}"
    def __str__(self):
        return self.error_message