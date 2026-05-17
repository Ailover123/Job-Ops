import re
import html
from typing import List, Tuple, Optional

# Comprehensive registry of common fresher-related tech skills
COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Vue", "Angular", "Node.js", "Express",
    "FastAPI", "Flask", "Django", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Docker", "AWS", "Google Cloud", "Azure", "HTML", "CSS", "Sass", "Tailwind",
    "Bootstrap", "Git", "GitHub", "Java", "Spring", "Kotlin", "C++", "C#", "Go",
    "Rust", "PHP", "Laravel", "Ruby", "Rails", "Kubernetes", "PyTorch", "TensorFlow",
    "Machine Learning", "Data Analysis", "Figma", "Redux", "GraphQL", "Next.js",
    "Linux", "Unit Testing", "Jest", "Pytest", "CI/CD", "Scikit-Learn", "Pandas", "NumPy"
]

def clean_html(raw_html: str) -> str:
    """Strip HTML tags and unescape HTML entities to produce clean plain text."""
    if not raw_html:
        return ""
    # Decode HTML entities first
    decoded = html.unescape(raw_html)
    # Remove script and style elements entirely
    decoded = re.sub(r'<(script|style)\b[^>]*>([\s\S]*?)<\/\1>', ' ', decoded, flags=re.IGNORECASE)
    # Replace HTML tags with space
    cleaned = re.sub(r'<[^>]+>', ' ', decoded)
    # Normalize whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_skills(text: str) -> List[str]:
    """
    Search case-insensitively for common skills in the given text.
    Uses word boundaries or specific matching rules to avoid false positives (e.g. 'Go' matching 'good').
    """
    if not text:
        return []
    
    text_lower = text.lower()
    matched_skills = []
    
    for skill in COMMON_SKILLS:
        skill_lower = skill.lower()
        
        # Define matching patterns for specific tricky skills
        if skill_lower == "go":
            # Match 'go' as a separate word, case-sensitive/case-insensitive with care
            # Usually written as 'Go' or 'Golang'. Let's search 'golang' or word boundary 'go'
            pattern = r'\b(go|golang)\b'
            if re.search(pattern, text_lower):
                matched_skills.append(skill)
        elif skill_lower == "c++":
            if "c++" in text_lower:
                matched_skills.append(skill)
        elif skill_lower == "c#":
            if "c#" in text_lower:
                matched_skills.append(skill)
        elif skill_lower == "next.js":
            if "next.js" in text_lower or "nextjs" in text_lower:
                matched_skills.append(skill)
        elif skill_lower == "node.js":
            if "node.js" in text_lower or "nodejs" in text_lower or "node js" in text_lower:
                matched_skills.append(skill)
        elif skill_lower == "unit testing":
            if "unit testing" in text_lower or "unit-testing" in text_lower or "testing" in text_lower:
                matched_skills.append(skill)
        elif skill_lower == "ci/cd":
            if "ci/cd" in text_lower or "ci-cd" in text_lower:
                matched_skills.append(skill)
        else:
            # General word-boundary case-insensitive search
            pattern = rf'\b{re.escape(skill_lower)}\b'
            if re.search(pattern, text_lower):
                matched_skills.append(skill)
                
    return sorted(list(set(matched_skills)))

def parse_experience(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Attempt to extract minimum and maximum years of experience mentioned in text.
    Examples: '1-3 years', '2+ years', 'minimum 2 years'.
    """
    if not text:
        return None, None
        
    text_lower = text.lower()
    
    # Check for '1-3 years', '0-2 years' etc.
    range_match = re.search(r'\b(\d+)\s*to\s*(\d+)\s*(?:years|yr|years?)\b', text_lower)
    if not range_match:
        range_match = re.search(r'\b(\d+)\s*-\s*(\d+)\s*(?:years|yr|years?)\b', text_lower)
        
    if range_match:
        try:
            exp_min = int(range_match.group(1))
            exp_max = int(range_match.group(2))
            return exp_min, exp_max
        except ValueError:
            pass
            
    # Check for '2+ years', '3+ yr' etc.
    plus_match = re.search(r'\b(\d+)\s*\+\s*(?:years|yr|years?)\b', text_lower)
    if plus_match:
        try:
            exp_min = int(plus_match.group(1))
            return exp_min, None
        except ValueError:
            pass
            
    # Check for 'minimum of 2 years', 'at least 1 year'
    min_match = re.search(r'(?:minimum|min|at least|required)\s*(?:of)?\s*(\d+)\s*(?:years|yr|years?)', text_lower)
    if min_match:
        try:
            exp_min = int(min_match.group(1))
            return exp_min, None
        except ValueError:
            pass
            
    return None, None
