FROM python:3.9-slim

# app is our wd
WORKDIR /app

#copy pip text
COPY requirements.txt /app/requirements.txt

#get all the stuff we need for our dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libpoppler-cpp-dev \
    pngquant \
    tesseract-ocr \
    gcc g++ \
    wget \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
    
# RUN apt-get update && apt-get install -y \
#     poppler-utils \
#     libpoppler-cpp-dev \
#     pngquant \
#     tesseract-ocr \
#     gcc g++ \
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get clean

# RUN apt-get update && apt-get install -y wget \
#     build-essential \
#     sudo

#get the ghostscript thingy, latest version
RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10050/ghostscript-10.05.0.tar.gz \
    && tar xzf ghostscript-10.05.0.tar.gz \
    && cd ghostscript-10.05.0 \
    && ./configure  && make && sudo make install

# # Configure, compile, and install Ghostscript
# WORKDIR ghostscript-10.05.0
# RUN ./configure \
#     && make \
#     && sudo make install

# # Verify installation is 10.05.0
RUN gs --version

#dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


RUN pip install ocrmypdf

#checks the version
RUN tesseract --version 

# Step 5: Expose the port your application will run on
EXPOSE 8000