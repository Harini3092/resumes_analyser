from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def resume_similarity(resume, jd):

    cv = CountVectorizer()

    vectors = cv.fit_transform([resume, jd])

    similarity = cosine_similarity(vectors)

    return round(similarity[0][1] * 100, 2)


def final_prediction(similarity,
                     percentage,
                     qualification,
                     passedout,
                     matched_skills):

    score = 0

    # Resume Similarity (50 Marks)
    score += similarity * 0.5

    # Academic Score (20 Marks)
    if percentage >= 85:
        score += 20
    elif percentage >= 75:
        score += 15
    elif percentage >= 65:
        score += 10
    elif percentage >= 55:
        score += 5

    # Qualification (10 Marks)
    if qualification in [
        "B.E",
        "B.Tech",
        "M.E",
        "M.Tech",
        "MCA"
    ]:
        score += 10

    # Passed Out Year (10 Marks)
    if passedout >= 2025:
        score += 10
    elif passedout >= 2023:
        score += 7
    elif passedout >= 2021:
        score += 5

    # Skills (10 Marks)
    score += min(len(matched_skills) * 2, 10)

    if score >= 85:
        result = "Excellent Candidate"

    elif score >= 70:
        result = "Highly Recommended"

    elif score >= 55:
        result = "Recommended"

    elif score >= 40:
        result = "Needs Improvement"

    else:
        result = "Not Suitable"

    return round(score, 2), result