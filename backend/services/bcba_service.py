from sqlite_repository import BaseSQLiteRepository, BaseSQLiteService
from models.bcba import Bcba
from utils.singleton import SingletonMeta
import database

class BcbaService(BaseSQLiteService[Bcba], metaclass=SingletonMeta):
    def __init__(self):
        repository = BaseSQLiteRepository(database.bcbas, Bcba)
        super().__init__(repository) 