sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
chmod +x Anaconda3-2021.11-Linux-x86_64.sh
sh Anaconda3-2021.11-Linux-x86_64.sh
rm Anaconda3-2021.11-Linux-x86_64.sh
source ~/.bashrc
conda config --set auto_activate_base false
source ~/.bashrc