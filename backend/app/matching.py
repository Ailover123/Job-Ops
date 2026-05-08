from app.models import CandidateProfile, Recommendation, SeedJob


FRESHER_POSITIVE_TERMS = {
    "fresher",
    "graduate",
    "new grad",
    "entry level",
    "junior",
    "trainee",
    "intern",
    "internship",
    "associate",
    "0-1",
    "0-2",
}

SENIOR_NEGATIVE_TERMS = {
    "senior",
    "staff",
    "principal",
    "lead",
    "manager",
    "architect",
    "5+",
    "7+",
    "8+",
}


def rank_jobs(profile: CandidateProfile, jobs: list[SeedJob]) -> list[Recommendation]:
    recommendations = [
        score_job(profile, job)
        for job in jobs
        if job.is_active and passes_hard_filters(profile, job)
    ]
    return sorted(recommendations, key=lambda item: item.final_score, reverse=True)


def passes_hard_filters(profile: CandidateProfile, job: SeedJob) -> bool:
    if profile.job_types and job.job_type not in profile.job_types:
        return False

    if _is_senior_only(job) and profile.experience_level == "fresher":
        return False

    if profile.remote_preference == "remote_only" and not job.is_remote:
        return False

    if profile.preferred_locations and not _location_matches(profile, job):
        return False

    return True


def score_job(profile: CandidateProfile, job: SeedJob) -> Recommendation:
    skill_score = _skill_score(profile, job)
    fresher_score = _fresher_score(job)
    location_score = _location_score(profile, job)
    experience_score = _experience_score(job)

    final = round(
        skill_score * 30
        + fresher_score * 25
        + location_score * 20
        + experience_score * 25
    )

    return Recommendation(
        job=job,
        skill_score=round(skill_score, 2),
        fresher_score=round(fresher_score, 2),
        location_score=round(location_score, 2),
        experience_score=round(experience_score, 2),
        final_score=final,
        score_label=_score_label(final),
        explanation=_explain(profile, job, final),
    )


def _skill_score(profile: CandidateProfile, job: SeedJob) -> float:
    if not profile.skills or not job.skills:
        return 0.4

    user_skills = {_normalize(skill) for skill in profile.skills}
    job_skills = {_normalize(skill) for skill in job.skills}
    matches = user_skills.intersection(job_skills)
    return len(matches) / max(len(job_skills), 1)


def _fresher_score(job: SeedJob) -> float:
    text = _job_text(job)

    if any(term in text for term in FRESHER_POSITIVE_TERMS):
        return 1.0

    if job.experience_min is not None and job.experience_min <= 1:
        return 0.9

    if job.experience_min is None:
        return 0.5

    if job.experience_min <= 2:
        return 0.7

    return 0.2


def _location_score(profile: CandidateProfile, job: SeedJob) -> float:
    if job.is_remote and profile.remote_preference in {"remote_only", "remote_or_hybrid"}:
        return 1.0

    if not profile.preferred_locations:
        return 0.7

    return 1.0 if _location_matches(profile, job) else 0.0


def _experience_score(job: SeedJob) -> float:
    if job.experience_min is None:
        return 0.6
    if job.experience_min <= 1:
        return 1.0
    if job.experience_min <= 2:
        return 0.8
    if job.experience_min <= 3:
        return 0.5
    return 0.2


def _location_matches(profile: CandidateProfile, job: SeedJob) -> bool:
    job_location = _normalize(" ".join(filter(None, [job.location, job.city, job.state, job.country])))
    preferred = {_normalize(location) for location in profile.preferred_locations}

    if job.is_remote and "remote" in preferred:
        return True

    return any(location in job_location for location in preferred)


def _is_senior_only(job: SeedJob) -> bool:
    text = _job_text(job)
    return any(term in text for term in SENIOR_NEGATIVE_TERMS)


def _job_text(job: SeedJob) -> str:
    return _normalize(f"{job.title} {job.description} {job.experience_min or ''}+")


def _normalize(value: str) -> str:
    return value.casefold().strip()


def _score_label(score: int) -> str:
    if score >= 85:
        return "Excellent match"
    if score >= 70:
        return "Good match"
    if score >= 55:
        return "Possible match"
    return "Low match"


def _explain(profile: CandidateProfile, job: SeedJob, score: int) -> str:
    matched_skills = sorted(
        {_normalize(skill) for skill in profile.skills}.intersection({_normalize(skill) for skill in job.skills})
    )

    reasons = []
    if matched_skills:
        reasons.append(f"matches your {', '.join(matched_skills[:3])} skills")
    if job.is_remote:
        reasons.append("supports remote work")
    if _fresher_score(job) >= 0.8:
        reasons.append("looks fresher-friendly")

    if not reasons:
        return f"{_score_label(score)} based on the available job details."

    return f"{_score_label(score)} because it " + ", ".join(reasons) + "."

