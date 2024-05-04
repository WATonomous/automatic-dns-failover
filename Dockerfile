FROM python:3.10-alpine

WORKDIR /automatic-dns-failover

COPY main.py /automatic-dns-failover
COPY cloudflare_dns.py /automatic-dns-failover
COPY helper.py /automatic-dns-failover

RUN pip install requests

CMD ["python3", "-u", "main.py"]