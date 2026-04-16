import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import Base, get_db
from app.models import models
import os

# Usamos SQLite para testes rápidos e isolados
# ... (rest of imports and engine setup)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_church.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture que cria/remove tabelas a cada sessão de teste
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    try:
        if os.path.exists("./test_church.db"):
            os.remove("./test_church.db")
    except PermissionError:
        print("Aviso: Não foi possível remover test_church.db porque está em uso.")

# Override do get_db para usar a sessão de teste
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

from app.core import security

@pytest.fixture
def test_church(db_session):
    church = models.Church(name="Igreja Teste QA", slug="qa-test")
    db_session.add(church)
    db_session.commit()
    db_session.refresh(church)
    return church

@pytest.fixture
def test_user(db_session, test_church):
    user = models.User(
        email="qa@test.com",
        name="QA User",
        hashed_password=security.get_password_hash("password"),
        church_id=test_church.id,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def user_token(test_user):
    return security.create_access_token(
        data={"sub": str(test_user.id), "church_id": str(test_user.church_id)}
    )

@pytest.fixture
def auth_client(client, user_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {user_token}"
    }
    return client

@pytest.fixture
def master_user(db_session):
    # Primeiro garante que a igreja master existe
    master_church = db_session.query(models.Church).filter(models.Church.slug == "master").first()
    if not master_church:
        master_church = models.Church(name="SaaS Master", slug="master")
        db_session.add(master_church)
        db_session.commit()
        db_session.refresh(master_church)

    user = models.User(
        email="master@test.com",
        name="Master Admin",
        hashed_password=security.get_password_hash("password"),
        church_id=master_church.id,
        is_admin=True,
        is_master=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def master_token(master_user):
    return security.create_access_token(
        data={"sub": str(master_user.id), "church_id": str(master_user.church_id)}
    )

@pytest.fixture
def master_client(client, master_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {master_token}"
    }
    return client
