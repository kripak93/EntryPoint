@echo off
echo Testing Python...
C:\Users\kripa\Desktop\python.exe --version
echo.
echo Testing imports...
C:\Users\kripa\Desktop\python.exe -c "import streamlit; print('Streamlit OK')"
echo.
echo Testing CSV read...
C:\Users\kripa\Desktop\python.exe -c "import pandas as pd; df = pd.read_csv('ipl_data.csv'); print(f'CSV loaded: {len(df)} rows')"
echo.
echo Done!
pause
