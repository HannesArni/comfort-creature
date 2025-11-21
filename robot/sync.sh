fswatch . | while read f; do rsync -av . hannesarni@raspberrypi5.local:~/comfort-creature/robot; done
