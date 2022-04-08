from urllib.parse import quote_plus as urlquote

from sqlalchemy import create_engine

user = "root"
password = "his@9000"
address = "localhost"
port = "3306"
database = "fund_io"
engine = create_engine(f'mysql+pymysql://{user}:{urlquote(password)}@{address}:{port}/{database}?charset=utf8')
