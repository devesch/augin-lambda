FROM amazonlinux:2

RUN yum update -y
RUN yum install -y wget tar gcc gcc-c++ epel-release freetype-devel yum-utils findutils openssl-devel groupinstall development bzip2-devel libffi-devel gzip make
WORKDIR /opt
RUN wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
RUN tar xvf Python-3.9.16.tgz
WORKDIR /opt/Python-3.9.16
RUN ./configure --enable-optimizations
RUN make altinstall
RUN rm -f /opt/Python-3.9.16.tgz

RUN yum install -y python3-pip zip
RUN yum -y clean all
RUN python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip install pandas openpyxl xlsxwriter -t /python
RUN find /python -name "*-info" -type d -exec rm -rdf {} +
RUN find /python -name "tests" -type d -exec rm -rdf {} +
RUN rm -rdf /python/boto3/
RUN rm -rdf /python/botocore/
RUN rm -rdf /python/docutils/
RUN rm -rdf /python/dateutil/
RUN rm -rdf /python/jmespath/
RUN rm -rdf /python/s3transfer/
RUN rm -rdf /python/__pycache__/
RUN find /python -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-39//'); cp $f $n; done;
RUN find /python -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find /python -type f -a -name '*.py' -print0 | xargs -0 rm -f
RUN zip -r /docker_layer.zip /python