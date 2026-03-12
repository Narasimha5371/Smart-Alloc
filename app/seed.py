"""
Seed script — populates the database with sample data for development.
Run with: python -m app.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import User, Skill, UserSkill, Project, ProjectSkill, Allocation, Notification
from app.models.enums import UserRole, ProjectStatus, Priority, AllocationStatus, NotificationType
from app.utils.security import get_password_hash
from datetime import date, datetime


def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already has data. Skipping seed.")
            print("To re-seed, delete smart_alloc.db and run again.")
            return

        print("Seeding database...")

        # --- Skills ---
        skill_data = [
            ("Python", "Technical"),
            ("JavaScript", "Technical"),
            ("React", "Technical"),
            ("Node.js", "Technical"),
            ("Java", "Technical"),
            ("C#", "Technical"),
            (".NET", "Technical"),
            ("SQL", "Technical"),
            ("PostgreSQL", "Technical"),
            ("MongoDB", "Technical"),
            ("AWS", "Cloud"),
            ("Azure", "Cloud"),
            ("Docker", "DevOps"),
            ("Kubernetes", "DevOps"),
            ("CI/CD", "DevOps"),
            ("Machine Learning", "Data Science"),
            ("Data Analysis", "Data Science"),
            ("TensorFlow", "Data Science"),
            ("UI/UX Design", "Design"),
            ("Figma", "Design"),
            ("Project Management", "Management"),
            ("Agile/Scrum", "Management"),
            ("Communication", "Soft Skill"),
            ("Leadership", "Soft Skill"),
            ("Problem Solving", "Soft Skill"),
            ("Flutter", "Mobile"),
            ("React Native", "Mobile"),
            ("Swift", "Mobile"),
            ("Cybersecurity", "Security"),
            ("API Development", "Technical"),
        ]

        skills = {}
        for name, category in skill_data:
            skill = Skill(name=name, category=category)
            db.add(skill)
            db.flush()
            skills[name] = skill
        print(f"  Created {len(skills)} skills")

        # --- Users ---
        # Admin
        admin = User(
            email="admin@smartalloc.com",
            full_name="System Admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            department="IT",
        )
        db.add(admin)

        # HR
        hr_user = User(
            email="hr@smartalloc.com",
            full_name="Sarah Johnson",
            hashed_password=get_password_hash("hr123456"),
            role=UserRole.HR,
            department="Human Resources",
        )
        db.add(hr_user)

        # Managers
        manager1 = User(
            email="manager1@smartalloc.com",
            full_name="Robert Chen",
            hashed_password=get_password_hash("manager123"),
            role=UserRole.MANAGER,
            department="Engineering",
        )
        db.add(manager1)

        manager2 = User(
            email="manager2@smartalloc.com",
            full_name="Lisa Park",
            hashed_password=get_password_hash("manager123"),
            role=UserRole.MANAGER,
            department="Design",
        )
        db.add(manager2)

        # Employees
        employees_data = [
            ("alice@smartalloc.com", "Alice Williams", "Engineering", ["Python", "Django", "SQL", "Docker", "API Development"]),
            ("bob@smartalloc.com", "Bob Martinez", "Engineering", ["JavaScript", "React", "Node.js", "MongoDB"]),
            ("carol@smartalloc.com", "Carol Davis", "Engineering", ["Java", "C#", ".NET", "SQL", "Azure"]),
            ("david@smartalloc.com", "David Kim", "Data Science", ["Python", "Machine Learning", "TensorFlow", "Data Analysis"]),
            ("emma@smartalloc.com", "Emma Thompson", "Design", ["UI/UX Design", "Figma", "React", "JavaScript"]),
            ("frank@smartalloc.com", "Frank Wilson", "DevOps", ["Docker", "Kubernetes", "AWS", "CI/CD", "Python"]),
            ("grace@smartalloc.com", "Grace Lee", "Engineering", ["Python", "React", "PostgreSQL", "API Development"]),
            ("henry@smartalloc.com", "Henry Brown", "Mobile", ["Flutter", "React Native", "JavaScript", "Swift"]),
            ("iris@smartalloc.com", "Iris Anderson", "Security", ["Cybersecurity", "Python", "AWS", "API Development"]),
            ("jack@smartalloc.com", "Jack Taylor", "Management", ["Project Management", "Agile/Scrum", "Leadership", "Communication"]),
        ]

        emp_objects = []
        for email, name, dept, emp_skills in employees_data:
            emp = User(
                email=email,
                full_name=name,
                hashed_password=get_password_hash("employee123"),
                role=UserRole.EMPLOYEE,
                department=dept,
            )
            db.add(emp)
            db.flush()
            emp_objects.append(emp)

            # Add skills
            for skill_name in emp_skills:
                if skill_name in skills:
                    us = UserSkill(
                        user_id=emp.id,
                        skill_id=skills[skill_name].id,
                        proficiency_level=3 + (hash(skill_name + email) % 3),  # Random 3-5
                    )
                    db.add(us)

        print(f"  Created {len(emp_objects)} employees with skills")

        # Clients
        client1 = User(
            email="client1@example.com",
            full_name="TechCorp Inc.",
            hashed_password=get_password_hash("client123"),
            role=UserRole.CLIENT,
        )
        db.add(client1)

        client2 = User(
            email="client2@example.com",
            full_name="DataViz Solutions",
            hashed_password=get_password_hash("client123"),
            role=UserRole.CLIENT,
        )
        db.add(client2)

        db.flush()
        print("  Created admin, HR, 2 managers, 2 clients")

        # --- Sample Projects ---
        # Project 1: Pending
        p1 = Project(
            title="E-Commerce Platform Redesign",
            description="Complete redesign and development of our e-commerce platform. Need modern UI, improved checkout flow, real-time inventory management, and mobile responsiveness. Integration with payment gateways and shipping APIs required.",
            client_id=client1.id,
            priority=Priority.HIGH,
            deadline=date(2026, 6, 30),
            budget=75000.0,
            status=ProjectStatus.PENDING,
        )
        db.add(p1)
        db.flush()
        for s_name in ["React", "Node.js", "PostgreSQL", "UI/UX Design", "API Development"]:
            if s_name in skills:
                db.add(ProjectSkill(project_id=p1.id, skill_id=skills[s_name].id, importance_level=4))

        # Project 2: Accepted
        p2 = Project(
            title="ML Recommendation Engine",
            description="Build a machine learning recommendation engine for our content platform. Needs collaborative filtering, content-based filtering, and real-time model serving. Data pipeline for training data collection.",
            client_id=client2.id,
            priority=Priority.MEDIUM,
            deadline=date(2026, 8, 15),
            budget=50000.0,
            status=ProjectStatus.ACCEPTED,
        )
        db.add(p2)
        db.flush()
        for s_name in ["Python", "Machine Learning", "TensorFlow", "Data Analysis", "Docker"]:
            if s_name in skills:
                db.add(ProjectSkill(project_id=p2.id, skill_id=skills[s_name].id, importance_level=5))

        # Project 3: In Progress
        p3 = Project(
            title="Internal Dashboard App",
            description="Internal analytics dashboard for tracking KPIs, team performance, and project metrics. Real-time data visualization, role-based access, CSV export functionality.",
            client_id=client1.id,
            priority=Priority.MEDIUM,
            deadline=date(2026, 5, 1),
            budget=30000.0,
            status=ProjectStatus.IN_PROGRESS,
        )
        db.add(p3)
        db.flush()
        for s_name in ["React", "Python", "PostgreSQL", "UI/UX Design"]:
            if s_name in skills:
                db.add(ProjectSkill(project_id=p3.id, skill_id=skills[s_name].id, importance_level=3))

        # Add some allocations for in-progress project
        alloc1 = Allocation(
            project_id=p3.id,
            employee_id=emp_objects[1].id,  # Bob
            allocated_by=manager1.id,
            role_in_project="Frontend Developer",
            status=AllocationStatus.ALLOCATED,
            progress_percent=60,
            start_date=date(2026, 2, 1),
        )
        db.add(alloc1)

        alloc2 = Allocation(
            project_id=p3.id,
            employee_id=emp_objects[6].id,  # Grace
            allocated_by=manager1.id,
            role_in_project="Backend Developer",
            status=AllocationStatus.ALLOCATED,
            progress_percent=45,
            start_date=date(2026, 2, 1),
        )
        db.add(alloc2)

        alloc3 = Allocation(
            project_id=p3.id,
            employee_id=emp_objects[4].id,  # Emma
            allocated_by=manager2.id,
            role_in_project="UI Designer",
            status=AllocationStatus.ALLOCATED,
            progress_percent=80,
            start_date=date(2026, 2, 1),
        )
        db.add(alloc3)

        print("  Created 3 sample projects with allocations")

        # --- Notifications ---
        notif1 = Notification(
            user_id=emp_objects[1].id,
            title="New Project Assignment",
            message='You have been assigned to project "Internal Dashboard App" as Frontend Developer.',
            type=NotificationType.ALLOCATION,
            link="/employee/dashboard",
        )
        db.add(notif1)

        notif2 = Notification(
            user_id=emp_objects[6].id,
            title="New Project Assignment",
            message='You have been assigned to project "Internal Dashboard App" as Backend Developer.',
            type=NotificationType.ALLOCATION,
            link="/employee/dashboard",
        )
        db.add(notif2)

        print("  Created sample notifications")

        db.commit()
        print("\nSeed completed successfully!")
        print("\n--- Login Credentials ---")
        print("Admin:    admin@smartalloc.com / admin123")
        print("HR:       hr@smartalloc.com / hr123456")
        print("Manager:  manager1@smartalloc.com / manager123")
        print("Employee: alice@smartalloc.com / employee123")
        print("Client:   client1@example.com / client123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
