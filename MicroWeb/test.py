import os
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MicroWeb.settings')
    django.setup()

import time
from wallpaper import models

start = time.clock()
# print(models.Wallpaper.objects.filter(user=models.MicroUser.objects.get(id=1)))
print(models.MicroUser.objects.get(id=1).collects.all())
end = time.clock()
print('Running time: %s Seconds' % (end - start))
