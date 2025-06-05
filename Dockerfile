FROM python:3.10.14-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ⚠️ Add system update step to patch vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get install -y gcc libpq-dev && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "credit_approval.wsgi:application", "--bind", "0.0.0.0:8000"]
