"""
Build the RF Knowledge Database.
"""

from pathlib import Path

from knowledge.database import RFKnowledgeDatabase


DATABASE = Path("knowledge/rf_knowledge.db")
CSV = Path("knowledge/data/rf_intel.csv")


def main():

    if DATABASE.exists():

        DATABASE.unlink()

        print("Removed existing database.")

    db = RFKnowledgeDatabase()

    print("Creating database...")

    db.initialize()

    print("Importing RF knowledge...")

    imported = db.import_csv(CSV)

    print(f"Imported {imported:,} signals.")

    print(f"Database contains {db.count():,} signals.")

    db.close()

    print("Done.")


if __name__ == "__main__":

    main()