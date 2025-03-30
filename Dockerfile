FROM python:3.9-slim

# app is our wd
WORKDIR /app

#copy pip text
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y \
    gcc g++ \
    pkg-config \
    poppler-utils \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*
    
#dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


RUN pip install ocrmypdf

# Step 5: Expose the port your application will run on
EXPOSE 8000