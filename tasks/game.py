import os

from invoke import task

from tasks.config import SOURCE_PATH

STREAMLIT_APP = os.path.join(SOURCE_PATH, 'ui/app.py')


@task
def play(ctx):
    """Starts a game of scoundrel using the recommended streamlit UI."""
    ctx.run(f"uv run streamlit run {STREAMLIT_APP}")
