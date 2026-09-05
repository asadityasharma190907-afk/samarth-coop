import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.booking import Booking
from app.models.booking_offer import BookingOffer
from app.models.user import User
from app.models.worker_profile import WorkerProfile
from app.services.auth import hash_password


def seed_demo_data():
    """
    Seeds a rich, realistic, multi-persona demonstration dataset.
    Covers:
      - Ministry / Federation view: Metrics, earnings chart across all buckets, pending verifications, active disputes, CSV export.
      - Citizen view: Active booking in progress, unrated completed booking with Star Rating prompt, disputed booking, clean booking wizard.
      - Worker view: Inbox with pending offer, active in-progress job, wallet with earnings & welfare fund, pending verification review banner.
    """
    db = SessionLocal()
    try:
        print("Starting comprehensive demo data seeding...")

        # 1. Clean up all existing demo/seed data
        db.query(BookingOffer).delete(synchronize_session=False)
        db.query(Booking).delete(synchronize_session=False)
        db.query(WorkerProfile).delete(synchronize_session=False)
        db.query(User).delete(synchronize_session=False)
        db.commit()
        print("Cleaned up previous database records.")

        default_password_hash = hash_password("password123")
        now = datetime.now(timezone.utc)

        # ─────────────────────────────────────────────────────────────────────
        # 1. ADMIN USER (Ministry of Cooperation / NCCT)
        # ─────────────────────────────────────────────────────────────────────
        admin = User(
            name="Ministry of Cooperation Admin",
            phone="9000000000",
            password_hash=default_password_hash,
            role="admin",
        )
        db.add(admin)
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 2. CITIZENS
        # ─────────────────────────────────────────────────────────────────────
        # Citizen 1: Ravi Sharma (Has active job in progress + unrated completed job)
        ravi = User(
            name="Ravi Sharma",
            phone="9555555555",
            password_hash=default_password_hash,
            role="citizen",
        )
        # Citizen 2: Priya Customer (Has an active disputed booking)
        priya_c = User(
            name="Priya Customer",
            phone="9666666666",
            password_hash=default_password_hash,
            role="citizen",
        )
        # Citizen 3: Vikram Mehta (Clean account for testing new booking wizard)
        vikram = User(
            name="Vikram Mehta",
            phone="9777777777",
            password_hash=default_password_hash,
            role="citizen",
        )
        # Citizen 4: Ananya Sen (Additional history)
        ananya = User(
            name="Ananya Sen",
            phone="9888888888",
            password_hash=default_password_hash,
            role="citizen",
        )
        db.add_all([ravi, priya_c, vikram, ananya])
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 3. WORKERS (Electricians, Plumbers, Carpenters, Painters, Cleaners)
        # ─────────────────────────────────────────────────────────────────────
        # W1: Suresh Kumar - Electrician (Rank 1, low earnings ₹200, rating 4.2)
        suresh = User(
            name="Suresh Kumar",
            phone="9111111111",
            password_hash=default_password_hash,
            role="worker",
        )
        # W2: Priya Gupta - Electrician (Rank 2, cold start ₹0, rating None -> 4.0)
        priya_w = User(
            name="Priya Gupta",
            phone="9222222222",
            password_hash=default_password_hash,
            role="worker",
        )
        # W3: Anil Yadav - Electrician (Rank 3, earnings ₹2,000, rating 4.5)
        anil = User(
            name="Anil Yadav",
            phone="9333333333",
            password_hash=default_password_hash,
            role="worker",
        )
        # W4: Meena Verma - Electrician (Rank 4, high earnings ₹4,500, rating 4.9)
        meena = User(
            name="Meena Verma",
            phone="9444444444",
            password_hash=default_password_hash,
            role="worker",
        )
        # W5: Rajesh Soni - Plumber (Verified, earnings ₹1,800, rating 4.6)
        rajesh = User(
            name="Rajesh Soni",
            phone="9123400001",
            password_hash=default_password_hash,
            role="worker",
        )
        # W6: Dinesh Carpenter - Carpenter (Verified, earnings ₹3,200, rating 4.7)
        dinesh = User(
            name="Dinesh Carpenter",
            phone="9123400002",
            password_hash=default_password_hash,
            role="worker",
        )
        # W7: Pooja Sharma - Painter (PENDING VERIFICATION - shows banner on worker dashboard)
        pooja = User(
            name="Pooja Sharma",
            phone="9123400003",
            password_hash=default_password_hash,
            role="worker",
        )
        # W8: Amit Kumar - Cleaner (PENDING VERIFICATION - shows in Ministry queue)
        amit = User(
            name="Amit Kumar",
            phone="9123400004",
            password_hash=default_password_hash,
            role="worker",
        )

        db.add_all([suresh, priya_w, anil, meena, rajesh, dinesh, pooja, amit])
        db.flush()

        # Worker Profiles (Locations in and around Jaipur)
        profiles = [
            WorkerProfile(
                user_id=suresh.id,
                skill="electrician",
                lat=Decimal("26.9280"),
                lng=Decimal("75.8100"),
                rating=Decimal("4.2"),
                rating_count=12,
                availability=True,
                verification_status="verified",
            ),
            WorkerProfile(
                user_id=priya_w.id,
                skill="electrician",
                lat=Decimal("26.8800"),
                lng=Decimal("75.7600"),
                rating=None,
                rating_count=0,
                availability=True,
                verification_status="verified",
            ),
            WorkerProfile(
                user_id=anil.id,
                skill="electrician",
                lat=Decimal("26.9200"),
                lng=Decimal("75.8000"),
                rating=Decimal("4.5"),
                rating_count=28,
                availability=True,
                verification_status="verified",
            ),
            WorkerProfile(
                user_id=meena.id,
                skill="electrician",
                lat=Decimal("26.9130"),
                lng=Decimal("75.7880"),
                rating=Decimal("4.9"),
                rating_count=45,
                availability=True,
                verification_status="verified",
            ),
            WorkerProfile(
                user_id=rajesh.id,
                skill="plumber",
                lat=Decimal("26.9150"),
                lng=Decimal("75.7820"),
                rating=Decimal("4.6"),
                rating_count=18,
                availability=True,
                verification_status="verified",
            ),
            WorkerProfile(
                user_id=dinesh.id,
                skill="carpenter",
                lat=Decimal("26.9050"),
                lng=Decimal("75.7950"),
                rating=Decimal("4.7"),
                rating_count=22,
                availability=True,
                verification_status="verified",
            ),
            WorkerProfile(
                user_id=pooja.id,
                skill="painter",
                lat=Decimal("26.9180"),
                lng=Decimal("75.7900"),
                rating=Decimal("4.0"),
                rating_count=0,
                availability=True,
                verification_status="pending",  # PENDING VERIFICATION
            ),
            WorkerProfile(
                user_id=amit.id,
                skill="cleaning",
                lat=Decimal("26.9220"),
                lng=Decimal("75.8050"),
                rating=Decimal("4.0"),
                rating_count=0,
                availability=True,
                verification_status="pending",  # PENDING VERIFICATION
            ),
        ]
        db.add_all(profiles)
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 4. COMPLETED BOOKINGS (Populating Economics & Earnings Distribution)
        # ─────────────────────────────────────────────────────────────────────
        # Weekly Earnings Target calculation: job_price * 0.95 = target worker payout
        completed_bookings = [
            # Suresh: ₹200 payout (Tier ₹0 - ₹1,000)
            Booking(
                citizen_id=ravi.id,
                worker_id=suresh.id,
                skill="electrician",
                lat=Decimal("26.9280"),
                lng=Decimal("75.8100"),
                description="Ceiling fan regulator replacement",
                job_price=Decimal("210.53"),
                platform_fee=Decimal("10.53"),
                rating=4,
                status="completed",
                created_at=now - timedelta(days=2),
            ),
            # Anil: ₹2,000 payout (Tier ₹1,000 - ₹3,000)
            Booking(
                citizen_id=ravi.id,
                worker_id=anil.id,
                skill="electrician",
                lat=Decimal("26.9200"),
                lng=Decimal("75.8000"),
                description="Switchboard & MCB main panel upgrade",
                job_price=Decimal("2105.26"),
                platform_fee=Decimal("105.26"),
                rating=5,
                status="completed",
                created_at=now - timedelta(days=3),
            ),
            # Meena: ₹4,500 payout (Tier ₹3,000 - ₹5,000)
            Booking(
                citizen_id=ananya.id,
                worker_id=meena.id,
                skill="electrician",
                lat=Decimal("26.9130"),
                lng=Decimal("75.7880"),
                description="3BHK full concealed rewiring & load balancing",
                job_price=Decimal("4736.84"),
                platform_fee=Decimal("236.84"),
                rating=5,
                status="completed",
                created_at=now - timedelta(days=4),
            ),
            # Rajesh: ₹1,800 payout (Tier ₹1,000 - ₹3,000)
            Booking(
                citizen_id=ananya.id,
                worker_id=rajesh.id,
                skill="plumber",
                lat=Decimal("26.9150"),
                lng=Decimal("75.7820"),
                description="Kitchen pipeline leakage and water motor fitting",
                job_price=Decimal("1894.74"),
                platform_fee=Decimal("94.74"),
                rating=5,
                status="completed",
                created_at=now - timedelta(days=1),
            ),
            # Dinesh: ₹3,200 payout (Tier ₹3,000 - ₹5,000)
            Booking(
                citizen_id=ravi.id,
                worker_id=dinesh.id,
                skill="carpenter",
                lat=Decimal("26.9050"),
                lng=Decimal("75.7950"),
                description="Custom wooden wardrobe repair and hinge alignment",
                job_price=Decimal("3368.42"),
                platform_fee=Decimal("168.42"),
                rating=4,
                status="completed",
                created_at=now - timedelta(days=2),
            ),
            # High Volume Job: ₹5,500 payout (Tier ₹5,000+) - Dinesh 2nd job
            Booking(
                citizen_id=ananya.id,
                worker_id=dinesh.id,
                skill="carpenter",
                lat=Decimal("26.9050"),
                lng=Decimal("75.7950"),
                description="Complete modular kitchen cabinet installation",
                job_price=Decimal("5789.47"),
                platform_fee=Decimal("289.47"),
                rating=5,
                status="completed",
                created_at=now - timedelta(days=1),
            ),
        ]
        db.add_all(completed_bookings)
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 5. UNRATED COMPLETED BOOKING (For Citizen Ravi to test Star Rating)
        # ─────────────────────────────────────────────────────────────────────
        unrated_booking = Booking(
            citizen_id=ravi.id,
            worker_id=suresh.id,
            skill="electrician",
            lat=Decimal("26.9124"),
            lng=Decimal("75.7873"),
            description="Emergency power outlet repair & fuse check",
            job_price=Decimal("500.00"),
            platform_fee=Decimal("25.00"),
            rating=None,  # Not yet rated by citizen!
            status="completed",
            created_at=now - timedelta(hours=3),
        )
        db.add(unrated_booking)
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 6. ACTIVE IN-PROGRESS BOOKING (Assigned to Suresh Kumar)
        # ─────────────────────────────────────────────────────────────────────
        active_booking = Booking(
            citizen_id=ravi.id,
            worker_id=suresh.id,
            skill="electrician",
            lat=Decimal("26.9124"),
            lng=Decimal("75.7873"),
            description="Air Conditioner MCB tripping investigation",
            job_price=Decimal("650.00"),
            platform_fee=Decimal("32.50"),
            status="assigned",  # Live In-Progress
            created_at=now - timedelta(minutes=45),
        )
        db.add(active_booking)
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 7. ACTIVE DISPUTED BOOKING (For Citizen Priya / Ministry Queue)
        # ─────────────────────────────────────────────────────────────────────
        disputed_booking = Booking(
            citizen_id=priya_c.id,
            worker_id=meena.id,
            skill="electrician",
            lat=Decimal("26.9130"),
            lng=Decimal("75.7880"),
            description="Geyser wiring installation",
            job_price=Decimal("800.00"),
            platform_fee=Decimal("40.00"),
            status="disputed",  # DISPUTED
            dispute_reason="Worker left live wires exposed in bathroom and did not ground the connection properly.",
            created_at=now - timedelta(hours=5),
        )
        db.add(disputed_booking)
        db.flush()

        # ─────────────────────────────────────────────────────────────────────
        # 8. PENDING BOOKING WITH LIVE OFFER (For Worker Suresh & Priya Inbox)
        # ─────────────────────────────────────────────────────────────────────
        pending_booking = Booking(
            citizen_id=vikram.id,
            worker_id=None,
            skill="electrician",
            lat=Decimal("26.9124"),
            lng=Decimal("75.7873"),
            description="Inverter battery terminal cleanup and voltage check",
            job_price=Decimal("450.00"),
            platform_fee=Decimal("22.50"),
            status="pending",
            created_at=now - timedelta(minutes=2),
        )
        db.add(pending_booking)
        db.flush()

        # Live Offer dispatched to Suresh Kumar (Rank #1)
        offer_suresh = BookingOffer(
            booking_id=pending_booking.id,
            worker_id=suresh.id,
            rank_at_offer=1,
            dispatch_score=Decimal("12550.00"),
            status="offered",  # Live offer in Suresh's Inbox!
            expires_at=now + timedelta(minutes=8),
            created_at=now - timedelta(minutes=2),
        )
        db.add(offer_suresh)
        db.flush()

        db.commit()
        print("\n" + "=" * 70)
        print("DEMO DATA SEEDED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Total Users: {db.query(User).count()}")
        print("  - Admin: 1 (9000000000 / password123)")
        print(f"  - Citizens: {db.query(User).filter(User.role == 'citizen').count()}")
        print(f"  - Workers: {db.query(User).filter(User.role == 'worker').count()}")
        print(f"Total Bookings: {db.query(Booking).count()}")
        print(
            f"  - Completed: {db.query(Booking).filter(Booking.status == 'completed').count()}"
        )
        print(
            f"  - In-Progress (Assigned): {db.query(Booking).filter(Booking.status == 'assigned').count()}"
        )
        print(
            f"  - Disputed: {db.query(Booking).filter(Booking.status == 'disputed').count()}"
        )
        print(
            f"  - Pending with Live Offer: {db.query(Booking).filter(Booking.status == 'pending').count()}"
        )
        print(
            f"Total Live Offers: {db.query(BookingOffer).filter(BookingOffer.status == 'offered').count()}"
        )
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"Error seeding demo data: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
