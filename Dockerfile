FROM python:3.11-bullseye

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y \
        pkg-config libcairo2-dev gcc python3-dev libgirepository1.0-dev gobject-introspection gir1.2-gtk-3.0 gir1.2-webkit2-4.0
RUN pip install PyGObject

RUN apt-get install -y \
    xvfb xauth

COPY ApiServer.py GTKWebView.py GtkHtml2Pdf.py ./

ENTRYPOINT ["/bin/sh", "-c", "/usr/bin/xvfb-run -a $@", ""]
CMD ["python3", "GtkHtml2Pdf.py"]
EXPOSE 8000
