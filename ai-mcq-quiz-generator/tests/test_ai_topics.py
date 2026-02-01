from app.ai_engine.ai_client import generate_mcqs


def test_topics_are_reflected_in_questions():
    subject = 'Calculus'
    topics = 'derivatives, integration'
    num = 6
    res = generate_mcqs(subject, num, 'Medium', topics=topics)

    assert 'questions' in res and len(res['questions']) == num
    qs = res['questions']
    topic_list = [t.strip().lower() for t in topics.split(',') if t.strip()]

    # Ensure each provided topic appears at least once among generated questions
    for t in topic_list:
        assert any(q.get('topic','').strip().lower() == t for q in qs), f"Topic '{t}' not present in generated questions"
