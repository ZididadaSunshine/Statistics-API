sshpass -p "toxic" scp sw704e18@192.168.1.100:~/snapshot_timer.dat snapshot_timer_r.dat
sshpass -p "toxic" scp sw704e18@192.168.1.100:~/overview_timer.dat overview_timer_r.dat
sshpass -p "doggoeyes" scp bottom@192.168.1.104:~/snapshot_timer.dat snapshot_timer_t.dat
sshpass -p "doggoeyes" scp bottom@192.168.1.104:~/overview_timer.dat overview_timer_t.dat

cat snapshot_timer_* >> snapshot_timer.dat
cat overview_timer_* >> overview_timer.dat

rm overview_timer_*
rm snapshot_timer_*