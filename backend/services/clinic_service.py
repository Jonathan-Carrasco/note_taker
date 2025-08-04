from sqlite_repository import BaseSQLiteRepository, BaseSQLiteService
from models.clinic import Clinic  
from utils.singleton import SingletonMeta
import database

class ClinicService(BaseSQLiteService[Clinic], metaclass=SingletonMeta):
    def __init__(self):
        repository = BaseSQLiteRepository(database.clinics, Clinic)
        super().__init__(repository) 