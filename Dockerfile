FROM python:3.10-alpine

WORKDIR /automatic-dns-failover

COPY main.py /automatic-dns-failover
COPY cloudflare_dns.py /automatic-dns-failover
COPY helper.py /automatic-dns-failover

RUN pip install requests

ENV DELAY=2
ENV CLOUDFLARE_WATCHER_NUM=3
#ENV EMAIL=<email>
#ENV API_KEY=<api-key>
#ENV API_TOKEN=<api-token>
ENV GET_TIMEOUT=2
ENV UP_NUM=3
ENV DOWN_NUM=2
ENV DOMAINS="watonomous.com:alvin-test,10.0.50.114,10.0.50.116:alvin-test2,10.0.50.113,10.0.50.115"

CMD ["python3", "main.py"]
