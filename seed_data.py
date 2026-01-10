# seed_data.py
from app.core.database import SessionLocal, engine
from app.models.models import Base, User, Referral, RewardConfig
import random
import string

def generate_referral_code():
    """Generate referral code in format SVH-AB12CD"""
    letters1 = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"SVH-{letters1}{digits}{letters2}"

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create reward configurations
        reward_configs = [
            {"reward_type": "SIGNUP", "reward_value": 100, "reward_unit": "points"},
            {"reward_type": "CONVERSION", "reward_value": 500, "reward_unit": "points"},
            {"reward_type": "PREMIUM_SIGNUP", "reward_value": 1000, "reward_unit": "points"}
        ]
        
        for config in reward_configs:
            existing = db.query(RewardConfig).filter(
                RewardConfig.reward_type == config["reward_type"]
            ).first()
            if not existing:
                db.add(RewardConfig(**config))
        
        # Create sample users
        sample_users = ["Alice", "Bob", "Charlie", "David", "Eve"]
        
        for i, username in enumerate(sample_users, 1):
            # Check if user exists
            user = db.query(User).filter(User.username == username).first()
            if not user:
                user = User(id=i, username=username)
                db.add(user)
                db.commit()
                db.refresh(user)
                
                # Create referral code
                code = generate_referral_code()
                referral = Referral(
                    referral_code=code,
                    referred_by=user.id
                )
                db.add(referral)
        
        db.commit()
        print("✅ Database seeded with sample data!")
        print("\nSample Users & Codes:")
        print("-" * 30)
        for user in db.query(User).all():
            referral = db.query(Referral).filter(Referral.referred_by == user.id).first()
            if referral:
                print(f"{user.username}: {referral.referral_code}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()