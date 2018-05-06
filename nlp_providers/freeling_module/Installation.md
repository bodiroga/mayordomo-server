# Freeling installation steps #

## Ubuntu/Debian from source and python API ##

### C++ compiler ###
- sudo apt install -y build-essential automake autoconf
- sudo apt install -y cmake
- cmake --version
  - sudo apt remove cmake
  - sudo apt purge --auto-remove cmake
  - mkdir ~/tmp && sudo mkdir /opt/cmake && cd ~/tmp
  - wget ... (https://cmake.org/files/LatestRelease/)
  - chmod +x cmake*.sh
  - sudo ./cmake*.sh --skip-license --prefix=/opt/cmake
  - sudo ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
  - cd
  - rm -rf ~/tmp

### Dependecies ###
- sudo apt install -y libboost-all-dev
- sudo apt install -y libboost-regex-dev libicu-dev
- sudo apt install -y libboost-system-dev libboost-program-options-dev
- sudo apt install -y libboost-thread-dev
- sudo apt install -y git

### Get source code ###
- git clone https://github.com/TALP-UPC/FreeLing.git
- cd FreeLing

### Installation ###
- mkdir build
- cd build
- cmake -DPYTHON2_API=ON ..
- sudo make -j 4 install

### Move python library ###
- sudo cp /usr/local/share/freeling/APIs/python2/_pyfreeling.so /usr/lib/python2.7/
- sudo cp /usr/local/share/freeling/APIs/python2/pyfreeling.py /usr/lib/python2.7/