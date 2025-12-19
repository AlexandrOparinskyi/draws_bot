FROM python:3.12-slim

WORKDIR app/

COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/
COPY reg_bot/ ./reg_bot/
COPY database/ ./database/
COPY I18N/ ./I18N/
COPY config.py .
COPY app.py .

CMD python app.py