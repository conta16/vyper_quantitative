This is a repository to develop vyper compiler by adding the while construct and implementing a command to obtain symbolic upper bounds. This is not the real repository for vyper's compiler.

The compiler uses KoAT (https://github.com/draperlaboratory/cage-koat) so it needs to be installed in order to use the compiler. Follow the instructions on their repository (you can avoid installing other commands like Kittel, the compiler only uses koat.native)

In order to run the compiler, type the command vyper -f itrs [file_name.vy]
