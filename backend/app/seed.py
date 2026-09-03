import os
import sys
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.booking import Booking
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import hash_password


def seed_data():
    db = SessionLocal()
    try:
        # Seed user phone numbers
        seed_phones = [
            "9000000000",  # Admin User
            "9111111111",  # Suresh Kumar
            "9222222222",  # Priya Gupta
            "9333333333",  # Anil Yadav
            "9444444444",  # Meena Verma
            "9555555555",  # Ravi Sharma
            "9666666666",  # Priya Customer
        ]

        # Cleanup existing seed data for idempotency
        existing_users = db.query(User).filter(User.phone.in_(seed_phones)).all()
        if existing_users:
            user_ids = [u.id for u in existing_users]
            # Delete bookings involving these users
            db.query(Booking).filter(
                (Booking.citizen_id.in_(user_ids)) | (Booking.worker_id.in_(user_ids))
            ).delete(synchronize_session=False)
            # Delete worker profiles
            db.query(WorkerProfile).filter(WorkerProfile.user_id.in_(user_ids)).delete(
                synchronize_session=False
            )
            # Delete users
            db.query(User).filter(User.id.in_(user_ids)).delete(
                synchronize_session=False
            )
            db.commit()
            print(f"Cleaned up {len(existing_users)} existing seed user(s).")

        default_password_hash = hash_password("password123")

        # 0. Create Admin
        admin_user = User(
            name="Admin User",
            phone="9000000000",
            password_hash=default_password_hash,
            role="admin",
        )
        db.add(admin_user)
        db.flush()

        # 1. Create Citizens
        ravi = User(
            name="Ravi Sharma",
            phone="9555555555",
            password_hash=default_password_hash,
            role="citizen",
        )
        priya_customer = User(
            name="Priya Customer",
            phone="9666666666",
            password_hash=default_password_hash,
            role="citizen",
        )
        db.add_all([ravi, priya_customer])
        db.flush()

        # 2. Create Workers
        # Suresh Kumar (Expected Rank: 1st)
        suresh_user = User(
            name="Suresh Kumar",
            phone="9111111111",
            password_hash=default_password_hash,
            role="worker",
        )
        db.add(suresh_user)
        db.flush()
        suresh_profile = WorkerProfile(
            user_id=suresh_user.id,
            skill="electrician",
            lat=Decimal("26.9280"),
            lng=Decimal("75.8100"),
            rating=Decimal("4.2"),
            availability=True,
            verification_status="verified",
        )
        db.add(suresh_profile)

        # Priya Gupta (Expected Rank: 2nd, new worker, rating null)
        priya_worker_user = User(
            name="Priya Gupta",
            phone="9222222222",
            password_hash=default_password_hash,
            role="worker",
        )
        db.add(priya_worker_user)
        db.flush()
        priya_worker_profile = WorkerProfile(
            user_id=priya_worker_user.id,
            skill="electrician",
            lat=Decimal("26.8800"),
            lng=Decimal("75.7600"),
            rating=None,
            availability=True,
            verification_status="verified",
        )
        db.add(priya_worker_profile)

        # Anil Yadav (Expected Rank: 3rd)
        anil_user = User(
            name="Anil Yadav",
            phone="9333333333",
            password_hash=default_password_hash,
            role="worker",
        )
        db.add(anil_user)
        db.flush()
        anil_profile = WorkerProfile(
            user_id=anil_user.id,
            skill="electrician",
            lat=Decimal("26.9200"),
            lng=Decimal("75.8000"),
            rating=Decimal("4.5"),
            availability=True,
            verification_status="verified",
        )
        db.add(anil_profile)

        # Meena Verma (Expected Rank: 4th)
        meena_user = User(
            name="Meena Verma",
            phone="9444444444",
            password_hash=default_password_hash,
            role="worker",
        )
        db.add(meena_user)
        db.flush()
        meena_profile = WorkerProfile(
            user_id=meena_user.id,
            skill="electrician",
            lat=Decimal("26.9130"),
            lng=Decimal("75.7880"),
            rating=Decimal("4.9"),
            availability=True,
            verification_status="verified",
        )
        db.add(meena_profile)

        db.flush()

        # 3. Create Completed Bookings for Weekly Earnings calculation (job_price * 0.95 = target_earnings)
        suresh_booking = Booking(
            citizen_id=ravi.id,
            worker_id=suresh_user.id,
            skill="electrician",
            lat=Decimal("26.9280"),
            lng=Decimal("75.8100"),
            description="Electrical wiring repair",
            job_price=Decimal("210.53"),  # 200 / 0.95
            platform_fee=Decimal("10.53"),
            status="completed",
        )

        anil_booking = Booking(
            citizen_id=ravi.id,
            worker_id=anil_user.id,
            skill="electrician",
            lat=Decimal("26.9200"),
            lng=Decimal("75.8000"),
            description="Switchboard & MCB installation",
            job_price=Decimal("2105.26"),  # 2000 / 0.95
            platform_fee=Decimal("105.26"),
            status="completed",
        )

        meena_booking = Booking(
            citizen_id=priya_customer.id,
            worker_id=meena_user.id,
            skill="electrician",
            lat=Decimal("26.9130"),
            lng=Decimal("75.7880"),
            description="Full apartment rewiring",
            job_price=Decimal("4736.84"),  # 4500 / 0.95
            platform_fee=Decimal("236.84"),
            status="completed",
        )

        db.add_all([suresh_booking, anil_booking, meena_booking])
        db.commit()

        print("Successfully seeded database:")
        print("  - 1 Admin (Admin User)")
        print("  - 2 Citizens (Ravi Sharma, Priya Customer)")
        print("  - 4 Workers (Suresh Kumar, Priya Gupta, Anil Yadav, Meena Verma)")
        print("  - 3 Completed Bookings for weekly earnings calculation")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
