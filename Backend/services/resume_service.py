import re
import uuid
from typing import Dict, List, Optional, Tuple, Union
from services.document_parser import DocumentParser
from schemas.candidate import (
    ParsedResume,
    ContactInfo,
    ResumeAnalysisResult,
    SkillsAnalysis,
    ExperienceAnalysis,
    EducationAnalysis,
    WorkExperience,
    Education,
    ProjectDetail,
    AchievementDetail,
)


class ResumeService:
    """
    Core service responsible for parsing resumes, extracting candidate contacts,
    skills categorization, and deeply analyzing candidate profiles for mock interviews.
    """

    SKILL_TAXONOMY = {
        "Languages": [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang",
            "Rust", "PHP", "Ruby", "Swift", "Kotlin", "SQL", "HTML", "CSS"
        ],
        "Frontend": [
            "React", "Next.js", "Vue.js", "Angular", "Svelte", "Redux", "Tailwind",
            "TailwindCSS", "Bootstrap", "Webpack", "Vite", "GraphQL"
        ],
        "Backend": [
            "FastAPI", "Django", "Flask", "Node.js", "Express", "Spring Boot",
            "NestJS", "REST API", "Microservices", "gRPC"
        ],
        "Database": [
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Cassandra",
            "Elasticsearch", "DynamoDB", "Prisma", "SQLAlchemy"
        ],
        "Cloud & DevOps": [
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub",
            "GitLab", "CI/CD", "Terraform", "Linux", "Nginx"
        ],
        "AI & Data": [
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-Learn",
            "OpenAI", "LangChain", "LLM", "HuggingFace"
        ],
        "Methodology & Soft Skills": [
            "System Design", "Agile", "Scrum", "STAR Method", "Test-Driven Development",
            "Code Review", "Leadership", "Problem Solving"
        ]
    }

    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
    LINKEDIN_REGEX = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+", re.IGNORECASE)
    GITHUB_REGEX = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+", re.IGNORECASE)
    YEAR_RANGE_REGEX = re.compile(r"\b(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|present|current)\b", re.IGNORECASE)

    SECTIONS = [
        "Experience", "Work Experience", "Employment History",
        "Education", "Academic Background",
        "Projects", "Personal Projects",
        "Skills", "Technical Skills", "Core Competencies",
        "Certifications", "Summary", "Professional Summary", "Achievements"
    ]

    @classmethod
    def parse_resume(cls, filename: str, content: bytes) -> ParsedResume:
        """
        Parses raw resume file bytes into a clean, structured ParsedResume object.
        """
        raw_text, page_count = DocumentParser.parse_file(filename, content)
        if not raw_text.strip():
            raise ValueError("Could not extract any readable text from the uploaded resume.")

        word_count = len(raw_text.split())
        contact_info = cls._extract_contact_info(raw_text)
        categorized_skills, all_detected_skills = cls._detect_skills(raw_text)
        sections_detected = cls._detect_sections(raw_text)

        preview_text = raw_text[:350].strip() + ("..." if len(raw_text) > 350 else "")
        resume_id = f"res_{uuid.uuid4().hex[:12]}"

        return ParsedResume(
            resume_id=resume_id,
            filename=filename,
            file_size_bytes=len(content),
            page_count=page_count,
            word_count=word_count,
            contact_info=contact_info,
            detected_skills=all_detected_skills,
            categorized_skills=categorized_skills,
            sections_detected=sections_detected,
            preview_text=preview_text,
            raw_text=raw_text
        )

    @classmethod
    def analyze_resume(cls, resume_input: Union[ParsedResume, str], filename: str = "resume.txt") -> ResumeAnalysisResult:
        """
        Deeply analyzes candidate skills, experience, education, projects, and achievements.
        Computes completeness score, primary domain, seniority level, and recommended interview focus.
        """
        if isinstance(resume_input, ParsedResume):
            raw_text = resume_input.raw_text
            resume_id = resume_input.resume_id
            candidate_name = resume_input.contact_info.name
        else:
            raw_text = resume_input
            resume_id = f"res_{uuid.uuid4().hex[:12]}"
            contact = cls._extract_contact_info(raw_text)
            candidate_name = contact.name

        skills_analysis = cls.extract_candidate_skills(raw_text)
        experience_analysis = cls.extract_candidate_experience(raw_text)
        education_analysis = cls.extract_candidate_education(raw_text)
        projects = cls.extract_candidate_projects(raw_text, skills_analysis.top_skills)
        achievements = cls.extract_candidate_achievements(raw_text)

        completeness_score = cls._calculate_completeness(
            raw_text=raw_text,
            skills_count=skills_analysis.total_skills_count,
            exp_count=len(experience_analysis.items),
            edu_count=len(education_analysis.items),
            projects_count=len(projects)
        )

        focus_areas = cls._generate_recommended_focus(
            primary_domain=skills_analysis.primary_domain,
            seniority=experience_analysis.seniority_level,
            top_skills=skills_analysis.top_skills,
            has_projects=bool(projects)
        )

        executive_summary = (
            f"{candidate_name or 'Candidate'} is a {experience_analysis.seniority_level} "
            f"specializing in {skills_analysis.primary_domain} with ~{experience_analysis.total_years_estimated:.1f} "
            f"years of estimated experience across {len(skills_analysis.top_skills)} core technical skills."
        )

        return ResumeAnalysisResult(
            resume_id=resume_id,
            candidate_name=candidate_name,
            executive_summary=executive_summary,
            skills_analysis=skills_analysis,
            experience_analysis=experience_analysis,
            education_analysis=education_analysis,
            projects=projects,
            achievements=achievements,
            completeness_score=completeness_score,
            recommended_interview_focus=focus_areas
        )

    @classmethod
    def extract_candidate_skills(cls, text: str) -> SkillsAnalysis:
        """Extract and categorize technical and soft skills, determining primary technical domain."""
        categorized, all_skills = cls._detect_skills(text)

        # Determine primary domain based on largest skill category
        category_counts = {cat: len(skills) for cat, skills in categorized.items() if cat != "Methodology & Soft Skills"}
        if category_counts:
            dominant = max(category_counts, key=category_counts.get)
            domain_map = {
                "Frontend": "Frontend Web Architecture",
                "Backend": "Backend & Distributed Systems",
                "Cloud & DevOps": "Cloud & DevOps Infrastructure",
                "AI & Data": "AI, ML & Data Engineering",
                "Languages": "Software Engineering & Algorithms",
                "Database": "Database & Data Architecture"
            }
            primary_domain = domain_map.get(dominant, "Fullstack Software Engineering")
            if "Frontend" in category_counts and "Backend" in category_counts:
                primary_domain = "Fullstack Software Engineering"
        else:
            primary_domain = "General Software Engineering"

        return SkillsAnalysis(
            total_skills_count=len(all_skills),
            primary_domain=primary_domain,
            top_skills=all_skills[:12],
            categorized=categorized
        )

    @classmethod
    def extract_candidate_experience(cls, text: str) -> ExperienceAnalysis:
        """Extract work experience entries, calculate total estimated years, and infer seniority level."""
        items: List[WorkExperience] = []
        
        # Isolate experience section to avoid picking up education degree years
        exp_section = cls._extract_section_text(text, ["Work Experience", "Experience", "Employment History"]) or text

        year_matches = list(cls.YEAR_RANGE_REGEX.finditer(exp_section))
        total_years = 0.0
        current_year = 2026

        for match in year_matches:
            start_str, end_str = match.groups()
            try:
                start_yr = int(start_str)
                is_curr = end_str.lower() in {"present", "current"}
                end_yr = current_year if is_curr else int(end_str)
                duration_yrs = max(0.5, end_yr - start_yr)
                total_years += duration_yrs

                # Extract line containing this match or lines above it
                pre_text = exp_section[:match.start()]
                last_line = pre_text.splitlines()[-1] if pre_text.splitlines() else ""
                
                # Role/company heuristic
                header_line = last_line.strip()
                role_guess = "Software Engineer"
                company_guess = None
                
                if "-" in header_line:
                    parts = header_line.split("-")
                    role_guess = parts[0].strip()
                    company_guess = parts[1].strip()
                elif header_line:
                    role_guess = header_line[:60]

                items.append(
                    WorkExperience(
                        role=role_guess,
                        company=company_guess,
                        duration=match.group(0),
                        start_year=start_yr,
                        end_year=end_yr,
                        is_current=is_curr,
                        description=header_line
                    )
                )
            except Exception:
                continue

        # Count metric/quantifiable indicators (e.g. 40%, $1M, 5x, 100k)
        metrics_found = len(re.findall(r"\b\d+%\b|\$\d+[\w.]*|\b\d+x\b|\b\d+\+?\s*(?:users|clients|rps|ms|qps|stars)\b", text, re.IGNORECASE))

        # Infer seniority level
        text_lower = text.lower()
        if total_years >= 8 or "staff" in text_lower or "principal" in text_lower:
            seniority = "Staff / Principal Engineer"
        elif total_years >= 4 or "senior" in text_lower:
            seniority = "Senior Engineer"
        elif total_years >= 2 or "mid" in text_lower:
            seniority = "Mid-Level Engineer"
        else:
            seniority = "Junior / Entry-Level Engineer"

        return ExperienceAnalysis(
            total_years_estimated=round(min(total_years, 20.0), 1),
            seniority_level=seniority,
            items=items[:6],
            quantifiable_metrics_count=metrics_found
        )

    @classmethod
    def extract_candidate_education(cls, text: str) -> EducationAnalysis:
        """Extract degree, major, and graduation year from education section."""
        items: List[Education] = []
        edu_patterns = [
            r"\b(Bachelor(?:'s)?|B\.?S\.?|B\.?Tech|B\.?E\.?|Master(?:'s)?|M\.?S\.?|M\.?Tech|Ph\.?D\.?)\b(?:\s+(?:of|in)\s+([A-Za-z\s]+))?",
            r"\b(Computer Science|Software Engineering|Information Technology|Electrical Engineering|Data Science)\b"
        ]

        degrees_found = re.findall(edu_patterns[0], text, re.IGNORECASE)
        highest_degree = None

        for match in degrees_found:
            degree_name = match[0] if isinstance(match, tuple) else match
            field = match[1] if isinstance(match, tuple) and len(match) > 1 else "Computer Science"
            if not highest_degree:
                highest_degree = degree_name

            items.append(
                Education(
                    degree=degree_name.strip(),
                    field_of_study=field.strip() if field else None,
                    institution="University / Institution",
                    year=None
                )
            )

        if not highest_degree and "bachelor" in text.lower():
            highest_degree = "Bachelor of Science"

        return EducationAnalysis(
            items=items[:3],
            highest_degree=highest_degree or "Bachelor's Degree"
        )

    @classmethod
    def extract_candidate_projects(cls, text: str, detected_skills: List[str]) -> List[ProjectDetail]:
        """Detect personal or professional project items."""
        projects: List[ProjectDetail] = []
        project_section = cls._extract_section_text(text, ["Projects", "Personal Projects", "Key Projects"])

        if project_section:
            # Split by bullet points or empty lines
            chunks = [c.strip() for c in re.split(r"\n(?=[A-Z0-9][\w\s-]{2,30}:|\n)", project_section) if c.strip()]
            for chunk in chunks[:4]:
                lines = chunk.splitlines()
                name = lines[0].strip()[:50]
                techs = [s for s in detected_skills if re.search(r"\b" + re.escape(s) + r"\b", chunk, re.IGNORECASE)]
                projects.append(
                    ProjectDetail(
                        name=name,
                        description=chunk[:200],
                        technologies=techs[:6],
                        highlights=lines[1:3] if len(lines) > 1 else []
                    )
                )

        return projects

    @classmethod
    def extract_candidate_achievements(cls, text: str) -> List[AchievementDetail]:
        """Extract certifications, honors, and competitive achievements."""
        achievements: List[AchievementDetail] = []
        cert_keywords = ["AWS Certified", "CKA", "GCP Certified", "Azure Certified", "Hackathon", "Dean's List", "Winner", "1st Place"]

        for kw in cert_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
                achievements.append(
                    AchievementDetail(
                        title=kw,
                        issuer_or_detail="Recognized Achievement / Certification"
                    )
                )

        return achievements

    @classmethod
    def _extract_contact_info(cls, text: str) -> ContactInfo:
        """Extract email, phone, and profile links from text."""
        email_match = cls.EMAIL_REGEX.search(text)
        phone_match = cls.PHONE_REGEX.search(text)
        linkedin_match = cls.LINKEDIN_REGEX.search(text)
        github_match = cls.GITHUB_REGEX.search(text)

        name: Optional[str] = None
        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned and len(cleaned) < 50 and not any(char in cleaned for char in "@/:\\"):
                if cleaned.lower() not in {"resume", "curriculum vitae", "cv"}:
                    name = cleaned
                    break

        return ContactInfo(
            name=name,
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0) if phone_match else None,
            linkedin=linkedin_match.group(0) if linkedin_match else None,
            github=github_match.group(0) if github_match else None
        )

    @classmethod
    def _detect_skills(cls, text: str) -> Tuple[Dict[str, List[str]], List[str]]:
        """Detect and classify technical skills using word boundary matching."""
        categorized: Dict[str, List[str]] = {}
        all_skills: List[str] = []
        text_lower = text.lower()

        for category, skills in cls.SKILL_TAXONOMY.items():
            matched_for_category = []
            for skill in skills:
                pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
                if re.search(pattern, text_lower):
                    matched_for_category.append(skill)
                    if skill not in all_skills:
                        all_skills.append(skill)
            if matched_for_category:
                categorized[category] = matched_for_category

        return categorized, all_skills

    @classmethod
    def _detect_sections(cls, text: str) -> List[str]:
        """Detect standard resume headings present in the document."""
        found = []
        text_lower = text.lower()
        for section in cls.SECTIONS:
            pattern = r"(?i)(?:^|\n)\s*" + re.escape(section) + r"\s*(?::|\n)"
            if re.search(pattern, text_lower):
                found.append(section)
        return found

    @classmethod
    def _extract_section_text(cls, text: str, header_aliases: List[str]) -> Optional[str]:
        """Extract the text body belonging to a specific section header."""
        for alias in header_aliases:
            pattern = r"(?i)(?:^|\n)\s*" + re.escape(alias) + r"\s*(?::|\n)([\s\S]*?)(?=\n[A-Z][A-Za-z\s]{3,25}(?::|\n)|$)"
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _calculate_completeness(raw_text: str, skills_count: int, exp_count: int, edu_count: int, projects_count: int) -> int:
        """Compute an overall resume completeness score (0-100)."""
        score = 0
        if len(raw_text.split()) > 150: score += 20
        if skills_count >= 5: score += 25
        elif skills_count >= 2: score += 15
        if exp_count >= 1: score += 25
        if edu_count >= 1: score += 15
        if projects_count >= 1: score += 15
        return min(score, 100)

    @staticmethod
    def _generate_recommended_focus(primary_domain: str, seniority: str, top_skills: List[str], has_projects: bool) -> List[str]:
        """Generate targeted recommendations for mock interview rounds."""
        focus = [
            f"Core {primary_domain} architectural problem-solving and trade-offs",
            f"STAR method deep-dive into {seniority} level past challenges",
            f"Hands-on technical questioning on {', '.join(top_skills[:3])}"
        ]
        if has_projects:
            focus.append("Deep dive into project architectural design choices and metrics")
        return focus
