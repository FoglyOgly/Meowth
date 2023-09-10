FROM ubuntu:22.04
LABEL maintainer="Jack Yaz <jackyaz@outlook.com>"

VOLUME /app/config

RUN apt-get update && apt-get install -y build-essential git libgflags-dev libgoogle-glog-dev libgtest-dev libssl-dev swig python3 python3-pip python3-dev python3-venv cmake openssl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

WORKDIR /src
RUN git clone https://github.com/google/googletest
RUN cmake -S /src/googletest -B /build/googletest -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/output -DBUILD_GMOCK=ON
RUN cmake --build /build/googletest --target install

WORKDIR /src
RUN git clone https://github.com/abseil/abseil-cpp
WORKDIR abseil-cpp/build
RUN cmake -S /src/abseil-cpp -B /build/abseil-cpp -DCMAKE_PREFIX_PATH=/output -DCMAKE_INSTALL_PREFIX=/output -DABSL_ENABLE_INSTALL=ON -DABSL_USE_EXTERNAL_GOOGLETEST=ON -DABSL_FIND_GOOGLETEST=ON -DCMAKE_CXX_STANDARD=17 -DCMAKE_POSITION_INDEPENDENT_CODE=ON
RUN cmake --build /build/abseil-cpp --target install

WORKDIR /src
RUN git clone https://github.com/google/s2geometry.git
WORKDIR /src/s2geometry/
RUN cmake -DCMAKE_PREFIX_PATH=/output/lib/cmake/absl -DCMAKE_CXX_STANDARD=17 -DWITH_PYTHON=ON
RUN make install -j $(nproc)

WORKDIR /src/s2geometry/

RUN sed -i "s/'-DWITH_PYTHON=ON'/'-DWITH_PYTHON=ON',/" /src/s2geometry/setup.py
RUN sed -i "/'-DWITH_PYTHON=ON',/a \                                        '-DCMAKE_PREFIX_PATH=/output/lib/cmake'" /src/s2geometry/setup.py
RUN sed -i "/'-DWITH_PYTHON=ON',/a \                                        '-DCMAKE_CXX_STANDARD=17'," /src/s2geometry/setup.py
RUN sed -i 's/install_prefix="s2geometry"/install_prefix="pywraps2"/' /src/s2geometry/setup.py

RUN pip install cmake_build_extension wheel
RUN python3 setup.py bdist_wheel

RUN pip install /src/s2geometry/dist/s2geometry-0.11.0.dev1-cp310-cp310-linux_x86_64.whl

RUN rm -rf /src
RUN rm -rf /build

COPY config /app/config
COPY database /app/database
COPY meowth /app/meowth
COPY requirements.txt /app/
COPY setup.py /app/
COPY README.md /app/
COPY LICENSE /app/
WORKDIR /app

RUN python3 -m pip install -r requirements.txt
RUN python3 setup.py install

ENV PYTHONPATH="${PYTHONPATH}:."

RUN ln -s /app/config/config.py /app/meowth/config.py

COPY entry.sh /
RUN chmod 0755 /entry.sh

ENTRYPOINT ["/entry.sh"]
