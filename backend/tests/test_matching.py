from app.matching import rank_jobs
from app.models import CandidateProfile, SeedJob


def test_senior_jobs_are_filtered_for_freshers():
    profile = CandidateProfile(skills=["Python"], preferred_locations=["Remote"])
    jobs = [
        SeedJob(
            external_id="senior",
            title="Senior Python Architect",
            company_name="Example",
            description="Requires 8+ years of Python architecture experience.",
            location="Remote",
            is_remote=True,
            job_type="full_time",
            experience_min=8,
            experience_max=12,
            skills=["Python"],
            apply_url="https://example.com",
            source_name="Seed",
        )
    ]

    assert rank_jobs(profile, jobs) == []


def test_fresher_python_remote_job_scores_well():
    profile = CandidateProfile(
        skills=["Python", "MySQL"],
        preferred_locations=["Remote"],
        remote_preference="remote_only",
    )
    jobs = [
        SeedJob(
            external_id="intern",
            title="Python Developer Intern",
            company_name="Example",
            description="Internship for freshers using Python and MySQL.",
            location="Remote",
            is_remote=True,
            job_type="internship",
            experience_min=0,
            experience_max=1,
            skills=["Python", "MySQL"],
            apply_url="https://example.com",
            source_name="Seed",
        )
    ]

    recommendations = rank_jobs(profile, jobs)

    assert recommendations[0].final_score >= 85

