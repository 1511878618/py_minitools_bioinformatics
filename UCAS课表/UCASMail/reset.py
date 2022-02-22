import os 
import shutil

def reset():
    try:
        shutil.rmtree("table/")
    except:
        pass
    try:
        shutil.rmtree("tomorrow/")
    except:
        pass    
    try:
        os.remove("semester.info")
    except:
        pass
    try:
        os.remove("user.csv")
    except:
        pass
reset()