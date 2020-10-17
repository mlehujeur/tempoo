# Timetools

Install 
```bash 
# cd <to/installation/path>
git clone https://gitlab.com/obsmax/timetools.git

conda remove --name py37-tt --all --yes
conda create --name py37-tt python=3.7 --yes
conda activate py37-tt

cd timetools 
pip install -e .
```