FROM python:3.12-slim

# bospy
COPY bindings/python/bospy/ /opt/bospy/
WORKDIR /opt/bospy/
RUN pip install -e .

WORKDIR /opt/app

COPY apps/occupied-hours/requirements.txt /opt/app
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

ENV SYSMOD_ADDR=nuc.local:2821
ENV DEVCTRL_ADDR=nuc.local:2822 
ENV HISTORY_ADDR=nuc.local:2823
ENV FORECAST_ADDR=nuc.local:2825 
ENV SCHEDULER_ADDR=nuc.local:2824

COPY apps/occupied-hours/ /opt/app

EXPOSE 5000

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]