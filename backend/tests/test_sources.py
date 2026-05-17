import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from app.db_models import CollectorSource
from app.main import app
from app.database import get_session

@pytest.fixture(name="test_session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

from app.routers.internal import verify_internal_key

@pytest.fixture(name="client")
def client_fixture(test_session: Session):
    def get_session_override():
        yield test_session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_internal_key] = lambda: None
    
    # Patch engine everywhere it might be used directly
    import app.database as db_mod
    import app.routers.internal as internal_mod
    orig_db_engine = db_mod.engine
    orig_int_engine = internal_mod.engine
    
    db_mod.engine = test_session.get_bind()
    internal_mod.engine = test_session.get_bind()

    with TestClient(app) as client:
        yield client

    db_mod.engine = orig_db_engine
    internal_mod.engine = orig_int_engine
    app.dependency_overrides.clear()


def test_create_valid_greenhouse_source(client: TestClient, test_session: Session):
    response = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Test Greenhouse",
            "source_type": "greenhouse",
            "board_token": "test-board"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Test Greenhouse"
    assert data["source_type"] == "greenhouse"
    assert data["board_token"] == "test-board"

    # Verify DB
    db_src = test_session.exec(select(CollectorSource).where(CollectorSource.company_name == "Test Greenhouse")).first()
    assert db_src is not None

def test_create_valid_lever_source(client: TestClient, test_session: Session):
    response = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Test Lever",
            "source_type": "lever",
            "company_id": "test-company"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "lever"
    assert data["company_id"] == "test-company"

def test_create_invalid_source_type(client: TestClient):
    response = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Invalid",
            "source_type": "workday"
        }
    )
    assert response.status_code == 422

def test_reject_missing_identifiers(client: TestClient):
    # Missing board_token for greenhouse
    response1 = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Test",
            "source_type": "greenhouse"
        }
    )
    assert response1.status_code == 422

    # Missing company_id for lever
    response2 = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Test",
            "source_type": "lever"
        }
    )
    assert response2.status_code == 422

def test_reject_duplicate_active_source(client: TestClient, test_session: Session):
    src = CollectorSource(company_name="Company1", source_type="lever", company_id="dup")
    test_session.add(src)
    test_session.commit()

    # Should reject same company_id
    response = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Company2",
            "source_type": "lever",
            "company_id": "dup"
        }
    )
    assert response.status_code == 400

    # Should allow same company_name but different company_id
    response2 = client.post(
        "/api/v1/internal/sources",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "company_name": "Company1",
            "source_type": "lever",
            "company_id": "different"
        }
    )
    assert response2.status_code == 200

def test_patch_rejects_invalid_config(client: TestClient, test_session: Session):
    src = CollectorSource(company_name="Patch Invalid", source_type="lever", company_id="patch1")
    test_session.add(src)
    test_session.commit()
    test_session.refresh(src)

    # Change to greenhouse without board_token
    response = client.patch(
        f"/api/v1/internal/sources/{src.id}",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "source_type": "greenhouse",
            "company_id": None
        }
    )
    assert response.status_code == 422

def test_patch_disables_source(client: TestClient, test_session: Session):
    src = CollectorSource(company_name="To Disable", source_type="lever", company_id="td")
    test_session.add(src)
    test_session.commit()
    test_session.refresh(src)

    response = client.patch(
        f"/api/v1/internal/sources/{src.id}",
        headers={"X-Internal-API-Key": "test-internal-key"},
        json={
            "enabled": False
        }
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is False

def test_delete_soft_disables_source(client: TestClient, test_session: Session):
    src = CollectorSource(company_name="To Delete", source_type="lever", company_id="del")
    test_session.add(src)
    test_session.commit()
    test_session.refresh(src)

    response = client.delete(
        f"/api/v1/internal/sources/{src.id}",
        headers={"X-Internal-API-Key": "test-internal-key"}
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is False

def test_disabled_source_skipped_by_collect_all(client: TestClient, test_session: Session):
    # Create one enabled and one disabled
    src1 = CollectorSource(company_name="Enabled Src", source_type="lever", company_id="en", enabled=True)
    src2 = CollectorSource(company_name="Disabled Src", source_type="lever", company_id="dis", enabled=False)
    test_session.add(src1)
    test_session.add(src2)
    test_session.commit()

    response = client.post(
        "/api/v1/internal/collect/all",
        headers={"X-Internal-API-Key": "test-internal-key"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # "Enabled Src" should be in results, "Disabled Src" should not
    # Actually, the default seeds might be there too, so we just check what's returned
    companies = [r["company"] for r in data.get("results", [])]
    assert "Enabled Src" in companies
    assert "Disabled Src" not in companies
