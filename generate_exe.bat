@echo off
pyinstaller --onefile --noconsole --icon=pictures\car.ico ^
--add-binary="%LocalAppData%\Programs\Python\Python36\Lib\site-packages\pymunk\chipmunk.dll;." ^
--add-data="pictures\icon.png;pictures" ^
--add-data="pictures\grass.jpg;pictures" ^
--add-data="pictures\track_default.png;pictures" ^
--add-data="pictures\car_white.png;pictures" ^
--add-data="pictures\car_yellow.png;pictures" ^
--add-data="pictures\car_red.png;pictures" ^
--add-data="pictures\car_green.png;pictures" ^
--add-data="pictures\car_blue.png;pictures" ^
Main.py
move dist\Main.exe AutonomousDriving.exe
rmdir __pycache__ /S /Q
rmdir build /S /Q
rmdir dist /S /Q
del *.spec /F /Q
