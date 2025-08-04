from sqlite_repository import BaseSQLiteRepository, BaseSQLiteService
from models.patient import Patient
from utils.singleton import SingletonMeta
import database

class PatientService(BaseSQLiteService[Patient], metaclass=SingletonMeta):
    def __init__(self):
        repository = BaseSQLiteRepository(database.patients, Patient)
        super().__init__(repository) 