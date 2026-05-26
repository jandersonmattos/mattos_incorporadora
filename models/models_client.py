from .models_core import *

class Cliente(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_type = Column(String(2), nullable=False)
    name = Column(String(255))
    cpf = Column(String(20))
    rg = Column(String(30))
    corporate_name = Column(String(255))
    trade_name = Column(String(255))
    cnpj = Column(String(25))
    email = Column(String(255))
    phone = Column(String(30))
    zip_code = Column(String(12))
    street = Column(String(255))
    number = Column(String(20))
    complement = Column(String(255))
    neighborhood = Column(String(255))
    city = Column(String(255))
    state = Column(String(100))
    country = Column(String(100), default="Brasil")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
