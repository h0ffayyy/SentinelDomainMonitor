FROM alpine:3.18.2
LABEL website="https://github.com/h0ffayyy/SentinelDomainMonitor"
LABEL desc="builds a docker image for SentinelDomainMonitor"
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache whois python3 py3-requests && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN mkdir -p /usr/DomainMonitor/
WORKDIR /usr/DomainMonitor/
COPY DomainMonitor DomainMonitor/
COPY requirements.txt .
#COPY domains.txt .
RUN mkdir -p logs
RUN pip3 install -r requirements.txt
CMD ["python3", "./DomainMonitor/domainmonitor.py"]