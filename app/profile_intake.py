from app.profile import UserProfile
from app.profile_store import save_profile


def collect_profile():

    print("\n=== AI ENGINEERING COMMAND CENTER ===\n")

    role = input("Desired role: ").strip()

    specialization = input(
        "Specialization / area of focus: "
    ).strip()

    companies_input = input(
        "Target companies (comma separated): "
    ).strip()

    preparation_days = int(
        input("How many days do you have to prepare? ").strip()
    )

    knowledge_input = input(
        "Current knowledge (comma separated): "
    ).strip()

    profile = UserProfile(
        role=role,
        specialization=specialization,
        target_companies=[
            company.strip()
            for company in companies_input.split(",")
            if company.strip()
        ],
        preparation_days=preparation_days,
        current_knowledge=[
            topic.strip()
            for topic in knowledge_input.split(",")
            if topic.strip()
        ],
    )

    save_profile(profile)

    print("\nProfile created successfully.")


if __name__ == "__main__":
    collect_profile()