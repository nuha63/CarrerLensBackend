"""
Seed Script - Populates 10 career roadmaps with 6-8 phases each into Neon PostgreSQL.
Run this once after the backend is started:
    python -m app.migrations.seed_roadmaps
"""
import os
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from app.database.service import get_db_service
from app.database.models import Base, CareerPath, RoadmapPhase, RoadmapSkill

ROADMAPS: list[dict] = [
    {
        "career_name": "Machine Learning Engineer",
        "description": "Master the art of building intelligent systems. Go from programming basics to deploying production-grade ML models.",
        "estimated_duration": "9-12 months",
        "icon_name": "psychology",
        "phases": [
            {"phase_number": 1, "phase_title": "Programming Fundamentals", "phase_description": "Learn Python programming from scratch. Understand variables, loops, functions, OOP, and file I/O. Build small CLI projects.", "estimated_weeks": 4, "completion_percentage": 14, "key_skills": ["Python", "OOP", "Data Structures", "Git"]},
            {"phase_number": 2, "phase_title": "Mathematics & Statistics", "phase_description": "Cover linear algebra, calculus, probability and statistics — the mathematical backbone of ML algorithms.", "estimated_weeks": 4, "completion_percentage": 28, "key_skills": ["Linear Algebra", "Calculus", "Statistics", "Probability"]},
            {"phase_number": 3, "phase_title": "Data Analysis & Visualization", "phase_description": "Manipulate and explore data using Pandas and NumPy. Visualize insights with Matplotlib and Seaborn.", "estimated_weeks": 3, "completion_percentage": 42, "key_skills": ["Pandas", "NumPy", "Matplotlib", "Seaborn", "SQL"]},
            {"phase_number": 4, "phase_title": "Machine Learning Fundamentals", "phase_description": "Learn supervised and unsupervised learning algorithms. Apply regression, classification, clustering, and dimensionality reduction.", "estimated_weeks": 5, "completion_percentage": 57, "key_skills": ["Scikit-learn", "Regression", "Classification", "Clustering", "Feature Engineering"]},
            {"phase_number": 5, "phase_title": "Deep Learning", "phase_description": "Build neural networks with TensorFlow and PyTorch. Cover CNNs, RNNs, LSTMs, and transformers.", "estimated_weeks": 6, "completion_percentage": 71, "key_skills": ["TensorFlow", "PyTorch", "Neural Networks", "CNN", "RNN", "NLP"]},
            {"phase_number": 6, "phase_title": "MLOps & Deployment", "phase_description": "Package models with Docker, serve them with FastAPI, and deploy on cloud platforms. Learn CI/CD for ML pipelines.", "estimated_weeks": 4, "completion_percentage": 85, "key_skills": ["Docker", "FastAPI", "AWS/GCP", "MLflow", "CI/CD"]},
            {"phase_number": 7, "phase_title": "Projects & Portfolio", "phase_description": "Build 3 end-to-end ML projects: image classifier, NLP sentiment analyser, and recommendation engine. Host on GitHub.", "estimated_weeks": 4, "completion_percentage": 95, "key_skills": ["Project Management", "GitHub", "Documentation", "APIs"]},
            {"phase_number": 8, "phase_title": "Interview Preparation", "phase_description": "Practice ML system design, coding challenges, and behavioural interviews. Prepare a polished CV and portfolio.", "estimated_weeks": 3, "completion_percentage": 100, "key_skills": ["System Design", "LeetCode", "Behavioural Interviews", "Resume"]},
        ]
    },
    {
        "career_name": "Data Scientist",
        "description": "Turn raw data into actionable insights. Learn statistics, data wrangling, machine learning, and storytelling with data.",
        "estimated_duration": "8-10 months",
        "icon_name": "bar_chart",
        "phases": [
            {"phase_number": 1, "phase_title": "Python & SQL Basics", "phase_description": "Build a solid foundation in Python scripting and SQL queries for data extraction and manipulation.", "estimated_weeks": 4, "completion_percentage": 16, "key_skills": ["Python", "SQL", "PostgreSQL", "Pandas"]},
            {"phase_number": 2, "phase_title": "Statistics & Probability", "phase_description": "Master descriptive and inferential statistics, hypothesis testing, A/B testing, and Bayesian thinking.", "estimated_weeks": 4, "completion_percentage": 33, "key_skills": ["Statistics", "Probability", "Hypothesis Testing", "A/B Testing"]},
            {"phase_number": 3, "phase_title": "Data Wrangling & EDA", "phase_description": "Clean messy datasets, handle missing values, and conduct in-depth Exploratory Data Analysis.", "estimated_weeks": 3, "completion_percentage": 49, "key_skills": ["Pandas", "NumPy", "Data Cleaning", "EDA", "Seaborn"]},
            {"phase_number": 4, "phase_title": "Machine Learning for DS", "phase_description": "Apply ML algorithms to real datasets. Focus on model selection, evaluation metrics, and interpretability.", "estimated_weeks": 5, "completion_percentage": 66, "key_skills": ["Scikit-learn", "XGBoost", "Model Evaluation", "Feature Selection"]},
            {"phase_number": 5, "phase_title": "Data Visualization & Storytelling", "phase_description": "Create compelling dashboards with Tableau and Power BI. Tell data stories that influence decisions.", "estimated_weeks": 3, "completion_percentage": 80, "key_skills": ["Tableau", "Power BI", "Matplotlib", "Plotly", "Storytelling"]},
            {"phase_number": 6, "phase_title": "Projects & Portfolio", "phase_description": "Build an end-to-end data science project: collect data, analyse, model, visualise, and present findings.", "estimated_weeks": 3, "completion_percentage": 92, "key_skills": ["Jupyter", "GitHub", "Kaggle", "Presentation"]},
            {"phase_number": 7, "phase_title": "Interview Preparation", "phase_description": "Tackle case interviews, SQL challenges, take-home assignments, and data science coding problems.", "estimated_weeks": 2, "completion_percentage": 100, "key_skills": ["Case Studies", "SQL Challenges", "Statistics Review", "Communication"]},
        ]
    },
    {
        "career_name": "Flutter Developer",
        "description": "Build beautiful cross-platform mobile apps for iOS and Android using Flutter and Dart.",
        "estimated_duration": "6-8 months",
        "icon_name": "phone_android",
        "phases": [
            {"phase_number": 1, "phase_title": "Dart Programming Language", "phase_description": "Learn Dart fundamentals: variables, control flow, functions, classes, async/await, and streams.", "estimated_weeks": 3, "completion_percentage": 17, "key_skills": ["Dart", "OOP", "Async/Await", "Streams"]},
            {"phase_number": 2, "phase_title": "Flutter Basics & Widgets", "phase_description": "Understand the Flutter widget tree. Build UIs with StatelessWidget, StatefulWidget, and Material components.", "estimated_weeks": 4, "completion_percentage": 33, "key_skills": ["Flutter", "Widgets", "Material Design", "Layouts"]},
            {"phase_number": 3, "phase_title": "State Management", "phase_description": "Master state management patterns: Provider, Riverpod, BLoC. Manage app state cleanly across screens.", "estimated_weeks": 4, "completion_percentage": 50, "key_skills": ["Provider", "Riverpod", "BLoC", "State Management"]},
            {"phase_number": 4, "phase_title": "API Integration & Storage", "phase_description": "Connect Flutter apps to REST APIs using http/dio. Persist data with SharedPreferences and SQLite.", "estimated_weeks": 3, "completion_percentage": 67, "key_skills": ["REST APIs", "HTTP", "Dio", "SharedPreferences", "SQLite"]},
            {"phase_number": 5, "phase_title": "Navigation & Architecture", "phase_description": "Implement named routes, deep linking, and clean architecture (Repository + Service layers).", "estimated_weeks": 3, "completion_percentage": 83, "key_skills": ["Navigation", "GoRouter", "Clean Architecture", "Dependency Injection"]},
            {"phase_number": 6, "phase_title": "Testing, Deployment & Portfolio", "phase_description": "Write unit, widget, and integration tests. Publish apps to Google Play and Apple App Store.", "estimated_weeks": 3, "completion_percentage": 100, "key_skills": ["Unit Testing", "Widget Testing", "Google Play", "App Store", "CI/CD"]},
        ]
    },
    {
        "career_name": "Android Developer",
        "description": "Build native Android apps with Kotlin and Android SDK, following Google's best practices.",
        "estimated_duration": "7-9 months",
        "icon_name": "android",
        "phases": [
            {"phase_number": 1, "phase_title": "Kotlin Fundamentals", "phase_description": "Learn Kotlin: null safety, extension functions, coroutines, and idiomatic Kotlin patterns.", "estimated_weeks": 4, "completion_percentage": 17, "key_skills": ["Kotlin", "Coroutines", "Null Safety", "OOP"]},
            {"phase_number": 2, "phase_title": "Android Fundamentals", "phase_description": "Understand Activity lifecycle, Fragments, Intents, and building layouts with XML/Compose.", "estimated_weeks": 4, "completion_percentage": 33, "key_skills": ["Android SDK", "Activities", "Fragments", "Jetpack Compose"]},
            {"phase_number": 3, "phase_title": "Jetpack & Architecture", "phase_description": "Use Jetpack components: ViewModel, LiveData, Room, Navigation Component. Apply MVVM architecture.", "estimated_weeks": 4, "completion_percentage": 50, "key_skills": ["ViewModel", "LiveData", "Room", "MVVM", "Navigation"]},
            {"phase_number": 4, "phase_title": "Networking & Data", "phase_description": "Integrate Retrofit and OkHttp for REST APIs. Handle JSON with Gson/Moshi. Use Hilt for DI.", "estimated_weeks": 3, "completion_percentage": 67, "key_skills": ["Retrofit", "OkHttp", "Hilt", "Coroutines Flow"]},
            {"phase_number": 5, "phase_title": "UI Polish & Performance", "phase_description": "Build responsive, accessible UIs. Profile and optimise app performance. Handle different screen sizes.", "estimated_weeks": 3, "completion_percentage": 83, "key_skills": ["Material You", "Accessibility", "Performance", "Profiling"]},
            {"phase_number": 6, "phase_title": "Testing & Play Store", "phase_description": "Write JUnit, Espresso, and Mockito tests. Publish to Google Play Store with CI/CD pipelines.", "estimated_weeks": 3, "completion_percentage": 100, "key_skills": ["JUnit", "Espresso", "Google Play", "Firebase", "CI/CD"]},
        ]
    },
    {
        "career_name": "Backend Developer",
        "description": "Design and build scalable server-side systems, REST APIs, and databases that power modern applications.",
        "estimated_duration": "7-9 months",
        "icon_name": "storage",
        "phases": [
            {"phase_number": 1, "phase_title": "Programming & Web Basics", "phase_description": "Master Python or Node.js. Understand HTTP, REST principles, JSON, and how the web works.", "estimated_weeks": 3, "completion_percentage": 17, "key_skills": ["Python", "Node.js", "HTTP", "REST", "JSON"]},
            {"phase_number": 2, "phase_title": "Databases & SQL", "phase_description": "Design relational schemas, write complex SQL queries, and learn PostgreSQL. Understand indexing and transactions.", "estimated_weeks": 3, "completion_percentage": 33, "key_skills": ["PostgreSQL", "SQL", "Schema Design", "Indexing", "Transactions"]},
            {"phase_number": 3, "phase_title": "API Development", "phase_description": "Build production-grade REST APIs with FastAPI or Express.js. Handle auth (JWT), validation, and error handling.", "estimated_weeks": 4, "completion_percentage": 50, "key_skills": ["FastAPI", "Express.js", "JWT", "Authentication", "Pydantic"]},
            {"phase_number": 4, "phase_title": "Caching & Async Systems", "phase_description": "Add Redis caching. Build async task queues with Celery or BullMQ. Design event-driven architectures.", "estimated_weeks": 3, "completion_percentage": 67, "key_skills": ["Redis", "Celery", "Message Queues", "Async Programming"]},
            {"phase_number": 5, "phase_title": "DevOps & Cloud Basics", "phase_description": "Containerise apps with Docker. Deploy on AWS/GCP. Set up basic CI/CD with GitHub Actions.", "estimated_weeks": 3, "completion_percentage": 83, "key_skills": ["Docker", "AWS", "GCP", "GitHub Actions", "Linux"]},
            {"phase_number": 6, "phase_title": "Projects & System Design", "phase_description": "Build a full-featured API project (e-commerce or social platform). Practice system design patterns.", "estimated_weeks": 4, "completion_percentage": 100, "key_skills": ["System Design", "Microservices", "API Documentation", "Swagger"]},
        ]
    },
    {
        "career_name": "Full Stack Developer",
        "description": "Master both frontend and backend development to build complete, production-ready web applications.",
        "estimated_duration": "10-12 months",
        "icon_name": "code",
        "phases": [
            {"phase_number": 1, "phase_title": "HTML, CSS & JavaScript", "phase_description": "Build the web foundation. Learn semantic HTML, CSS flexbox/grid, and JavaScript ES6+.", "estimated_weeks": 4, "completion_percentage": 14, "key_skills": ["HTML5", "CSS3", "JavaScript", "ES6", "Responsive Design"]},
            {"phase_number": 2, "phase_title": "React.js Frontend", "phase_description": "Build modern SPAs with React. Master hooks, state management with Redux/Context, and React Router.", "estimated_weeks": 5, "completion_percentage": 28, "key_skills": ["React", "Hooks", "Redux", "React Router", "TypeScript"]},
            {"phase_number": 3, "phase_title": "Backend with Node.js", "phase_description": "Build REST APIs with Express.js and Node.js. Handle middleware, routing, and error handling.", "estimated_weeks": 4, "completion_percentage": 42, "key_skills": ["Node.js", "Express.js", "REST APIs", "Middleware", "JWT"]},
            {"phase_number": 4, "phase_title": "Databases", "phase_description": "Work with both SQL (PostgreSQL) and NoSQL (MongoDB). Use ORMs like Prisma or Mongoose.", "estimated_weeks": 3, "completion_percentage": 57, "key_skills": ["PostgreSQL", "MongoDB", "Prisma", "Mongoose", "SQL"]},
            {"phase_number": 5, "phase_title": "Authentication & Security", "phase_description": "Implement secure auth flows: JWT, OAuth2, session management, HTTPS, and common security best practices.", "estimated_weeks": 2, "completion_percentage": 71, "key_skills": ["JWT", "OAuth2", "Security", "CORS", "HTTPS"]},
            {"phase_number": 6, "phase_title": "Deployment & Cloud", "phase_description": "Deploy full-stack apps with Docker and cloud platforms. Set up CI/CD pipelines and monitoring.", "estimated_weeks": 3, "completion_percentage": 85, "key_skills": ["Docker", "Vercel", "Railway", "GitHub Actions", "Monitoring"]},
            {"phase_number": 7, "phase_title": "Portfolio Projects & Interview Prep", "phase_description": "Build 2 complete full-stack projects. Practice system design and full-stack coding interviews.", "estimated_weeks": 4, "completion_percentage": 100, "key_skills": ["Portfolio", "System Design", "Technical Interviews", "GitHub"]},
        ]
    },
    {
        "career_name": "UI/UX Designer",
        "description": "Design intuitive, beautiful digital products. Master the design process from user research to high-fidelity prototypes.",
        "estimated_duration": "6-8 months",
        "icon_name": "design_services",
        "phases": [
            {"phase_number": 1, "phase_title": "Design Fundamentals", "phase_description": "Learn visual design principles: typography, colour theory, spacing, hierarchy, and grid systems.", "estimated_weeks": 3, "completion_percentage": 17, "key_skills": ["Typography", "Color Theory", "Layout", "Visual Design", "Grid Systems"]},
            {"phase_number": 2, "phase_title": "UX Research & Strategy", "phase_description": "Conduct user interviews, create personas, map user journeys, and define problem statements.", "estimated_weeks": 3, "completion_percentage": 33, "key_skills": ["User Research", "Personas", "User Journeys", "Empathy Mapping", "Problem Definition"]},
            {"phase_number": 3, "phase_title": "Figma Mastery", "phase_description": "Master Figma for wireframing, component libraries, auto-layout, and collaborative design.", "estimated_weeks": 4, "completion_percentage": 50, "key_skills": ["Figma", "Wireframing", "Prototyping", "Components", "Auto Layout"]},
            {"phase_number": 4, "phase_title": "Interaction & Prototyping", "phase_description": "Design micro-interactions, animations, and interactive prototypes. Test flows end-to-end.", "estimated_weeks": 3, "completion_percentage": 67, "key_skills": ["Micro-interactions", "Prototyping", "Animation", "Usability Testing"]},
            {"phase_number": 5, "phase_title": "Design Systems", "phase_description": "Build scalable design systems with reusable components, tokens, and documentation.", "estimated_weeks": 3, "completion_percentage": 83, "key_skills": ["Design Systems", "Component Libraries", "Style Guides", "Documentation"]},
            {"phase_number": 6, "phase_title": "Portfolio & Case Studies", "phase_description": "Document 3 full UX case studies showcasing research, process, and final designs. Build your portfolio website.", "estimated_weeks": 3, "completion_percentage": 100, "key_skills": ["Case Studies", "Portfolio", "Presentation", "Behance", "Dribbble"]},
        ]
    },
    {
        "career_name": "Cybersecurity Analyst",
        "description": "Protect systems and data from cyber threats. Learn networking, ethical hacking, and security operations.",
        "estimated_duration": "9-12 months",
        "icon_name": "security",
        "phases": [
            {"phase_number": 1, "phase_title": "Networking Fundamentals", "phase_description": "Understand TCP/IP, DNS, HTTP/HTTPS, firewalls, VPNs, and the OSI model.", "estimated_weeks": 4, "completion_percentage": 14, "key_skills": ["TCP/IP", "DNS", "HTTP/HTTPS", "Firewalls", "OSI Model"]},
            {"phase_number": 2, "phase_title": "Linux & Command Line", "phase_description": "Become proficient in Linux: file system, permissions, process management, scripting, and networking tools.", "estimated_weeks": 4, "completion_percentage": 28, "key_skills": ["Linux", "Bash", "Shell Scripting", "Permissions", "Networking Tools"]},
            {"phase_number": 3, "phase_title": "Security Fundamentals", "phase_description": "Study CIA triad, cryptography, PKI, authentication protocols, and common vulnerabilities (OWASP Top 10).", "estimated_weeks": 4, "completion_percentage": 42, "key_skills": ["Cryptography", "PKI", "OWASP", "Authentication", "Vulnerabilities"]},
            {"phase_number": 4, "phase_title": "Ethical Hacking & Penetration Testing", "phase_description": "Learn offensive techniques: reconnaissance, exploitation, privilege escalation with tools like Metasploit and Burp Suite.", "estimated_weeks": 5, "completion_percentage": 57, "key_skills": ["Metasploit", "Burp Suite", "Pen Testing", "Kali Linux", "Nmap"]},
            {"phase_number": 5, "phase_title": "Security Operations (SOC)", "phase_description": "Monitor networks with SIEM tools. Perform incident response, log analysis, and threat hunting.", "estimated_weeks": 4, "completion_percentage": 71, "key_skills": ["SIEM", "Splunk", "Incident Response", "Log Analysis", "Threat Hunting"]},
            {"phase_number": 6, "phase_title": "Cloud & Application Security", "phase_description": "Secure cloud environments (AWS/Azure) and applications. Learn IAM, compliance, and DevSecOps.", "estimated_weeks": 4, "completion_percentage": 85, "key_skills": ["AWS Security", "IAM", "DevSecOps", "Compliance", "Zero Trust"]},
            {"phase_number": 7, "phase_title": "Certifications & Job Prep", "phase_description": "Prepare for CompTIA Security+, CEH, or eJPT. Build a home lab portfolio and practice interviews.", "estimated_weeks": 4, "completion_percentage": 100, "key_skills": ["CompTIA Security+", "CEH", "Home Lab", "CTF", "Resume"]},
        ]
    },
    {
        "career_name": "DevOps Engineer",
        "description": "Bridge development and operations. Automate infrastructure, build CI/CD pipelines, and ensure system reliability.",
        "estimated_duration": "9-11 months",
        "icon_name": "settings_suggest",
        "phases": [
            {"phase_number": 1, "phase_title": "Linux & Scripting", "phase_description": "Master Linux administration, Bash scripting, and Python automation for infrastructure tasks.", "estimated_weeks": 4, "completion_percentage": 14, "key_skills": ["Linux", "Bash", "Python", "Shell Scripting", "Cron"]},
            {"phase_number": 2, "phase_title": "Git & Version Control", "phase_description": "Advanced Git workflows: branching strategies, rebasing, PR reviews, and monorepo management.", "estimated_weeks": 2, "completion_percentage": 28, "key_skills": ["Git", "GitHub", "GitFlow", "Code Review", "Monorepo"]},
            {"phase_number": 3, "phase_title": "Containers with Docker", "phase_description": "Build, ship, and run containers. Write Dockerfiles, compose multi-container apps, and manage images.", "estimated_weeks": 3, "completion_percentage": 42, "key_skills": ["Docker", "Docker Compose", "Dockerfile", "Container Registry"]},
            {"phase_number": 4, "phase_title": "Kubernetes Orchestration", "phase_description": "Deploy and manage containerised apps at scale with Kubernetes: pods, services, deployments, and Helm.", "estimated_weeks": 5, "completion_percentage": 57, "key_skills": ["Kubernetes", "kubectl", "Helm", "Pods", "Services", "Ingress"]},
            {"phase_number": 5, "phase_title": "CI/CD Pipelines", "phase_description": "Build automated pipelines with GitHub Actions, Jenkins, or GitLab CI. Implement automated testing and deployment.", "estimated_weeks": 3, "completion_percentage": 71, "key_skills": ["GitHub Actions", "Jenkins", "GitLab CI", "CI/CD", "Pipeline as Code"]},
            {"phase_number": 6, "phase_title": "Infrastructure as Code", "phase_description": "Provision cloud resources with Terraform and manage configuration with Ansible.", "estimated_weeks": 4, "completion_percentage": 85, "key_skills": ["Terraform", "Ansible", "IaC", "AWS", "GCP"]},
            {"phase_number": 7, "phase_title": "Monitoring & SRE Practices", "phase_description": "Set up observability with Prometheus, Grafana, and ELK stack. Learn SLOs, SLAs, and on-call practices.", "estimated_weeks": 3, "completion_percentage": 100, "key_skills": ["Prometheus", "Grafana", "ELK Stack", "SRE", "Alerting"]},
        ]
    },
    {
        "career_name": "QA Engineer",
        "description": "Ensure software quality through systematic testing, automation, and quality processes that prevent bugs before they reach users.",
        "estimated_duration": "6-8 months",
        "icon_name": "fact_check",
        "phases": [
            {"phase_number": 1, "phase_title": "Software Testing Fundamentals", "phase_description": "Understand the SDLC, testing types (unit, integration, E2E), test planning, and defect lifecycle.", "estimated_weeks": 3, "completion_percentage": 17, "key_skills": ["SDLC", "Test Planning", "Test Cases", "Bug Reporting", "JIRA"]},
            {"phase_number": 2, "phase_title": "Manual Testing Techniques", "phase_description": "Practice black-box and white-box testing. Write detailed test cases, execute regression, and exploratory testing.", "estimated_weeks": 3, "completion_percentage": 33, "key_skills": ["Black-box Testing", "White-box Testing", "Regression Testing", "Test Documentation"]},
            {"phase_number": 3, "phase_title": "Python for Automation", "phase_description": "Learn Python basics focused on test automation: scripting, file handling, and working with APIs.", "estimated_weeks": 3, "completion_percentage": 50, "key_skills": ["Python", "Scripting", "REST API Testing", "JSON", "Requests"]},
            {"phase_number": 4, "phase_title": "Test Automation with Selenium & Pytest", "phase_description": "Automate web UI tests with Selenium WebDriver. Build test suites with Pytest and generate reports.", "estimated_weeks": 4, "completion_percentage": 67, "key_skills": ["Selenium", "Pytest", "WebDriver", "Test Reports", "Page Object Model"]},
            {"phase_number": 5, "phase_title": "API Testing & Performance", "phase_description": "Test REST APIs with Postman and RestAssured. Run performance/load tests with JMeter or k6.", "estimated_weeks": 3, "completion_percentage": 83, "key_skills": ["Postman", "API Testing", "JMeter", "k6", "Load Testing"]},
            {"phase_number": 6, "phase_title": "CI/CD Integration & Portfolio", "phase_description": "Integrate tests into CI/CD pipelines. Build a QA portfolio with automation frameworks and test reports.", "estimated_weeks": 3, "completion_percentage": 100, "key_skills": ["GitHub Actions", "CI/CD", "Test Coverage", "Portfolio", "Agile QA"]},
        ]
    },
]


def seed():
    db_service = get_db_service()

    # Ensure tables exist
    from app.database.models import Base
    Base.metadata.create_all(bind=db_service.engine)

    db = db_service.get_session()
    try:
        seeded = 0
        for rm_data in ROADMAPS:
            # Check if already exists
            existing = db.query(CareerPath).filter(
                CareerPath.name == rm_data["career_name"]
            ).first()

            if existing:
                print(f"  [SKIP] {rm_data['career_name']} already exists.")
                continue

            roadmap = CareerPath(
                name=rm_data["career_name"],
                description=rm_data["description"],
            )
            db.add(roadmap)
            db.flush()  # get roadmap.id before phases

            for ph in rm_data["phases"]:
                phase = RoadmapPhase(
                    career_id=roadmap.id,
                    phase_order=ph["phase_number"],
                    phase_name=ph["phase_title"],
                )
                db.add(phase)
                db.flush()  # get phase.id before skills

                # Add skills for this phase
                for idx, skill_name in enumerate(ph["key_skills"]):
                    skill = RoadmapSkill(
                        phase_id=phase.id,
                        skill_order=idx + 1,
                        skill_name=skill_name,
                    )
                    db.add(skill)

            db.commit()
            seeded += 1
            print(f"  [OK] Seeded: {rm_data['career_name']} ({len(rm_data['phases'])} phases)")

        print(f"\n✅ Seeding complete. {seeded} new roadmaps added.")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding career roadmaps...")
    seed()
