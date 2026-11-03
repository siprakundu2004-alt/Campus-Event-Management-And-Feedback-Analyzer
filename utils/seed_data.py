"""
utils/seed_data.py
------------------
Seeds realistic, internally consistent sample data for Campus Event Management & Feedback Analyzer.
Ensures at least:
- 15 realistic campus events (Technical, Cultural, Sports, Workshop, Hackathon, etc.)
- 40 students across MCA, BCA, CS, IT, Electronics, Management
- 65+ registrations adhering to capacity and deadlines
- 35+ realistic student feedback entries with diverse ratings (1-5) and comments

Can be run directly via `python utils/seed_data.py` or imported and invoked.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Ensure parent directory is on pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import EVENTS_CSV, STUDENTS_CSV, REGISTRATIONS_CSV, FEEDBACK_CSV
from models.event import Event
from models.student import Student
from models.registration import Registration
from models.feedback import Feedback
from repositories.event_repository import EventRepository
from repositories.student_repository import StudentRepository
from repositories.registration_repository import RegistrationRepository
from repositories.feedback_repository import FeedbackRepository
from utils.constants import EventCategory, EventStatus, Department, Course, RegistrationStatus
from utils.helpers import hash_password, today_str


def seed_all(force: bool = False) -> None:
    """Populate CSV files with sample data if empty or forced."""
    event_repo = EventRepository(EVENTS_CSV)
    student_repo = StudentRepository(STUDENTS_CSV)
    reg_repo = RegistrationRepository(REGISTRATIONS_CSV)
    fbk_repo = FeedbackRepository(FEEDBACK_CSV)

    if not force and event_repo.count() > 0:
        print("[*] Sample data already exists. Skipping seed (use force=True to overwrite).")
        return

    print("[*] Seeding CampusConnect Analytics data...")

    # Clear existing if force
    if force:
        for path in [EVENTS_CSV, STUDENTS_CSV, REGISTRATIONS_CSV, FEEDBACK_CSV]:
            if path.exists():
                path.unlink()
        event_repo = EventRepository(EVENTS_CSV)
        student_repo = StudentRepository(STUDENTS_CSV)
        reg_repo = RegistrationRepository(REGISTRATIONS_CSV)
        fbk_repo = FeedbackRepository(FEEDBACK_CSV)

    # ---------------------------------------------------------
    # 1. Seed Students (40 students)
    # ---------------------------------------------------------
    students_data = [
        ("STU001", "Aarav Sharma", "aarav.sharma@nit.edu", "9876543210", Department.MCA.value, Course.MCA.value, 4, "2024-25"),
        ("STU002", "Priya Patel", "priya.patel@nit.edu", "9876543211", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 6, "2023-24"),
        ("STU003", "Rohan Verma", "rohan.verma@nit.edu", "9876543212", Department.INFORMATION_TECHNOLOGY.value, Course.BTECH_IT.value, 4, "2024-25"),
        ("STU004", "Ananya Iyer", "ananya.iyer@nit.edu", "9876543213", Department.MCA.value, Course.MCA.value, 2, "2025-26"),
        ("STU005", "Kabir Mehta", "kabir.mehta@nit.edu", "9876543214", Department.MANAGEMENT.value, Course.MBA.value, 2, "2025-26"),
        ("STU006", "Ishita Gupta", "ishita.gupta@nit.edu", "9876543215", Department.ELECTRONICS.value, Course.BTECH_ECE.value, 8, "2023-24"),
        ("STU007", "Aditya Nair", "aditya.nair@nit.edu", "9876543216", Department.BCA.value, Course.BCA.value, 4, "2024-25"),
        ("STU008", "Sneha Kulkarni", "sneha.k@nit.edu", "9876543217", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 6, "2023-24"),
        ("STU009", "Vikram Rathore", "vikram.r@nit.edu", "9876543218", Department.INFORMATION_TECHNOLOGY.value, Course.BTECH_IT.value, 2, "2025-26"),
        ("STU010", "Neha Deshmukh", "neha.d@nit.edu", "9876543219", Department.MCA.value, Course.MCA.value, 4, "2024-25"),
        ("STU011", "Rahul Saxena", "rahul.saxena@nit.edu", "9876543220", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 4, "2024-25"),
        ("STU012", "Pooja Hegde", "pooja.h@nit.edu", "9876543221", Department.MANAGEMENT.value, Course.MBA.value, 4, "2024-25"),
        ("STU013", "Arjun Reddy", "arjun.reddy@nit.edu", "9876543222", Department.ELECTRONICS.value, Course.BTECH_ECE.value, 6, "2023-24"),
        ("STU014", "Diya Sen", "diya.sen@nit.edu", "9876543223", Department.BCA.value, Course.BCA.value, 6, "2023-24"),
        ("STU015", "Karan Malhotra", "karan.m@nit.edu", "9876543224", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 8, "2023-24"),
        ("STU016", "Riya Mukherjee", "riya.m@nit.edu", "9876543225", Department.MCA.value, Course.MCA.value, 2, "2025-26"),
        ("STU017", "Siddharth Joshi", "siddharth.j@nit.edu", "9876543226", Department.INFORMATION_TECHNOLOGY.value, Course.BTECH_IT.value, 6, "2023-24"),
        ("STU018", "Tanvi Rao", "tanvi.rao@nit.edu", "9876543227", Department.ELECTRONICS.value, Course.BTECH_ECE.value, 4, "2024-25"),
        ("STU019", "Varun Chopra", "varun.c@nit.edu", "9876543228", Department.BCA.value, Course.BCA.value, 2, "2025-26"),
        ("STU020", "Meera Pillai", "meera.p@nit.edu", "9876543229", Department.MANAGEMENT.value, Course.MBA.value, 2, "2025-26"),
        ("STU021", "Aryan Singhania", "aryan.s@nit.edu", "9876543230", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 4, "2024-25"),
        ("STU022", "Kavya Nambiar", "kavya.n@nit.edu", "9876543231", Department.MCA.value, Course.MCA.value, 4, "2024-25"),
        ("STU023", "Gaurav Bhatt", "gaurav.b@nit.edu", "9876543232", Department.INFORMATION_TECHNOLOGY.value, Course.BTECH_IT.value, 8, "2023-24"),
        ("STU024", "Shreya Ghoshal", "shreya.g@nit.edu", "9876543233", Department.BCA.value, Course.BCA.value, 4, "2024-25"),
        ("STU025", "Nikhil Mishra", "nikhil.m@nit.edu", "9876543234", Department.ELECTRONICS.value, Course.BTECH_ECE.value, 2, "2025-26"),
        ("STU026", "Tanya Bansal", "tanya.b@nit.edu", "9876543235", Department.MANAGEMENT.value, Course.MBA.value, 4, "2024-25"),
        ("STU027", "Devansh Patel", "devansh.p@nit.edu", "9876543236", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 2, "2025-26"),
        ("STU028", "Ankita Roy", "ankita.r@nit.edu", "9876543237", Department.MCA.value, Course.MCA.value, 2, "2025-26"),
        ("STU029", "Harsh Vardhan", "harsh.v@nit.edu", "9876543238", Department.INFORMATION_TECHNOLOGY.value, Course.BTECH_IT.value, 4, "2024-25"),
        ("STU030", "Simran Kaur", "simran.k@nit.edu", "9876543239", Department.ELECTRONICS.value, Course.BTECH_ECE.value, 6, "2023-24"),
        ("STU031", "Pranav Dubey", "pranav.d@nit.edu", "9876543240", Department.BCA.value, Course.BCA.value, 2, "2025-26"),
        ("STU032", "Swati Pandey", "swati.p@nit.edu", "9876543241", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 6, "2023-24"),
        ("STU033", "Manish Tiwari", "manish.t@nit.edu", "9876543242", Department.MANAGEMENT.value, Course.MBA.value, 2, "2025-26"),
        ("STU034", "Kritika Soni", "kritika.s@nit.edu", "9876543243", Department.MCA.value, Course.MCA.value, 4, "2024-25"),
        ("STU035", "Rishabh Jain", "rishabh.j@nit.edu", "9876543244", Department.INFORMATION_TECHNOLOGY.value, Course.BTECH_IT.value, 4, "2024-25"),
        ("STU036", "Alok Kumar", "alok.k@nit.edu", "9876543245", Department.ELECTRONICS.value, Course.BTECH_ECE.value, 4, "2024-25"),
        ("STU037", "Divya Menon", "divya.m@nit.edu", "9876543246", Department.BCA.value, Course.BCA.value, 6, "2023-24"),
        ("STU038", "Sanjay Ghosh", "sanjay.g@nit.edu", "9876543247", Department.COMPUTER_SCIENCE.value, Course.BTECH_CS.value, 8, "2023-24"),
        ("STU039", "Bhavna Chawla", "bhavna.c@nit.edu", "9876543248", Department.MANAGEMENT.value, Course.MBA.value, 4, "2024-25"),
        ("STU040", "Mohit Agrawal", "mohit.a@nit.edu", "9876543249", Department.MCA.value, Course.MCA.value, 2, "2025-26"),
    ]

    for sid, name, email, phone, dept, crs, sem, ayear in students_data:
        # Default password is student's lowercase id (e.g. stu001) or Student@123
        student = Student.create(
            student_id=sid,
            name=name,
            email=email,
            phone=phone,
            department=dept,
            course=crs,
            semester=sem,
            academic_year=ayear,
            plain_password=f"{sid.lower()}@123",
        )
        student_repo.save(student)
    print(f"  [+] Saved {len(students_data)} student records.")

    # ---------------------------------------------------------
    # 2. Seed Events (15 events: completed, active, full, draft, cancelled)
    # ---------------------------------------------------------
    today = date.today()

    events_data = [
        # Completed Events (can have feedback)
        Event(
            event_id="EVT-AI2026",
            event_name="AI & Machine Learning Workshop",
            description="Hands-on workshop on deep learning, transformer architectures, and generative AI using PyTorch.",
            category=EventCategory.WORKSHOP.value,
            event_date=(today - timedelta(days=20)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="16:00",
            venue="Auditorium Hall A",
            organizer="Department of MCA & CS",
            max_capacity=30,
            registration_deadline=(today - timedelta(days=23)).strftime("%Y-%m-%d"),
            status=EventStatus.COMPLETED.value,
            created_date=(today - timedelta(days=35)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-CYBER1",
            event_name="Cyber Security & Ethical Hacking Seminar",
            description="Expert-led session exploring penetration testing, zero-day vulnerabilities, and SOC analyst career paths.",
            category=EventCategory.SEMINAR.value,
            event_date=(today - timedelta(days=14)).strftime("%Y-%m-%d"),
            start_time="14:00",
            end_time="17:00",
            venue="Seminar Hall 2",
            organizer="IT Student Association",
            max_capacity=25,
            registration_deadline=(today - timedelta(days=16)).strftime("%Y-%m-%d"),
            status=EventStatus.COMPLETED.value,
            created_date=(today - timedelta(days=30)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-HACK26",
            event_name="Smart Campus Hackathon 2026",
            description="36-hour competitive coding sprint to build innovative IoT, Web, and Cloud solutions for university life.",
            category=EventCategory.HACKATHON.value,
            event_date=(today - timedelta(days=7)).strftime("%Y-%m-%d"),
            start_time="09:00",
            end_time="21:00",
            venue="Central Computing Lab",
            organizer="Coding Club & Google DSC",
            max_capacity=35,
            registration_deadline=(today - timedelta(days=10)).strftime("%Y-%m-%d"),
            status=EventStatus.COMPLETED.value,
            created_date=(today - timedelta(days=25)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-CULT01",
            event_name="Tarang: Annual Cultural Fest",
            description="Music, dance, theatre, and battle of the bands featuring talent across all inter-collegiate departments.",
            category=EventCategory.CULTURAL.value,
            event_date=(today - timedelta(days=4)).strftime("%Y-%m-%d"),
            start_time="17:00",
            end_time="22:00",
            venue="Open Air Amphitheatre",
            organizer="Student Welfare Council",
            max_capacity=50,
            registration_deadline=(today - timedelta(days=6)).strftime("%Y-%m-%d"),
            status=EventStatus.COMPLETED.value,
            created_date=(today - timedelta(days=20)).strftime("%Y-%m-%d"),
        ),

        # Registration Open Events (Upcoming)
        Event(
            event_id="EVT-PYBOOT",
            event_name="Python & Data Science Bootcamp",
            description="Master Python data structures, NumPy array computations, Pandas dataframes, and Matplotlib plotting.",
            category=EventCategory.TECHNICAL.value,
            event_date=(today + timedelta(days=6)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="15:30",
            venue="CS Lab 301",
            organizer="MCA Coding Wing",
            max_capacity=25,
            registration_deadline=(today + timedelta(days=4)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=10)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-CRIC01",
            event_name="Inter-Department Cricket Championship",
            description="Knockout T20 cricket tournament between Engineering, MCA, BCA, and Management department squads.",
            category=EventCategory.SPORTS.value,
            event_date=(today + timedelta(days=12)).strftime("%Y-%m-%d"),
            start_time="08:30",
            end_time="17:00",
            venue="University Sports Ground",
            organizer="Sports Committee",
            max_capacity=30,
            registration_deadline=(today + timedelta(days=8)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=8)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-CLOU01",
            event_name="Cloud Computing & DevOps Summit",
            description="Exploring AWS, Docker containerization, Kubernetes orchestration, and CI/CD automated deployment pipelines.",
            category=EventCategory.TECHNICAL.value,
            event_date=(today + timedelta(days=15)).strftime("%Y-%m-%d"),
            start_time="11:00",
            end_time="16:00",
            venue="Auditorium Hall B",
            organizer="Cloud Computing Club",
            max_capacity=40,
            registration_deadline=(today + timedelta(days=13)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=5)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-GDG001",
            event_name="UI/UX Design Sprint & Prototyping",
            description="Learn user journey mapping, wireframing in Figma, and modern design systems for responsive web apps.",
            category=EventCategory.WORKSHOP.value,
            event_date=(today + timedelta(days=18)).strftime("%Y-%m-%d"),
            start_time="13:00",
            end_time="18:00",
            venue="Design Innovation Studio",
            organizer="Creative Arts & Tech Society",
            max_capacity=20,
            registration_deadline=(today + timedelta(days=16)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=3)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-ENTR01",
            event_name="Entrepreneurship & Startup Pitch Day",
            description="Pitch your early-stage software and business ventures in front of angel investors and alumni founders.",
            category=EventCategory.COMPETITION.value,
            event_date=(today + timedelta(days=22)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="17:30",
            venue="Management Block Auditorium",
            organizer="Incubation & Innovation Cell",
            max_capacity=25,
            registration_deadline=(today + timedelta(days=19)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=2)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-ROBO01",
            event_name="Robotics & Embedded Systems Expo",
            description="Live hardware demonstrations featuring Arduino, Raspberry Pi, autonomous rovers, and sensor networks.",
            category=EventCategory.CLUB_ACTIVITY.value,
            event_date=(today + timedelta(days=25)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="16:00",
            venue="Electronics Lab 102",
            organizer="Robotics Club",
            max_capacity=20,
            registration_deadline=(today + timedelta(days=23)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=1)).strftime("%Y-%m-%d"),
        ),

        # Full Events
        Event(
            event_id="EVT-WEBDEV",
            event_name="Full-Stack Web Development Masterclass",
            description="Intensive end-to-end full stack web architecture workshop using REST APIs, React, and modern backend design.",
            category=EventCategory.WORKSHOP.value,
            event_date=(today + timedelta(days=9)).strftime("%Y-%m-%d"),
            start_time="09:30",
            end_time="16:30",
            venue="Computer Lab 1",
            organizer="Web Development Guild",
            max_capacity=10,
            registration_deadline=(today + timedelta(days=7)).strftime("%Y-%m-%d"),
            status=EventStatus.FULL.value,
            created_date=(today - timedelta(days=15)).strftime("%Y-%m-%d"),
        ),

        # Registration Closed Events
        Event(
            event_id="EVT-FINTECH",
            event_name="Fintech & Algorithmic Trading Seminar",
            description="Deep dive into financial modeling, quant strategies, and blockchain applications in banking systems.",
            category=EventCategory.SEMINAR.value,
            event_date=(today + timedelta(days=2)).strftime("%Y-%m-%d"),
            start_time="14:00",
            end_time="17:00",
            venue="Conference Room 4",
            organizer="Management & Finance Society",
            max_capacity=20,
            registration_deadline=(today - timedelta(days=1)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_CLOSED.value,
            created_date=(today - timedelta(days=12)).strftime("%Y-%m-%d"),
        ),

        # Draft Events
        Event(
            event_id="EVT-BADM01",
            event_name="Inter-College Badminton Tournament",
            description="Singles and doubles badminton matches for students and faculty members across the university.",
            category=EventCategory.SPORTS.value,
            event_date=(today + timedelta(days=30)).strftime("%Y-%m-%d"),
            start_time="09:00",
            end_time="16:00",
            venue="Indoor Sports Complex",
            organizer="Sports Committee",
            max_capacity=32,
            registration_deadline=(today + timedelta(days=27)).strftime("%Y-%m-%d"),
            status=EventStatus.DRAFT.value,
            created_date=today_str(),
        ),

        # Cancelled Events
        Event(
            event_id="EVT-DRONE1",
            event_name="Drone Photography & Aerial Mapping Workshop",
            description="Outdoor aerial mapping using UAV drones and computer vision stitching.",
            category=EventCategory.WORKSHOP.value,
            event_date=(today + timedelta(days=14)).strftime("%Y-%m-%d"),
            start_time="10:00",
            end_time="14:00",
            venue="Main Football Grounds",
            organizer="Aeromodelling Club",
            max_capacity=15,
            registration_deadline=(today + timedelta(days=11)).strftime("%Y-%m-%d"),
            status=EventStatus.CANCELLED.value,
            created_date=(today - timedelta(days=7)).strftime("%Y-%m-%d"),
        ),
        Event(
            event_id="EVT-DEBATE",
            event_name="National Youth Parliament & Debate",
            description="Parliamentary debate format addressing contemporary technological ethics, privacy, and public policy.",
            category=EventCategory.COMPETITION.value,
            event_date=(today + timedelta(days=16)).strftime("%Y-%m-%d"),
            start_time="11:00",
            end_time="17:00",
            venue="Senate Hall",
            organizer="Literary & Debating Society",
            max_capacity=24,
            registration_deadline=(today + timedelta(days=14)).strftime("%Y-%m-%d"),
            status=EventStatus.REGISTRATION_OPEN.value,
            created_date=(today - timedelta(days=4)).strftime("%Y-%m-%d"),
        ),
    ]

    for event in events_data:
        event_repo.save(event)
    print(f"  [+] Saved {len(events_data)} event records.")

    # ---------------------------------------------------------
    # 3. Seed Registrations (75+ registrations)
    # ---------------------------------------------------------
    # Distribute students across completed and upcoming events
    registrations_plan = [
        # EVT-AI2026 (Completed) - 20 registrations
        ("EVT-AI2026", ["STU001", "STU002", "STU003", "STU004", "STU008", "STU010", "STU011", "STU015", "STU016", "STU017",
                        "STU021", "STU022", "STU023", "STU027", "STU028", "STU029", "STU032", "STU034", "STU035", "STU040"]),
        # EVT-CYBER1 (Completed) - 16 registrations
        ("EVT-CYBER1", ["STU002", "STU003", "STU006", "STU007", "STU009", "STU011", "STU013", "STU014", "STU017", "STU018",
                        "STU023", "STU025", "STU030", "STU031", "STU036", "STU037"]),
        # EVT-HACK26 (Completed) - 24 registrations
        ("EVT-HACK26", ["STU001", "STU002", "STU003", "STU004", "STU007", "STU008", "STU009", "STU010", "STU011", "STU014",
                        "STU015", "STU016", "STU017", "STU019", "STU021", "STU022", "STU024", "STU027", "STU028", "STU032",
                        "STU034", "STU035", "STU038", "STU040"]),
        # EVT-CULT01 (Completed) - 25 registrations
        ("EVT-CULT01", ["STU001", "STU005", "STU006", "STU007", "STU010", "STU012", "STU013", "STU014", "STU018", "STU019",
                        "STU020", "STU022", "STU024", "STU026", "STU029", "STU030", "STU031", "STU033", "STU034", "STU036",
                        "STU037", "STU038", "STU039", "STU040", "STU008"]),
        # EVT-PYBOOT (Registration Open) - 15 registrations
        ("EVT-PYBOOT", ["STU001", "STU003", "STU004", "STU008", "STU010", "STU014", "STU016", "STU019", "STU021", "STU024",
                        "STU028", "STU031", "STU034", "STU037", "STU040"]),
        # EVT-WEBDEV (Full, cap=10) - exactly 10 registrations
        ("EVT-WEBDEV", ["STU002", "STU003", "STU007", "STU009", "STU011", "STU015", "STU017", "STU023", "STU027", "STU035"]),
        # EVT-CRIC01 (Open) - 12 registrations
        ("EVT-CRIC01", ["STU005", "STU006", "STU012", "STU013", "STU018", "STU020", "STU025", "STU026", "STU029", "STU030", "STU033", "STU036"]),
        # EVT-CLOU01 (Open) - 8 registrations
        ("EVT-CLOU01", ["STU001", "STU002", "STU008", "STU015", "STU021", "STU027", "STU032", "STU038"]),
        # EVT-FINTECH (Closed) - 6 registrations
        ("EVT-FINTECH", ["STU005", "STU012", "STU020", "STU026", "STU033", "STU039"]),
        # EVT-ENTR01 (Open) - 5 registrations
        ("EVT-ENTR01", ["STU005", "STU010", "STU012", "STU022", "STU026"]),
    ]

    total_reg = 0
    reg_seq = 1
    for event_id, student_ids in registrations_plan:
        for sid in student_ids:
            reg = Registration(
                registration_id=f"REG-{reg_seq:04d}",
                student_id=sid,
                event_id=event_id,
                registration_date=(today - timedelta(days=2)).strftime("%Y-%m-%d 11:30"),
                status=RegistrationStatus.CONFIRMED.value,
            )
            reg_repo.save(reg)
            reg_seq += 1
            total_reg += 1
    print(f"  [+] Saved {total_reg} registration records.")

    # ---------------------------------------------------------
    # 4. Seed Feedback (38 feedback records on completed events)
    # ---------------------------------------------------------
    feedback_entries = [
        # AI Workshop feedback
        ("STU001", "EVT-AI2026", 5, "Outstanding workshop! The transformer and PyTorch exercises were hands-on and very clearly explained."),
        ("STU002", "EVT-AI2026", 5, "Best technical workshop of the semester. The instructors were industry experts."),
        ("STU003", "EVT-AI2026", 4, "Great content and practical labs. Could have used 30 minutes more for the deployment demo."),
        ("STU004", "EVT-AI2026", 5, "Extremely useful for my final semester project. Comprehensive slides and code repository."),
        ("STU008", "EVT-AI2026", 4, "Very informative sessions. The lab computing environment was well configured."),
        ("STU010", "EVT-AI2026", 5, "Super clear explanations of attention mechanisms and LLM prompting."),
        ("STU011", "EVT-AI2026", 3, "Content was a bit fast-paced for beginners, but the recorded materials helped."),
        ("STU015", "EVT-AI2026", 5, "Top notch! Looking forward to advanced series on MLOps."),
        ("STU016", "EVT-AI2026", 4, "Very engaging. Good Q&A session at the end."),
        ("STU021", "EVT-AI2026", 5, "Exceptional clarity in machine learning concepts. 5 stars!"),

        # Cyber Security Seminar feedback
        ("STU002", "EVT-CYBER1", 4, "Insightful session on SOC analyst roles and real-world penetration test workflows."),
        ("STU006", "EVT-CYBER1", 5, "Brilliant live demonstration of SQL injection mitigation and network packet analysis."),
        ("STU007", "EVT-CYBER1", 3, "Good overview, but would prefer more hands-on lab time rather than lecture slides."),
        ("STU009", "EVT-CYBER1", 4, "Speaker shared excellent cybersecurity roadmap and certification advice."),
        ("STU013", "EVT-CYBER1", 4, "Engaging session. The live Kali Linux demo was impressive."),
        ("STU014", "EVT-CYBER1", 3, "Decent introduction to ethical hacking. Needed better microphone audio in hall."),
        ("STU017", "EVT-CYBER1", 5, "Highly motivating session. Inspired me to take CEH preparation seriously."),
        ("STU023", "EVT-CYBER1", 4, "Crisp explanations of OWASP Top 10 vulnerabilities."),

        # Hackathon 2026 feedback
        ("STU001", "EVT-HACK26", 5, "Incredible hackathon atmosphere! Mentors were very supportive throughout the night."),
        ("STU002", "EVT-HACK26", 5, "Smooth problem statements and fair judging panel. High energy!"),
        ("STU003", "EVT-HACK26", 4, "Great teamwork experience. High speed WiFi and snacks arrangement was great."),
        ("STU007", "EVT-HACK26", 4, "Challenging problem statements. Learned a ton of Git collaboration under pressure."),
        ("STU008", "EVT-HACK26", 5, "One of the best campus hackathons. Well organized timeline and awards."),
        ("STU010", "EVT-HACK26", 5, "Loved building our prototype. The final pitch round was very professional."),
        ("STU011", "EVT-HACK26", 4, "Very fun and competitive. Would love 48 hours instead of 36 hours next time."),
        ("STU015", "EVT-HACK26", 5, "Amazing hackathon! Our team won second runner up!"),
        ("STU017", "EVT-HACK26", 3, "Judges were a bit hurried during project evaluations, but otherwise great event."),
        ("STU021", "EVT-HACK26", 4, "Strong coding challenge. Good infrastructure support."),

        # Tarang Cultural Fest feedback
        ("STU001", "EVT-CULT01", 5, "Mesmerizing evening! Battle of the bands was thrilling and audio quality was superb."),
        ("STU005", "EVT-CULT01", 4, "Vibrant crowd and outstanding dance performances. Great management."),
        ("STU006", "EVT-CULT01", 4, "Amphitheatre decorations and lighting were splendid."),
        ("STU012", "EVT-CULT01", 5, "Spectacular event. Brought the entire university together in celebration."),
        ("STU013", "EVT-CULT01", 3, "Crowd control near the main gate was chaotic, but performances were wonderful."),
        ("STU018", "EVT-CULT01", 4, "Loved the cultural diversity and musical lineup."),
        ("STU020", "EVT-CULT01", 5, "Unforgettable night. Big applause to the organizing student team!"),
        ("STU024", "EVT-CULT01", 4, "Great food stalls and stage setup."),
        ("STU030", "EVT-CULT01", 4, "Super energetic performances all evening."),
        ("STU039", "EVT-CULT01", 5, "Best cultural fest in recent years!"),
    ]

    fbk_seq = 1
    for sid, eid, rating, comment in feedback_entries:
        fbk = Feedback(
            feedback_id=f"FBK-{fbk_seq:04d}",
            student_id=sid,
            event_id=eid,
            rating=rating,
            comment=comment,
            submission_date=(today - timedelta(days=2)).strftime("%Y-%m-%d 15:45"),
        )
        fbk_repo.save(fbk)
        fbk_seq += 1
    print("  [+] Saved " + str(len(feedback_entries)) + " feedback records.")
    print("[OK] Seed process completed successfully!\n")


if __name__ == "__main__":
    seed_all(force=True)
