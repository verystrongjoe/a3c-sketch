import threading
import sub1
import sub2


def sum(low, high):
    total = 0
    for i in range(low, high):
        total += i
    print("Subthread", total)


t = threading.Thread(target=sum, args=(1, 100000))
t.start()

print("Main Thread")