FROM ubuntu:latest

ENV TZ=Europe/Rome

RUN apt-get update && \ 
    # Installing latex and fonts
    DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata && \
    apt-get install texlive-full -y && \
    apt-get install poppler-utils -y && \
    apt-get install fonts-roboto -y && \
    apt-get install fonts-indic -y && \
    fc-cache -f

    # Installing pip and python dependencies
RUN apt install python3-pip -y
RUN pip3 install instabot bs4 wget pdf2image poppler-utils Babel

RUN apt-get install git -y

# TODO verificare con la documentazione di github actions
WORKDIR /app

CMD ["/bin/bash"]