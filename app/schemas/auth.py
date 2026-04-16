from pydantic import BaseModel

class ChurchRegister(BaseModel):
    church_name: str
    admin_name: str
    admin_email: str
    admin_password: str
