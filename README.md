## Application setup

**Setup environment**
```bash
python -m pip install pyside6
```

**Run application**
```bash
python main.py
```

## PX4 SITL setup
**Setup environment:**
Execute command in windows terminal or PowerShell
```powershell
wsl --install Ubuntu-26.04
```

**Enter ubuntu environment**
```powershell
wsl
```

**Setup ubuntu environment**
```bash
sudo apt update
sudo apt install python3-dev python3-pip python3-venv make cmake build-essential
mkdir ~/dev
cd ~/dev
git clone 
python3 -m venv venv
source venv/bin/activate
python -m pip install kconfiglib pyros-genmsg numpy empy==3.3.4 jinja2 pyyaml jsonschema mavproxy future
```

**Start PX4 SITL**
```bash
make px4_sitl_sih sihsim_quadx
mavproxy.py --master udp:127.0.0.1:14550 --out tcpin:127.0.0.1:5760
```

## MavLink source code generation
```bash
git clone https://github.com/mavlink/mavlink.git --recursive
cd mavlinink
python3 -m venv venv
source venv/bin/activate
python -m pip install -r pymavlink/requirements.txt
python -m pymavlink.tools.mavgen --lang=Python3 --wire-protocol=2.0 --output=mavlink message_definitions/v1.0/all.xml
```
Then copy output file (mavlink.py) to project directory