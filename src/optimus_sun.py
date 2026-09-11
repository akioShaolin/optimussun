#optimus_sun.py
#                                               ;   :   ;
#                                            .   \_,!,_/   ,
#                                             `.,'     `.,'
#                                              /         \
#                                        ~ -- :           : -- ~
#
#                                             OPTIMUS SUN
#                                                v2.6.0
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠀⠀⠀⣤⣤⣤⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⣠⡶⢿⡇⢿⣿⡏⢳⣦⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡛⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⣼⣿⣴⣋⡽⠮⠿⢭⣟⣏⣷⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣧⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡼⣇⣿⡿⠶⣶⣿⣟⡛⣷⣿⢠⠙⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡈⣏⠇⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⢹⠁⣿⠋⠉⢹⠉⠙⣿⡇⣾⣀⣾⠀⢀⣤⡀⢀⡀⠀⠀⢀⣠⣴⣾⠛⢻⡛⢻⡄⢀⣳⡀⢀⣠⠄⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣷⣾⢀⣿⡇⠀⠸⠀⠀⣿⣧⡽⠿⣟⣺⣭⠴⢿⡏⣩⣷⡾⢛⣭⣴⣿⣇⠘⣿⣷⣿⡛⠉⢻⣟⣷⠄⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠿⢿⣟⣿⣿⡦⣶⣪⡭⠿⣚⣫⣭⣽⣶⡄⠀⢸⡇⣿⡙⣿⣿⣿⣿⣿⣿⣆⠹⣿⣿⣷⡀⠀⢿⡉⠁⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣤⣶⣿⠿⠛⣉⣭⣶⣾⣿⠿⠟⠛⠉⠉⢻⠀⢸⣷⣿⣇⢻⡿⣿⣿⣿⣿⠟⠀⠹⣿⣿⠃⠀⠘⣷⡀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣦⣼⣿⠿⠛⣋⡁⣼⢠⣿⡿⠛⠉⠁⠀⠀⢀⡀⢀⣴⣾⠀⢸⣿⡇⢻⡄⠙⠿⠻⠛⠁⠀⢀⣠⣽⣿⣇⡀⠀⠸⣧⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠿⣛⣭⣴⡾⠟⠛⣧⣿⢸⡿⠀⠀⠀⠀⣰⣿⣿⣷⣾⣿⣿⠀⢸⡏⣇⢸⣷⡀⠀⢀⣠⣴⣾⠿⠛⣿⢻⣿⣹⡀⠀⢻⣆⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡟⣦⠀⠀⠀⢀⡿⣵⡿⠛⠉⣡⣶⣤⣄⣿⣯⢸⣇⠀⠀⢠⣾⣿⡿⣿⣿⣿⣿⡿⠀⢸⡇⢻⡼⣿⣷⣶⠿⠛⠉⠀⠀⠀⠸⡇⣿⣿⣧⠀⠘⣿⡀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⢹⠀⢀⣠⣼⣿⣿⠀⢀⣼⣿⣿⣿⣿⡇⣿⢸⣿⣀⣀⣿⡿⠿⠶⠚⠛⠉⠉⠀⠀⢸⡇⠀⢻⣾⣝⣿⡆⠀⢀⣠⡴⠖⠛⢻⡾⣿⣿⣆⠀⢹⡇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣇⣼⡾⠟⠋⣿⢻⣇⣤⣌⠻⢿⣿⣿⣿⠃⢿⠀⠉⠉⠁⠀⠀⠀⣀⣤⡤⠶⠶⠒⠚⣻⣷⣄⠈⣿⣿⣿⣿⡞⠉⠀⠀⠀⠀⠀⣿⢿⣿⣾⣋⣽⠇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣹⠏⠀⠀⠀⣿⢿⣿⣿⣯⡴⠾⠛⢋⣡⠶⠛⠛⠋⣉⣉⣉⣙⢻⣿⠀⠀⠀⠀⠀⢠⡟⠀⠈⠻⢦⣈⣿⣿⣧⠀⠀⢀⣠⣴⡾⢿⣿⣿⣿⣿⣿⡀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⣿⡟⠀⠀⠀⣿⠈⠋⠉⢀⣠⠴⣛⣩⣤⣶⣞⣭⣿⢿⣿⣿⣻⣼⣿⣆⣀⣤⣤⣴⣿⣄⣠⣶⣦⣀⣙⣿⣿⣿⡶⣿⠟⠋⣁⣶⠟⢻⣽⣿⣿⣿⠇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢠⣿⣇⠀⠀⠀⢹⣠⡴⠖⢻⣷⢫⣿⣿⣿⣯⣿⣟⣿⣿⣭⣽⣿⡿⣿⣿⣿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⠋⠉⣿⠀⢸⣿⣿⣿⣿⣷⡀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣼⣿⣿⣤⣴⣾⢿⡅⠀⣀⣾⢿⣿⣿⣿⣿⣿⣿⡿⣿⣷⣿⣿⣿⡇⣿⣿⡇⠀⠀⢸⣿⣿⡟⢿⣿⣿⣿⣿⣿⣣⣿⠁⣿⣀⣤⡿⠀⢀⣿⣿⣿⣿⣿⡇⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠻⣿⠛⠉⠀⠈⣿⠛⢽⣿⢻⣿⣿⢿⣿⣿⣿⡇⣿⠿⣶⣶⣚⣧⣿⣿⡇⠀⠀⣸⣿⣿⣿⣄⣈⢿⣿⢿⣷⣿⣿⠀⠉⠉⠀⠀⠀⠘⡇⣿⣿⣿⣿⡇⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⡀⣷⡆⠀⠀⠀⠸⣧⣻⣿⢸⣿⣿⡿⢿⣾⣻⡇⣿⣿⣿⣿⣿⣿⣿⠿⠷⠾⠛⠛⠿⢿⣿⣿⣿⣄⣿⠿⠋⢸⣿⠀⠀⠀⠀⠀⠀⠀⡇⣿⣿⣿⣿⣿⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⡇⣿⡇⠀⠀⠀⠀⣿⣿⣿⡾⢿⣿⣿⣿⣿⡶⠷⠾⠛⠛⠉⠁⢀⣠⠤⠴⠒⡆⢠⠀⢰⡉⠻⣿⣽⡏⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⡇⣿⡿⣿⣿⣿⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⣿⠿⢀⣀⣤⣴⣿⣿⣿⡷⠾⠛⠋⠉⢀⣀⣠⠤⠴⠒⠻⡆⢸⠀⠀⢀⡠⠇⠸⡄⠈⣇⠀⠈⡻⢦⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⡇⣿⣧⡘⠿⢻⡆
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣆⣿⣿⣿⣿⣿⡿⠛⣉⣀⡀⣠⠴⠒⠋⠉⠁⠀⠀⠀⠀⠀⡇⢸⣠⠴⣫⡄⠀⠀⡇⠀⢹⠀⠀⣿⠦⢿⡀⢸⡇⠀⠀⣀⣤⣤⣿⠀⡇⣿⣿⣿⣆⢸⡇
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⢿⡟⣽⣿⠀⣏⠁⠀⡇⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⠀⡖⣻⠋⠀⠀⠈⢻⠀⢈⡇⠀⠸⡄⠘⣧⢸⡇⠀⢸⣷⣾⣿⠏⠀⡇⣿⣿⣿⣿⢸⡇
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠏⠛⠋⢡⣿⠀⠸⣿⣟⡃⣇⠀⠀⠀⠀⠀⣀⣠⡤⠶⠒⠋⠀⠛⠁⠀⣀⣤⣶⣿⣿⣿⣿⣷⣤⡈⠁⢻⡞⣿⠀⠈⠻⣴⠏⠀⠀⠿⢹⣿⣎⢻⣿⡇
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⡟⠀⠀⢀⡿⣿⠀⠀⠈⠳⡇⠻⠤⠶⠚⠋⠉⠁⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⣿⣿⠿⠛⠻⣿⣿⣿⣷⣜⣷⣿⠀⠀⢀⣀⣤⣤⣶⣾⣶⣿⣿⠃⢸⡇
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡶⠶⠖⠚⢛⠛⠳⢶⣼⡟⠀⠀⢀⣼⣹⣿⢀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⢀⣀⣠⡤⢤⣾⣿⣿⣿⡿⠿⠛⠉⠹⡇⠀⠀⣿⣿⣟⢿⣿⣿⠹⣶⣿⡿⠛⠻⣏⠀⠉⠉⡛⣿⡿⣾⡇
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠞⠋⢰⡇⢰⣿⢻⢻⢻⢶⣦⠙⣷⡀⠀⣸⢧⠟⢿⣿⣿⣿⣷⣶⣶⣤⣴⣲⡾⠿⠟⠒⠒⠛⡇⠙⣿⠉⠀⢧⠀⠀⠀⠀⣧⠀⠀⢸⣿⣿⡎⣿⠁⢀⣼⣏⢀⣠⣤⣸⣶⠀⠀⣿⣿⣿⠛⠁
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠃⠀⣠⡬⣤⣼⣛⠾⣼⣞⡾⡟⠀⠘⣧⣠⣏⡞⠀⠈⠻⣿⡏⢹⡟⠛⠻⣿⠁⠀⠀⠀⠀⠀⠀⣇⠀⣿⠀⠀⢸⡄⠀⠀⠀⢸⠀⠀⠘⣿⣿⣇⣿⣴⡞⢣⣽⣿⣿⣿⣿⣿⠀⠀⣿⣿⡟⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡶⣿⣿⣸⣿⣿⣿⠿⠷⠾⢽⣅⡲⠶⢻⣿⣼⢁⣠⣤⣶⣿⣿⠘⡇⠀⠀⢻⡆⠀⠀⠀⠀⠀⢀⣸⡀⢹⡇⠀⠈⡇⠀⠀⠀⠈⡇⠀⠀⢿⣿⣿⢹⣿⣤⣿⣿⣿⣿⡿⢿⣟⡀⠀⣿⣿⡇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⢯⣜⣿⠏⠀⠀⠀⢀⡿⣨⣿⣶⣤⣿⣷⣯⣿⣿⣿⣿⣿⠀⡇⠀⠀⠐⡿⣦⣰⣒⣶⣿⣿⣿⣷⣾⣇⠀⠀⢻⠀⠀⠀⠀⢷⠀⠀⢸⣿⣿⣾⣿⣸⣿⡏⢠⠟⣠⣿⣿⣿⣦⡈⢹⡇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⣾⠄⠀⠀⣸⡇⣿⣿⣿⠟⠋⠛⢿⣿⣿⣿⣿⣿⡄⢻⠀⠀⠀⡇⠈⠙⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⢸⡆⠀⠀⠀⢸⡄⠀⠀⣿⣿⣇⣿⠛⠛⠻⣿⣺⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢧⡇⠀⠀⠀⣿⢸⣿⣿⡿⢦⣴⣿⣿⣷⡿⣿⡿⣿⡇⢸⡄⠀⠀⢹⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⣇⠀⠀⠀⠀⣇⠀⠀⢸⣿⣟⢿⡀⠀⠀⠈⠉⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣨⡧⠤⠤⢤⣇⡾⣿⣿⣠⣿⣿⣿⣿⣿⣿⣽⣿⣿⣷⠀⣇⠀⠀⢸⠀⠀⢸⢻⣿⣿⣿⣿⡇⣿⣿⠀⠀⢹⡄⠀⠀⢀⣸⠀⠀⠸⣿⣿⣼⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⣧⣤⠶⠦⣼⣿⣿⣿⡏⠈⣿⣿⢿⣿⣿⣿⣏⠉⢹⣿⡀⢻⠀⠀⠘⡇⠀⠸⡄⠙⢿⣿⣿⠇⣿⣿⡄⠀⠈⠓⠒⠋⠉⠀⠀⠀⠀⢿⠹⣯⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⢃⡏⠀⠀⢻⣿⣿⣽⣿⣦⠘⣿⣿⣿⣿⣿⢻⣿⣾⣿⡇⠘⡇⠀⠀⣇⠀⠀⣇⠀⠀⠙⢿⡇⣿⢸⣧⠀⠀⠀⠀⡴⠒⢶⠀⠀⠀⠘⣆⠀⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⡅⣸⢁⣄⡄⣾⣿⢿⣿⠿⣿⣿⢻⣿⣿⣟⣿⣸⣻⡿⣿⣧⠀⠙⠒⠛⠛⠀⠀⢿⣿⣄⠀⠀⠀⣿⠈⣿⡄⠀⠀⠀⡇⠀⠘⡇⠀⠀⠀⢿⣦⢸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⡇⣿⣼⣿⠃⣿⣿⣾⣿⣷⣤⡿⠿⢿⣿⣿⣇⣿⡟⠋⠀⣿⡀⠀⣴⠲⡆⠀⠀⠸⣿⣿⣦⠀⠀⢸⡀⢹⣧⠀⠀⠀⣇⠀⠀⢹⠀⠀⠀⠸⣿⡟⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢽⡿⣷⠏⠛⠿⢠⣿⣿⣿⣿⢿⣯⡇⠀⠀⠈⠁⠀⠀⠀⠀⠀⢸⣇⠀⢻⠀⢳⠀⠀⠀⣿⣿⣿⣷⣾⢸⡇⠈⣿⡀⠀⠀⢸⠀⠀⠈⡇⠀⠀⢀⣿⣿⣷⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⡙⣀⣀⣀⣸⣿⣽⣿⣿⠀⠈⠙⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡀⢸⡀⠸⡄⠀⠀⢻⣿⣿⣿⣿⡼⡇⠀⢘⣧⣤⡴⠾⠷⠶⠖⠛⠛⢛⠋⠉⢿⢹⠉⣭⡿⠿⠷⠶⢦⡄⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣟⣁⣸⣿⣿⣧⡿⠿⣿⣀⡀⠀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣇⣈⣧⣘⣷⣤⣤⣼⠿⠿⣿⣿⣧⣧⡀⣸⢹⡏⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⢸⢸⡄⡿⠖⠚⠉⡉⠓⢿⡀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡴⣾⠋⠉⢙⣻⣷⠛⠛⠳⠶⠶⠽⠿⠃⠀⠀⠀⠀⠀⣀⡤⣼⡿⠋⠉⠁⠀⠀⣠⠀⣿⣿⠀⠀⠀⠀⠈⠉⠻⣿⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠸⡏⡇⣿⠀⠀⠀⢻⣷⢸⡇⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⠀⡟⠀⠀⢸⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⡥⢺⠏⡆⠀⠀⠀⠀⠀⡏⠀⡟⡇⠀⠀⠀⠀⠀⠀⢀⡇⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⡇⡇⢿⠀⠀⠀⢸⣿⡌⣷⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠇⢠⡇⠀⠀⢰⣿⣯⣏⣻⡆⠀⠀⠀⠀⠀⠀⠀⠀⣸⠃⢀⡿⢸⡇⠀⠀⠀⠀⢠⡇⠀⡇⡇⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⡆⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⡇⢿⢸⠀⠀⠀⠈⣿⡇⢹⡀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⡄⣼⠀⠀⢀⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⢸⡇⣸⡇⠀⠀⠀⠀⢸⠁⢸⣷⡇⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⢻⠀⠀⢹⢸⣼⡀⠀⣀⣀⣿⣧⣸⡇⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢧⣇⡏⠀⠀⣸⣿⠿⢭⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⢰⡏⠀⣿⠀⣿⡇⠀⠀⠀⠀⢸⠀⢸⢸⠁⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⣿⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢸⢸⣿⡏⢉⣁⣤⣤⣄⢈⡇⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢼⣿⠃⠀⠀⣿⣿⠀⢸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⡇⢠⡿⢰⣿⠃⠀⠀⠀⠀⣼⠀⢸⢸⠀⠀⠀⠀⠀⠀⠀⢸⡇⢸⢹⣸⣦⣤⣤⣤⣶⣶⣶⡿⠀⠀⢸⡄⡇⣧⣽⣿⣿⣿⡽⠟⠁⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⢻⡏⠀⠀⢰⣿⣿⣟⠛⢿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⠗⣻⡇⢸⢹⣆⣀⣀⣀⣤⡏⠀⢸⢸⠀⠀⠀⠀⠀⠀⠀⢸⡇⢸⠈⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⠈⡇⣿⠘⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠛⠤⢤⣤⣘⢺⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠸⢧⣿⠃⠘⠓⠛⠛⠛⠋⠉⠁⠀⢼⢸⠀⢰⡾⠿⠛⠛⠿⢿⡇⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢸⠀⠙⣿⣿⣿⠀⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⣶⡶⠚⠿⢿⣿⣩⢿⢿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣸⠀⢸⡇⠀⠀⠀⠀⣿⡇⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⢸⡀⠀⠈⠁⢸⡇⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣹⠃⠀⢰⣷⢻⠁⠈⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⣹⠀⢸⠃⠀⠀⠀⠀⣿⠇⠜⠀⣤⠶⠖⠛⠛⠋⠉⠉⢩⣿⡇⠀⢸⠸⡇⠀⠀⠀⠘⡇⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠏⠀⠀⣾⣿⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡇⠀⢀⣴⠶⠞⠛⠛⣻⣷⠀⡏⣿⠀⢸⢀⣴⣷⣦⡀⣿⠇⡇⠀⡟⠀⣀⣀⣀⣀⣀⣀⣸⣿⡇⠀⢸⡆⡇⠀⠀⠀⠀⣷⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠇⠀⠀⢸⣿⡇⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣾⣀⣀⣤⣤⣶⣿⡿⠀⡇⣿⠀⢸⣿⣿⣿⣫⣾⣿⠀⡇⢠⣟⣿⣿⣿⡿⠿⠿⠿⠿⠁⡇⠀⠈⡇⣷⢀⡀⠀⠀⢻⠀⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡼⠀⠀⡟⣿⣷⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠀⢀⡟⡿⠿⠟⠛⠛⣃⡇⠀⡇⣿⠀⢸⣿⣿⣿⣿⣿⣿⡄⡇⢸⡇⠀⠀⠀⠀⠀⠀⠀⢰⣶⡇⠀⠀⣇⢹⣾⣿⠀⣰⢾⡆⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⠀⢸⣷⣿⣹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⢸⡇⠀⠀⠀⠀⢰⣿⡇⠀⡇⣿⠀⣾⣿⣿⣿⣿⣿⣿⡃⡇⢸⣧⣤⣤⣴⣶⣶⣶⣶⣾⣿⡇⠀⠀⢿⢸⣿⣿⣾⣿⣸⡇⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢭⠥⠦⣬⣽⣧⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠀⢸⢵⣶⣾⣿⣿⣿⡿⡇⠀⡇⣿⠀⣿⣿⣿⣿⣿⣿⣿⡇⡇⢸⡏⠿⠟⠛⠛⠛⠛⠛⠛⣧⣷⠀⠀⢸⠀⣿⣿⣿⣿⠛⣇⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣸⠁⢠⣿⣿⣹⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⢸⠉⠉⠉⠁⠀⢠⣾⡇⠀⡇⣿⠀⣿⣿⣿⣿⣿⣿⣿⠇⡇⢸⡇⠀⣀⣀⣀⣀⣀⣀⣰⣿⣿⠀⠀⠸⠀⣿⣿⣿⣵⡇⣿⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⣰⠞⣞⣷⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⢸⣀⣀⣠⣤⣤⣼⣿⡇⠀⡇⣿⠀⢈⣭⣭⠭⠽⠭⣿⡇⡇⢸⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⢻⣟⣾⣿⣿⢻⠀⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣿⠿⠿⠿⠿⠟⢛⣻⡇⠀⡇⢻⠀⢸⠁⠀⠀⠀⠀⣿⡇⡇⠸⡏⠉⠀⠀⠀⠀⠀⠀⠀⣼⣿⡇⠀⠀⠀⢸⣿⣿⣿⣿⢸⡆⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣇⠀⣿⣀⣤⣤⣤⣤⣼⣿⡇⠀⡇⢸⠀⢸⠀⣠⣶⣄⠀⣿⡇⣇⠀⡇⣴⣶⣶⣾⣿⣿⣿⣿⣿⣿⣇⣀⣂⠀⢸⣿⣿⣿⣿⣿⡇⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡿⠴⠿⠿⠿⠿⠿⠿⠿⠿⠷⣦⡄⢸⠀⢸⣾⣿⣿⢟⣴⣿⣷⣼⠶⠗⠛⠛⠛⠛⠛⠛⠛⠋⠉⠉⠉⢉⡟⣧⠈⣿⣿⣿⣿⡿⣧⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⡇⢸⣴⢾⣿⡿⣻⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⣿⣿⣿⣿⣿⣿⠀⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⡇⢸⣿⢸⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⡀⣿⣿⣿⣿⣿⣿⡄⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⡇⢸⣿⢸⣿⣿⣿⣿⣿⠃⠀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣿⣿⣿⡇⢸⣿⣿⣿⣿⢻⡇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣷⣶⣶⣶⣶⣶⣶⣶⡶⠶⠦⠤⣾⣿⣿⣿⣿⣷⢘⣿⢸⣿⣿⣿⣿⡏⣭⠭⠭⠭⠤⠤⠤⠴⠶⠶⠶⠶⠶⠶⠶⠱⣌⢻⣿⣧⢸⣿⣿⣿⣿⣾⣇⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡾⠟⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⣉⣽⣿⣾⣿⣿⣿⣿⣿⠀⣿⢸⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡞⣿⢻⠈⣿⣿⣿⣿⣿⣿⠀⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⠛⢹⠀⣿⣾⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⢻⣿⡀⣿⣿⣿⣿⣿⣿⡄⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣀⣤⣄⣤⣤⣄⣀⣀⣀⣀⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣅⢸⠀⣿⡿⣿⣿⣤⣤⣤⡤⠤⠤⠶⠶⠶⠖⠒⠒⠒⠚⠛⠛⠛⠺⣿⣿⣿⡇⠹⡇⣿⣿⣿⣿⣿⣿⡇⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⡟⠉⢹⣿⣿⣿⣿⡿⠿⡾⠀⣿⡇⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠰⠇⣿⣿⣿⣿⡿⣿⡇⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⠛⠉⠁⠀⠀⠀⠙⠛⠉⠁⠀⠀⠁⠀⣛⣁⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⠟⣹⡇⢀⣙⣿⣯⡷⠿⠛⠁⠀
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⠉⠉⠉⠉⠉⠹⠷⣦⣤⣤⣤⣤⣤⣤⣤⣤⣤⣶⣶⣶⡶⠶⠶⠶⠶⠾⠿⠛⠛⠋⠉⠉⠁⠀⠀⠀⠀⠀⠀
# 
#                                                   "Em qualquer guerra, há calma entre as tempestades." 
#                                                                                        ~ Optimus Prime

import sqlite3
import tkinter as tk
import matplotlib.pyplot as plt
import math
import sys

from contextlib import closing
from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from functools import partial
from optimus_lib import (
    compensacao_termica,
    formatar_tupla,
    limite_strings_curto_circuito,
    limite_strings_operacao,
    limite_modulos_sobrecarga,
    limites_modulos_serie,
    minimo_valido,
    mppt_index_dec,
    validar,
    vv,
)
from equipment_search import EquipmentSearchRepository
from equipment_search_gui import EquipmentSearchPanel, SearchVisibilityController, format_selection_card
from overload_control import OverloadSession, bind_overload_entry, valid_registered_percent
from focus_navigation import prepare_toplevel
from version import APP_VERSION

# Identidade visual centralizada
COLORS = {
    "background": "#F4F7FA",
    "surface": "#FFFFFF",
    "surface_alt": "#E8EEF5",
    "primary": "#1F4E78",
    "primary_soft": "#DCEAF7",
    "text": "#17212B",
    "muted": "#5D6B78",
    "border": "#CBD5E1",
    "success": "#2E7D32",
    "warning": "#D97706",
    "error": "#C62828",
    "ignored": "#8A94A3",
}
FONT_FAMILY = "Segoe UI"
bg_c = COLORS["background"]

# Armazena todas as Toplevels abertas para finalizar elas depois
toplevels = []

# Tuplas que armazenam fabricantes e seus IDs
fab_inversor = {}
fab_modulo = {}

# Armazena Tuplas de inversores e seus IDs
inversores = {}
modulos = {}

# inv_selec - Dados atribuídos a partir das chaves da tabela do banco de dados 
inv_selec = {
                "ID": None,                                 # Chave Primária
       	        "MODEL": None,                              # Modelo
   		        "MANUFACTURER_ID": None,                    # ID do fabricante
                "MANUFACTURER_NAME": None,                  # Nome do fabricante
		        "DIM_WIDTH": None,                          # Largura
                "DIM_HEIGHT": None,                         # Altura
		        "DIM_DEPTH": None,                          # Profundidade
		        "DIM_WEIGHT": None,                         # Peso
		        "MAX_OPERATING_TEMPERATURE": None,          # Temperatura máxima de operação
		        "MIN_OPERATING_TEMPERATURE": None,          # Temperatura mínima de operação
		        "COOLING_MODE": None,                       # Modo de refrigeração
		        "PROTECTION_DEGREE": None,                  # Grau de Proteção IP
		        "TOPOLOGY": None,                           # Topologia
	            "RATED_ACTIVE_POWER": None,                 # Potência ativa nominal
		        "MAX_ACTIVE_POWER": None,                   # Potência ativa máxima
	            "RATED_OUTPUT_VOLTAGE": None,               # Tensão nominal de saída
		        "RATED_OUTPUT_CURRENT": None,               # Corrente nominal de saída
		        "MAX_OUTPUT_CURRENT": None,                 # Corrente máxima de saída
		        "OVERLOAD": None,                           # Sobrecarga
		        "NUMBER_OF_TRACKERS": None,                 # Número de MPPTs
		        "NUMBER_OF_INPUTS": None,                   # Número de entradas do inversor
		        "ACTIVE": None,                             # Ativo ou Inativo 
                "MPPT":
                [
                    {
                       "ID": None,                          # ID do MPPT
                       "INVERTER_ID": None,                 # ID do inversor que contém esse MPPT
                       "MPPT_INDEX": None,                  # Índice do MPPT (0 se todos forem iguais,
                                                            # produto de primos para o caso de MPPTs diferentes, para identificar sua posição)
                       "NUMBER_OF_INPUTS": None,            # Número de entradas do MPPT
                       "MAX_INPUT_VOLTAGE": None,           # Tensão máxima de entrada
                       "MIN_STARTUP_VOLTAGE": None,         # Tensão mínima de partida
                       "MAX_OPERATING_VOLTAGE": None,       # Tensão máxima de operação
                       "MIN_OPERATING_VOLTAGE": None,       # Tensão mínima de operação
                       "MAX_FULL_LOAD_VOLTAGE": None,       # Tensão máxima de carga máxima (Full Load)
                       "MIN_FULL_LOAD_VOLTAGE": None,       # Tensão mínima de carga máxima (Full Load)
                       "RATED_OUTPUT_VOLTAGE": None,        # Tensão nominal do MPPT
                       "MAX_SHORT_CIRCUIT_CURRENT": None,   # Corrente máxima de curto circuito
                       "MAX_OPERATING_CURRENT": None        # Corrente máxima de operação
                    }
                ],
               "SYSTEM_TYPE": [],                           # Tipos de sistema (ongrid, offgrid, hibrido, etc)
               "COMMUNICATION_TYPE": [],                    # Tipos de comunicação (Led, Wifi, RS485, etc)
               "OUTPUT_MODE": []                            # Tipo de saída (Monofásico, Trifásico 3 fios, Trifásico 4 fios)
    }

# mod_selec - Dados atribuídos a partir das chaves da tabela do banco de dados 
mod_selec = {
		        "ID": None,                                 # Chave Primária
		        "MODEL": None,                              # Modelo
		        "MANUFACTURER_ID": None,                    # ID do fabricante
                "MANUFACTURER_NAME": None,                  # Nome do fabricante
		        "DIM_WIDTH": None,                          # Largura
		        "DIM_HEIGHT": None,                         # Altura
		        "DIM_DEPTH": None,                          # Profundidade
		        "DIM_WEIGHT": None,                         # Peso
		        "WP": None,                                 # Potência nominal
                "VMPP": None,                               # Tensão em máxima potência
		        "IMPP": None,                               # Corrente em máxima potência
		        "VOC": None,                                # Tensão de circuito aberto
		        "ISC": None,                                # Corrente de curto circuito
		        "SOLAR_CELLS": None,                        # Monocristalino ou Policristalino
		        "CELL_TYPE": None,                          # Half Cell ou Full Cell
		        "SURFACE_TYPE": None,                       # Bifacial ou Monofacial
		        "COEF_PMAX": None,                          # Coeficiente de temperatura de potência máxima
		        "COEF_VOC": None,                           # Coeficiente de temperatura de tensão de circuito aberto
		        "COEF_ISC": None,                           # Coeficiente de temperatura de corrente de curto circuito
		        "ACTIVE": None                              # Ativo ou Inativo
    }

# Dicionário utilizado para fazer e armazenar os calculos
calculos_cc = {
    # Dados do(s) MPPT(s) do inversor escolhido
    "mppt":
        [
            {
                "mppt_index": None,                         # Índice do MPPT. 0 se forem todos iguais
                "n_in_mppt": None,                          # Número de entradas por MPPT
                "max_i_v": None,                            # Tensão máxima de entrada
                "min_i_v": None,                            # Tensão mínima de entrada
                "max_o_v": None,                            # Tensão máxima de operação
                "min_o_v": None,                            # Tensão mínima de operação
                "max_fl_v": None,                           # Tensão máxima de carga máxima (full load)
                "min_fl_v": None,                           # Tensão mínima de carga máxima (full load)
                "max_sc_i": None,                           # Corrente máxima de curto circuito
                "max_o_i": None,                            # Corrente máxima de operação
                # Aqui é onde são calculadas as quantidades de módulos e entradas a serem utilizadas
                "n_min_in": None,                           # Número mínimo de módulos para ligar o MPPT
                "n_max_in": None,                           # Número máximo de módulos suportadas pelo MPPT
                "n_min_o": None,                            # Número mínimo de módulos em operação
                "n_max_o": None,                            # Número máximo de módulos em operação
                "n_min_fl": None,                           # Número mínimo de módulos em carga máxima (full load)
                "n_max_fl": None,                           # Número máximo de módulos em carga máxima (full load)
                "q_min_o": None,                            # Escolhe o valor maior entre n_min_in e n_min_o
                "q_max_o": None,                            # Escolhe o valor menor entre n_max_in e n_max_o
                "q_min_fl": None,                           # Escolhe o valor maior entre n_min_in, n_min_o e n_min_fl
                "q_max_fl": None,                           # Escolhe o valor menor entre n_max_in, n_max_o e n_max_fl
                "n_max_sc_mppt": None,                      # Número máximo de strings no MPPT por corrente de curto circuito
                "n_max_o_mppt": None,                       # Número máximo de strings no MPPT por corrente de operação
                "q_s_mppt": None,                           # Escolhe o valor menor entre n_in_mppt, n_max_sc_mppt e n_max_o_mppt
                "n_mod_mppt": None,                         # Quantidade máxima de módulos por MPPT (considerando multiplas strings)
                "p_mod_mppt": None                          # Potencia máxima de entrada por MPPT (considerando multiplas strings) 
            }
        ],
    "inv": 
        {
                "pn": None,                                 # Potência nominal
                "sb": None,                                 # Sobrecarga admitida
                "n_tr": None,                               # Quantidade de MPPTs
                "n_in": None,                               # Quantidade de Strings
                "q_max_in": None,                           # Calcula a quantidade máxima de módulos respeitando a entrada
                "q_max_o": None,                            # Calcula a quantidade máxima de módulos respeitando a operação
                "q_max_fl": None,                           # Calcula a quantidade máxima de módulos respeitando a Carga máxima
                "q_max_sb": None,                           # Calcula a quantidade máxima de módulos respeitando a sobrecarga
                "p_max_sb_fl": None,                        # Quantidade em sobrecarga do módulo selecionado (Full Load)
                "p_max_sb_fl_per": None,                    # Quantidade em sobrecarga em porcentagem do módulo selecionado (Full Load)
                "p_max_sb_o": None,                         # Quantidade em sobrecarga do módulo selecionado (Operação)
                "p_max_sb_o_per": None                      # Quantidade em sobrecarga em porcentagem do módulo selecionado (Operação)   
        },
    # Dados do módulo após compensação térmica   
    "mod": 
        {
            "p_nom": None,                                      # Potência nominal
            "p_min": None,                                      # Potência mínima
            "p_max": None,                                      # Potência máxima
            "vmpp_min": None,                                   # Tensão mínima de em potência máxima
            "vmpp_max": None,                                   # Tensão máxima de em potência máxima
            "voc_min": None,                                    # Tensão mínima de circuito aberto
            "voc_max": None,                                    # Tensão máxima de circuito aberto
            "isc_min": None,                                    # Corrente mínima de curto circuito
            "isc_max": None,                                    # Corrente máxima de curto circuito
            "impp_min": None,                                   # Corrente mínima em potência máxima
            "impp_max": None,                                   # Corrente máxima em potência máxima
            "coef_pmax": None,                                  # Coeficiente de temperatura da potência máxima
            "coef_voc": None,                                   # Coeficiente de temperatura da tensão de circuito aberto
            "coef_isc": None                                    # Coeficiente de temperatura da corrente de curto circuito
        },
    # Parâmetros de temperatura da celula
    "amb": 
        {
        "t_cell_max": 50,                                       # Temperatura máxima
        "t_cell_min": 10                                        # Temperatura mínima
        },
    # Dados de tolerância
    "tol": 
        {
            "pot": 0.005,                                       # Tolerância do calculo de potência
            "op_i": 0                                           # Tolerância no calculo de corrente de operação
        }
    }
##################################################################################################################################

# Função repetitiva. Tem como função criar labels de vários tipos
def criar_label(container, texto, linha, coluna, style=0, colspan=1):

    if style == 'h1':

        label = ttk.Label(container, text=texto, style="h1.TLabel")
        label.grid(row=linha, column=coluna, columnspan=colspan, sticky='w', padx=5, pady=5)

        return label

    if style == 'table':

        cell_frame = tk.Frame(container, borderwidth=0, background=COLORS["surface"])
        cell_frame.grid(row=linha, column=coluna, columnspan=colspan, sticky="nsew", padx=1, pady=1)
        label = ttk.Label(cell_frame, text=texto, justify='left', anchor='w', wraplength=260, style="table.TLabel").grid(row=0, column=0, sticky="ew")

        return  label
    
    label = ttk.Label(container, text=texto).grid(row=linha, column=coluna, sticky='w', padx=3, pady=3)

    return label
##################################################################################################################################

# Conectar ao banco de dados para coletar os nomes e IDs dos fabricantes
def carregar_fabricante():
    global fab_inversor, fab_modulo
    global mod_selec, inv_selec, calculos_cc

    mod_selec.clear()
    inv_selec.clear()
    calculos_cc["mod"] = {}
    calculos_cc["mppt"].clear()
    calculos_cc["inv"] = {}

    try:
        with closing(sqlite3.connect(db_path)) as conexao:
            cursor = conexao.cursor()
            # Carregar fabricantes dos inversores em ordem alfabética
            cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (0, 2)")
            fab_inversor = dict(sorted(
                {row[1]: row[0] for row in cursor.fetchall()}.items(),
                key=lambda item: item[0].lower()
            )) # {Nome : ID}

            # Carregar fabricantes dos módulos em ordem alfabetica
            cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (1, 2)")
            fab_modulo = dict(sorted(
                {row[1]: row[0] for row in cursor.fetchall()}.items(),
                key=lambda item: item[0].lower()
            )) # {Nome : ID}
        
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao carregar fabricantes: \n{e}")

##################################################################################################################################

# Busca modelos com base no fabricante selecionado
def carregar_modelo(fab_nome, equipamento):

    global inversores, modulos
    global inv_selec, mod_selec, calculos_cc
    global flag_no_iop, flag_no_fl

    close_topLevels()

    try:
        with closing(sqlite3.connect(db_path)) as conexao:
            cursor = conexao.cursor()
            limpar_saidas()
            frame_img.pack(fill='x', padx=30, pady=5)

            if equipamento == "inversor":
                # Limpa a variável inv_selec
                inv_selec = {}

                # Reseta as opções de ignorar as faixas de operação e carga máxima
                flag_no_iop.set(False)
                chk_iop.config(state="disabled")
                flag_no_fl.set(False)
                chk_fl.config(state="disabled")

                # Adiciona os modelos de inversores do fabricante selecionado
                fab_id = fab_inversor.get(fab_nome)
                cursor.execute("SELECT ID, MODEL FROM inverter WHERE MANUFACTURER_ID = ?",(fab_id, ))
                inversores = dict(sorted(
                    {row[1]: row[0] for row in cursor.fetchall()}.items(),
                    key=lambda item: item[0].lower()
                    ))
                inversor_cb["values"] = list(inversores.keys())
                inversor_cb.set("")

            elif equipamento == "modulo":
                # Limpa a varíavel mod_selec
                mod_selec = {}

                # Adiciona os modelos de módulos do fabricante selecionado
                fab_id = fab_modulo.get(fab_nome)
                cursor.execute("SELECT ID, MODEL FROM module WHERE MANUFACTURER_ID = ?", (fab_id, ))
                modulos = dict(sorted(
                    {row[1]: row[0] for row in cursor.fetchall()}.items(),
                    key=lambda item: item[0].lower()
                ))
                modulo_cb["values"] = list(modulos.keys())
                modulo_cb.set("")
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao carregar modelos: \n{e}")
##################################################################################################################################

# Ao selecionar o inversor ou módulo, este código solicita os dados ao database
def carregar_dados(modelo, equipamento):
    
    global mod_selec, inv_selec
    global calculos_cc
    global flag_no_fl, flag_no_iop

    close_topLevels()

    # Conecta ao banco de dados para solicitar os dados do inversor e MPPT
    conexao = None
    try:
        conexao = sqlite3.connect(db_path)
        cursor = conexao.cursor()

        if (equipamento == "modulo"):
            
            mod_id = modulos.get(modelo)
            cursor.execute("SELECT * FROM module WHERE ID = ?", (mod_id, ))
            linha = cursor.fetchone()

            if linha:
                colunas = [col[0] for col in cursor.description]
                mod_selec = dict(zip(colunas, linha))

            man_id = mod_selec["MANUFACTURER_ID"]
            cursor.execute("SELECT NAME FROM manufacturer WHERE ID = ?", (man_id, ))
            man_name = cursor.fetchone()
            mod_selec["MANUFACTURER_NAME"] = man_name[0]        

        elif (equipamento == "inversor"):

            # Reseta as opções de ignorar as faixas de operação e carga máxima
            chk_iop.config(state="normal")
            flag_no_iop.set(False)
            chk_fl.config(state="normal")
            flag_no_fl.set(False)

            # Solicita os dados dos inversores
            inv_id = inversores.get(modelo)
            cursor.execute("SELECT * FROM inverter WHERE ID = ?", (inv_id,))
            colunas = [col[0] for col in cursor.description]
            valores = cursor.fetchone()
            inv_selec = dict(zip(colunas, valores)) if valores else {}

            # Solicita o nome do fabricante a partir do ID
            man_id = inv_selec["MANUFACTURER_ID"]
            cursor.execute("SELECT NAME FROM manufacturer WHERE ID = ?", (man_id, ))
            man_name = cursor.fetchone()
            inv_selec["MANUFACTURER_NAME"] = man_name[0]

            # Verifica os sistemas de funcionamento do inversor
            cursor.execute("SELECT SYSTEM_TYPE FROM inverter_system WHERE INVERTER_ID = ?", (inv_id, ))
            sys_t = [row[0] for row in cursor.fetchall()]
            inv_selec["SYSTEM_TYPE"] = sys_t

            # Verifica os métodos de comunicação do inversor
            cursor.execute("SELECT COMMUNICATION_TYPE FROM inverter_communication WHERE INVERTER_ID = ?", (inv_id, ))
            comm_t = [row[0] for row in cursor.fetchall()]
            inv_selec["COMMUNICATION_TYPE"] = comm_t

            # Verifica os métodos de saída do inversor
            cursor.execute("SELECT OUTPUT_MODE FROM inverter_output_mode WHERE INVERTER_ID = ?", (inv_id, ))
            out_m = [row[0] for row in cursor.fetchall()]
            inv_selec["OUTPUT_MODE"] = out_m

            # Adiciona os MPPTs no inversor
            cursor.execute("SELECT * FROM mppt WHERE INVERTER_ID = ?", (inv_id,))
            colunas_mppt = [col[0] for col in cursor.description]
            mppt_data = cursor.fetchall()
            mppt_list = [dict(zip(colunas_mppt, linha)) for linha in mppt_data]

            inv_selec["MPPT"] = mppt_list
            overload_session.select_inverter(inv_id, inv_selec.get("OVERLOAD"))
            sync_overload_controls()

        else:
            # Somente atualiza os calculos, caso inversor e módulo não for selecionado
            pass

    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao carregar dados do {equipamento}:\n{e}")
    finally:
        if conexao is not None:
            conexao.close()
    ##########
    
    # Verifica se as variáveis de inversor e módulos estão preenchidas para fazer os calculos
    if mod_selec and inv_selec:
        try:
            effective_overload = overload_session.effective_fraction()
        except ValueError as error:
            limpar_saidas()
            overload_effective_text.set(f"Não calculado: {error}")
            return False
        
# -------- Calculos dos Módulos --------

        # Oculta a imagem do Optimus Sun quando os resultados são exibidos
        frame_img.pack_forget()

        # Limpa os dados do módulo corrigidos
        calculos_cc["mod"] = {}

        # Calcula as correções térmicas das tensões e correntes do módulo
        calculos_cc["mod"]["p_nom"] = mod_selec["WP"]
        calculos_cc["mod"]["coef_pmax"] = mod_selec["COEF_PMAX"] / 100
        calculos_cc["mod"]["coef_voc"] = mod_selec["COEF_VOC"] / 100
        calculos_cc["mod"]["coef_isc"] = mod_selec["COEF_ISC"] / 100
        calculos_cc["mod"]["p_min"], calculos_cc["mod"]["p_max"] = compensacao_termica(
                                                                    calculos_cc["mod"]["coef_pmax"], 
                                                                    calculos_cc["amb"]["t_cell_min"], 
                                                                    calculos_cc["amb"]["t_cell_max"], 
                                                                    mod_selec["WP"])
        # Premissa: como o banco não possui coeficientes específicos de Vmpp e Impp,
        # Vmpp usa COEF_VOC e Impp usa COEF_ISC como aproximações.
        calculos_cc["mod"]["vmpp_min"], calculos_cc["mod"]["vmpp_max"] = compensacao_termica(
                                                                    calculos_cc["mod"]["coef_voc"], 
                                                                    calculos_cc["amb"]["t_cell_min"], 
                                                                    calculos_cc["amb"]["t_cell_max"], 
                                                                    mod_selec["VMPP"])
        calculos_cc["mod"]["voc_min"], calculos_cc["mod"]["voc_max"] = compensacao_termica(
                                                                    calculos_cc["mod"]["coef_voc"], 
                                                                    calculos_cc["amb"]["t_cell_min"], 
                                                                    calculos_cc["amb"]["t_cell_max"], 
                                                                    mod_selec["VOC"])
        calculos_cc["mod"]["isc_min"], calculos_cc["mod"]["isc_max"] = compensacao_termica(
                                                                    calculos_cc["mod"]["coef_isc"],
                                                                    calculos_cc["amb"]["t_cell_min"], 
                                                                    calculos_cc["amb"]["t_cell_max"], 
                                                                    mod_selec["ISC"])
        calculos_cc["mod"]["impp_min"], calculos_cc["mod"]["impp_max"] = compensacao_termica(
                                                                    calculos_cc["mod"]["coef_isc"], 
                                                                    calculos_cc["amb"]["t_cell_min"], 
                                                                    calculos_cc["amb"]["t_cell_max"], 
                                                                    mod_selec["IMPP"]) 
        
        print(f"""
            Módulo
              
            Vmpp Max: {calculos_cc["mod"]["vmpp_max"]:.2f}
            Vmpp Min: {calculos_cc["mod"]["vmpp_min"]:.2f}
            Voc Max: {calculos_cc["mod"]["voc_max"]:.2f}
            Voc Min {calculos_cc["mod"]["voc_min"]:.2f}
            Isc Max: {calculos_cc["mod"]["isc_max"]:.2f}
            Isc Min: {calculos_cc["mod"]["isc_min"]:.2f}
            Impp Max: {calculos_cc["mod"]["impp_max"]:.2f}
            Impp Min: {calculos_cc["mod"]["impp_min"]:.2f}
            """)
        
# -------- Calculos dos MPPTs --------
        # Limpa a lista de MPPTs
        calculos_cc["mppt"] = []
        # Armazena as grandezas na variável de calculos
        for i in range(len(inv_selec["MPPT"])):
            mppt = inv_selec["MPPT"][i]

            calculos_cc["mppt"].append({
                "mppt_index": mppt["MPPT_INDEX"],
                "n_in_mppt": mppt["NUMBER_OF_INPUTS"],
                "max_i_v" : mppt["MAX_INPUT_VOLTAGE"],
                "min_i_v" : mppt["MIN_STARTUP_VOLTAGE"],
                "max_o_v" : mppt["MAX_OPERATING_VOLTAGE"],
                "min_o_v" : mppt["MIN_OPERATING_VOLTAGE"],
                "max_fl_v" : mppt["MAX_FULL_LOAD_VOLTAGE"],
                "min_fl_v" : mppt["MIN_FULL_LOAD_VOLTAGE"],
                "max_sc_i" : mppt["MAX_SHORT_CIRCUIT_CURRENT"],
                "max_o_i" : mppt["MAX_OPERATING_CURRENT"],
                # Inicializa os campos a serem calculados como None
                "n_min_in": None,
                "n_max_in": None,
                "n_min_o": None,
                "n_max_o": None,
                "n_min_fl": None,
                "n_max_fl": None,
                "q_min_o": None,
                "q_max_o": None,
                "q_min_fl": None,
                "q_max_fl": None,
                "n_max_sc_mppt": None,
                "n_max_o_mppt": None,
                "q_s_mppt": None,
                "n_mod_o_mppt": None,
                "p_mod_o_mppt": None,
                "n_mod_fl_mppt": None,
                "p_mod_fl_mppt": None,    
            })

        for i in range(len(calculos_cc["mppt"])):

            print(f"""
            MPPT {formatar_tupla(mppt_index_dec(calculos_cc['mppt'][i]["mppt_index"]))}

            Input Voltage Range: {calculos_cc["mppt"][i]["min_i_v"]:.2f}, {calculos_cc["mppt"][i]["max_i_v"]:.2f};
            Operating Voltage Range: {calculos_cc["mppt"][i]["min_o_v"]:.2f}, {calculos_cc["mppt"][i]["max_o_v"]:.2f};
            Full Load Voltage Range: {calculos_cc["mppt"][i]["min_fl_v"]:.2f}, {calculos_cc["mppt"][i]["max_fl_v"]:.2f};
            Max Short Circuit Current: {calculos_cc["mppt"][i]["max_sc_i"]:.2f};
            Max Operating Current:  {calculos_cc["mppt"][i]["max_o_i"]:.2f};

                """)

            # Calcular quantidades máximas de módulos e entradas do MPPT para compatibilidade entre equipamentos 
            calculos_cc["mppt"][i]["n_max_sc_mppt"] = limite_strings_curto_circuito(
                calculos_cc["mppt"][i]["max_sc_i"], calculos_cc["mod"]["isc_max"]
            )
            calculos_cc["mppt"][i]["n_max_o_mppt"] = limite_strings_operacao(
                calculos_cc["mppt"][i]["max_o_i"],
                calculos_cc["mod"]["impp_max"],
                calculos_cc["tol"]["op_i"],
            )
            
            # Variável temporária para calcular q_s_mppt, considerando ou não a corrente de operação
            if flag_no_iop.get():
                q_s_mppt = [
                    calculos_cc["mppt"][i]["n_in_mppt"],
                    calculos_cc["mppt"][i]["n_max_sc_mppt"],
                ]
            else:
                q_s_mppt = [
                    calculos_cc["mppt"][i]["n_in_mppt"],
                    calculos_cc["mppt"][i]["n_max_sc_mppt"],
                    calculos_cc["mppt"][i]["n_max_o_mppt"]
                ]

            calculos_cc["mppt"][i]["q_s_mppt"] = minimo_valido(q_s_mppt)

            # Se o valor for 0, o programa nem perde tempo calculando as quantidades de módulos compatíveis
            if (calculos_cc["mppt"][i]["q_s_mppt"] > 0 and vv(calculos_cc["mppt"][i]["q_s_mppt"])):
                calculos_cc["mppt"][i]["n_min_in"], calculos_cc["mppt"][i]["n_max_in"] = limites_modulos_serie(
                    calculos_cc["mppt"][i]["min_i_v"], calculos_cc["mppt"][i]["max_i_v"],
                    calculos_cc["mod"]["voc_min"], calculos_cc["mod"]["voc_max"],
                )
                calculos_cc["mppt"][i]["n_min_o"], calculos_cc["mppt"][i]["n_max_o"] = limites_modulos_serie(
                    calculos_cc["mppt"][i]["min_o_v"], calculos_cc["mppt"][i]["max_o_v"],
                    calculos_cc["mod"]["vmpp_min"], calculos_cc["mod"]["vmpp_max"],
                )
                calculos_cc["mppt"][i]["n_min_fl"], calculos_cc["mppt"][i]["n_max_fl"] = limites_modulos_serie(
                    calculos_cc["mppt"][i]["min_fl_v"], calculos_cc["mppt"][i]["max_fl_v"],
                    calculos_cc["mod"]["vmpp_min"], calculos_cc["mod"]["vmpp_max"],
                )

            else:
                calculos_cc["mppt"][i]["n_min_in"] = 0
                calculos_cc["mppt"][i]["n_max_in"] = 0
                calculos_cc["mppt"][i]["n_min_o"] = 0
                calculos_cc["mppt"][i]["n_max_o"] = 0
                calculos_cc["mppt"][i]["n_min_fl"] = 0
                calculos_cc["mppt"][i]["n_max_fl"] = 0

            if vv(calculos_cc["mppt"][i]["n_min_in"], calculos_cc["mppt"][i]["n_min_o"], calculos_cc["mppt"][i]["n_max_in"], calculos_cc["mppt"][i]["n_max_o"]):
                calculos_cc["mppt"][i]["q_min_o"] = max(calculos_cc["mppt"][i]["n_min_in"], calculos_cc["mppt"][i]["n_min_o"])
                calculos_cc["mppt"][i]["q_max_o"] = min(calculos_cc["mppt"][i]["n_max_in"], calculos_cc["mppt"][i]["n_max_o"])
                calculos_cc["mppt"][i]["n_mod_o_mppt"] = calculos_cc["mppt"][i]["q_max_o"] * calculos_cc["mppt"][i]["q_s_mppt"]
                calculos_cc["mppt"][i]["p_mod_o_mppt"] = calculos_cc["mppt"][i]["n_mod_o_mppt"] * calculos_cc["mod"]["p_nom"] / 1000
            else:
                calculos_cc["mppt"][i]["q_min_o"] = -1
                calculos_cc["mppt"][i]["q_max_o"] = -1
                calculos_cc["mppt"][i]["n_mod_o_mppt"] = -1
                calculos_cc["mppt"][i]["p_mod_o_mppt"] = -1
            
            if vv(calculos_cc["mppt"][i]["q_min_o"], calculos_cc["mppt"][i]["q_max_o"], calculos_cc["mppt"][i]["n_min_fl"], calculos_cc["mppt"][i]["n_max_fl"]):
                calculos_cc["mppt"][i]["q_min_fl"] = max(calculos_cc["mppt"][i]["n_min_in"], calculos_cc["mppt"][i]["n_min_o"], calculos_cc["mppt"][i]["n_min_fl"])
                calculos_cc["mppt"][i]["q_max_fl"] = min(calculos_cc["mppt"][i]["n_max_in"], calculos_cc["mppt"][i]["n_max_o"], calculos_cc["mppt"][i]["n_max_fl"])
                calculos_cc["mppt"][i]["n_mod_fl_mppt"] = calculos_cc["mppt"][i]["q_max_fl"] * calculos_cc["mppt"][i]["q_s_mppt"]
                calculos_cc["mppt"][i]["p_mod_fl_mppt"] = calculos_cc["mppt"][i]["n_mod_fl_mppt"] * calculos_cc["mod"]["p_nom"] / 1000   
    
            else:
                calculos_cc["mppt"][i]["q_min_fl"] = -1
                calculos_cc["mppt"][i]["q_max_fl"] = -1
                calculos_cc["mppt"][i]["n_mod_fl_mppt"] = -1
                calculos_cc["mppt"][i]["p_mod_fl_mppt"] = -1

            print(f"""
            Quantidade máxima de séries por MPPT: {calculos_cc["mppt"][i]["q_s_mppt"]}
            Quantidade mínima de módulos por string: {calculos_cc["mppt"][i]["q_min_o"]}
            Quantidade máxima de módulos por string: {calculos_cc["mppt"][i]["q_max_o"]}
            Quantidade mínima de módulos em Carga máxima: {calculos_cc["mppt"][i]["q_min_fl"]}
            Quantidade máxima de módulos em Carga máxima: {calculos_cc["mppt"][i]["q_max_fl"]}
            """)

# -------- Calculos do Inversor --------
        calculos_cc["inv"] = {}
        calculos_cc["inv"]["n_tr"] = inv_selec["NUMBER_OF_TRACKERS"]
        # O cadastro e a entrada da GUI estão em percentual de acréscimo; a
        # função matemática recebe a fração (50% -> 0,5), convertida uma vez.
        calculos_cc["inv"]["sb"] = effective_overload
        calculos_cc["inv"]["pn"] = inv_selec["RATED_ACTIVE_POWER"]
        calculos_cc["inv"]["n_in"] = inv_selec["NUMBER_OF_INPUTS"]
        calculos_cc["inv"]["n_tr"] = inv_selec["NUMBER_OF_TRACKERS"]

        for i in range(len(calculos_cc["mppt"])):
            mppt = calculos_cc["mppt"][i]

            if mppt["mppt_index"] == 0:
                if vv(calculos_cc["mppt"][i]["n_max_in"], calculos_cc["inv"]["n_tr"], calculos_cc["mppt"][i]["q_s_mppt"]):
                    calculos_cc["inv"]["n_max_in"] = calculos_cc["mppt"][i]["n_max_in"] * calculos_cc["inv"]["n_tr"] * calculos_cc["mppt"][i]["q_s_mppt"]
                else:
                    calculos_cc["inv"]["n_max_in"] = -1

                if vv(calculos_cc["mppt"][i]["n_max_o"], calculos_cc["inv"]["n_tr"], calculos_cc["mppt"][i]["q_s_mppt"]):
                    calculos_cc["inv"]["n_max_o"] = calculos_cc["mppt"][i]["n_max_o"] * calculos_cc["inv"]["n_tr"] * calculos_cc["mppt"][i]["q_s_mppt"]
                else:
                    calculos_cc["inv"]["n_max_o"] = -1
                    
                if vv(calculos_cc["mppt"][i]["n_max_fl"], calculos_cc["inv"]["n_tr"], calculos_cc["mppt"][i]["q_s_mppt"]):
                    calculos_cc["inv"]["n_max_fl"] = calculos_cc["mppt"][i]["n_max_fl"] * calculos_cc["inv"]["n_tr"] * calculos_cc["mppt"][i]["q_s_mppt"]
                else:
                    calculos_cc["inv"]["n_max_fl"] = -1

            # Trata de inversores com dois ou mais MPPTs diferentes
            else:
                qtd_mppt = len(mppt_index_dec(calculos_cc["mppt"][i]['mppt_index']))

                if vv(calculos_cc["mppt"][i]["n_max_in"], calculos_cc["mppt"][i]["q_s_mppt"]):
                    if calculos_cc["inv"].get("n_max_in") != -1:
                        calculos_cc["inv"]["n_max_in"] = calculos_cc["inv"].get("n_max_in", 0) + calculos_cc["mppt"][i]["n_max_in"] * qtd_mppt * calculos_cc["mppt"][i]["q_s_mppt"]
                    else:
                        calculos_cc["inv"]["n_max_in"] = -1
                else:
                    calculos_cc["inv"]["n_max_in"] = -1

                if vv(calculos_cc["mppt"][i]["n_max_o"], calculos_cc["mppt"][i]["q_s_mppt"]):
                    if calculos_cc["inv"].get("n_max_o") != -1:
                        calculos_cc["inv"]["n_max_o"] = calculos_cc["inv"].get("n_max_o", 0) + calculos_cc["mppt"][i]["n_max_o"] * qtd_mppt * calculos_cc["mppt"][i]["q_s_mppt"]
                    else:
                        calculos_cc["inv"]["n_max_o"] = -1                
                else:
                    calculos_cc["inv"]["n_max_o"] = -1
                    
                if vv(calculos_cc["mppt"][i]["n_max_fl"], calculos_cc["mppt"][i]["q_s_mppt"]):
                    if calculos_cc["inv"].get("n_max_fl") != -1:
                        calculos_cc["inv"]["n_max_fl"] = calculos_cc["inv"].get("n_max_fl", 0) + calculos_cc["mppt"][i]["n_max_fl"] * qtd_mppt * calculos_cc["mppt"][i]["q_s_mppt"]
                    else:
                        calculos_cc["inv"]["n_max_fl"] = -1  
                else:
                    calculos_cc["inv"]["n_max_fl"] = -1

        calculos_cc["inv"]["n_max_sb"] = limite_modulos_sobrecarga(
            calculos_cc["inv"].get("pn"),
            calculos_cc["inv"].get("sb"),
            calculos_cc["tol"].get("pot"),
            calculos_cc["mod"].get("p_nom"),
        )

        if flag_no_fl.get():
            q_max_o = [
                calculos_cc["inv"]["n_max_in"],
                calculos_cc["inv"]["n_max_sb"]
            ]
        else:
            q_max_o = [
                calculos_cc["inv"]["n_max_in"],
                calculos_cc["inv"]["n_max_o"],
                calculos_cc["inv"]["n_max_sb"]
            ]

        if [v for v in q_max_o if v != -1 and v is not None]:
            calculos_cc["inv"]["q_max_o"] = min(q_max_o)
        else:
            calculos_cc["inv"]["q_max_o"] = -1

        if vv(calculos_cc["inv"]["q_max_o"]):
            calculos_cc["inv"]["p_max_sb_o"] = round(calculos_cc["mod"]["p_nom"] * calculos_cc["inv"]["q_max_o"] / 1000, 1)
            calculos_cc["inv"]["p_max_sb_o_per"] = math.trunc((calculos_cc["inv"]["p_max_sb_o"] * 1000 - calculos_cc["inv"]["pn"]) * 100 / calculos_cc["inv"]["pn"])
        else:
            calculos_cc["inv"]["p_max_sb_o"] = -1
            calculos_cc["inv"]["p_max_sb_o_per"] = -1

        q_max_fl = [
            calculos_cc["inv"]["n_max_in"],
            calculos_cc["inv"]["n_max_o"],
            calculos_cc["inv"]["n_max_fl"],
            calculos_cc["inv"]["n_max_sb"]
        ]

        # Filtra apenas os que são válidos (≠ -1 e ≠ None)
        if [v for v in q_max_fl if v != -1 and v is not None]:
            print(q_max_fl)
            calculos_cc["inv"]["q_max_fl"] = min(q_max_fl)
        else:
            calculos_cc["inv"]["q_max_fl"] = -1

        # Calculo das potências
        
        if vv(calculos_cc["inv"]["q_max_fl"]):
            calculos_cc["inv"]["p_max_sb_fl"] = round(calculos_cc["mod"]["p_nom"] * calculos_cc["inv"]["q_max_fl"] / 1000, 1)
            calculos_cc["inv"]["p_max_sb_fl_per"] = math.trunc((calculos_cc["inv"]["p_max_sb_fl"] * 1000 - calculos_cc["inv"]["pn"]) * 100 / calculos_cc["inv"]["pn"])
        else:
            calculos_cc["inv"]["p_max_sb_fl"] = -1
            calculos_cc["inv"]["p_max_sb_fl_per"] = -1
                    
        overload_effective_text.set(
            f"Valor efetivamente usado no cálculo: {overload_session.effective_percent():g}%"
        )
        atualizar_saida()
        return True
    return False
##################################################################################################################################

# Deleta os campos e limpa o campos de saída
def limpar_saidas():

    frame_qtd_mod_inv.pack_forget()
    if not frame_img.winfo_manager():
        frame_img.pack(fill="x", padx=30, pady=2)

    for widget in notebook.winfo_children():
        widget.destroy() 
##################################################################################################################################

# Função para criar ou atualizar as saídas
def atualizar_saida():

    largura = 500
    altura = 100

    def valor_maximo(n):
        if n % 5 == 0:
            return n + 5
        return n + (5 - (n % 5))
    
    min_operacao = []
    max_operacao = []
    min_carga_max = []
    max_carga_max = []
    valor_max = []
    aba = []

    # Limpar notebook antes (remove widgets filhos)
    for widget in notebook.winfo_children():
        widget.destroy()

    for i, mppt in enumerate(calculos_cc["mppt"]):
        
        aba.append(tk.Frame(notebook, bg=bg_c))
        notebook.add(aba[-1], text=f"MPPT {format_mppt_display(mppt.get('mppt_index'))}")

        min_operacao.append(mppt.get("q_min_o") if vv(mppt.get("q_min_o")) else None)
        max_operacao.append(mppt.get("q_max_o") if vv(mppt.get("q_max_o")) else None)
        min_carga_max.append(mppt.get("q_min_fl") if vv(mppt.get("q_min_fl")) else None)
        max_carga_max.append(mppt.get("q_max_fl") if vv(mppt.get("q_max_fl")) else None)
        valor_max.append(valor_maximo(mppt.get("q_max_o")))

        # Atualização do aviso
        atualizar_aviso()

        # Canvas novo
        altura_barras = 30
        espaco_topo = 20
        ttk.Label(aba[i], text="Quantidade de módulos por String", style="h1.TLabel").pack(fill="x", side="top")

        canvas = tk.Canvas(aba[i], width=largura + 50, height=altura + 30, bg=bg_c, bd=0, highlightthickness=0)
        canvas._last_width = largura + 50

        def redimensionar_canvas(event, target=canvas):
            if event.width <= 1 or target._last_width <= 1:
                return
            escala_x = event.width / target._last_width
            target.scale("all", 0, 0, escala_x, 1)
            target._last_width = event.width

        canvas.bind("<Configure>", redimensionar_canvas)
        canvas.pack(fill="x", expand=True, padx=20, pady=(10, 5))

        # Centralizar: definir ponto inicial
        x_offset = 25
        barra_total = largura

        # Função para converter valor -> posição X
        def valor_para_x(valor):
            return x_offset + (valor / valor_max[i]) * barra_total

        # Função auxiliar para garantir largura mínima
        def faixa_com_largura(x1, x2, min_largura=20):
            if abs(x1 - x2) < min_largura:
                meio = (x1 + x2) / 2
                return meio - min_largura / 2, meio + min_largura / 2
            return x1, x2

        # Desenhar barras
        # Barra vermelha (fundo)
        canvas.create_rectangle(
            valor_para_x(0), espaco_topo, 
            valor_para_x(valor_max[i]), espaco_topo + altura_barras, 
            fill='red', outline='black'
        )

        # Barra amarela (faixa de operação)
        if min_operacao[i] is not None and max_operacao[i] is not None:
            
            x1, x2 = valor_para_x(min_operacao[i]), valor_para_x(max_operacao[i])
            x1, x2 = faixa_com_largura(x1, x2)

            canvas.create_rectangle(                
                x1, espaco_topo, x2, espaco_topo + altura_barras, 
                fill='yellow', outline='black'
            )

        # Barra verde (faixa de carga máxima)
        if min_carga_max[i] is not None and max_carga_max[i] is not None:

            x1, x2 = valor_para_x(min_carga_max[i]), valor_para_x(max_carga_max[i])
            x1, x2 = faixa_com_largura(x1, x2)

            canvas.create_rectangle(
                x1, espaco_topo, x2, espaco_topo + altura_barras, 
                fill='green' if not flag_no_fl.get() else 'gray', outline='black'
            )

        # Função para desenhar marcador + label
        def marcador(valor):
            x = valor_para_x(valor)
            canvas.create_line(x, espaco_topo + altura_barras, x, espaco_topo + altura_barras + 20, arrow=tk.LAST)
            canvas.create_text(x, espaco_topo + altura_barras + 35, text=str(valor), font=('Arial', 10, 'bold'))

        # Desenhar marcadores
        for v in [0, min_operacao[i], min_carga_max[i], max_carga_max[i], max_operacao[i]]:
            if v is not None:
                marcador(v)

        # Legenda (na parte de baixo)
        legenda_y = espaco_topo + altura_barras + 60
        canvas.create_rectangle(50, legenda_y, 70, legenda_y + 15, fill='red', outline='black')
        canvas.create_text(80, legenda_y + 7, text="Fora da faixa", anchor='w', font=('Arial', 9))

        canvas.create_rectangle(200, legenda_y, 220, legenda_y + 15, fill='yellow', outline='black')
        canvas.create_text(230, legenda_y + 7, text="Faixa de operação", anchor='w', font=('Arial', 9))

        canvas.create_rectangle(400, legenda_y, 420, legenda_y + 15, fill='green' if not flag_no_fl.get() else 'gray', outline='black')
        canvas.create_text(430, legenda_y + 7, text="Carga máxima", anchor='w', font=('Arial', 9))

        linha_final = tk.Frame(aba[i], bg=bg_c)
        linha_final.pack(side="bottom", fill='x', padx=10, pady=(5, 10))

        # Texto informativo sobre strings
        qtd_strings = f"Quantidade máxima de Strings por MPPT: {mppt.get('q_s_mppt', 'N/A')}/{mppt.get('n_in_mppt', 'N/A')}"
        ttk.Label(linha_final, text=qtd_strings, style="h1.TLabel").pack(side="left", pady=(5,10))
    
        # Criação do botão que abre a Toplevel dos calculos
        btn_detalhes_mppt = ttk.Button(linha_final, text="Calculos")
        btn_detalhes_mppt.config(command=partial(open_detalhes_graficos, btn_detalhes_mppt, i))
        btn_detalhes_mppt.pack(side="right", pady=(5, 10), padx=10)

    q_mod = calculos_cc["inv"]["q_max_fl"] if vv(calculos_cc["inv"]["q_max_fl"]) and not flag_no_fl.get() else calculos_cc["inv"]["q_max_o"]
    p_sob = calculos_cc["inv"]["p_max_sb_fl"] if vv(calculos_cc["inv"]["p_max_sb_fl"]) and not flag_no_fl.get() else calculos_cc["inv"]["p_max_sb_o"]
    p_sob_per = calculos_cc["inv"]["p_max_sb_fl_per"] if vv(calculos_cc["inv"]["p_max_sb_fl_per"]) and not flag_no_fl.get() else calculos_cc["inv"]["p_max_sb_o_per"]

    # Atualização dos campos de saída
    frame_qtd_mod_inv.pack(before=notebook, fill='x', padx=30, pady=5)

    entry_modulos.config(state='normal')
    entry_modulos.delete(0, tk.END)
    entry_modulos.insert(0, str(q_mod))
    entry_modulos.config(state='readonly')

    entry_sobrecarga.config(state='normal')
    entry_sobrecarga.delete(0, tk.END)
    entry_sobrecarga.insert(0, f"{str(p_sob)} kW")
    entry_sobrecarga.config(state='readonly')

    entry_sobrecarga_percent.config(state='normal')
    entry_sobrecarga_percent.delete(0, tk.END)
    entry_sobrecarga_percent.insert(0, f"{str(p_sob_per)} %")
    entry_sobrecarga_percent.config(state='readonly')
##################################################################################################################################

# Janela auxiliar de detalhes dos inversores e módulos
def open_detalhes(me):
    eq = getattr(me, "eq", None)
    if eq not in ("inversor", "modulo"):
        messagebox.showerror("Erro", "Tipo de equipamento desconhecido.")
        return
    
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_close():
        # Reabilita o botão de chamada ao fechar
        me.config(state='normal')

        if detalhes.winfo_exists():
            detalhes.unbind("<MouseWheel>")

        unregister_toplevel(detalhes)
        detalhes.destroy()

    # Desabilita o botão de chamada
    me.config(state='disabled')

    detalhes = tk.Toplevel(root)
    detalhes.protocol("WM_DELETE_WINDOW", on_close)
    detalhes.iconphoto(False, icone)
    register_toplevel(detalhes, on_close)

    detalhes.configure(background=bg_c) 

    # Vincular evento de rolagem para a janela inteira (detalhes_inv)
    detalhes.bind("<MouseWheel>", _on_mousewheel)
    canvas = tk.Canvas(detalhes, takefocus=True)
    initial_focus = canvas
    scrollbar = ttk.Scrollbar(detalhes, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_c, padx=30)
    scrollable_frame.columnconfigure(0, weight=1)
    scrollable_frame.columnconfigure(1, weight=1)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )        
    canvas_window = canvas.create_window((0,0), window=scrollable_frame, anchor='nw')
    canvas.bind("<Configure>", lambda event: canvas.itemconfigure(canvas_window, width=event.width))
    canvas.configure(yscrollcommand=scrollbar.set, background=bg_c)
    canvas.pack(side='left', fill="both", expand=True)
    scrollbar.pack(side='right', fill='y')
    
    # caso o botão de chamada for identificado como o botão dos detalhes do inversor
    if  eq == "inversor":
        detalhes.title("Detalhes do Inversor")
        center_window(detalhes, 560, 700, min_width=460, min_height=480)

        if not inv_selec:
            messagebox.showinfo("Aviso", "Selecione um inversor.")
            on_close()
            return
        
        secoes_inv = [
    {
        "titulo": "Inversor",
        "subtitulo": None,
        "dados": [
            ("ID", "ID"),
            ("Fabricante", "MANUFACTURER_NAME"),
            ("Modelo", "MODEL"),
            ("Quantidade de MPPTs", "NUMBER_OF_TRACKERS"),
            ("Quantidade de Entradas", "NUMBER_OF_INPUTS"),
            ("Sobrecarga Admitida (%)", "OVERLOAD"),
            ("Sistema", "SYSTEM_TYPE")
        ],
        "fonte": "inv"
    },
    {
        "titulo": "Propriedades Elétricas",
        "subtitulo": "Dados de saída",
        "dados": [
            ("Potência de saída nominal (W)", "RATED_ACTIVE_POWER"),
            ("Potência de saída máx. (W)", "MAX_ACTIVE_POWER"),
            ("Tensão nominal (Vac)", "RATED_OUTPUT_VOLTAGE"),
            ("Corrente nominal (Aac)", "RATED_OUTPUT_CURRENT"),
            ("Corrente máx. (Aac)", "MAX_OUTPUT_CURRENT"),
            ("Configuração de Rede", "OUTPUT_MODE")
        ],
        "fonte": "inv"
    },
    {
        "titulo": None,
        "subtitulo": "MPPT",
        "dados": [
            ("Entradas por MPPT", "NUMBER_OF_INPUTS"),
            ("Tensão mín. de entrada (Vcc)", "MIN_STARTUP_VOLTAGE"),
            ("Tensão máx. de entrada (Vcc)", "MAX_INPUT_VOLTAGE"),
            ("Tensão mín. de oper. (Vcc)", "MIN_OPERATING_VOLTAGE"),
            ("Tensão máx. de oper. (Vcc)", "MAX_OPERATING_VOLTAGE"),
            ("Tensão mín. de Carga máx. (Vcc)", "MIN_FULL_LOAD_VOLTAGE"),
            ("Tensão máx. de Carga máx. (Vcc)", "MAX_FULL_LOAD_VOLTAGE"),
            ("Corr. de Curto-Circuito máx. (Acc)", "MAX_SHORT_CIRCUIT_CURRENT"),
            ("Corrente de oper. máx. (Acc)", "MAX_OPERATING_CURRENT"),
        ],
        "fonte": "mppt"
    },
    {
        "titulo": "Propriedades Mecânicas",
        "subtitulo": None,
        "dados": [
            ("Largura (mm)", "DIM_WIDTH"),
            ("Altura (mm)", "DIM_HEIGHT"),
            ("Profundidade (mm)", "DIM_DEPTH"),
            ("Peso (kg)", "DIM_WEIGHT"),
            ("Refrigeração", "COOLING_MODE"),
            ("Grau de Proteção", "PROTECTION_DEGREE")
        ],
        "fonte": "inv"
    }
]
        linha = 0

        for secao in secoes_inv:
            if secao["titulo"]:
                criar_label(scrollable_frame, secao["titulo"], linha, 0, style="h1", colspan=2)
                linha += 1
            if secao["subtitulo"] and secao["fonte"] != "mppt":
                criar_label(scrollable_frame, secao["subtitulo"], linha, 0, style="table", colspan=2)
                linha += 1

            if secao["fonte"] == "mppt":
                # Criar um Notebook
                notebook_mppt = ttk.Notebook(scrollable_frame, style="Detalhes.TNotebook")
                notebook_mppt.grid(row=linha, column=0, columnspan=2, sticky="nsew", pady=0, padx=0)
                initial_focus = notebook_mppt
                linha += 1

                for idx, mppt in enumerate(inv_selec["MPPT"]):
                    frame = tk.Frame(notebook_mppt, bg=bg_c, bd=0, highlightthickness=0)#, padx=0, pady=0)
                    frame.columnconfigure(0, weight=1)
                    frame.columnconfigure(1, weight=1)
                    notebook_mppt.add(frame, text=f"MPPT {format_mppt_display(mppt['MPPT_INDEX'])}")

                    for i, (label_txt, chave) in enumerate(secao["dados"]):
                        criar_label(frame, label_txt, i, 0, style="table")
                        valor = validar(mppt.get(chave, ""))
                        criar_label(frame, valor, i, 1, style="table")

                continue # Pula o resto do loop já que a MPPT foi tratada separadamente

            for label_txt, chave in secao["dados"]:
                criar_label(scrollable_frame, label_txt, linha, 0, style="table")

                if secao["fonte"] == "inv":
                    valor = validar(inv_selec[chave])
                else:
                    valor = "N/A"

                criar_label(scrollable_frame, valor, linha, 1, style="table")
                linha += 1

            #Espaço entre as Seções
            criar_label(scrollable_frame, "", linha, 0)
            linha += 1

    elif eq == "modulo":
        detalhes.title("Detalhes do Módulo")
        center_window(detalhes, 560, 700, min_width=460, min_height=480)
        # Desabilita o botão de chamada
        me.config(state='disabled') 

        if not mod_selec:
            messagebox.showinfo("Aviso", "Selecione um módulo.")
            on_close()
            return
        
        secoes_mod = [
    {
        "titulo": "Módulo",
        "fonte": "modulo",
        "labels": [
            ("ID", "ID"),
            ("Fabricante", "MANUFACTURER_NAME"),
            ("Modelo", "MODEL"),
            ("Material", "SOLAR_CELLS"),
            ("Célula", "CELL_TYPE"),
            ("Superfície", "SURFACE_TYPE"),
        ]
    },
    {
        "titulo": "Dados elétricos",
        "fonte": "modulo",
        "labels": [
            ("Potência Nominal (W)", "WP"),
            ("Voc (Vcc)", "VOC"),
            ("Isc (Acc)", "ISC"),
            ("Vmpp (Vcc)", "VMPP"),
            ("Impp (Acc)", "IMPP"),
        ]
    },
    {
        "titulo": "Coeficientes de Temperatura",
        "fonte": "modulo_raw",  # evitar validar coeficientes negativos
        "labels": [
            ("Coef. temp. PN (%/°C)", "COEF_PMAX"),
            ("Coef. temp. Voc (%/°C)", "COEF_VOC"),
            ("Coef. temp. Isc (%/°C)", "COEF_ISC"),
        ]
    },
    {
        "titulo": "Dados Mecânicos",
        "fonte": "modulo",
        "labels": [
            ("Largura (mm)", "DIM_WIDTH"),
            ("Altura (mm)", "DIM_HEIGHT"),
            ("Profundidade (mm)", "DIM_DEPTH"),
            ("Peso (kg)", "DIM_WEIGHT"),
        ]
    }
]
        linha = 0
        for secao in secoes_mod:
            if linha != 0:
                criar_label(scrollable_frame, "", linha, 0)
                linha += 1

            criar_label(scrollable_frame, secao["titulo"], linha, 0, style="h1" if linha == 0 else "table", colspan=2)
            linha += 1

            for nome_label, chave_dado in secao["labels"]:
                criar_label(scrollable_frame, nome_label, linha, 0, style="table")

                valor = mod_selec.get(chave_dado, "Não informado")
                if secao["fonte"] == "modulo":
                    valor = validar(valor)

                criar_label(scrollable_frame, valor, linha, 1, style="table")
                linha += 1    
    prepare_toplevel(detalhes, opener=me, initial=initial_focus, canvas=canvas)
##################################################################################################################################
        
# Abre janela com os gráficos da quantidades de strings a serem ligadas por MPPT e Quantidade máxima de módulos
def open_detalhes_graficos(me, indice_mppt):
    figuras = []

    # Ao fechar, destrói os gráficos
    def on_close():
        me.config(state="normal")
        for figura in figuras:
            plt.close(figura)
        unregister_toplevel(detalhes_graficos)
        detalhes_graficos.destroy()

    # Desabilita o botão de chamada

        # Desabilita o botão de chamada
    me.config(state='disabled')

    detalhes_graficos = tk.Toplevel(root)
    detalhes_graficos.iconphoto(False, icone)
    center_window(detalhes_graficos, 1100, 700, min_width=760, min_height=520)
    detalhes_graficos.protocol("WM_DELETE_WINDOW", on_close)
    detalhes_graficos.configure(background=bg_c)

    register_toplevel(detalhes_graficos, on_close)

    detalhes_graficos.title("Detalhes dos Limites")

    frame_titulo = tk.Frame(detalhes_graficos, bg=COLORS["surface"])
    frame_titulo.pack(side="top", fill="x", padx=12, pady=(10, 4))
    ttk.Label(
        frame_titulo,
        text=f"{inv_selec['MODEL']} | {mod_selec['MODEL']}",
        style="WindowTitle.TLabel",
    ).pack(pady=(6, 1))
    mppt_texto = format_mppt_display(calculos_cc["mppt"][indice_mppt]["mppt_index"])
    ttk.Label(frame_titulo, text=f"MPPT: {mppt_texto}", style="WindowSubtitle.TLabel").pack(pady=(1, 6))

    frame_conteudo = tk.Frame(detalhes_graficos, bg=bg_c)
    frame_conteudo.pack(side='top', fill='both', expand=True, padx=8, pady=(0, 8))
    frame_conteudo.grid_rowconfigure(0, weight=1)
    frame_conteudo.grid_columnconfigure(0, weight=1, uniform="graficos")
    frame_conteudo.grid_columnconfigure(1, weight=1, uniform="graficos")

    # Gráfico #1: Séries por MPPT
    entradas_por_mppt = {
        "Curto-circuito": calculos_cc["mppt"][indice_mppt]["n_max_sc_mppt"],
        "Entradas": calculos_cc["mppt"][indice_mppt]["n_in_mppt"],
        "Operação": calculos_cc["mppt"][indice_mppt]["n_max_o_mppt"]
    }

    ignorar_chave_iop = "Operação" if flag_no_iop.get() else None
    val_validos1 = [v for k, v in entradas_por_mppt.items() if k != ignorar_chave_iop and vv(v)]

    menor1 = min(val_validos1) if val_validos1 else None
    cores1 = []

    for k, v in entradas_por_mppt.items():
        if k == ignorar_chave_iop or not vv(v):
            cores1.append(COLORS["ignored"])
        elif menor1 is not None and v == menor1:
            cores1.append(COLORS["error"])
        else:
            cores1.append(COLORS["success"])

    fig1, ax1 = plt.subplots(figsize=(4, 3))
    figuras.append(fig1)
    valores_plot1 = [v if vv(v) and v >= 0 else 0 for v in entradas_por_mppt.values()]
    ax1.bar(entradas_por_mppt.keys(), valores_plot1, color=cores1, edgecolor=COLORS["border"], linewidth=1)

    for i, valor in enumerate(entradas_por_mppt.values()):
        texto = str(valor) if vv(valor) else "N/D"
        ax1.text(i, max(valores_plot1[i] * 0.5, 0.08), texto, ha='center', va='center', color='white', fontsize=10, weight='bold')
    
    style_chart(ax1, "Máximo de strings por MPPT", "Strings")
    add_chart_legend(ax1, cores1)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.set_xticks(range(len(entradas_por_mppt)))
    ax1.set_xticklabels(entradas_por_mppt.keys(), rotation=15, ha="right")
    try:
        fig1.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_conteudo)
        canvas1.draw()
        canvas1.get_tk_widget().configure(takefocus=True)
        canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=(4, 6), pady=4)
    except Exception as e:
        messagebox.showerror("Erro ao gerar gráfico", f"Detalhes: {e}")

    # Gráfico #2: Módulos
    q_max_raw_str = {
        "Circuito aberto": calculos_cc["mppt"][indice_mppt]["n_max_in"],
        "Operação": calculos_cc["mppt"][indice_mppt]["n_max_o"],
        "Carga máx": calculos_cc["mppt"][indice_mppt]["n_max_fl"]
        }

    q_max_modulos_str = {k: v for k, v in q_max_raw_str.items() if v != -1 and v is not None}

    ignorar_chave_fl = "Carga máx" if flag_no_fl.get() else None
    val_validos2 = [v for k, v in q_max_modulos_str.items() if k != ignorar_chave_fl]

    menor2 = min(val_validos2) if val_validos2 else None
    cores2 = []

    for k, v in q_max_modulos_str.items():
        if k == ignorar_chave_fl:
            cores2.append(COLORS["ignored"])
        elif menor2 is not None and v == menor2:
            cores2.append(COLORS["error"])
        else:
            cores2.append(COLORS["success"])

    fig2, ax2 = plt.subplots(figsize=(4, 3))
    figuras.append(fig2)
    ax2.bar(q_max_modulos_str.keys(), q_max_modulos_str.values(), color=cores2, edgecolor=COLORS["border"], linewidth=1)

    for i, (label, valor) in enumerate(zip(q_max_modulos_str.keys(), q_max_modulos_str.values())):
        ax2.text(i, valor * 0.5, str(valor), ha='center', va='center', color='white', fontsize=10, weight='bold')
    
    style_chart(ax2, "Quantidade máxima de módulos por string", "Módulos")
    add_chart_legend(ax2, cores2)
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax2.set_xticks(range(len(q_max_modulos_str)))
    ax2.set_xticklabels(q_max_modulos_str.keys(), rotation=15, ha="right")
    try:
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_conteudo)
        canvas2.draw()
        canvas2.get_tk_widget().configure(takefocus=True)
        canvas2.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(6, 4), pady=4)
    except Exception as e:
        messagebox.showerror("Erro ao gerar gráfico", f"Detalhes: {e}")
    prepare_toplevel(
        detalhes_graficos,
        opener=me,
        initial=canvas1.get_tk_widget() if "canvas1" in locals() else None,
    )
##################################################################################################################################

# Abre uma janela com os gráficos da quantidade de placas suportadas pelo inversor
def open_resumo_geral(me):
    figuras = []

    # Ao fechar, destrói os gráficos
    def on_close():
        me.config(state="normal")
        for figura in figuras:
            plt.close(figura)
        unregister_toplevel(resumo_geral)
        resumo_geral.destroy()

    # Desabilita o botão de chamada
    me.config(state='disabled')

    resumo_geral = tk.Toplevel(root)
    resumo_geral.iconphoto(False, icone)

    center_window(resumo_geral, 1180, 760, min_width=900, min_height=600)

    resumo_geral.protocol("WM_DELETE_WINDOW", on_close)
    resumo_geral.configure(background=bg_c)
    
    # Permite que linhas e colunas principais se expandam
    resumo_geral.grid_rowconfigure(1, weight=1)
    resumo_geral.grid_columnconfigure(0, weight=1)

    register_toplevel(resumo_geral, on_close)

    resumo_geral.title("Resumo Geral do Inversor")

    # Frame do título
    frame_titulo = tk.Frame(resumo_geral, bg=bg_c)
    frame_titulo.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
    ttk.Label(frame_titulo, text=f"{inv_selec['MODEL']} | {mod_selec['MODEL']}", style="WindowTitle.TLabel", anchor="center", justify="center").grid(row=0, column=0, sticky="ew", padx=10, pady=6)

    frame_titulo.grid_columnconfigure(0, weight=1)

    # Frame horizontal contendo gráfico e MPPTs
    frame_conteudo = tk.Frame(resumo_geral, bg=bg_c)
    frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=12, pady=(4, 12))

    frame_conteudo.grid_columnconfigure(0, weight=1)
    frame_conteudo.grid_columnconfigure(1, weight=0, minsize=340)
    frame_conteudo.grid_rowconfigure(0, weight=1)

    # Frame do gráfico principal
    frame_grafico = tk.Frame(frame_conteudo, bg=bg_c)
    frame_grafico.grid(row=0, column=0, sticky="nsew")

    q_max_raw_inv = {
        "Circuito aberto": calculos_cc["inv"]["n_max_in"],
        "Operação": calculos_cc["inv"]["n_max_o"],
        "Potência\nem sobrecarga": calculos_cc["inv"]["n_max_sb"],
        "Carga máx": calculos_cc["inv"]["n_max_fl"]
    }

    q_max_modulos_inv = {k: v for k, v in q_max_raw_inv.items() if v != -1 and v is not None}

    ignorar_chave_fl = "Carga máx" if flag_no_fl.get() else None
    val_validos = [v for k, v in q_max_modulos_inv.items() if k != ignorar_chave_fl]

    menor = min(val_validos) if val_validos else None
    cores = []

    for k, v in q_max_modulos_inv.items():
        if k == ignorar_chave_fl:
            cores.append(COLORS["ignored"])
        elif menor is not None and v == menor:
            cores.append(COLORS["error"])
        else:
            cores.append(COLORS["success"])

    legenda = []

    if COLORS["ignored"] in cores:
        legenda.append(Patch(facecolor=COLORS["ignored"], edgecolor=COLORS["border"], label="Faixa ignorada (Carga máx)"))
    if COLORS["error"] in cores:
        legenda.append(Patch(facecolor=COLORS["error"], edgecolor=COLORS["border"], label="Valor limitante"))
    if COLORS["success"] in cores:
        legenda.append(Patch(facecolor=COLORS["success"], edgecolor=COLORS["border"], label="Faixa válida"))

    fig, ax = plt.subplots(figsize=(5, 4))
    figuras.append(fig)
    ax.bar(q_max_modulos_inv.keys(), q_max_modulos_inv.values(), color=cores, edgecolor=COLORS["border"], linewidth=1)
    if legenda:
        ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, 1.0), frameon=False, ncol=len(legenda), fontsize=8)
    
    for i, (label, val) in enumerate(q_max_modulos_inv.items()):
        cor_texto = COLORS["text"] if cores[i] == COLORS["ignored"] else "white"
        ax.text(i, val*0.5, str(val), ha="center", va="center", color=cor_texto, fontsize=10, weight="bold")

    style_chart(ax, "Quantidade máxima de módulos por inversor", "Módulos")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xticks(range(len(q_max_modulos_inv)))
    ax.set_xticklabels(q_max_modulos_inv.keys(), rotation=15, ha="center")
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    canvas=FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().configure(takefocus=True)
    canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Frame com informações por MPPT
    frame_mppt = tk.Frame(frame_conteudo, bg=bg_c, bd=2, relief="groove")
    frame_mppt.grid(row=0, column=1, sticky="ns", padx=(12, 0), pady=4)

    # Informações Gerais
    # Título
    tk.Label(frame_mppt, text="Potência Máxima no Inversor", font=("Arial", 11, "bold"), bg=bg_c).pack(anchor="w", fill='x', padx=10)
    frame_info = tk.Frame(frame_mppt, bg=bg_c)
    frame_info.pack(anchor="w", padx=10)

    tk.Label(frame_info, text="Quantidade máxima de módulos:", bg=bg_c, font=("Arial", 10)).grid(row=0, column=0, sticky="w")
    tk.Label(frame_info, text=f"{calculos_cc["inv"]["q_max_fl"] if vv(calculos_cc["inv"]["q_max_fl"]) else calculos_cc["inv"]["q_max_o"]}", bg="#d9d9d9", font=("Arial", 10), width=10).grid(row=0, column=1, sticky="w", padx=(5, 0))

    tk.Label(frame_info, text="Sobrecarga admitida:", bg=bg_c, font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=2)
    tk.Label(frame_info, text=f"{calculos_cc["inv"]["p_max_sb_fl"] if vv(calculos_cc["inv"]["p_max_sb_fl"]) else calculos_cc["inv"]["p_max_sb_o"]} kW", bg="#d9d9d9", font=("Arial", 10), width=10).grid(row=1, column=1, sticky="w", padx=(5, 0))

    tk.Label(frame_info, text=f"{calculos_cc["inv"]["p_max_sb_fl_per"] if vv(calculos_cc["inv"]["p_max_sb_fl_per"]) else calculos_cc["inv"]["p_max_sb_o_per"]} %", bg="#d9d9d9", font=("Arial", 10), width=5).grid(row=1, column=2, sticky="w", padx=(5, 0))

    # Espaçamento
    ttk.Separator(frame_mppt, orient='horizontal').pack(fill='x', padx=10, pady=5)

    # Título
    tk.Label(frame_mppt, text="Resumo por MPPT", font=("Arial", 11, "bold"), bg=bg_c).pack(anchor="w", fill='x', padx=10)
    
    # Tabela: Módulos em Operação

    frame_op = tk.Frame(frame_mppt, bg=bg_c)
    frame_op.pack(fill='x', padx=10)

    tk.Label(frame_op, text="Módulos em Operação", font=("Arial", 10, "bold"), bg="#ffff33", pady=5).grid(row=0, column=0, columnspan=3, sticky="nsew", padx=1)
    tk.Label(frame_op, text="MPPT", width=10, font=("Arial", 10, "bold"), bg="#d9edf7", anchor="center").grid(row=1, column=0, sticky="nsew", padx=1)
    tk.Label(frame_op, text="Qtd. Módulos", width=10, font=("Arial", 10, "bold"), bg="#d9edf7").grid(row=1, column=1, sticky="nsew", padx=1)
    tk.Label(frame_op, text="Potência (kW)", width=12, font=("Arial", 10, "bold"), bg="#d9edf7").grid(row=1, column=2, sticky="nsew", padx=1)

    for i, mppt in enumerate(calculos_cc["mppt"]):
        bg = "#f0f8ff" if i % 2 == 0 else bg_c
        tk.Label(frame_op, text=format_mppt_display(mppt["mppt_index"]), bg=bg, anchor="center").grid(row=i+2, column=0, sticky="nsew", padx=1)
        tk.Label(frame_op, text=mppt["n_mod_o_mppt"], bg=bg, anchor="center").grid(row=i+2, column=1, sticky="nsew", padx=1)
        tk.Label(frame_op, text=f"{mppt['p_mod_o_mppt']:.1f}", bg=bg, anchor="center").grid(row=i+2, column=2, sticky="nsew", padx=1)

    # Espaçamento
    ttk.Separator(frame_mppt, orient='horizontal').pack(fill='x', padx=10, pady=5)

    # Tabela: Módulos em Carga Máxima

    frame_max = tk.Frame(frame_mppt, bg=bg_c)
    frame_max.pack(fill='x', padx=10)

    tk.Label(frame_max, text="Módulos em Carga Máxima", font=("Arial", 10, "bold"), bg="#009900", pady=5).grid(row=0, column=0, columnspan=3, sticky="nsew", padx=1)
    tk.Label(frame_max, text="MPPT", width=10, font=("Arial", 10, "bold"), bg="#d9edf7", anchor="center").grid(row=1, column=0, sticky="nsew", padx=1)
    tk.Label(frame_max, text="Qtd. Módulos", width=10, font=("Arial", 10, "bold"), bg="#d9edf7").grid(row=1, column=1, sticky="nsew", padx=1)
    tk.Label(frame_max, text="Potência (kW)", width=12, font=("Arial", 10, "bold"), bg="#d9edf7").grid(row=1, column=2, sticky="nsew", padx=1)

    for i, mppt in enumerate(calculos_cc["mppt"]):
        bg = "#f0f8ff" if i % 2 == 0 else bg_c
        tk.Label(frame_max, text=format_mppt_display(mppt["mppt_index"]), bg=bg, anchor="center").grid(row=i+2, column=0, sticky="nsew", padx=1)
        tk.Label(frame_max, text=mppt["n_mod_fl_mppt"] if vv(mppt["n_mod_fl_mppt"]) else "Não Informado", bg=bg, anchor="center").grid(row=i+2, column=1, sticky="nsew", padx=1)
        tk.Label(frame_max, text=f"{mppt["p_mod_fl_mppt"]:.1f}" if vv(mppt['p_mod_fl_mppt']) else "Não Informado", bg=bg, anchor="center").grid(row=i+2, column=2, sticky="nsew", padx=1)
    prepare_toplevel(resumo_geral, opener=me, initial=canvas.get_tk_widget())
##################################################################################################################################

# Atualização do aviso de prejuízo na geração
def atualizar_aviso():
    if flag_no_fl.get() or flag_no_iop.get():
        aviso.grid()
    else:
        aviso.grid_remove()
##################################################################################################################################

## Funções referentes ao funcionamento da janela ##

def center_window(
    window,
    width,
    height,
    min_width=None,
    min_height=None,
    vertical_offset=0,
    screen_margin=100,
):
    """Dimensiona e posiciona uma janela sem ultrapassar a área útil da tela."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width = min(width, max(320, screen_width - 80))
    height = min(height, max(240, screen_height - screen_margin))
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2 + vertical_offset)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.minsize(min_width or min(width, 420), min_height or min(height, 320))
    window.resizable(True, True)


def format_mppt_display(mppt_index):
    """Formata a identificação visual sem alterar a codificação dos MPPTs."""
    indices = mppt_index_dec(mppt_index)
    if indices:
        return formatar_tupla(indices)
    if mppt_index == 0:
        total = inv_selec.get("NUMBER_OF_TRACKERS")
        if vv(total) and total > 0:
            return "1" if total == 1 else f"1 a {total}"
    return "Não informado"


def register_toplevel(window, close_callback):
    """Registra uma janela auxiliar para fechamento coordenado da aplicação."""
    toplevels.append((window, close_callback))


def unregister_toplevel(window):
    """Remove referências a uma janela auxiliar já encerrada."""
    toplevels[:] = [(item, callback) for item, callback in toplevels if item is not window]


def style_chart(ax, title, ylabel="Quantidade"):
    """Aplica identidade visual e legibilidade consistentes aos gráficos."""
    ax.set_title(title, fontsize=12, fontweight="semibold", color=COLORS["text"], pad=16)
    ax.set_ylabel(ylabel, color=COLORS["muted"])
    ax.set_facecolor(COLORS["surface"])
    ax.grid(axis="y", color=COLORS["border"], linewidth=0.8, alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["border"])
    ax.spines["bottom"].set_color(COLORS["border"])


def add_chart_legend(ax, colors):
    """Explica a semântica das cores para que elas não sejam o único indicador."""
    labels = (
        ("error", "Valor limitante"),
        ("success", "Condição válida"),
        ("ignored", "Ignorado ou não informado"),
    )
    handles = [
        Patch(facecolor=COLORS[key], edgecolor=COLORS["border"], label=label)
        for key, label in labels
        if COLORS[key] in colors
    ]
    if handles:
        ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=8)


# Exemplo de build a partir de src/; o banco permanece externo ao bundle.
# O empacotamento oficial dos três aplicativos é definido no arquivo .spec da versão.

# Evento de fechamento da janela
def on_close_all():

    close_topLevels()
    root.destroy()
##################################################################################################################################

# Evento de fechamento das TopLevels
def close_topLevels():
    for janela, fechar in list(toplevels):
        try:
            if janela.winfo_exists():
                fechar()
        except tk.TclError:
            unregister_toplevel(janela)
################################################################################################################################## 

# Endereço dos arquivos

def resource_path(relative_path: str) -> str:
    """Resolve recursos internos tanto no código-fonte quanto no bundle PyInstaller."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return str((base_path / relative_path).resolve())

def external_path(filename: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = Path(__file__).resolve().parent
    return str((base_path / filename).resolve())

db_path = external_path("optimus_sun.db")
img_path = resource_path("optimus_sun.png")
icon_path = resource_path("optimus_sun.ico")
logo_path = resource_path("optimus_sun.png")

# Criar interface Tkinter
root = tk.Tk()
root.iconbitmap(icon_path)
root.title(f"Optimus Sun {APP_VERSION}")
root.configure(background=bg_c)
center_window(
    root,
    1180,
    720,
    min_width=960,
    min_height=600,
    vertical_offset=-50,
    screen_margin=65,
)

icone = tk.PhotoImage(file=logo_path)

# Estilos
style = ttk.Style()
style.theme_use("clam")

style.configure(".", font=(FONT_FAMILY, 10), background=bg_c, foreground=COLORS["text"])
style.configure("TFrame", background=bg_c)
style.configure("TNotebook", background=bg_c, bordercolor=COLORS["border"])
style.configure("TNotebook.Tab", background=COLORS["surface_alt"], padding=(12, 7))
style.map("TNotebook.Tab", background=[("selected", COLORS["surface"])], foreground=[("selected", COLORS["primary"])])
style.configure("Detalhes.TNotebook", background=bg_c, borderwidth=0, padding=0)
style.configure("Detalhes.TNotebook.Tab", padding=[5, 2], focuscolor=style.configure(".")["background"])
style.map("Detalhes.TNotebook.Tab", background=[("selected", COLORS["primary_soft"])])
style.configure("TLabel", padding=3, font=(FONT_FAMILY, 10), background=bg_c, foreground=COLORS["text"])
style.configure("h1.TLabel", padding=(4, 8), font=(FONT_FAMILY, 13, "bold"), foreground=COLORS["primary"])
style.configure("table.TLabel", padding=(8, 5), font=(FONT_FAMILY, 9), background=COLORS["surface"])
style.configure("WindowTitle.TLabel", padding=2, font=(FONT_FAMILY, 13, "bold"), background=COLORS["surface"], foreground=COLORS["primary"])
style.configure("WindowSubtitle.TLabel", padding=2, font=(FONT_FAMILY, 10), background=COLORS["surface"], foreground=COLORS["muted"])
style.configure("TCombobox", padding=4, font=(FONT_FAMILY, 10))
style.configure("TEntry", padding=4, font=(FONT_FAMILY, 10))
style.configure("TButton", padding=(10, 5), font=(FONT_FAMILY, 10))
style.configure("TCanvas", background=bg_c)
style.configure("TScrollbar", background=bg_c)
style.configure("TCheckbutton", font=(FONT_FAMILY, 10))
style.configure("Search.TNotebook", tabmargins=(0, 0, 0, 0))
style.configure("Search.TNotebook.Tab", padding=(18, 9), font=(FONT_FAMILY, 11, "bold"), anchor="center")
style.map("Search.TNotebook.Tab",
          background=[("selected", COLORS["primary_soft"]), ("!selected", COLORS["surface_alt"])],
          foreground=[("selected", COLORS["primary"]), ("!selected", COLORS["text"])])

# Mantém o carregamento legado dos dicionários, sem torná-lo requisito para busca.
carregar_fabricante()

frame_entrada = tk.Frame(root, bg=bg_c)                # Campos de Entrada
separador1 = ttk.Separator(root, orient="horizontal")         # Separador
results_shell = tk.Frame(root, bg=bg_c)
results_canvas = tk.Canvas(results_shell, bg=bg_c, highlightthickness=0)
results_scrollbar = ttk.Scrollbar(results_shell, orient="vertical", command=results_canvas.yview)
results_content = tk.Frame(results_canvas, bg=bg_c)
results_window = results_canvas.create_window((0, 0), window=results_content, anchor="nw")
results_canvas.configure(yscrollcommand=results_scrollbar.set)
results_content.bind("<Configure>", lambda _e: results_canvas.configure(scrollregion=results_canvas.bbox("all")))
results_canvas.bind("<Configure>", lambda event: results_canvas.itemconfigure(results_window, width=event.width))
results_shell.grid_columnconfigure(0, weight=1); results_shell.grid_rowconfigure(0, weight=1)
results_canvas.grid(row=0, column=0, sticky="nsew"); results_scrollbar.grid(row=0, column=1, sticky="ns")

def scroll_results(event):
    if event.widget.winfo_class() == "Treeview":
        return
    x, y = root.winfo_pointerxy()
    left, top = results_canvas.winfo_rootx(), results_canvas.winfo_rooty()
    if not (left <= x <= left + results_canvas.winfo_width() and top <= y <= top + results_canvas.winfo_height()):
        return
    delta = -1 if getattr(event, "delta", 0) > 0 else 1
    if getattr(event, "num", None) in (4, 5): delta = -1 if event.num == 4 else 1
    results_canvas.yview_scroll(delta, "units")
    return "break"

for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
    root.bind(sequence, scroll_results, add="+")
results_canvas.bind("<Button-1>", lambda _event: results_canvas.focus_set())
results_canvas.bind("<Prior>", lambda _event: results_canvas.yview_scroll(-1, "pages"))
results_canvas.bind("<Next>", lambda _event: results_canvas.yview_scroll(1, "pages"))
frame_qtd_mod_inv = tk.Frame(results_content, bg=bg_c)            # Informações de carga do inversor
notebook = ttk.Notebook(results_content)                                 # Campos de Saída
frame_img = tk.Frame(results_content, bg=bg_c)                    # Imagem do Optimus Sun
rodape = ttk.Label(root, text=f"Optimus Sun {APP_VERSION} — Pedro Akio Sakuma © 2025–2026", anchor='e', font=("Arial", 8)) # Label fixo no rodapé

frame_entrada.pack(fill="x", padx=16, pady=(8, 4))
separador1.pack(fill='x', padx=10, pady=5)
frame_qtd_mod_inv.pack(fill='x', padx=30, pady=5)
notebook.pack(fill='both', padx=10, pady=10)
results_shell.pack(expand=True, fill='both', padx=(10, 4))
frame_img.pack(fill='x', padx=30, pady=5)
rodape.pack(side="bottom", fill='x', pady=(5,3))

frame_entrada.grid_columnconfigure(0, weight=1)

# ----------------------------------- #
# ---------- frame_entrada ---------- #
# Variáveis compatíveis com os callbacks de cálculo existentes.
inversor_cb = tk.StringVar()
modulo_cb = tk.StringVar()
selected_inverter_title = tk.StringVar()
selected_inverter_details = tk.StringVar()
selected_module_title = tk.StringVar()
selected_module_details = tk.StringVar()
selected_inverter_title.set(format_selection_card("inverter", None)[0])
selected_inverter_details.set(format_selection_card("inverter", None)[1])
selected_module_title.set(format_selection_card("module", None)[0])
selected_module_details.set(format_selection_card("module", None)[1])
overload_session = OverloadSession()
overload_mode = tk.StringVar(value="registered")
custom_overload_text = tk.StringVar()
registered_overload_text = tk.StringVar(value="Cadastrada: nenhum inversor selecionado")
overload_effective_text = tk.StringVar(value="Valor efetivo: não disponível")


def sync_overload_controls():
    """Sincroniza widgets sem alterar o cadastro ou disparar cálculo."""
    has_inverter = bool(inv_selec)
    overload_mode.set(overload_session.mode)
    custom_overload_text.set(overload_session.custom_text)
    registered = overload_session.registered_percent
    registered_overload_text.set(
        f"Cadastrada: {registered:g}%" if valid_registered_percent(registered)
        else "Cadastrada: não informada"
    )
    state = "normal" if has_inverter else "disabled"
    registered_overload_radio.configure(state=state)
    custom_overload_radio.configure(state=state)
    custom_overload_entry.configure(state="normal" if has_inverter and overload_session.mode == "custom" else "disabled")
    try:
        effective = overload_session.effective_percent()
        overload_effective_text.set(f"Valor efetivo no próximo cálculo: {effective:g}%")
    except ValueError as error:
        overload_effective_text.set(f"Não calculado: {error}" if has_inverter else "Valor efetivo: não disponível")


def select_overload_mode(mode):
    overload_session.mode = mode
    overload_session.custom_text = custom_overload_text.get()
    sync_overload_controls()
    if mode == "registered" and mod_selec and inv_selec:
        carregar_dados(inversor_cb.get(), "")
    elif mode == "custom":
        close_topLevels()
        limpar_saidas()


def mark_custom_overload_dirty(_event=None):
    overload_session.custom_text = custom_overload_text.get()
    overload_effective_text.set("Valor personalizado alterado — pressione Enter para calcular.")
    close_topLevels()
    limpar_saidas()


def apply_custom_overload(_event=None):
    overload_session.custom_text = custom_overload_text.get()
    try:
        effective = overload_session.effective_percent()
    except ValueError as error:
        overload_effective_text.set(f"Não calculado: {error}")
        return
    overload_effective_text.set(f"Valor efetivo no próximo cálculo: {effective:g}%")
    if mod_selec and inv_selec:
        carregar_dados(inversor_cb.get(), "")


def selecionar_resultado_busca(row, equipamento):
    """Mantém seleção por Id e limpa somente o equipamento que saiu do filtro."""
    global inversores, modulos, inv_selec, mod_selec
    if row is None:
        if equipamento == "inversor":
            inversores = {}; inversor_cb.set(""); inv_selec = {}
            selected_inverter_title.set(format_selection_card("inverter", None)[0])
            selected_inverter_details.set(format_selection_card("inverter", None)[1])
            overload_session.clear(); sync_overload_controls()
            flag_no_iop.set(False); flag_no_fl.set(False)
            chk_iop.config(state="disabled"); chk_fl.config(state="disabled")
            detalhes_inv_btn.config(state="disabled")
        else:
            modulos = {}; modulo_cb.set(""); mod_selec = {}
            selected_module_title.set(format_selection_card("module", None)[0])
            selected_module_details.set(format_selection_card("module", None)[1])
            detalhes_mod_btn.config(state="disabled")
        limpar_saidas()
        return
    label = f"Id {row['ID']} — {row['MANUFACTURER']} — {row['MODEL']}"
    if equipamento == "inversor":
        inversores = {label: row["ID"]}; inversor_cb.set(label)
        title, details = format_selection_card("inverter", row)
        selected_inverter_title.set(title); selected_inverter_details.set(details)
        detalhes_inv_btn.config(state="normal")
    else:
        modulos = {label: row["ID"]}; modulo_cb.set(label)
        title, details = format_selection_card("module", row)
        selected_module_title.set(title); selected_module_details.set(details)
        detalhes_mod_btn.config(state="normal")
    calculated = carregar_dados(label, equipamento)
    search_visibility.after_selection(calculated, bool(inv_selec and mod_selec))


search_repository = EquipmentSearchRepository(db_path)
search_header = ttk.Frame(frame_entrada)
search_header.grid(row=0, column=0, sticky="ew", columnspan=4, padx=4)
search_header.columnconfigure(0, weight=1)
search_hint = ttk.Label(search_header, text="Pesquisa expandida — filtros e listas preservam seu estado.", foreground=COLORS["muted"])
search_hint.grid(row=0, column=0, sticky="w")
search_toggle_button = ttk.Button(search_header, text="Recolher pesquisa")
search_toggle_button.grid(row=0, column=1, sticky="e")

search_notebook = ttk.Notebook(frame_entrada, style="Search.TNotebook")
search_notebook.grid(row=1, column=0, sticky="nsew", columnspan=4, pady=(3, 0))
inverter_search = EquipmentSearchPanel(
    search_notebook, search_repository, "inverter",
    lambda row: selecionar_resultado_busca(row, "inversor"),
)
module_search = EquipmentSearchPanel(
    search_notebook, search_repository, "module",
    lambda row: selecionar_resultado_busca(row, "modulo"),
)
search_notebook.add(inverter_search, text="Inversores")
search_notebook.add(module_search, text="Módulos")


search_tab_width = None


def resize_search_tabs(event):
    global search_tab_width
    # O width das abas ttk é expresso em caracteres; o divisor mantém cada uma
    # próxima de metade da largura útil sem duplicar os painéis existentes.
    width = max(14, int((event.width - 24) / 15))
    if width != search_tab_width:
        search_tab_width = width
        style.configure("Search.TNotebook.Tab", width=width)


search_visibility = SearchVisibilityController(search_notebook, search_toggle_button, search_hint, lambda _expanded: root.update_idletasks())
search_notebook.bind("<Configure>", resize_search_tabs, add="+")

selection_summary = ttk.LabelFrame(frame_entrada, text="Equipamentos selecionados", padding=(7, 5))
selection_summary.grid(row=2, column=0, columnspan=4, sticky="ew", padx=4, pady=(6, 1))
selection_summary.columnconfigure(0, weight=1, uniform="selection"); selection_summary.columnconfigure(1, weight=1, uniform="selection")

inverter_card = tk.Frame(selection_summary, bg="#E8F0F8", highlightbackground="#4F779F", highlightthickness=1)
inverter_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
tk.Frame(inverter_card, bg="#4F779F", width=5).pack(side="left", fill="y")
inverter_card_body = tk.Frame(inverter_card, bg="#E8F0F8"); inverter_card_body.pack(side="left", fill="both", expand=True, padx=8, pady=5)
inverter_card_body.columnconfigure(0, weight=1)
tk.Label(inverter_card_body, textvariable=selected_inverter_title, bg="#E8F0F8", fg=COLORS["text"], font=(FONT_FAMILY, 10, "bold"), anchor="w").grid(row=0, column=0, sticky="ew")
tk.Label(inverter_card_body, textvariable=selected_inverter_details, bg="#E8F0F8", fg=COLORS["muted"], font=(FONT_FAMILY, 9), anchor="w").grid(row=1, column=0, sticky="ew")

module_card = tk.Frame(selection_summary, bg="#F0EDF7", highlightbackground="#76639A", highlightthickness=1)
module_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
tk.Frame(module_card, bg="#76639A", width=5).pack(side="left", fill="y")
module_card_body = tk.Frame(module_card, bg="#F0EDF7"); module_card_body.pack(side="left", fill="both", expand=True, padx=8, pady=5)
module_card_body.columnconfigure(0, weight=1)
tk.Label(module_card_body, textvariable=selected_module_title, bg="#F0EDF7", fg=COLORS["text"], font=(FONT_FAMILY, 10, "bold"), anchor="w").grid(row=0, column=0, sticky="ew")
tk.Label(module_card_body, textvariable=selected_module_details, bg="#F0EDF7", fg=COLORS["muted"], font=(FONT_FAMILY, 9), anchor="w").grid(row=1, column=0, sticky="ew")

# Condições de funcionamento do inversor
calculation_settings = ttk.Frame(frame_entrada)
calculation_settings.grid(row=3, column=0, columnspan=4, sticky="ew", padx=4, pady=(3, 0))
calculation_options = ttk.LabelFrame(calculation_settings, text="Opções de cálculo", padding=(7, 4))
calculation_options.columnconfigure(0, weight=1); calculation_options.columnconfigure(1, weight=1)

# Ignorar corrente de operação
flag_no_iop = tk.BooleanVar(value=False)
chk_iop = tk.Checkbutton(calculation_options, text="  Ignorar corrente de operação", variable=flag_no_iop, onvalue=True, offvalue=False, bg=bg_c, activebackground=bg_c, selectcolor=COLORS["primary_soft"], font=(FONT_FAMILY, 10), anchor="w", padx=5, pady=4, takefocus=True, state='disabled')
chk_iop.grid(row=0, column=0, sticky="ew", padx=(0, 6))
chk_iop.config(command=lambda: carregar_dados(inversor_cb.get(), ""))

# Ignorar faixa de carga máxima
flag_no_fl = tk.BooleanVar(value=False)
chk_fl = tk.Checkbutton(calculation_options, text="  Ignorar faixa de carga máxima", variable=flag_no_fl, onvalue=True, offvalue=False, bg=bg_c, activebackground=bg_c, selectcolor=COLORS["primary_soft"], font=(FONT_FAMILY, 10), anchor="w", padx=5, pady=4, takefocus=True, state='disabled')
chk_fl.grid(row=0, column=1, sticky="ew", padx=(6, 0))
chk_fl.config(command=lambda: carregar_dados(inversor_cb.get(), ""))

# Botão de detalhes do inversor
detalhes_inv_btn = ttk.Button(inverter_card_body, text="Detalhes do inversor", command=lambda: open_detalhes(detalhes_inv_btn), state="disabled")
detalhes_inv_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(8, 0))
detalhes_inv_btn.eq = "inversor"

# Botão de detalhes do modulo
detalhes_mod_btn = ttk.Button(module_card_body, text="Detalhes do módulo", command=lambda: open_detalhes(detalhes_mod_btn), state="disabled")
detalhes_mod_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(8, 0))
detalhes_mod_btn.eq = "modulo"

overload_frame = ttk.LabelFrame(calculation_settings, text="Sobrecarga usada no cálculo", padding=(7, 4))
registered_overload_radio = ttk.Radiobutton(overload_frame, text="Usar sobrecarga cadastrada", variable=overload_mode, value="registered", command=lambda: select_overload_mode("registered"), state="disabled")
registered_overload_radio.grid(row=0, column=0, sticky="w")
ttk.Label(overload_frame, textvariable=registered_overload_text).grid(row=0, column=1, sticky="w", padx=(5, 18))
custom_overload_radio = ttk.Radiobutton(overload_frame, text="Personalizar sobrecarga (%)", variable=overload_mode, value="custom", command=lambda: select_overload_mode("custom"), state="disabled")
custom_overload_radio.grid(row=0, column=2, sticky="w")
custom_overload_entry = ttk.Entry(overload_frame, textvariable=custom_overload_text, width=10, state="disabled")
custom_overload_entry.grid(row=0, column=3, sticky="w", padx=5)
bind_overload_entry(custom_overload_entry, mark_custom_overload_dirty, apply_custom_overload)
ttk.Label(overload_frame, textvariable=overload_effective_text).grid(row=1, column=0, columnspan=4, sticky="w", pady=(3, 0))


calculation_layout_mode = None


def layout_calculation_settings(event=None):
    global calculation_layout_mode
    width = event.width if event is not None else calculation_settings.winfo_width()
    mode = "side" if width >= 1180 else "stacked"
    if mode == calculation_layout_mode:
        return
    calculation_layout_mode = mode
    overload_frame.grid_forget(); calculation_options.grid_forget()
    if mode == "side":
        calculation_settings.columnconfigure(0, weight=3); calculation_settings.columnconfigure(1, weight=2)
        overload_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        calculation_options.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
    else:
        calculation_settings.columnconfigure(0, weight=1); calculation_settings.columnconfigure(1, weight=0)
        overload_frame.grid(row=0, column=0, sticky="ew")
        calculation_options.grid(row=1, column=0, sticky="ew", pady=(4, 0))


calculation_settings.bind("<Configure>", layout_calculation_settings, add="+")
layout_calculation_settings()
# ---------- frame_entrada ---------- #
# ----------------------------------- #

# -------- frame_qtd_mod_inv -------- #
# ----------------------------------- #
ttk.Label(frame_qtd_mod_inv, text="Potência máxima no inversor", style="h1.TLabel").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')
btn_resumo_geral = ttk.Button(frame_qtd_mod_inv, text="Gráfico e cálculos", command=lambda: open_resumo_geral(btn_resumo_geral))
ttk.Label(frame_qtd_mod_inv, text="Qtd. máx. de módulos:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
entry_modulos = ttk.Entry(frame_qtd_mod_inv, width=10, state="readonly")
ttk.Label(frame_qtd_mod_inv, text="Sobrecarga admitida:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
entry_sobrecarga = ttk.Entry(frame_qtd_mod_inv, width=10, state="readonly")
entry_sobrecarga_percent = ttk.Entry(frame_qtd_mod_inv, width=10, state="readonly")
aviso = tk.Label(frame_qtd_mod_inv, text="ATENÇÃO:\nA geração do sistema\npode ser comprometida!",
                 fg="red", bg=bg_c, font=("Trebuchet MS", 12, "bold"), justify="center")

frame_qtd_mod_inv.grid_columnconfigure(3, weight=1)

btn_resumo_geral.grid(row=1, column=4, rowspan=2, padx=12, pady=5, sticky="ns")
entry_modulos.grid(row=1, column=1, padx=5, pady=5)
entry_sobrecarga.grid(row=2, column=1, padx=5, pady=5)
entry_sobrecarga_percent.grid(row=2, column=2, padx=5, pady=5)
aviso.grid(row=0, column=5, rowspan=3, padx=12, pady=5, sticky="e")
aviso.grid_remove()

# -------- frame_qtd_mod_inv -------- #
# ----------------------------------- #

# ----------------------------------- #
# ------------ frame_img ------------ #
logo = Image.open(img_path)
logo_redim = logo.copy()
logo_redim.thumbnail((48, 48), Image.Resampling.LANCZOS)
img = ImageTk.PhotoImage(logo_redim)

label_img = tk.Label(frame_img, image=img, bg=bg_c)
label_img.image = img
label_img.pack(fill='x')
# ------------ frame_img ------------ #
# ----------------------------------- #

frame_qtd_mod_inv.pack_forget()

root.protocol("WM_DELETE_WINDOW", on_close_all)

print(r"""
                                               ;   :   ;
                                            .   \_,!,_/   ,
                                             `.,'     `.,'
                                              /         \
                                        ~ -- :           : -- ~ 
                 OPTIMUS SUN
                    v2.6.0
""")
##################################################################################################################################

root.mainloop()
