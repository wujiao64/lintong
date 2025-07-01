yes | sudo pip install --upgrade pip
#sudo python -m pip install --upgrade pip
yes | sudo apt install python3-pip python3-numpy
yes | sudo apt-get install libatlas-base-dev
yes | pip3 install numpy transforms3d pigpio pyserial
yes | pip install numpy transforms3d pigpio pyserial
yes | sudo pip install numpy transforms3d pigpio pyserial

yes | sudo pip3 install rpi_ws281x Adafruit_Blinka Adafruit_GPIO Adafruit_BBIO Adafruit-SSD1306 
yes | sudo apt-get install -y libsdl-ttf2.0-0
yes | sudo pip3 install ds4drv
yes | sudo pip3 install pygame

cd ../UDPComms
sudo bash install.sh
cd ..


#cd ..
#git clone https://github.com/stanfordroboticsclub/PupperCommand.git
cd PupperCommand
#sudo bash install.sh
sudo ln -s $(realpath .)/joystick.service /etc/systemd/system/
cd ..

#git clone https://github.com/stanfordroboticsclub/PS4Joystick.git
cd PS4Joystick
#sudo bash install.sh
sudo python3 setup.py clean --all install
cd ..
#sudo systemctl enable joystick

#wget https://github.com/joan2937/pigpio/archive/v74.zip
#unzip v74.zip
cd pigpio-74
make
sudo make install
cd ..

cd piQuadruped
sudo ln -s $(realpath .)/robot.service /etc/systemd/system/
sudo ln -s $(realpath .)/robotvideo.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable joystick
sudo systemctl start joystick

sudo systemctl enable robot
sudo systemctl start robot

sudo systemctl enable robotvideo
sudo systemctl start robotvideo


sudo apt-get install -y libjpeg-dev libatlas-base-dev libjpeg-dev libtiff5-dev li.jpg12-dev libqtgui4 libqt4-test libjasper-dev
sudo pip3 install opencv-python
sudo pip3 install imutils