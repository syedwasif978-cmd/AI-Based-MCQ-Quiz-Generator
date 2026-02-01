# AI-Based MCQ Quiz Generator (Professor-only)

Short: Flask app that generates unique MCQ quizzes using an LLM, stores encrypted answer keys, and exports two PDFs (question paper and separate answer key).

## Quick start

1. Copy `.env.example` to `.env` and fill in values (OPENAI_API_KEY, DATABASE_URL, FERNET_KEY, SECRET_KEY).
   - Optional: set `OPENAI_MODEL` to control which OpenAI model to use (defaults to `gpt-3.5-turbo` to reduce cost). Example: `OPENAI_MODEL=gpt-3.5-turbo`
   - Optional: you can use **Hugging Face Inference API** instead of OpenAI by setting `HUGGINGFACE_API_KEY` and `HUGGINGFACE_MODEL` in `.env`. If `HUGGINGFACE_API_KEY` is set, the app will prefer Hugging Face for generation. Example: `HUGGINGFACE_API_KEY=hf_...` and `HUGGINGFACE_MODEL=google/flan-t5-large`
2. Install dependencies: `pip install -r requirements.txt`
3. Create DB schema in Oracle SQL Developer using `migrations/initial_migration.sql` (see notes below).
4. Run app: `python run.py` (development).

## Notes
- Database: Oracle XE (use SQL Developer). Example DDL provided in `migrations/initial_migration.sql` and `app/database/schema.sql`.
- This scaffold includes AI client stubs; replace with valid provider credentials.

## Files generated
See project structure in task description. Tests are under `tests/`.
