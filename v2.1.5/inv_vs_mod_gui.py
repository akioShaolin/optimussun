#inv_vs_mod_gui.py
#                                                                       ;   :   ;
#                                                                    .   \_,!,_/   ,
#                                                                     `.,'     `.,'
#                                                                      /         \
#                                                                ~ -- :           : -- ~
#   ██████╗ ██████╗ ████████╗██╗███╗   ███╗██╗   ██╗███████╗    ███████╗██╗   ██╗███╗   ██╗    ██╗   ██╗██████╗     ██╗   ███████╗
#  ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗ ████║██║   ██║██╔════╝    ██╔════╝██║   ██║████╗  ██║    ██║   ██║╚════██╗   ███║   ██╔════╝
#  ██║   ██║██████╔╝   ██║   ██║██╔████╔██║██║   ██║███████╗    ███████╗██║   ██║██╔██╗ ██║    ██║   ██║ █████╔╝   ╚██║   ███████╗
#  ██║   ██║██╔═══╝    ██║   ██║██║╚██╔╝██║██║   ██║╚════██║    ╚════██║██║   ██║██║╚██╗██║    ╚██╗ ██╔╝██╔═══╝     ██║   ╚════██║
#  ╚██████╔╝██║        ██║   ██║██║ ╚═╝ ██║╚██████╔╝███████║    ███████║╚██████╔╝██║ ╚████║     ╚████╔╝ ███████╗██╗ ██║██╗███████║
#   ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝    ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝      ╚═══╝  ╚══════╝╚═╝ ╚═╝╚═╝╚══════╝
#   
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

import sqlite3
import tkinter as tk
import matplotlib.pyplot as plt
import math
import os
import sys

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from optimus_lib import compensacao_termica, validar, vv

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
                "q_s_mppt": None                            # Escolhe o valor menor entre n_in_mppt, n_max_sc_mppt e n_max_o_mppt
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
        "t_cell_max": 50,                                       # Temperatura mínima
        "t_cell_min": 10                                        # Temperatura máxima
        },
    # Dados de tolerância
    "tol": 
        {
            "pot": 0.005,                                       # Tolerância do calculo de potência
            "op_i": 0.1                                         # Tolerância no calculo de corrente de operação
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

        cell_frame = tk.Frame(container, borderwidth=1, relief="solid", padx=None, pady=None, background="#e6f2ff")
        cell_frame.grid(row=linha, column=coluna, columnspan=colspan, sticky="nsew")
        label = ttk.Label(cell_frame, text=texto, justify='left', anchor='w', wraplength=200, style="table.TLabel").grid(row=0, column=0, sticky="w")

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
        conexao = sqlite3.connect(resource_path("optimus_sun.db"))
        cursor = conexao.cursor()
        
        # Carregar fabricantes dos inversores
        cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (0, 2)")
        fab_inversor = {row[1]: row[0] for row in cursor.fetchall()} # {Nome : ID}
        
        # Carregar fabricantes dos módulos
        cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (1, 2)")
        fab_modulo = {row[1]: row[0] for row in cursor.fetchall()} # {Nome : ID}
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao carregar fabricantes: \n{e}")

    finally:
        conexao.close()
##################################################################################################################################

# Busca modelos com base no fabricante selecionado
def carregar_modelo(fab_nome, equipamento):

    global inversores, modulos
    global inv_selec, mod_selec, calculos_cc

    try:
        conexao = sqlite3.connect(resource_path("optimus_sun.db"))
        cursor = conexao.cursor()
        
        limpar_saidas()
        frame_img.pack(fill='x', padx=30, pady=5)

        if equipamento == "inversor":
            # Limpa a variável inv_selec
            inv_selec = {}

            # Adiciona os modelos de inversores do fabricante selecionado
            fab_id = fab_inversor.get(fab_nome)
            cursor.execute("SELECT ID, MODEL FROM inverter WHERE MANUFACTURER_ID = ?",(fab_id, ))
            inversores = {row[1]: row[0] for row in cursor.fetchall()}
            inversor_cb["values"] = list(inversores.keys())
            inversor_cb.set("")

        elif equipamento == "modulo": 
            # Limpa a varíavel mod_selec
            mod_selec = {}

            # Adiciona os modelos de módulos do fabricante selecionado
            fab_id = fab_modulo.get(fab_nome)
            cursor.execute("SELECT ID, MODEL FROM module WHERE MANUFACTURER_ID = ?", (fab_id, ))
            modulos = {row[1]: row[0] for row in cursor.fetchall()}
            modulo_cb["values"] = list(modulos.keys())
            modulo_cb.set("")
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao carregar modelos: \n{e}")
    finally:        
        conexao.close()
##################################################################################################################################

# Ao selecionar o inversor ou módulo, este código solicita os dados ao database
def carregar_dados(modelo, equipamento):
    
    global mod_selec, inv_selec
    global calculos_cc

    # Conecta ao banco de dados para solicitar os dados do inversor e MPPT
    try:
        conexao = sqlite3.connect(resource_path("optimus_sun.db"))
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
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao carregar dados do {equipamento}:\n{e}")
    finally:
        conexao.close()
    ##########
    
    # Verifica se as variáveis de inversor e módulos estão preenchidas para fazer os calculos
    if mod_selec and inv_selec:
        
# -------- Calculos dos Módulos --------

        # Oculta a imagem do logo da Ecopower
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
                "n_in_mppt": mppt["NUMBER_OF_INPUTS"],
                "max_i_v" : mppt["MAX_INPUT_VOLTAGE"],
                "min_i_v" : mppt["MIN_STARTUP_VOLTAGE"],
                "max_o_v" : mppt["MAX_OPERATING_VOLTAGE"],
                "min_o_v" : mppt["MIN_OPERATING_VOLTAGE"],
                "max_fl_v" : mppt["MAX_FULL_LOAD_VOLTAGE"],
                "min_fl_v" : mppt["MIN_FULL_LOAD_VOLTAGE"],
                "max_sc_i" : mppt["MAX_SHORT_CIRCUIT_CURRENT"],
                "max_o_i" : mppt["MAX_OPERATING_CURRENT"],
                "mppt_index": mppt["MPPT_INDEX"],
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
                "q_s_mppt": None 
            })

        for i in range(len(calculos_cc["mppt"])):

            print(f"""
            MPPT {i+1}

            Input Voltage Range: {calculos_cc["mppt"][i]["min_i_v"]:.2f}, {calculos_cc["mppt"][i]["max_i_v"]:.2f}
            Operating Voltage Range: {calculos_cc["mppt"][i]["min_o_v"]:.2f}, {calculos_cc["mppt"][i]["max_o_v"]:.2f}
            Full Load Voltage Range: {calculos_cc["mppt"][i]["min_fl_v"]:.2f}, {calculos_cc["mppt"][i]["max_fl_v"]:.2f}
            Max Short Circuit Current: {calculos_cc["mppt"][i]["max_sc_i"]:.2f}
            Max Operating Current:  {calculos_cc["mppt"][i]["max_o_i"]:.2f}

                """)

            # Calcular quantidades máximas de módulos e entradas do MPPT para compatibilidade entre equipamentos 
            if vv(calculos_cc["mppt"][i]["max_sc_i"], calculos_cc["mod"]["impp_max"]):
                calculos_cc["mppt"][i]["n_max_sc_mppt"] = math.trunc(calculos_cc["mppt"][i]["max_sc_i"]/calculos_cc["mod"]["isc_max"])
            else:
                calculos_cc["mppt"][i]["n_max_sc_mppt"] = -1

            if vv(calculos_cc["mppt"][i]["max_o_i"], calculos_cc["mod"]["impp_max"]):
                calculos_cc["mppt"][i]["n_max_o_mppt"] = math.trunc(calculos_cc["mppt"][i]["max_o_i"] * (1 + calculos_cc["tol"]["op_i"]) / calculos_cc["mod"]["impp_max"])
            else:
                calculos_cc["mppt"][i]["n_max_o_mppt"] = -1
            
            # Variável temporária para calcular q_s_mppt

            q_s_mppt = [
                calculos_cc["mppt"][i]["n_in_mppt"],
                calculos_cc["mppt"][i]["n_max_sc_mppt"],
                calculos_cc["mppt"][i]["n_max_o_mppt"]
            ]

            # Filtra apenas os valores válidos (≠ -1 e ≠ None)
            if [v for v in q_s_mppt if v != -1 and v is not None]:
                calculos_cc["mppt"][i]["q_s_mppt"] = min(q_s_mppt)
            else:
                calculos_cc["mppt"][i]["q_s_mppt"] = -1

            # Se o valor for 0, o programa nem perde tempo calculando as quantidades de módulos compatíveis
            if (calculos_cc["mppt"][i]["q_s_mppt"] > 0 and vv(calculos_cc["mppt"][i]["q_s_mppt"])):
                if vv(calculos_cc["mppt"][i]["min_i_v"], calculos_cc["mod"]["voc_min"], calculos_cc["mppt"][i]["max_i_v"], calculos_cc["mod"]["voc_max"]):
                    calculos_cc["mppt"][i]["n_min_in"] = math.ceil(calculos_cc["mppt"][i]["min_i_v"]/calculos_cc["mod"]["voc_min"])
                    calculos_cc["mppt"][i]["n_max_in"] = math.trunc(calculos_cc["mppt"][i]["max_i_v"]/calculos_cc["mod"]["voc_max"])
                else:
                    calculos_cc["mppt"][i]["n_min_in"] = -1
                    calculos_cc["mppt"][i]["n_max_in"] = -1
                    
                if vv(calculos_cc["mppt"][i]["min_o_v"], calculos_cc["mod"]["vmpp_min"], calculos_cc["mppt"][i]["max_o_v"], calculos_cc["mod"]["vmpp_max"]):
                    calculos_cc["mppt"][i]["n_min_o"] = math.ceil(calculos_cc["mppt"][i]["min_o_v"]/calculos_cc["mod"]["vmpp_min"])
                    calculos_cc["mppt"][i]["n_max_o"] = math.trunc(calculos_cc["mppt"][i]["max_o_v"]/calculos_cc["mod"]["vmpp_max"])
                else:
                    calculos_cc["mppt"][i]["n_min_o"] = -1
                    calculos_cc["mppt"][i]["n_max_o"] = -1

                if vv(calculos_cc["mppt"][i]["min_fl_v"], calculos_cc["mod"]["vmpp_min"], calculos_cc["mppt"][i]["max_fl_v"], calculos_cc["mod"]["vmpp_max"]):
                    calculos_cc["mppt"][i]["n_min_fl"] = math.ceil(calculos_cc["mppt"][i]["min_fl_v"]/calculos_cc["mod"]["vmpp_min"])
                    calculos_cc["mppt"][i]["n_max_fl"] = math.trunc(calculos_cc["mppt"][i]["max_fl_v"]/calculos_cc["mod"]["vmpp_max"])
                else:
                    calculos_cc["mppt"][i]["n_min_fl"] = -1
                    calculos_cc["mppt"][i]["n_max_fl"] = -1

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
            else:
                calculos_cc["mppt"][i]["q_min_o"] = -1
                calculos_cc["mppt"][i]["q_max_o"] = -1
            
            if vv(calculos_cc["mppt"][i]["q_min_o"], calculos_cc["mppt"][i]["q_max_o"], calculos_cc["mppt"][i]["n_min_fl"], calculos_cc["mppt"][i]["n_max_fl"]):
                calculos_cc["mppt"][i]["q_min_fl"] = max(calculos_cc["mppt"][i]["n_min_in"], calculos_cc["mppt"][i]["n_min_o"], calculos_cc["mppt"][i]["n_min_fl"])
                calculos_cc["mppt"][i]["q_max_fl"] = min(calculos_cc["mppt"][i]["n_max_in"], calculos_cc["mppt"][i]["n_max_o"], calculos_cc["mppt"][i]["n_max_fl"])
            else:
                calculos_cc["mppt"][i]["q_min_fl"] = -1
                calculos_cc["mppt"][i]["q_max_fl"] = -1

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
        calculos_cc["inv"]["sb"] = inv_selec["OVERLOAD"] / 100      # Calculo em porcentagem
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

                try:
                    calculos_cc["inv"]["n_max_sb"] = math.trunc(calculos_cc["inv"]["pn"] * (1 + calculos_cc["inv"]["sb"]) * (1 + calculos_cc["tol"]["pot"]) / calculos_cc["mod"]["p_nom"])
                except (ZeroDivisionError, TypeError, KeyError):
                    calculos_cc["inv"]["n_max_sb"] = 0

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
                    
        def mod_max(n):
            if n % 5 == 0:
                return n + 5
            return n + (5 - (n % 5))

        faixa_de_funcionamento(
            container=frame_grafico,
            min_operacao=calculos_cc["mppt"][0]["q_min_o"] if vv(calculos_cc["mppt"][0]["q_min_o"]) else None,
            max_operacao=calculos_cc["mppt"][0]["q_max_o"] if vv(calculos_cc["mppt"][0]["q_max_o"]) else None,
            min_carga_max=calculos_cc["mppt"][0]["q_min_fl"] if vv(calculos_cc["mppt"][0]["q_min_fl"]) else None,
            max_carga_max=calculos_cc["mppt"][0]["q_max_fl"] if vv(calculos_cc["mppt"][0]["q_max_fl"]) else None,
            valor_maximo=mod_max(calculos_cc["mppt"][0]["q_max_o"])
        )

        frame_qtd_modulos.pack(after=separador2, fill="x", padx=30, pady=5)

        entry_series.config(state='normal')
        entry_series.delete(0, tk.END)
        entry_series.insert(0, str(calculos_cc["mppt"][0]["q_s_mppt"] if vv(calculos_cc["mppt"][0]["q_s_mppt"]) else "N/A"))
        entry_series.config(state='readonly')

        entry_modulos.config(state='normal')
        entry_modulos.delete(0, tk.END)
        entry_modulos.insert(0, str(calculos_cc["inv"]["q_max_fl"] if vv(calculos_cc["inv"]["q_max_fl"]) else calculos_cc["inv"]["q_max_o"]))
        entry_modulos.config(state='readonly')

        entry_sobrecarga.config(state='normal')
        entry_sobrecarga.delete(0, tk.END)
        entry_sobrecarga.insert(0, f"{str(calculos_cc["inv"]["p_max_sb_fl"] if vv(calculos_cc["inv"]["p_max_sb_fl"]) else calculos_cc["inv"]["p_max_sb_o"])} kW")
        entry_sobrecarga.config(state='readonly')

        entry_sobrecarga_percent.config(state='normal')
        entry_sobrecarga_percent.delete(0, tk.END)
        entry_sobrecarga_percent.insert(0, f"{str(calculos_cc["inv"]["p_max_sb_fl_per"] if vv(calculos_cc["inv"]["p_max_sb_fl_per"]) else calculos_cc["inv"]["p_max_sb_o_per"])} %")
        entry_sobrecarga_percent.config(state='readonly')

        print(calculos_cc)
##################################################################################################################################

# Exibe os dados dos MPPTs diferentes em guias separadas
def exibir_mppt_gui(notebook, mppts_data):
    """
    Cria uma guia no Notebook para cada MPPT, com os cados e gráficos correspondentes.
    mppt_data: Lista de dicionários, cada um com dados de um MPPT
    """
    for i, mppt in enumerate(mppts_data):
        aba = ttk.Frame(notebook)
        notebook.add(aba, text=f"MPPT {i + 1}")

        frame_topo = ttk.Frame(aba)
        frame_topo.pack(pady=1, padx=10, fill="x")

        #informações do MPPT
        info = ""
        info += f"Entradas por MPPT: {mppt.get('n_in_mppt', 'N/A')}\n"

        if vv(mppt.get("n_max_sc_mppt")):
            info += f"Máx. séries por corrente de curto: {mppt["n_max_sc_mppt"]}\n"
        else:
            info += "Máx. séries por corrente de curto: Não informado\n"

        if vv(mppt.get("n_max_o_mppt")):
            info += f"Máx. séries por corrente de operação: {mppt["n_max_o_mppt"]}\n"
        else:
            info += "Máx. séries por corrente de operação: Não informado\n"

        ttk.Label(frame_topo, text=info, justify='left').pack(anchor='w')

        # Gráfico
        if vv(mppt.get("n_in_mppt"), mppt.get("n_max_sc_mppt"), mppt.get("n_max_o_mppt")):
            fig, ax = plt.subplots(figsize=(4, 3))
            dados = {
                "Entradas": mppt["n_in_mppt"],
                "Curto": mppt["n_max_sc_mppt"],
                "Operação": mppt["n_max_o_mppt"]
            }

            menor = min(dados.values())
            cores = ["red" if v == menor else "blue" for v in dados.values()]
            ax.bar(dados.keys(), dados.values(), color=cores)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            for i, (k, v) in enumerate(dados.items()):
                ax.text(i, v * 0.5, str(v), ha='center', va='center', color='white')
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=aba)
            canvas.draw()
            canvas.get_tk_widget().pack()(pady=10)
        else:
            ttk.Label(aba, txt="Dados insuficientes para gerar gráfico.", foreground="gray").pack(pady=10)
##################################################################################################################################

# Abre janela com os gráficos da quantidades de strings a serem ligadas por MPPT e Quantidade máxima de módulos
def open_detalhes_graficos(me):

    # Ao fechar, destrói os gráficos
    def on_close():
        me.config(state="normal")
        plt.close('all')
        if detalhes_graficos in toplevels:
            toplevels.remove(detalhes_graficos)

        detalhes_graficos.destroy()

    # Desabilita o botão de chamada
    me.config(state='disabled')

    detalhes_graficos = tk.Toplevel(root)
    detalhes_graficos.protocol("WM_DELETE_WINDOW", on_close)
    detalhes_graficos.configure(background="#e6f2ff")

    toplevels.append((detalhes_graficos, on_close))

    detalhes_graficos.title("Detalhes dos Limites")
    detalhes_graficos.geometry("1000x400")

    frame_titulo = tk.Frame(detalhes_graficos, bg="#e6f2ff")
    frame_titulo.pack(side="top", fill="both", expand=True)
    ttk.Label(frame_titulo, text=f"{inv_selec["MODEL"]}\t | \t{mod_selec["MODEL"]}", font=('Arial', 12, 'bold')).pack()

    frame_limites = tk.Frame(detalhes_graficos, bg="#e6f2ff")
    frame_limites.pack(side='top', fill='both', expand=True)

    # Gráfico #1: Séries por MPPT
    entradas_por_mppt = {
        "N° de Entradas": calculos_cc["mppt"][0]["n_in_mppt"],
        "Corrente\nde curto circuito": calculos_cc["mppt"][0]["n_max_sc_mppt"],
        "Corrente\nde operação": calculos_cc["mppt"][0]["n_max_o_mppt"]
    }

    menor1 = min(entradas_por_mppt.values())
    cores1 = ["red" if val == menor1 else "blue" for val in entradas_por_mppt.values()]
    fig1, ax1 = plt.subplots(figsize=(4, 3))
    ax1.bar(entradas_por_mppt.keys(), entradas_por_mppt.values(), color=cores1)

    for i, (label, valor) in enumerate(zip(entradas_por_mppt.keys(), entradas_por_mppt.values())):
        ax1.text(i, valor * 0.5, str(valor), ha='center', va='center', color='white', fontsize=10, weight='bold')
    
    ax1.set_title("Máximo de strings por MPPT", pad=15)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    try:
        fig1.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_limites)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side='left', fill='both', padx=10, pady=10, expand=True)
    except Exception as e:
        messagebox.showerror("Erro ao gerar gráfico", f"Detalhes: {e}")

    # Gráfico #2: Módulos
    q_max_raw_str = {
        "Circuito aberto": calculos_cc["mppt"][0]["n_max_in"],
        "Carga máx": calculos_cc["mppt"][0]["n_max_fl"],
        "Operação": calculos_cc["mppt"][0]["n_max_o"],
    }

    q_max_modulos_str = {k: v for k, v in q_max_raw_str.items() if v != -1 and v is not None}

    menor2 = min(q_max_modulos_str.values())
    cores2 = ["red" if val == menor2 else "blue" for val in q_max_modulos_str.values()]
    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.bar(q_max_modulos_str.keys(), q_max_modulos_str.values(), color=cores2)

    for i, (label, valor) in enumerate(zip(q_max_modulos_str.keys(), q_max_modulos_str.values())):
        ax2.text(i, valor * 0.5, str(valor), ha='center', va='center', color='white', fontsize=10, weight='bold')
    
    ax2.set_title("Quantidade máxima de módulos por string", pad=15)
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    try:
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_limites)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side='left', fill='both', padx=10, pady=10, expand=True)
    except Exception as e:
        messagebox.showerror("Erro ao gerar gráfico", f"Detalhes: {e}")

    # Gráfico #3: Inversor
    q_max_raw_inv = {
        "Circuito aberto": calculos_cc["inv"]["n_max_in"],
        "Carga máx": calculos_cc["inv"]["n_max_fl"],
        "Operação": calculos_cc["inv"]["n_max_o"],
        "Potência\nem sobrecarga": calculos_cc["inv"]["n_max_sb"]
    }

    q_max_modulos_inv = {k: v for k, v in q_max_raw_inv.items() if v != -1 and v is not None}

    menor3 = min(q_max_modulos_inv.values())
    cores3 = ["red" if val == menor3 else "blue" for val in q_max_modulos_inv.values()]
    fig3, ax3 = plt.subplots(figsize=(4, 3))
    ax3.bar(q_max_modulos_inv.keys(), q_max_modulos_inv.values(), color=cores3)

    for i, (label, valor) in enumerate(zip(q_max_modulos_inv.keys(), q_max_modulos_inv.values())):
        ax3.text(i, valor * 0.5, str(valor), ha='center', va='center', color='white', fontsize=10, weight='bold')
    
    ax3.set_title("Quantidade máxima de módulos por inversor", pad=15)
    ax3.yaxis.set_major_locator(MaxNLocator(integer=True))
    try:
        fig3.tight_layout()
        canvas3 = FigureCanvasTkAgg(fig3, master=frame_limites)
        canvas3.draw()
        canvas3.get_tk_widget().pack(side='left', fill='both', padx=10, pady=10, expand=True)
    except Exception as e:
        messagebox.showerror("Erro ao gerar gráfico", f"Detalhes: {e}")

    frame_calculos = ttk.Frame(detalhes_graficos)
    frame_calculos. pack(side='top', fill='x', padx=10, pady=10)
##################################################################################################################################

# Deleta os campos e limpa o campos de saída
def limpar_saidas():

    frame_grafico.pack_forget()
    frame_qtd_modulos.pack_forget()

    for widget in frame_grafico.winfo_children():
        widget.destroy() 
##################################################################################################################################

# Janela auxiliar de detalhes dos inversores e módulos
def open_detalhes(me):
    
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_close():
        # Reabilita o botão de chamada ao fechar
        me.config(state='normal')

        if detalhes.winfo_exists():
            detalhes.unbind("<MouseWheel>")

        detalhes.destroy()

    # Desabilita o botão de chamada
    me.config(state='disabled')

    detalhes = tk.Toplevel(root)
    detalhes.protocol("WM_DELETE_WINDOW", on_close)
    toplevels.append((detalhes, on_close))

    detalhes.configure(background="#e6f2ff") 

    # Vincular evento de rolagem para a janela inteira (detalhes_inv)
    detalhes.bind("<MouseWheel>", _on_mousewheel)
    canvas = tk.Canvas(detalhes)
    scrollbar = ttk.Scrollbar(detalhes, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#e6f2ff", padx=30)
    scrollable_frame.columnconfigure(0, weight=1)
    scrollable_frame.columnconfigure(1, weight=1)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )        
    canvas.create_window((0,0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set, background="#e6f2ff")
    canvas.pack(side='left', fill="both", expand=True)
    scrollbar.pack(side='right', fill='y')
    
    # Coleta o atributo do botão, definido na declaração
    eq = getattr(me, "eq", None)

    if eq not in ['inversor', 'modulo']:
        messagebox.showerror("Erro", "Tipo de equipamento desconhecido.")
        return

    # caso o botão de chamada for identificado como o botão dos detalhes do inversor
    if  eq == "inversor":
        detalhes.title("Detalhes do Inversor")
        detalhes.geometry("358x530+650+0")

        if not inv_selec:
            messagebox.showinfo("Aviso", "Selecione um inversor.")
            on_close()
            return
        
        # Adicionar os Labels e dados
        legenda_labels = [
        # Inversor [0-6]
        "ID", "Fabricante", "Modelo", "Quantidade de MPPTs", "Quantidade de Entradas",
        "Sobrecarga Admitida (%)", "Sistema",
        # Dados de Saída [7-12]
        "Potência de saída nominal (W)", "Potência de saída máx. (W)", "Tensão nominal (Vac)",
        "Corrente nominal (Aac)", "Corrente máx. (Aac)", "Configuração de Rede",
        # MPPT [13-22]
        "Entradas por MPPT", "Tensão mín. de entrada (Vcc)", "Tensão máx. de entrada (Vcc)",
        "Tensão mín. de oper. (Vcc)", "Tensão máx. de oper. (Vcc)", "Tensão mín. de Carga máx. (Vcc)",
        "Tensão máx. de Carga máx. (Vcc)", "Corr. de Curto-Circuito máx. (Acc)",
        "Corrente de oper. máx. (Acc)", "Quantidade de entradas por MPPT",
        # Dados Mecânicos [23-28]
        "Largura (mm)", "Altura (mm)", "Profundidade (mm)", "Peso (kg)", "Refrigeração", "Grau de Proteção"
        ]

        # Procura pelos dados dos inversores no banco de dados
        dicionario_inversor = [
        # Inversor [0-6]
        "ID", "MANUFACTURER_NAME", "MODEL", "NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS",
        "OVERLOAD", "SYSTEM_TYPE",
        # Dados de Saída [7-12]
        "RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER", "RATED_OUTPUT_VOLTAGE", "RATED_OUTPUT_CURRENT",
        "MAX_OUTPUT_CURRENT", "OUTPUT_MODE",
        # MPPT [13-22]
        "NUMBER_OF_INPUTS", "MIN_STARTUP_VOLTAGE", "MAX_INPUT_VOLTAGE",
        "MIN_OPERATING_VOLTAGE", "MAX_OPERATING_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE",
        "MAX_FULL_LOAD_VOLTAGE", "MAX_SHORT_CIRCUIT_CURRENT",
        "MAX_OPERATING_CURRENT", "NUMBER_OF_INPUTS",
        # Dados Mecânicos [23-28]
        "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "COOLING_MODE", "PROTECTION_DEGREE"

        ]

        criar_label(scrollable_frame, "Inversor", 0, 0, style="h1", colspan=2)

        for i, label in enumerate(legenda_labels[:7], start=1):
            txt = inv_selec[dicionario_inversor[i-1]]
            print(txt)
            
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(inv_selec[dicionario_inversor[i-1]]), i, 1, style="table")

        criar_label(scrollable_frame, "", 8, 0) 
        criar_label(scrollable_frame, "Propriedades Elétricas", 9, 0, style="h1", colspan=2)
        criar_label(scrollable_frame, "Dados de saída", 10, 0, style="table", colspan=2)

        for i, label in enumerate(legenda_labels[7:13], start=11):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(inv_selec[dicionario_inversor[i-4]]), i, 1, style="table")

        criar_label(scrollable_frame, "", 17, 0) 
        criar_label(scrollable_frame, "MPPT", 18, 0, style="table", colspan=2)

        for i, label in enumerate(legenda_labels[13:22], start=19):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(inv_selec["MPPT"][0][dicionario_inversor[i-6]]), i, 1, style="table")  

        criar_label(scrollable_frame, "", 28, 0) 
        criar_label(scrollable_frame, "Propriedades Mecânicas", 29, 0, style="h1", colspan=2)       

        # Caso for incluir as temperaturas de operação, elas podem ter valores de temperaturas negativos. Colocar em um bloco separado sem a validação
        for i, label in enumerate(legenda_labels[23:], start=30):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(inv_selec[dicionario_inversor[i-7]]), i, 1, style="table")  

    elif eq == "modulo":
        detalhes.title("Detalhes do Módulo")
        detalhes.geometry("358x530+1008+0")
        # Desabilita o botão de chamada
        me.config(state='disabled') 

        if not mod_selec:
            messagebox.showinfo("Aviso", "Selecione um módulo.")
            on_close()
            return
        
        # Adicionar os Labels e dados
        legenda_labels = [
        # Módulo [0-5]
        "ID", "Fabricante", "Modelo", "Material", "Célula", "Superfície",
        # Dados elétricos [6-10]
        "Potência Nominal (W)", "Voc (Vcc)", "Isc (Acc)", "Vmpp (Vcc)", "Impp (Acc)",
        # Coeficientes de Temperatura [11-13]
        "Coef. temp. PN (%/°C)", "Coef. temp. Voc (%/°C)" , "Coef. temp. Isc (%/°C)",
        # Dados Mecânicos [14-17]
        "Largura (mm)", "Altura (mm)", "Profundidade (mm)", "Peso (kg)"
        ]

        # Procura pelos dados dos inversores no banco de dados
        dicionario_modulo = [
        # Módulo [0-5]
        "ID", "MANUFACTURER_NAME", "MODEL", "SOLAR_CELLS", "CELL_TYPE", "SURFACE_TYPE",
        # Dados eétricos [6-10]
        "WP", "VOC", "ISC", "VMPP", "IMPP",
        # Coeficientes de temperatura [11-13]
        "COEF_PMAX", "COEF_VOC", "COEF_ISC",
        # Dados Mecânicos [14-17]
        "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT"
        ]  

        criar_label(scrollable_frame, "Módulo", 0, 0, style="h1", colspan=2)

        for i, label in enumerate(legenda_labels[:6], start=1):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(mod_selec[dicionario_modulo[i-1]]), i, 1, style="table")

        criar_label(scrollable_frame, "", 7, 0) 
        criar_label(scrollable_frame, "Dados elétricos", 8, 0, style="table", colspan=2)

        for i, label in enumerate(legenda_labels[6:11], start=9):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(mod_selec[dicionario_modulo[i-3]]), i, 1, style="table")

        criar_label(scrollable_frame, "", 14, 0) 
        criar_label(scrollable_frame, "Coeficientes de Temperatura", 15, 0, style="table", colspan=2)

        # Aqui não se pode validar os dados, pois há coeficientes negativos
        for i, label in enumerate(legenda_labels[11:14], start=16):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, mod_selec[dicionario_modulo[i-5]], i, 1, style="table")  

        criar_label(scrollable_frame, "", 19, 0)
        criar_label(scrollable_frame, "Dados Mecânicos", 20, 0, style="table", colspan=2) 

        for i, label in enumerate(legenda_labels[14:], start=21):
            criar_label(scrollable_frame, label, i, 0, style="table")
            criar_label(scrollable_frame, validar(mod_selec[dicionario_modulo[i-7]]), i, 1, style="table")     
##################################################################################################################################
        
# Função para criar ou atualizar o gráfico
def faixa_de_funcionamento(container, 
                               min_operacao, max_operacao, 
                               min_carga_max, max_carga_max, 
                               valor_maximo, largura=500, altura=100):

    container.pack(after=separador1 , fill='x', padx=30, pady=5)
    # Limpar container antes (remove widgets filhos)
    for widget in container.winfo_children():
        widget.destroy()
    
    # Canvas novo
    altura_barras = 30
    espaco_topo = 20
    ttk.Label(container, text="Quantidade de módulos por String", style="h1.TLabel").pack(fill="x", side="top")

    canvas = tk.Canvas(container, width=largura + 50, height=altura + 50, bg="#e6f2ff", bd=0, highlightthickness=0)
    canvas.pack() 

    # Centralizar: definir ponto inicial
    x_offset = 25
    barra_total = largura
    valor_max = valor_maximo

    # Função para converter valor -> posição X
    def valor_para_x(valor):
        return x_offset + (valor / valor_max) * barra_total

    # Desenhar barras
    # Barra vermelha (fundo)
    canvas.create_rectangle(
        valor_para_x(0), espaco_topo, 
        valor_para_x(valor_max), espaco_topo + altura_barras, 
        fill='red', outline='black'
    )

    # Barra amarela (faixa de operação)
    if min_operacao is not None and max_operacao is not None:
        canvas.create_rectangle(
            valor_para_x(min_operacao), espaco_topo, 
            valor_para_x(max_operacao), espaco_topo + altura_barras, 
            fill='yellow', outline='black'
        )

    # Barra verde (faixa de carga máxima)
    if min_carga_max is not None and max_carga_max is not None:
        canvas.create_rectangle(
            valor_para_x(min_carga_max), espaco_topo, 
            valor_para_x(max_carga_max), espaco_topo + altura_barras, 
            fill='green', outline='black'
        )

    # Função para desenhar marcador + label
    def marcador(valor):
        x = valor_para_x(valor)
        canvas.create_line(x, espaco_topo + altura_barras, x, espaco_topo + altura_barras + 20, arrow=tk.LAST)
        canvas.create_text(x, espaco_topo + altura_barras + 35, text=str(valor), font=('Arial', 10, 'bold'))

    # Desenhar marcadores
    for v in [0, min_operacao, min_carga_max, max_carga_max, max_operacao]:
        if v is not None:
            marcador(v)

    # Legenda (na parte de baixo)
    legenda_y = espaco_topo + altura_barras + 60
    canvas.create_rectangle(50, legenda_y, 70, legenda_y + 15, fill='red', outline='black')
    canvas.create_text(80, legenda_y + 7, text="Fora da faixa", anchor='w', font=('Arial', 9))

    canvas.create_rectangle(200, legenda_y, 220, legenda_y + 15, fill='yellow', outline='black')
    canvas.create_text(230, legenda_y + 7, text="Faixa de operação", anchor='w', font=('Arial', 9))

    canvas.create_rectangle(400, legenda_y, 420, legenda_y + 15, fill='green', outline='black')
    canvas.create_text(430, legenda_y + 7, text="Carga máxima", anchor='w', font=('Arial', 9))
##################################################################################################################################

## Funções referentes ao funcionamento da janela ##
# Define o caminho do ícone
def resource_path(relative_path):
    try:
        # Quando empacotado com PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Quando executado como script normal
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
##################################################################################################################################

# Evento de fechamento da janela
def on_close_all():

    for janela, fechar in toplevels:
        try:
            if janela.winfo_exists():
                fechar()
        except:
            pass
    root.destroy()
##################################################################################################################################

# Criar interface Tkinter
root = tk.Tk()
root.iconbitmap(resource_path("optimus_sun.ico"))
root.title("Optimus Sun 2.1.5")
root.configure(background="#e6f2ff")
root.geometry("650x530+0+0")
root.resizable(False, False)

# Estilos
style = ttk.Style()
style.configure("TLabel", padding=2, font=("Trebuchet MS", 10), background="#e6f2ff")
style.configure("h1.TLabel", padding=2, font=("Trebuchet MS", 12, "bold"))
style.configure("table.TLabel", padding=2, font=("Trebuchet MS", 8))
style.configure("TCombobox", padding=3, font=("Trebuchet MS", 10))
style.configure("TEntry", padding=2, font=("Trebuchet MS", 10))
style.configure("TButton", font=("Trebuchet MS", 10))
style.configure("TCanvas", background="#e6f2ff")
style.configure("TScrollbar", background="#e6f2ff")

# Carregar fabricantes antes de criar os widgets
carregar_fabricante()

frame_entrada = tk.Frame(root, bg="#e6f2ff")
frame_entrada.pack(fill="x", padx=10, pady=5)

# Selecionar fabricante do Inversor
criar_label(frame_entrada, "Fabricante do inversor:", 0, 0)
fab_inversor_cb = ttk.Combobox(frame_entrada, values = list(fab_inversor.keys()), state = "readonly")
fab_inversor_cb.grid(row = 0, column = 1, padx = 5, pady = 5)
fab_inversor_cb.bind("<<ComboboxSelected>>", lambda e: carregar_modelo(fab_inversor_cb.get(), "inversor"))

# Selecionar fabricante do Módulo
criar_label(frame_entrada, "Fabricante do módulo:", 0, 2)
fab_modulo_cb = ttk.Combobox(frame_entrada, values = list(fab_modulo.keys()), state = "readonly", width=23)
fab_modulo_cb.grid(row=0, column=3, padx = 5, pady = 5)
fab_modulo_cb.bind("<<ComboboxSelected>>", lambda e: carregar_modelo(fab_modulo_cb.get(), "modulo"))

# Seleção de inversor por modelo
criar_label(frame_entrada, "Selecione o inversor:", 1, 0)
inversor_cb = ttk.Combobox(frame_entrada, state = "readonly")
inversor_cb.grid(row=1, column=1, padx=5, pady=5)
inversor_cb.bind("<<ComboboxSelected>>", lambda e: carregar_dados(inversor_cb.get(), "inversor"))

# Seleção de módulo por modelo
criar_label(frame_entrada, "Selecione o módulo:", 1, 2)
modulo_cb = ttk.Combobox(frame_entrada, state = "readonly", width=23)
modulo_cb.grid(row=1, column=3, padx=5, pady=5)
modulo_cb.bind("<<ComboboxSelected>>", lambda e: carregar_dados(modulo_cb.get(), "modulo"))

#Botão de detalhes do inversor
detalhes_inv_btn = ttk.Button(frame_entrada, text="Detalhes", command=lambda: open_detalhes(detalhes_inv_btn))
detalhes_inv_btn.grid(row=2, column=1, padx=5, pady=5)
detalhes_inv_btn.eq = "inversor"

#Botão de detalhes do modulo
detalhes_mod_btn = ttk.Button(frame_entrada, text="Detalhes", command=lambda: open_detalhes(detalhes_mod_btn))
detalhes_mod_btn.grid(row=2, column=3, padx=5, pady=5)
detalhes_mod_btn.eq = "modulo"

#---------- Separador de frames ----------
separador1 = ttk.Separator(root, orient="horizontal")
separador1.pack(fill='x', padx=10, pady=5)

# Gráfico de quantidade de módulos por string
frame_grafico = tk.Frame(root, bg="#e6f2ff")
frame_grafico.pack(fill="x", padx=30, pady=5)
frame_grafico.pack_forget()

#---------- Separador de frames ----------
separador2 = ttk.Separator(root, orient="horizontal")
separador2.pack(fill='x', padx=10, pady=5)

# Frame onde vai ser especificado a quantidade de módulos e strings máximas a serem ligadas por MPPT
frame_qtd_modulos = tk.Frame(root, bg="#e6f2ff")
frame_qtd_modulos.pack(fill='x', padx=30, pady=5)

ttk.Label(frame_qtd_modulos, text="Potência máxima e Ligação do MPPT", style="h1.TLabel").grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='w')

btn_detalhes_grafico = ttk.Button(frame_qtd_modulos, text="Calculos", command=lambda: open_detalhes_graficos(btn_detalhes_grafico))
btn_detalhes_grafico.grid(row=1, column=0, rowspan=3, padx=5, pady=5, sticky="nsew")

ttk.Label(frame_qtd_modulos, text="Máximo de Strings por MPPT:").grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='w')
entry_series = ttk.Entry(frame_qtd_modulos, width=10, state="readonly")
entry_series.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(frame_qtd_modulos, text="Qtd. máx. de módulos:").grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='w')
entry_modulos = ttk.Entry(frame_qtd_modulos, width=10, state="readonly")
entry_modulos.grid(row=2, column=3, padx=5, pady=5)

ttk.Label(frame_qtd_modulos, text="Sobrecarga admitida:").grid(row=3, column=1, padx=5, pady=5, sticky='w')
entry_sobrecarga = ttk.Entry(frame_qtd_modulos, width=10, state="readonly")
entry_sobrecarga.grid(row=3, column=2, padx=5, pady=5)
entry_sobrecarga_percent = ttk.Entry(frame_qtd_modulos, width=10, state="readonly")
entry_sobrecarga_percent.grid(row=3, column=3, padx=5, pady=5)

frame_qtd_modulos.pack_forget()

frame_img = tk.Frame(root, bg="#e7f2ff")
frame_img.pack(fill='x', padx=30, pady=5)

logo = Image.open(resource_path("logo.png"))
logo_redim = logo.resize((600, 175))
img = ImageTk.PhotoImage(logo_redim)

label_img = tk.Label(frame_img, image=img, bg="#e7f2ff")
label_img.image = img
label_img.pack(fill='x')

# Label fixo no rodapé
rodape = ttk.Label(root, text="Desenvolvido por Pedro Akio Sakuma - Engenharia de Desenvolvimento © 2025", anchor='e', font=("Arial", 8))
rodape.pack(side="bottom", fill='x', pady=(5,3))

root.protocol("WM_DELETE_WINDOW", on_close_all)

print("""
                                                                       ;   :   ;
                                                                    .   \\_,!,_/   ,
                                                                     `.,'     `.,'
                                                                      /         \\
                                                                ~ -- :           : -- ~                                     
   ██████╗ ██████╗ ████████╗██╗███╗   ███╗██╗   ██╗███████╗    ███████╗██╗   ██╗███╗   ██╗    ██╗   ██╗██████╗     ██╗   ███████╗
  ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗ ████║██║   ██║██╔════╝    ██╔════╝██║   ██║████╗  ██║    ██║   ██║╚════██╗   ███║   ██╔════╝
  ██║   ██║██████╔╝   ██║   ██║██╔████╔██║██║   ██║███████╗    ███████╗██║   ██║██╔██╗ ██║    ██║   ██║ █████╔╝   ╚██║   ███████╗
  ██║   ██║██╔═══╝    ██║   ██║██║╚██╔╝██║██║   ██║╚════██║    ╚════██║██║   ██║██║╚██╗██║    ╚██╗ ██╔╝██╔═══╝     ██║   ╚════██║
  ╚██████╔╝██║        ██║   ██║██║ ╚═╝ ██║╚██████╔╝███████║    ███████║╚██████╔╝██║ ╚████║     ╚████╔╝ ███████╗██╗ ██║██╗███████║
   ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝    ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝      ╚═══╝  ╚══════╝╚═╝ ╚═╝╚═╝╚══════╝
        
""")
##################################################################################################################################

root.mainloop()