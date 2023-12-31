FROM amazonlinux:2

RUN yum update -y
RUN yum install -y perl libssl-dev pyopenssl wget tar libxslt-devel libxml2-devel python3-11 gcc gcc-c++ epel-release freetype-devel yum-utils findutils openssl-devel groupinstall development bzip2-devel libffi-devel gzip make
WORKDIR /opt
RUN wget https://ftp.openssl.org/source/openssl-1.1.1q.tar.gz --no-check-certificate
RUN tar -xzvf openssl-1.1.1q.tar.gz
WORKDIR /opt/openssl-1.1.1q
RUN ./config --prefix=/usr --openssldir=/etc/ssl --libdir=lib no-shared zlib-dynamic
RUN make
RUN make install

WORKDIR /opt/
RUN wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz
RUN tar xvf Python-3.11.5.tgz
WORKDIR /opt/Python-3.11.5
RUN ./configure --enable-optimizations --with-openssl=/usr
RUN make install
RUN rm -f /opt/Python-3.11.5.tgz

RUN yum install -y python3-pip zip
RUN yum -y clean all
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install certifi

WORKDIR /opt
COPY ../requirements.txt /opt/requirements.txt
RUN sed -i 's/^bpy/#bpy/' requirements.txt
RUN sed -i 's/^pywin32/#pywin32/' requirements.txt

RUN python3.11 -m pip install -r requirements.txt -t /python
RUN python3.11 -m pip install signxml -t /python
# RUN python3.11 -m pip install sl-zerobounce --no-deps -t /python
#RUN cp /usr/lib64/libxml2.so.2.9.1 /python/libxml2.so.2
#RUN cp /usr/lib64/libgcrypt.so.11.8.2 /python/libgcrypt.so.11
#RUN cp /usr/lib64/libexslt.so.0.8.17 /python/libexslt.so.0
#RUN cp /usr/lib64/libxslt.so.1.1.28 /python/libxslt.so.1
#RUN cp /usr/lib64/libgpg-error.so.0.10.0 /python/libgpg-error.so.0

RUN find /python -name "*-info" -type d -exec rm -rdf {} +
RUN find /python -name "tests" -type d -exec rm -rdf {} +
RUN rm -rdf /python/boto3/
RUN rm -rdf /python/botocore/
RUN rm -rdf /python/docutils/
RUN rm -rdf /python/dateutil/
RUN rm -rdf /python/jmespath/
RUN rm -rdf /python/s3transfer/
RUN rm -rdf /python/__pycache__/
RUN find /python -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-311//'); cp $f $n; done;
RUN find /python -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find /python -type f -a -name '*.py' -print0 | xargs -0 rm -f
RUN python3.11 -m pip install typing-extensions -t /python
RUN python3.11 -m pip install pypng -t /python
RUN zip -r /docker_layer.zip /python