Installing Pylucene
===================
I found installing pylucene to be a little... challenging. So, this is what it
took to get it installed. First, you should have elasticsearch in the vein of
[this gist](https://gist.github.com/3783941), though that's mostly for the yum
dependencies and for the directory setup, RAID array, etc.

__This assumes you have this repo checked out in `~/git/elasticsearch-utils`__

```bash
# Let's use Java 1.7!
sudo yum install -y java-1.7.0-openjdk{,-devel}.x86_64
# And some other dependencies
sudo yum install -y ant icu apachy-ivy{,-javadoc} python-pivy ivykis{,-devel}
# And make sure we don't do anything with Java 1.6
sudo yum remove -y java-1.6.0-openjdk{,-demo,-devel,-javadoc,-src}

# Apachy Ivy is a dependency
cd && curl -OL http://archive.apache.org/dist/ant/ivy/2.2.0/apache-ivy-2.2.0-bin-with-deps.tar.gz
tar xf apache-ivy-2.2.0-bin-with-deps.tar.gz 
cd apache-ivy-2.2.0
sudo cp ivy-2.2.0.jar /usr/share/ant/lib/

# Set up ldconfig for libjava and libjvm
sudo find / -name 'libjava.so' | sed -E 's#/[^/]+$##' | sudo tee -a /etc/ld.so.conf
sudo find / -name 'libjvm.so' | sed -E 's#/[^/]+$##' | sudo tee -a /etc/ld.so.conf
sudo ldconfig

# Download pylucene
export PYLUCENE_VERSION=3.6.1-2
cd && curl -OL http://apache.cs.utah.edu/lucene/pylucene/pylucene-$PYLUCENE_VERSION-src.tar.gz
tar xf pylucene-$PYLUCENE_VERSION-src.tar.gz

# It took a while to get these set up, so they should just be copied from here
cp ~/git/elasticsearch-utils/pylucene/jcc/setup.py \
    ~/pylucene-$PYLUCENE_VERSION/jcc/
cp ~/git/elsaticsearch-utils/pylucene/Makefile \
    ~/pylucene-$PYLUCENE_VERSION/

# Now, build JCC
export NO_SHARED=1
cd ~/pylucene-$PYLUCENE_VERSION/jcc
python2.7 setup.py build
sudo NO_SHARED=1 python2.7 setup.py install

# Set up of some environment variables 
cd ~/pylucene-$PYLUCENE_VERSION/
export ANT=ant
export PREFIX_PYTHON=/usr
export PYTHON=$PREFIX_PYTHON/bin/python27
export JCC="$PYTHON $PREFIX_PYTHON/lib64/python2.7/site-packages/JCC-2.14-py2.7-linux-x86_64.egg/jcc/__init__.py"
export NUM_FILES=4
export CLASSPATH=/home/ec2-user/apache-ivy-2.2.0/ivy-2.2.0.jar 

# Now time to build some stuff
make
sudo PREFIX_PYTHON=/usr \
    ANT=ant \
    PYTHON=$PREFIX_PYTHON/bin/python27 \
    JCC="$PYTHON $PREFIX_PYTHON/lib64/python2.7/site-packages/JCC-2.14-py2.7-linux-x86_64.egg/jcc/__init__.py" \
    NUM_FILES=4 \
    make install
```
