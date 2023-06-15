FROM python:3.10.9
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set the working directory to /app
WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt
