from app.ai_engine.ai_client import generate_mcqs


def test_contentful_questions_in_fallback():
    subject = 'Maths'
    topics = 'derivatives, integration'
    num = 6
    res = generate_mcqs(subject, num, 'Medium', topics=topics)

    assert 'questions' in res and len(res['questions']) == num
    qs = res['questions']

    # Ensure that questions are substantive (not just 'Sample' placeholders)
    for q in qs:
        assert len(q.get('q','')) > 30, f"Question too short: {q.get('q')!r}"
        assert not q.get('q','').lower().startswith('sample'), "Found placeholder-style question"

    # Ensure topics are present
    topic_list = [t.strip().lower() for t in topics.split(',') if t.strip()]
    for t in topic_list:
        assert any(q.get('topic','').strip().lower() == t for q in qs), f"Topic '{t}' not present"