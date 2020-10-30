# -*- coding: utf-8 -*-


from sqlalchemy import DATE, Column, Integer, SmallInteger, String, create_engine
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from gaycore.api_spider import get_audios_info
from gaycore.config import AUDIOS_API
# from gaycore.utils import *

