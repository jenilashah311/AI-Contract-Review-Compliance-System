"""Seed database with sample standard clauses."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, StandardClause
from app.utils.embeddings import generate_embeddings_batch


def create_sample_clauses():
    """Create 20 sample standard clauses."""
    sample_clauses = [
        {
            "category": "Confidentiality",
            "title": "Non-Disclosure Obligation",
            "text": "The receiving party agrees to maintain in strict confidence all Confidential Information disclosed by the disclosing party and shall not disclose such information to any third party without prior written consent."
        },
        {
            "category": "Confidentiality",
            "title": "Confidential Information Definition",
            "text": "Confidential Information means any information, technical data, trade secrets, or know-how, including but not limited to research, product plans, products, services, customers, customer lists, markets, software, developments, inventions, processes, formulas, technology, designs, drawings, engineering, hardware configuration information, marketing, finances or other business information."
        },
        {
            "category": "Term and Termination",
            "title": "Agreement Duration",
            "text": "This Agreement shall commence on the Effective Date and continue for a period of one (1) year, unless earlier terminated in accordance with the provisions herein."
        },
        {
            "category": "Term and Termination",
            "title": "Termination for Convenience",
            "text": "Either party may terminate this Agreement for any reason upon providing thirty (30) days written notice to the other party."
        },
        {
            "category": "Term and Termination",
            "title": "Termination for Cause",
            "text": "Either party may terminate this Agreement immediately upon written notice if the other party materially breaches any provision of this Agreement and fails to cure such breach within fifteen (15) days of receiving written notice."
        },
        {
            "category": "Payment",
            "title": "Payment Terms",
            "text": "Client agrees to pay all fees within thirty (30) days of receipt of invoice. Late payments shall accrue interest at a rate of 1.5% per month or the maximum rate permitted by law, whichever is lower."
        },
        {
            "category": "Payment",
            "title": "Fee Schedule",
            "text": "The fees for services under this Agreement are set forth in Exhibit A attached hereto. All fees are exclusive of applicable taxes, which shall be the responsibility of the Client."
        },
        {
            "category": "Liability",
            "title": "Limitation of Liability",
            "text": "In no event shall either party be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses."
        },
        {
            "category": "Liability",
            "title": "Cap on Damages",
            "text": "The total aggregate liability of either party arising out of or related to this Agreement shall not exceed the total amount paid by Client to Provider in the twelve (12) months preceding the event giving rise to such liability."
        },
        {
            "category": "Intellectual Property",
            "title": "IP Ownership",
            "text": "All intellectual property rights in any work product, deliverables, or materials created by Provider under this Agreement shall be owned exclusively by Client upon full payment of all fees."
        },
        {
            "category": "Intellectual Property",
            "title": "License Grant",
            "text": "Provider hereby grants Client a perpetual, worldwide, non-exclusive, royalty-free license to use, reproduce, and distribute all deliverables created under this Agreement."
        },
        {
            "category": "Warranty",
            "title": "Service Warranty",
            "text": "Provider warrants that all services shall be performed in a professional and workmanlike manner in accordance with industry standards."
        },
        {
            "category": "Warranty",
            "title": "Disclaimer of Warranties",
            "text": "Except as expressly stated herein, Provider makes no warranties of any kind, whether express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement."
        },
        {
            "category": "Indemnification",
            "title": "Mutual Indemnification",
            "text": "Each party agrees to indemnify, defend, and hold harmless the other party from and against any and all claims, damages, liabilities, costs, and expenses arising out of or related to any breach of this Agreement by the indemnifying party."
        },
        {
            "category": "Indemnification",
            "title": "IP Indemnification",
            "text": "Provider shall indemnify and hold harmless Client from any claims that the deliverables or services provided infringe upon any third-party intellectual property rights."
        },
        {
            "category": "Dispute Resolution",
            "title": "Arbitration Clause",
            "text": "Any dispute arising out of or relating to this Agreement shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association."
        },
        {
            "category": "Dispute Resolution",
            "title": "Governing Law",
            "text": "This Agreement shall be governed by and construed in accordance with the laws of the State of [State], without regard to its conflict of law provisions."
        },
        {
            "category": "General Provisions",
            "title": "Force Majeure",
            "text": "Neither party shall be liable for any failure or delay in performance due to circumstances beyond its reasonable control, including but not limited to acts of God, war, terrorism, civil unrest, labor disputes, or governmental actions."
        },
        {
            "category": "General Provisions",
            "title": "Assignment",
            "text": "Neither party may assign this Agreement or any rights or obligations hereunder without the prior written consent of the other party, except that either party may assign this Agreement to a successor in connection with a merger, acquisition, or sale of all or substantially all of its assets."
        },
        {
            "category": "General Provisions",
            "title": "Entire Agreement",
            "text": "This Agreement constitutes the entire agreement between the parties concerning the subject matter hereof and supersedes all prior or contemporaneous agreements, understandings, and communications, whether written or oral."
        }
    ]
    
    return sample_clauses


def seed_database():
    """Seed database with sample standard clauses."""
    print("Starting database seed...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if clauses already exist
        existing_count = db.query(StandardClause).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} clauses. Skipping seed.")
            return
        
        # Get sample clauses
        clauses_data = create_sample_clauses()
        
        print(f"Generating embeddings for {len(clauses_data)} clauses...")
        # Generate embeddings in batch
        texts = [clause["text"] for clause in clauses_data]
        embeddings = generate_embeddings_batch(texts)
        
        print("Inserting clauses into database...")
        # Create clause objects
        clauses = []
        for clause_data, embedding in zip(clauses_data, embeddings):
            clause = StandardClause(
                category=clause_data["category"],
                title=clause_data["title"],
                text=clause_data["text"],
                embedding=embedding
            )
            clauses.append(clause)
        
        # Bulk insert
        db.bulk_save_objects(clauses)
        db.commit()
        
        print(f"✓ Successfully seeded {len(clauses)} standard clauses")
        
        # Print summary
        categories = db.query(StandardClause.category).distinct().all()
        print(f"\nCategories seeded:")
        for cat in categories:
            count = db.query(StandardClause).filter(StandardClause.category == cat[0]).count()
            print(f"  - {cat[0]}: {count} clauses")
    
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
