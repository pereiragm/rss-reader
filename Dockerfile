FROM python:3.11.2

# Create a new virtual env and activate it
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -U pip && \
    pip install poetry==1.4.2

WORKDIR /code
COPY . .

# Project initialization:
RUN poetry config virtualenvs.create false && \
#     poetry install --no-interaction --no-ansi
    poetry install

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
