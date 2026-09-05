import uuid
from decimal import Decimal

from conftest import TestingSessionLocal
from fastapi.testclient import TestClient

from app.main import app
from app.models.booking import Booking

client = TestClient(app)


def test_create_enterprise_bulk_booking_success():
    payload = {
        "institution_name": "District Collectorate, Jaipur",
        "bookings": [
            {
                "skill": "electrician",
                "quantity": 4,
                "schedule": "weekly_monday",
                "months": 1,
            },
            {
                "skill": "cleaner",
                "quantity": 22,
                "schedule": "daily",
                "months": 1,
            },
        ],
    }

    response = client.post("/enterprise/bookings", json=payload)
    assert response.status_code == 201

    data = response.json()
    # Validate contract ID is a valid UUID
    assert "contract_id" in data
    uuid.UUID(data["contract_id"])

    assert data["institution"] == "District Collectorate, Jaipur"
    assert data["total_bookings"] == 26
    assert data["cooperative_workers_needed"] > 0

    # Line item 1: 4 electricians * ₹500 * 4 days/month = ₹8,000
    # Line item 2: 22 cleaners * ₹400 * 22 days/month = ₹193,600
    expected_electrician_monthly = Decimal("500.00") * 4 * 4
    expected_cleaner_monthly = Decimal("400.00") * 22 * 22
    expected_total_monthly = expected_electrician_monthly + expected_cleaner_monthly
    expected_welfare = (expected_total_monthly * Decimal("0.05")).quantize(
        Decimal("0.01")
    )

    assert Decimal(str(data["estimated_monthly_cost"])) == expected_total_monthly
    assert Decimal(str(data["welfare_fund_contribution"])) == expected_welfare
    assert len(data["line_items"]) == 2

    # Check line items structure
    item1 = data["line_items"][0]
    assert item1["skill"] == "electrician"
    assert item1["quantity"] == 4
    assert item1["schedule_multiplier"] == 4
    assert Decimal(str(item1["monthly_cost"])) == expected_electrician_monthly
    assert Decimal(str(item1["total_cost"])) == expected_electrician_monthly

    item2 = data["line_items"][1]
    assert item2["skill"] == "cleaner"
    assert item2["quantity"] == 22
    assert item2["schedule_multiplier"] == 22
    assert Decimal(str(item2["monthly_cost"])) == expected_cleaner_monthly
    assert Decimal(str(item2["total_cost"])) == expected_cleaner_monthly


def test_enterprise_schedule_multipliers():
    payload = {
        "institution_name": "Municipal Corporation",
        "bookings": [
            {"skill": "plumber", "quantity": 1, "schedule": "daily", "months": 3},
            {
                "skill": "carpenter",
                "quantity": 1,
                "schedule": "biweekly",
                "months": 3,
            },
            {"skill": "painter", "quantity": 1, "schedule": "monthly", "months": 3},
        ],
    }

    response = client.post("/enterprise/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()

    line_items = data["line_items"]
    assert line_items[0]["schedule_multiplier"] == 22  # daily
    assert line_items[1]["schedule_multiplier"] == 2  # biweekly
    assert line_items[2]["schedule_multiplier"] == 1  # monthly

    # Check multi-month total cost = monthly_cost * 3
    for item in line_items:
        monthly = Decimal(str(item["monthly_cost"]))
        total = Decimal(str(item["total_cost"]))
        assert total == monthly * 3


def test_enterprise_skill_normalization():
    payload = {
        "institution_name": "Health Department",
        "bookings": [
            {"skill": "  ELECTRICIAN  ", "quantity": 2, "schedule": "weekly"},
            {"skill": "unknown_custom_skill", "quantity": 1, "schedule": "daily"},
        ],
    }

    response = client.post("/enterprise/bookings", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Electrician rate = 500
    assert Decimal(str(data["line_items"][0]["base_rate"])) == Decimal("500.00")
    # Unknown skill fallback rate = 500
    assert Decimal(str(data["line_items"][1]["base_rate"])) == Decimal("500.00")


def test_enterprise_validation_empty_institution():
    payload = {
        "institution_name": "   ",
        "bookings": [{"skill": "electrician", "quantity": 1, "schedule": "daily"}],
    }
    response = client.post("/enterprise/bookings", json=payload)
    assert response.status_code == 422


def test_enterprise_validation_empty_bookings():
    payload = {
        "institution_name": "District Office",
        "bookings": [],
    }
    response = client.post("/enterprise/bookings", json=payload)
    assert response.status_code == 422


def test_enterprise_validation_invalid_quantity_and_months():
    payload = {
        "institution_name": "District Office",
        "bookings": [
            {"skill": "cleaner", "quantity": 0, "schedule": "daily", "months": 0}
        ],
    }
    response = client.post("/enterprise/bookings", json=payload)
    assert response.status_code == 422


def test_enterprise_no_db_booking_side_effects():
    db = TestingSessionLocal()
    try:
        initial_count = db.query(Booking).count()

        payload = {
            "institution_name": "State Secretariat",
            "bookings": [
                {
                    "skill": "cleaner",
                    "quantity": 10,
                    "schedule": "daily",
                    "months": 12,
                }
            ],
        }
        response = client.post("/enterprise/bookings", json=payload)
        assert response.status_code == 201

        final_count = db.query(Booking).count()
        assert initial_count == final_count
    finally:
        db.close()
