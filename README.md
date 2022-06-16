# Data-Monger
 
## Usage
Data Monger is used to practice or test the use of joins and unions on your data without effecting your data. This is great to test the feasibility of the join, tweaking join logic and QA'ing the output.

To run
```
pip install -r requirements.txt

python main.py
```

## Create exe
A .exe is great to package and move your program around. 

```
pyinstaller (--onefile or onedir) -y --clean --debug=all --add-data="assets;assets" --hidden-import=dash --hidden-import=pandas main.py
```