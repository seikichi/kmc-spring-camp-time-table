FROM debian:wheezy
MAINTAINER seikichi <seikichi@kmc.gr.jp>

RUN apt-get update && apt-get install --no-install-recommends -y python3 unzip wget
WORKDIR /spring-camp-time-table
RUN wget http://scip.zib.de/download/release/scip-3.1.0.linux.x86_64.gnu.opt.spx.zip
RUN unzip scip-3.1.0.linux.x86_64.gnu.opt.spx.zip
ADD milp.py time_table.py /spring-camp-time-table/
CMD cat > config.json && python3 time_table.py --scip=./scip-3.1.0.linux.x86_64.gnu.opt.spx config.json
