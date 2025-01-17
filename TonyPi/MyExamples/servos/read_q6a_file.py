# read_q-a_file.py
# V1.0
# 
# # open .d6a file dans display content
#
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

path = "TonyPi/ActionGroups/stand.d6a"
#path = "TonyPi/ActionGroups/16.d6a"
col_count = 22
row_count = 0

print(f'ouverture de la base {path}')
rbt = QSqlDatabase.addDatabase("QSQLITE")
rbt.setDatabaseName(path)

if rbt.open():
    actgrp = QSqlQuery()
    if (actgrp.exec("select * from ActionGroup ")):
        totalTime = 0
        print('Step t  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20')
        while (actgrp.next()):
            row_count += 1
            for i in range(col_count):
                if actgrp.value(i) is None:
                    print(' - ', end=" ")
                else:
                    print(actgrp.value(i), end=" ")
                if i == 1:
                    totalTime += actgrp.value(i)
            print('')
    else:
        print('unexpected SQL query result')

    rbt.close()
    print(f'Row count: {row_count}, total time = {totalTime}')
else:
    print("Impossible d'ouvrir la base de données") 
                
                      