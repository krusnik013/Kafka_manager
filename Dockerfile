# change the image depending on your OS/ARCH

FROM python:3.11 

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV ZMQ_SERVER_HOST=0.0.0.0
ENV ZMQ_SERVER_PORT=5555

# Expose ZMQ port (if you want to connect from host)
EXPOSE 5555

# Run your Python app
CMD ["python", "src/main.py"]