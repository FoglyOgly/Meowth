#!/bin/bash

# tested on Ubuntu Server 22.04

apt update
apt install -y build-essential libgflags-dev libgoogle-glog-dev libgtest-dev libssl-dev swig python3 python3-pip python3-dev python3-venv cmake openssl

cd /
mkdir src
cd src
git clone https://github.com/google/googletest
cmake -S /src/googletest -B /build/googletest -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/output -DBUILD_GMOCK=ON
cmake --build /build/googletest --install

cd /
mkdir src
cd src
git clone https://github.com/abseil/abseil-cpp
cd abseil-cpp
mkdir build
cd build
cmake -S /src/abseil-cpp -B /build/abseil-cpp -DCMAKE_PREFIX_PATH=/output -DCMAKE_INSTALL_PREFIX=/output -DABSL_ENABLE_INSTALL=ON -DABSL_USE_EXTERNAL_GOOGLETEST=ON -DABSL_FIND_GOOGLETEST=ON -DCMAKE_CXX_STANDARD=17 -DCMAKE_POSITION_INDEPENDENT_CODE=ON
cmake --build /build/abseil-cpp --target install

cd /src
git clone https://github.com/google/s2geometry.git
cd s2geometry/
cmake -DCMAKE_PREFIX_PATH=/output/lib/cmake/absl -DCMAKE_CXX_STANDARD=17 -DWITH_PYTHON=ON
make install -j $(nproc)

cd /src/s2geometry

sed -i "s/'-DWITH_PYTHON=ON'/'-DWITH_PYTHON=ON',/" /src/s2geometry/setup.py
sed -i "/'-DWITH_PYTHON=ON',/a \                                        '-DCMAKE_PREFIX_PATH=/output/lib/cmake'" /src/s2geometry/setup.py
sed -i "/'-DWITH_PYTHON=ON',/a \                                        '-DCMAKE_CXX_STANDARD=17'," /src/s2geometry/setup.py
sed -i 's/install_prefix="s2geometry"/install_prefix="pywraps2"/' /src/s2geometry/setup.py

#python3 -m venv venv
#source venv/bin/activate

pip install cmake_build_extension wheel
python3 setup.py bdist_wheel

pip install /src/s2geometry/dist/s2geometry-0.11.0.dev1-cp310-cp310-linux_x86_64.whl
